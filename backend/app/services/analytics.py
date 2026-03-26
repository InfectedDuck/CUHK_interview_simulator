"""
Cross-session analytics — progress tracking, weakness detection, and practice suggestions.
"""
import json
from . import ollama


async def get_progress_summary(db, user_id: int) -> dict:
    """Compute cross-session trends and category averages."""
    sessions = await db.execute_fetchall(
        "SELECT * FROM sessions WHERE user_id = ? AND status = 'completed' ORDER BY started_at",
        (user_id,),
    )

    if not sessions:
        return {"sessions_completed": 0, "trends": [], "category_averages": {}}

    trends = []
    all_content = []
    all_relevance = []
    all_clarity = []

    for s in sessions:
        s = dict(s)
        exchanges = await db.execute_fetchall(
            "SELECT * FROM exchanges WHERE session_id = ? AND answer_text IS NOT NULL",
            (s["id"],),
        )
        exchanges = [dict(e) for e in exchanges]

        if not exchanges:
            continue

        content_avg = sum(e["content_score"] for e in exchanges if e["content_score"]) / len(exchanges)
        relevance_avg = sum(e["relevance_score"] for e in exchanges if e["relevance_score"]) / len(exchanges)
        clarity_avg = sum(e["clarity_score"] for e in exchanges if e["clarity_score"]) / len(exchanges)

        all_content.append(content_avg)
        all_relevance.append(relevance_avg)
        all_clarity.append(clarity_avg)

        trends.append({
            "session_id": s["id"],
            "date": s["started_at"],
            "university": s["target_university"],
            "program": s.get("target_program"),
            "overall_score": s.get("overall_score"),
            "content_avg": round(content_avg, 1),
            "relevance_avg": round(relevance_avg, 1),
            "clarity_avg": round(clarity_avg, 1),
        })

    # Calculate improvement velocity (compare first half to second half)
    improvement = {}
    if len(all_content) >= 2:
        mid = len(all_content) // 2
        for name, scores in [("content", all_content), ("relevance", all_relevance), ("clarity", all_clarity)]:
            first_half = sum(scores[:mid]) / mid
            second_half = sum(scores[mid:]) / (len(scores) - mid)
            improvement[name] = round(((second_half - first_half) / max(first_half, 1)) * 100, 1)

    return {
        "sessions_completed": len(trends),
        "trends": trends,
        "category_averages": {
            "content": round(sum(all_content) / len(all_content), 1) if all_content else 0,
            "relevance": round(sum(all_relevance) / len(all_relevance), 1) if all_relevance else 0,
            "clarity": round(sum(all_clarity) / len(all_clarity), 1) if all_clarity else 0,
        },
        "improvement_velocity": improvement,
    }


async def detect_weakness_patterns(db, user_id: int) -> list[dict]:
    """Analyze all low-scoring answers to find recurring weakness patterns."""
    exchanges = await db.execute_fetchall(
        """SELECT e.*, s.target_university, s.target_program
        FROM exchanges e
        JOIN sessions s ON e.session_id = s.id
        WHERE s.user_id = ? AND e.answer_text IS NOT NULL
        AND (e.content_score < 6 OR e.relevance_score < 6 OR e.clarity_score < 6)
        ORDER BY e.created_at""",
        (user_id,),
    )

    if not exchanges:
        return []

    # Build a summary of weak answers for Ollama analysis
    weak_answers = []
    for e in exchanges:
        e = dict(e)
        weak_answers.append(
            f"Q: {e['question_text']}\n"
            f"A: {e['answer_text'][:200]}\n"
            f"Scores: content={e['content_score']}, relevance={e['relevance_score']}, clarity={e['clarity_score']}\n"
            f"Feedback: {e.get('feedback', 'N/A')}"
        )

    prompt = f"""Analyze these weak interview answers from the same student and identify 3-5 recurring patterns or weaknesses.

{chr(10).join(weak_answers[:10])}

Return a JSON array of weakness patterns. Each item should have:
- "pattern": A short name for the weakness (e.g., "Lacks specific examples")
- "description": 1-2 sentence explanation
- "frequency": How many answers show this pattern
- "practice_suggestion": What the student should practice to fix this

Return ONLY the JSON array."""

    response = await ollama.generate(prompt)
    text = response.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return [{"pattern": "Analysis unavailable", "description": response.strip()[:200], "frequency": 0, "practice_suggestion": "Continue practicing"}]


async def get_strengths(db, user_id: int) -> list[dict]:
    """Analyze high-scoring answers to identify strengths."""
    exchanges = await db.execute_fetchall(
        """SELECT e.*
        FROM exchanges e
        JOIN sessions s ON e.session_id = s.id
        WHERE s.user_id = ? AND e.answer_text IS NOT NULL
        AND e.content_score >= 7 AND e.relevance_score >= 7 AND e.clarity_score >= 7
        ORDER BY e.created_at""",
        (user_id,),
    )

    if not exchanges:
        return []

    strong_answers = []
    for e in exchanges:
        e = dict(e)
        strong_answers.append(
            f"Q: {e['question_text']}\nA: {e['answer_text'][:200]}\n"
            f"Scores: content={e['content_score']}, relevance={e['relevance_score']}, clarity={e['clarity_score']}"
        )

    prompt = f"""Analyze these strong interview answers and identify 2-4 strengths this student consistently demonstrates.

{chr(10).join(strong_answers[:8])}

Return a JSON array. Each item: {{"strength": "name", "description": "explanation"}}
Return ONLY the JSON array."""

    response = await ollama.generate(prompt)
    text = response.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return []
