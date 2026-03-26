import json
from . import ollama

SYSTEM_PROMPT = """You are an expert at extracting structured information from text.
A student is preparing for a university admission interview practice session.
You must return ONLY valid JSON with no explanation or markdown formatting."""

JSON_FIELDS = """- "education": {{"level": "...", "institution": "...", "major": "...", "gpa": "..."}} (null if not mentioned)
- "skills": ["skill1", "skill2", ...]
- "experience": [{{"title": "...", "organization": "...", "description": "..."}}]
- "projects": [{{"name": "project name", "description": "what the project does", "technologies": ["tech1", "tech2"], "role": "your role/contribution", "outcome": "results or impact"}}] — extract ALL projects, personal projects, academic projects, hackathon projects, etc. Include as much detail as possible about each project.
- "goals": "string describing their goals"
- "target_programs": ["program1", "program2", ...]
- "target_universities": ["university1", "university2", ...]
- "achievements": ["achievement1", "achievement2", ...]
- "interests": ["interest1", "interest2", ...]
- "personality_traits": ["trait1", "trait2", ...]"""

EXTRACTION_PROMPT = """Extract the following fields from this student's self-introduction as a JSON object:
{fields}

If a field is not mentioned, set it to null.
Return ONLY the JSON object.

Student introduction:
"{transcript}"
"""

DOCUMENT_PROMPT = """Analyze this document (a {doc_type}) and extract structured information about the student as a JSON object:
{fields}

If a field is not found in the document, set it to null.
For CVs/resumes: pay special attention to PROJECTS — extract every project with its name, description, technologies used, the student's role, and outcomes/impact. Do not skip any projects.
For essays, also infer personality_traits and interests from the writing style and content.
Return ONLY the JSON object.

Document content:
\"\"\"{content}\"\"\"
"""

MERGE_PROMPT = """You have two JSON profiles for the same student. Merge them into one comprehensive profile.
Keep ALL information from both — do not drop anything. If both have values for a field, combine them (merge lists, pick the more detailed object).

Return ONLY a valid JSON object with these fields:
{fields}

Profile A (existing):
{profile_a}

Profile B (new document):
{profile_b}
"""


def _parse_json_response(response: str) -> dict | None:
    """Try to parse JSON from LLM response, stripping markdown fences."""
    text = response.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _empty_profile() -> dict:
    return {
        "education": None, "skills": None, "experience": None, "projects": None,
        "goals": None, "target_programs": None, "target_universities": None,
        "achievements": None, "interests": None, "personality_traits": None,
    }


async def _extract_with_retry(prompt: str) -> dict:
    response = await ollama.generate(prompt, system=SYSTEM_PROMPT)
    result = _parse_json_response(response)
    if result:
        return result

    # Retry with stricter prompt
    retry_prompt = (
        f"The following text needs to be converted to valid JSON. "
        f"Return ONLY the JSON object, no explanation:\n{response}"
    )
    retry_response = await ollama.generate(retry_prompt, system=SYSTEM_PROMPT)
    result = _parse_json_response(retry_response)
    if result:
        return result

    fallback = _empty_profile()
    fallback["_raw_response"] = response
    fallback["_parse_error"] = True
    return fallback


async def extract_profile(transcript: str) -> dict:
    prompt = EXTRACTION_PROMPT.format(fields=JSON_FIELDS, transcript=transcript)
    return await _extract_with_retry(prompt)


async def extract_from_document(content: str, doc_type: str = "document") -> dict:
    prompt = DOCUMENT_PROMPT.format(
        fields=JSON_FIELDS, content=content, doc_type=doc_type
    )
    return await _extract_with_retry(prompt)


async def merge_profiles(existing: dict, new_data: dict) -> dict:
    prompt = MERGE_PROMPT.format(
        fields=JSON_FIELDS,
        profile_a=json.dumps(existing, indent=2),
        profile_b=json.dumps(new_data, indent=2),
    )
    return await _extract_with_retry(prompt)
