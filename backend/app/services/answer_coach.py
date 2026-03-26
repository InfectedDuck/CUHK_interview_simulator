"""
Answer Improvement Coach — generates improved versions of student answers
with side-by-side comparison and STAR method breakdown.
"""
import json
from . import ollama

SYSTEM_PROMPT = """You are an expert interview coach who helps students improve their answers.
You must return ONLY valid JSON with no explanation or markdown formatting."""

IMPROVE_PROMPT = """A student answered a CUHK admission interview question. Rewrite their answer to be significantly better while keeping their personal stories and authentic voice.

Question: "{question}"
Original answer: "{answer}"
Student profile: {profile_json}
Original scores: content={content_score}, relevance={relevance_score}, clarity={clarity_score}

Create an improved version that:
1. KEEPS the student's real experiences and stories (do NOT fabricate new ones)
2. Restructures for clarity and impact (strong opening, clear structure, memorable close)
3. Adds specificity where the student was vague (numbers, names, concrete details from their profile)
4. Connects naturally to CUHK values (social responsibility, whole-person development) where appropriate
5. Uses the STAR method (Situation, Task, Action, Result) for experience-based answers

Return a JSON object with:
- "improved_answer": the full rewritten answer (keep similar length, not much longer)
- "key_changes": ["change1", "change2", ...] — list of 3-5 specific improvements made
- "star_breakdown": {{"situation": "...", "task": "...", "action": "...", "result": "..."}} — only if the answer involves a personal experience, null otherwise
"""


def _parse_json(response: str) -> dict | None:
    text = response.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


async def generate_improved_answer(
    question: str,
    answer: str,
    profile: dict,
    scores: dict,
) -> dict:
    prompt = IMPROVE_PROMPT.format(
        question=question,
        answer=answer,
        profile_json=json.dumps(profile, indent=2),
        content_score=scores.get("content_score", "?"),
        relevance_score=scores.get("relevance_score", "?"),
        clarity_score=scores.get("clarity_score", "?"),
    )

    response = await ollama.generate(prompt, system=SYSTEM_PROMPT)
    result = _parse_json(response)

    if result:
        return {
            "improved_answer": result.get("improved_answer", ""),
            "key_changes": result.get("key_changes", []),
            "star_breakdown": result.get("star_breakdown"),
        }

    # Fallback: treat entire response as the improved answer
    return {
        "improved_answer": response.strip(),
        "key_changes": ["Could not parse structured changes"],
        "star_breakdown": None,
    }
