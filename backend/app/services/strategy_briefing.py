"""
Pre-Interview Strategy Briefing — generates personalized coaching report
based on profile, past performance, and CUHK-specific knowledge.
"""
import json
from . import ollama
from .cuhk_knowledge import get_program_context, get_interview_format_info

SYSTEM_PROMPT = """You are a top-tier university admission interview coach preparing a student for their CUHK interview.
You must return ONLY valid JSON with no explanation or markdown formatting."""

BRIEFING_PROMPT = """Generate a personalized pre-interview strategy briefing for a student about to interview at {university} for {program}.

{cuhk_context}

STUDENT PROFILE:
{profile_json}

PAST PERFORMANCE:
{performance_summary}

Create a comprehensive coaching briefing. Return a JSON object with:
- "likely_questions": [
    {{"question": "...", "why_they_ask": "...", "your_angle": "How you specifically should approach this based on your profile"}}
  ] (generate 5-6 likely questions)
- "key_talking_points": [
    {{"topic": "...", "your_story": "A specific story/example from YOUR profile to use", "connection_to_cuhk": "How this connects to CUHK values"}}
  ] (3-4 talking points)
- "areas_to_practice": [
    {{"weakness": "...", "exercise": "A specific practice exercise"}}
  ] (2-3 areas based on past performance, or general tips if no history)
- "dos": ["do1", "do2", ...] (5 specific dos)
- "donts": ["dont1", "dont2", ...] (5 specific don'ts)
- "opening_strategy": "How to make a strong first impression in this specific interview"
- "closing_strategy": "How to end the interview memorably"

Make everything SPECIFIC to this student's profile — no generic advice. Reference their actual experiences, skills, and goals.
Return ONLY the JSON object."""


async def generate_briefing(
    profile: dict,
    university: str,
    program: str,
    past_performance: str = "No previous interview sessions.",
) -> dict:
    cuhk_context = ""
    if "CUHK" in university.upper():
        cuhk_context = get_program_context(program or "General / Undecided")

    prompt = BRIEFING_PROMPT.format(
        university=university,
        program=program or "General Admission",
        cuhk_context=cuhk_context,
        profile_json=json.dumps(profile, indent=2),
        performance_summary=past_performance,
    )

    response = await ollama.generate(prompt, system=SYSTEM_PROMPT)

    text = response.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]

    try:
        result = json.loads(text)
        return result
    except json.JSONDecodeError:
        return {
            "likely_questions": [],
            "key_talking_points": [],
            "areas_to_practice": [],
            "dos": ["Be yourself", "Use specific examples", "Show genuine enthusiasm"],
            "donts": ["Don't memorize answers", "Don't be arrogant", "Don't speak too fast"],
            "opening_strategy": "Start with a warm greeting and be ready to introduce yourself concisely.",
            "closing_strategy": "Thank the interviewer and mention something specific about CUHK that excites you.",
            "_raw_response": response.strip()[:500],
        }


def get_format_briefing(university: str, program: str) -> dict:
    """Get non-AI interview format information (instant, no Ollama needed)."""
    if "CUHK" in university.upper():
        return get_interview_format_info(program or "General / Undecided")
    return {
        "faculty": "General",
        "program": program or "General",
        "format": "Individual interview, approximately 15-20 minutes.",
        "competencies": ["Communication", "Critical thinking", "Self-awareness"],
        "tips": "Be authentic and specific in your responses.",
        "what_they_value": "Well-rounded individuals with genuine passion.",
    }
