import json
import re
from . import ollama
from .cuhk_knowledge import get_scoring_rubric

SYSTEM_PROMPT = """You are a STRICT and HONEST interview coach scoring a student's response.
You must return ONLY valid JSON with no explanation or markdown formatting.
You are NOT generous. You give low scores when deserved. A bad answer gets 1-3, not 5."""

ANALYSIS_PROMPT = """Score this interview response STRICTLY and HONESTLY.

University: {university}
Program: {program}
Question: "{question}"
Student's answer: "{answer}"

STRICT SCORING RULES (1-10 scale):
- 1-2: Gibberish, random characters, completely off-topic, or essentially empty/meaningless
- 3-4: Very weak — vague, generic, no substance, doesn't address the question
- 5-6: Mediocre — partially addresses the question but lacks depth, specifics, or structure
- 7-8: Good — clear, relevant, has specific examples and reasonable depth
- 9-10: Excellent — outstanding structure, compelling examples, deep insight, memorable

CRITICAL: If the answer is random text, gibberish, extremely short (under 10 words with no meaning), or completely unrelated to the question, ALL scores MUST be 1-2. Do NOT be generous with bad answers.

Student profile (for context only): {profile_json}

{cuhk_rubric}

Score on these criteria:
- "content_score": How substantive and well-developed? (gibberish = 1)
- "relevance_score": How well does it address the question? (off-topic/gibberish = 1)
- "clarity_score": How clear and well-communicated? (incoherent = 1)
{extra_scoring}
- "feedback": Specific, actionable suggestions. If the answer is gibberish or empty, say so directly — don't sugarcoat.

Return ONLY a JSON object with these fields."""

SIMULATION_TIME_SCORING = """- "time_management_score": Score 1-10 based on response time of {time}s. Under 10s is too short (rushing). 30-90s is ideal. Over 120s is too long (rambling). Penalize extremes."""


def _parse_json(response: str) -> dict | None:
    text = response.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _is_gibberish(text: str) -> bool:
    """Detect obviously nonsensical input before sending to LLM."""
    cleaned = text.strip()
    # Too short to be meaningful
    if len(cleaned) < 5:
        return True
    # Mostly non-alphabetic characters
    alpha_chars = sum(1 for c in cleaned if c.isalpha())
    if len(cleaned) > 0 and alpha_chars / len(cleaned) < 0.4:
        return True
    # Check if it has at least 3 real words (2+ chars each)
    words = [w for w in re.findall(r'[a-zA-Z]+', cleaned) if len(w) >= 2]
    if len(words) < 3:
        return True
    # Very short answers (under 15 chars) are likely not meaningful
    if len(cleaned) < 15:
        return True
    return False


def _gibberish_response(answer: str) -> dict:
    """Return minimum scores for gibberish/empty answers."""
    return {
        "content_score": 1.0,
        "relevance_score": 1.0,
        "clarity_score": 1.0,
        "values_alignment_score": None,
        "self_awareness_score": None,
        "time_management_score": None,
        "feedback": f"Your answer ('{answer[:50]}') does not appear to be a meaningful response. Please provide a real answer that addresses the interview question. Speak clearly about your experiences, motivations, and goals.",
    }


async def analyze_response(
    question: str,
    answer: str,
    profile: dict,
    university: str,
    program: str | None = None,
    response_time: float | None = None,
    mode: str = "practice",
) -> dict:
    # Pre-check: catch obvious gibberish before wasting an LLM call
    if _is_gibberish(answer):
        return _gibberish_response(answer)

    # Build CUHK-specific rubric if applicable
    cuhk_rubric = ""
    extra_scoring = ""
    if "CUHK" in university.upper() and program:
        cuhk_rubric = get_scoring_rubric(program)
        extra_scoring = '- "values_alignment_score": How well does the answer reflect CUHK values?\n- "self_awareness_score": Does the student show genuine self-reflection?'

    if mode == "simulation" and response_time is not None:
        extra_scoring += "\n" + SIMULATION_TIME_SCORING.format(time=response_time)

    prompt = ANALYSIS_PROMPT.format(
        university=university,
        program=program or "General",
        question=question,
        answer=answer,
        profile_json=json.dumps(profile, indent=2),
        cuhk_rubric=cuhk_rubric,
        extra_scoring=extra_scoring,
    )
    response = await ollama.generate(prompt, system=SYSTEM_PROMPT)

    result = _parse_json(response)
    if result:
        return {
            "content_score": float(result.get("content_score", 1)),
            "relevance_score": float(result.get("relevance_score", 1)),
            "clarity_score": float(result.get("clarity_score", 1)),
            "values_alignment_score": float(result["values_alignment_score"]) if "values_alignment_score" in result else None,
            "self_awareness_score": float(result["self_awareness_score"]) if "self_awareness_score" in result else None,
            "time_management_score": float(result["time_management_score"]) if "time_management_score" in result else None,
            "feedback": result.get("feedback", "No feedback available."),
        }

    # Fallback: if LLM fails to return JSON, give low scores (not 5)
    return {
        "content_score": 2.0,
        "relevance_score": 2.0,
        "clarity_score": 2.0,
        "values_alignment_score": None,
        "self_awareness_score": None,
        "time_management_score": None,
        "feedback": response.strip() or "Unable to analyze response. Please try again with a more detailed answer.",
    }
