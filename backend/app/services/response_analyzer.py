import json
from . import ollama

SYSTEM_PROMPT = """You are an expert interview coach analyzing a student's response to an admission interview question.
You must return ONLY valid JSON with no explanation or markdown formatting."""

ANALYSIS_PROMPT = """Analyze this interview response and score it.

University: {university}
Question: "{question}"
Student's answer: "{answer}"
Student profile: {profile_json}

Score the answer on these criteria (1-10 scale):
- "content_score": How substantive and well-developed is the answer?
- "relevance_score": How well does it address the question asked?
- "clarity_score": How clear and well-communicated is the response?
- "feedback": Specific, actionable suggestions for improvement (2-3 sentences).

Return ONLY a JSON object with these four fields."""


async def analyze_response(
    question: str,
    answer: str,
    profile: dict,
    university: str,
) -> dict:
    prompt = ANALYSIS_PROMPT.format(
        university=university,
        question=question,
        answer=answer,
        profile_json=json.dumps(profile, indent=2),
    )
    response = await ollama.generate(prompt, system=SYSTEM_PROMPT)

    try:
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        result = json.loads(text)
        return {
            "content_score": float(result.get("content_score", 5)),
            "relevance_score": float(result.get("relevance_score", 5)),
            "clarity_score": float(result.get("clarity_score", 5)),
            "feedback": result.get("feedback", "No feedback available."),
        }
    except (json.JSONDecodeError, ValueError):
        return {
            "content_score": 5.0,
            "relevance_score": 5.0,
            "clarity_score": 5.0,
            "feedback": response.strip(),
        }
