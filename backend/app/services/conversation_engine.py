"""
Conversational Interview Engine — generates context-aware questions
that reference previous answers, probe deeper, and adapt difficulty.
"""
import json
from . import ollama
from .cuhk_knowledge import get_program_context

SYSTEM_PROMPT = """You are a skilled admission interviewer at a prestigious Hong Kong university.
You conduct natural, conversational interviews that flow logically.
You listen carefully to student answers and ask thoughtful follow-up questions.
You are warm but probing — you want to understand the student deeply.
Return ONLY the question text, nothing else. No quotes, no preamble."""

QUESTION_PROMPT = """You are conducting an admission interview for {university} ({program}).

{cuhk_context}

STUDENT PROFILE:
{profile_json}

{projects_context}

INTERVIEW SO FAR:
{conversation_history}

CURRENT STATE:
- This is question {question_number} in the interview
- Question strategy: {strategy}
- Difficulty level: {difficulty}
- {strategy_instruction}

{difficulty_instruction}

IMPORTANT: The student's profile includes their PROJECTS. You should ask about specific projects — what motivated them, technical challenges they faced, what they learned, how it connects to their goals. Reference project names and details directly.

Generate ONE natural interview question. {strategy_detail}
Return ONLY the question text."""


def _build_conversation_history(exchanges: list[dict]) -> str:
    """Format previous exchanges into a readable conversation transcript."""
    if not exchanges:
        return "(This is the first question — no conversation yet)"

    lines = []
    for ex in exchanges:
        lines.append(f"Q{ex['question_number']} [{ex.get('question_type', 'question')}]: {ex['question_text']}")
        if ex.get("answer_text"):
            lines.append(f"Student: {ex['answer_text']}")
            scores = []
            if ex.get("content_score") is not None:
                scores.append(f"content={ex['content_score']}")
            if ex.get("relevance_score") is not None:
                scores.append(f"relevance={ex['relevance_score']}")
            if ex.get("clarity_score") is not None:
                scores.append(f"clarity={ex['clarity_score']}")
            if scores:
                lines.append(f"[Scores: {', '.join(scores)}]")
            if ex.get("feedback"):
                lines.append(f"[Coach note: {ex['feedback']}]")
        lines.append("")
    return "\n".join(lines)


def _determine_strategy(
    question_number: int,
    max_questions: int,
    exchanges: list[dict],
) -> tuple[str, str, str]:
    """
    Determine question strategy based on position and previous answer quality.
    Returns (strategy_name, instruction, detail).
    """
    if question_number == 1:
        return (
            "warmup",
            "Start with a warm, open-ended question to put the student at ease.",
            "Make it welcoming and broad enough for the student to showcase themselves. Reference something from their profile if possible.",
        )

    # Look at the most recent answered exchange
    last_answered = None
    for ex in reversed(exchanges):
        if ex.get("answer_text"):
            last_answered = ex
            break

    if not last_answered:
        return (
            "warmup",
            "Ask a general warm-up question.",
            "The student hasn't answered yet, so start gently.",
        )

    avg_score = 0
    score_count = 0
    for key in ("content_score", "relevance_score", "clarity_score"):
        if last_answered.get(key) is not None:
            avg_score += last_answered[key]
            score_count += 1
    avg_score = avg_score / max(score_count, 1)

    # Final question
    if question_number >= max_questions:
        return (
            "closing",
            "This is the final question. Ask something forward-looking or reflective.",
            "Ask about their vision, what they'd contribute to CUHK, or give them a chance to address anything they haven't mentioned. Make it memorable.",
        )

    # Low score → follow-up probe
    if avg_score < 5:
        return (
            "follow_up",
            f"The student's previous answer was weak (avg {avg_score:.1f}/10). Ask a follow-up to help them elaborate.",
            f"Reference something specific from their previous answer and give them a chance to go deeper. Be encouraging, not challenging. Their last answer was about: '{last_answered['answer_text'][:100]}...'",
        )

    # Medium score → clarifying question
    if avg_score < 7:
        return (
            "probe",
            f"The student's previous answer was decent (avg {avg_score:.1f}/10) but could be deeper. Probe for specifics.",
            f"Pick one interesting thing from their answer and ask them to elaborate with a concrete example or deeper reflection. Their last answer mentioned: '{last_answered['answer_text'][:100]}...'",
        )

    # High score → advance to new topic, increase challenge
    progress = question_number / max_questions
    if progress < 0.5:
        return (
            "challenge",
            f"The student is performing well (avg {avg_score:.1f}/10). Advance to a more challenging topic.",
            "Ask a thought-provoking question that tests deeper critical thinking. You can reference their strong previous answer as a springboard to a harder topic.",
        )

    return (
        "challenge",
        f"The student is performing well. Ask a challenging question appropriate for the late stage of the interview.",
        "Push them intellectually. Ask about trade-offs, ethical gray areas, or hypothetical scenarios relevant to their program.",
    )


