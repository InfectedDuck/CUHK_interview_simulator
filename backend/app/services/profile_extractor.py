import json
from . import ollama

SYSTEM_PROMPT = """You are an expert at extracting structured information from conversational text.
A student is introducing themselves for a university admission interview practice session.
You must return ONLY valid JSON with no explanation or markdown formatting."""

EXTRACTION_PROMPT = """Extract the following fields from this student's self-introduction as a JSON object:
- "education": {{"level": "...", "institution": "...", "major": "...", "gpa": "..."}} (null if not mentioned)
- "skills": ["skill1", "skill2", ...]
- "experience": [{{"title": "...", "organization": "...", "description": "..."}}]
- "goals": "string describing their goals"
- "target_programs": ["program1", "program2", ...]
- "target_universities": ["university1", "university2", ...]

If a field is not mentioned, set it to null.
Return ONLY the JSON object.

Student introduction:
"{transcript}"
"""


async def extract_profile(transcript: str) -> dict:
    prompt = EXTRACTION_PROMPT.format(transcript=transcript)
    response = await ollama.generate(prompt, system=SYSTEM_PROMPT)

    # Try to parse JSON from the response
    try:
        # Strip markdown code fences if present
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        return json.loads(text)
    except json.JSONDecodeError:
        # Retry with stricter prompt
        retry_prompt = (
            f"The following text needs to be converted to valid JSON. "
            f"Return ONLY the JSON object, no explanation:\n{response}"
        )
        retry_response = await ollama.generate(retry_prompt, system=SYSTEM_PROMPT)
        text = retry_response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "education": None,
                "skills": None,
                "experience": None,
                "goals": None,
                "target_programs": None,
                "target_universities": None,
                "_raw_response": response,
                "_parse_error": True,
            }
