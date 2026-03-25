from . import ollama

SYSTEM_PROMPT = """You are simulating an admission interviewer for a prestigious Hong Kong university.
Generate realistic, thoughtful interview questions that test critical thinking, self-awareness, and communication.
Return ONLY the question text, nothing else."""

QUESTION_PROMPT = """You are interviewing a student for admission to {university}.

Student profile:
{profile_json}

This is question {question_number} of {total_questions} in the interview.

University interview style guide:
- CUHK: Focus on community involvement, personal growth, and social responsibility.
- HKU: Focus on analytical thinking, global perspective, and leadership.
- HKUST: Focus on innovation, STEM aptitude, and problem-solving.
- PolyU: Focus on practical skills, industry relevance, and professional development.
- CityU: Focus on creativity, interdisciplinary thinking, and urban challenges.

Adjust difficulty: early questions should be warm-up, middle questions should probe deeper, final questions should be challenging.

Generate one interview question appropriate for {university}. Return ONLY the question."""


async def generate_question(
    profile: dict,
    university: str,
    question_number: int,
    total_questions: int,
) -> str:
    import json

    prompt = QUESTION_PROMPT.format(
        university=university,
        profile_json=json.dumps(profile, indent=2),
        question_number=question_number,
        total_questions=total_questions,
    )
    response = await ollama.generate(prompt, system=SYSTEM_PROMPT)
    return response.strip().strip('"')