DIFFICULTY_INSTRUCTIONS = {
    "easy": "DIFFICULTY: EASY. Ask straightforward, encouraging questions. Use simple vocabulary. Focus on the student's strengths and let them talk about what they're passionate about. Be warm and supportive.",
    "medium": "DIFFICULTY: MEDIUM. Ask balanced questions that probe for depth but remain fair. Expect reasonable specificity and some critical thinking.",
    "hard": "DIFFICULTY: HARD. Be a tough interviewer. Ask multi-layered questions. Play devil's advocate. Challenge assumptions. Expect nuanced, well-reasoned answers with concrete evidence. Push the student to think on their feet.",
}


async def generate_next_question(
    profile: dict,
    university: str,
    program: str,
    question_number: int,
    max_questions: int,
    exchanges: list[dict],
    difficulty: str = "medium",
) -> tuple[str, str]:
    """
    Generate the next interview question with full conversation context.
    Returns (question_text, question_type).
    """
    strategy, instruction, detail = _determine_strategy(
        question_number, max_questions, exchanges
    )

    cuhk_context = ""
    if "CUHK" in university.upper():
        cuhk_context = get_program_context(program or "General / Undecided")

    conversation_history = _build_conversation_history(exchanges)

    # Build projects context for targeted project questions
    projects_context = ""
    if profile.get("projects"):
        projects_list = []
        for p in profile["projects"]:
            if isinstance(p, dict):
                name = p.get("name", "Unnamed")
                desc = p.get("description", "")
                techs = ", ".join(p.get("technologies", [])) if p.get("technologies") else ""
                role = p.get("role", "")
                outcome = p.get("outcome", "")
                projects_list.append(
                    f"- {name}: {desc}"
                    + (f" [Tech: {techs}]" if techs else "")
                    + (f" [Role: {role}]" if role else "")
                    + (f" [Outcome: {outcome}]" if outcome else "")
                )
        if projects_list:
            projects_context = "STUDENT'S PROJECTS (ask about these!):\n" + "\n".join(projects_list)

    prompt = QUESTION_PROMPT.format(
        university=university,
        program=program or "General Admission",
        cuhk_context=cuhk_context,
        profile_json=json.dumps(profile, indent=2),
        projects_context=projects_context,
        conversation_history=conversation_history,
        question_number=question_number,
        strategy=strategy,
        difficulty=difficulty,
        difficulty_instruction=DIFFICULTY_INSTRUCTIONS.get(difficulty, DIFFICULTY_INSTRUCTIONS["medium"]),
        strategy_instruction=instruction,
        strategy_detail=detail,
    )

    response = await ollama.generate(prompt, system=SYSTEM_PROMPT)
    question_text = response.strip().strip('"').strip("'")

    return question_text, strategy


def should_add_followup(
    exchanges: list[dict],
    current_max: int,
    absolute_max: int = 8,
) -> bool:
    """Decide if the session should be extended with a follow-up question."""
    if current_max >= absolute_max:
        return False

    # Count how many follow-ups we've already added
    followups = sum(1 for ex in exchanges if ex.get("question_type") in ("follow_up", "probe"))
    if followups >= 3:
        return False

    # Check if the last answer was weak enough to warrant a follow-up
    last = None
    for ex in reversed(exchanges):
        if ex.get("answer_text"):
            last = ex
            break

    if not last:
        return False

    avg = 0
    count = 0
    for key in ("content_score", "relevance_score", "clarity_score"):
        if last.get(key) is not None:
            avg += last[key]
            count += 1

    return count > 0 and (avg / count) < 4.5
