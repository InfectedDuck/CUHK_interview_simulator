import json
from fastapi import APIRouter, HTTPException
from ..database import get_db
from ..config import settings
from ..models.interview import (
    InterviewStartRequest,
    InterviewStartResponse,
    AnswerRequest,
    AnswerResponse,
    AnswerFeedback,
)
from ..services.question_generator import generate_question
from ..services.response_analyzer import analyze_response

router = APIRouter(tags=["interview"])


def _load_profile(row: dict) -> dict:
    """Load profile from DB row, parsing JSON fields."""
    result = {}
    for field in ("education", "skills", "experience", "target_programs", "target_universities"):
        val = row.get(field)
        if val and isinstance(val, str):
            try:
                result[field] = json.loads(val)
            except json.JSONDecodeError:
                result[field] = val
        else:
            result[field] = val
    result["goals"] = row.get("goals")
    return result


@router.post("/interview/start", response_model=InterviewStartResponse)
async def start_interview(data: InterviewStartRequest):
    db = await get_db()
    try:
        # Check user and profile exist
        profile_rows = await db.execute_fetchall(
            "SELECT * FROM profiles WHERE user_id = ?", (data.user_id,)
        )
        if not profile_rows:
            raise HTTPException(
                status_code=400,
                detail="Please create a profile first by recording your introduction.",
            )

        profile = _load_profile(dict(profile_rows[0]))

        # Create session
        cursor = await db.execute(
            "INSERT INTO sessions (user_id, target_university) VALUES (?, ?)",
            (data.user_id, data.target_university),
        )
        await db.commit()
        session_id = cursor.lastrowid

        # Generate first question
        question_text = await generate_question(
            profile=profile,
            university=data.target_university,
            question_number=1,
            total_questions=settings.max_questions_per_session,
        )

        # Store exchange
        await db.execute(
            "INSERT INTO exchanges (session_id, question_number, question_text) VALUES (?, ?, ?)",
            (session_id, 1, question_text),
        )
        await db.commit()

        return InterviewStartResponse(
            session_id=session_id,
            question_number=1,
            question_text=question_text,
        )
    finally:
        await db.close()


@router.post("/interview/{session_id}/answer", response_model=AnswerResponse)
async def submit_answer(session_id: int, data: AnswerRequest):
    db = await get_db()
    try:
        # Get session
        session_rows = await db.execute_fetchall(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        )
        if not session_rows:
            raise HTTPException(status_code=404, detail="Session not found")

        session = dict(session_rows[0])
        if session["status"] == "completed":
            raise HTTPException(status_code=400, detail="Session already completed")

        # Get current unanswered exchange
        exchange_rows = await db.execute_fetchall(
            "SELECT * FROM exchanges WHERE session_id = ? AND answer_text IS NULL ORDER BY question_number LIMIT 1",
            (session_id,),
        )
        if not exchange_rows:
            raise HTTPException(status_code=400, detail="No pending question found")

        exchange = dict(exchange_rows[0])

        # Get profile
        profile_rows = await db.execute_fetchall(
            "SELECT * FROM profiles WHERE user_id = ?", (session["user_id"],)
        )
        profile = _load_profile(dict(profile_rows[0])) if profile_rows else {}

        # Analyze the answer
        analysis = await analyze_response(
            question=exchange["question_text"],
            answer=data.answer_text,
            profile=profile,
            university=session["target_university"],
        )

        # Update exchange with answer and scores
        await db.execute(
            """UPDATE exchanges
            SET answer_text = ?, content_score = ?, relevance_score = ?, clarity_score = ?, feedback = ?
            WHERE id = ?""",
            (
                data.answer_text,
                analysis["content_score"],
                analysis["relevance_score"],
                analysis["clarity_score"],
                analysis["feedback"],
                exchange["id"],
            ),
        )
        await db.commit()

        feedback = AnswerFeedback(**analysis)

        # Check if we need more questions
        current_q = exchange["question_number"]
        max_q = settings.max_questions_per_session

        if current_q < max_q:
            # Generate next question
            next_question_text = await generate_question(
                profile=profile,
                university=session["target_university"],
                question_number=current_q + 1,
                total_questions=max_q,
            )
            await db.execute(
                "INSERT INTO exchanges (session_id, question_number, question_text) VALUES (?, ?, ?)",
                (session_id, current_q + 1, next_question_text),
            )
            await db.commit()

            return AnswerResponse(
                feedback=feedback,
                next_question=InterviewStartResponse(
                    session_id=session_id,
                    question_number=current_q + 1,
                    question_text=next_question_text,
                ),
            )
        else:
            # Session complete - compute overall scores
            all_exchanges = await db.execute_fetchall(
                "SELECT content_score, relevance_score, clarity_score FROM exchanges WHERE session_id = ?",
                (session_id,),
            )
            scores = [dict(e) for e in all_exchanges]
            avg_score = sum(
                (e["content_score"] + e["relevance_score"] + e["clarity_score"]) / 3
                for e in scores
            ) / len(scores)

            # Generate summary feedback
            from ..services import ollama

            summary_prompt = f"""Summarize this student's interview performance in 3-4 sentences.
Overall average score: {avg_score:.1f}/10.
They interviewed for {session['target_university']}.
Provide encouragement and 2-3 key areas for improvement."""

            summary = await ollama.generate(summary_prompt)

            await db.execute(
                """UPDATE sessions
                SET status = 'completed', overall_score = ?, summary_feedback = ?, completed_at = datetime('now')
                WHERE id = ?""",
                (avg_score, summary.strip(), session_id),
            )
            await db.commit()

            return AnswerResponse(
                feedback=feedback,
                session_complete=True,
                overall_score=avg_score,
                summary_feedback=summary.strip(),
            )
    finally:
        await db.close()


@router.post("/interview/{session_id}/end")
async def end_interview_early(session_id: int):
    db = await get_db()
    try:
        session_rows = await db.execute_fetchall(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        )
        if not session_rows:
            raise HTTPException(status_code=404, detail="Session not found")

        session = dict(session_rows[0])
        if session["status"] == "completed":
            return {"message": "Session already completed"}

        # Compute scores from answered exchanges
        answered = await db.execute_fetchall(
            "SELECT content_score, relevance_score, clarity_score FROM exchanges WHERE session_id = ? AND answer_text IS NOT NULL",
            (session_id,),
        )

        avg_score = None
        if answered:
            scores = [dict(e) for e in answered]
            avg_score = sum(
                (e["content_score"] + e["relevance_score"] + e["clarity_score"]) / 3
                for e in scores
            ) / len(scores)

        await db.execute(
            """UPDATE sessions
            SET status = 'completed', overall_score = ?, completed_at = datetime('now')
            WHERE id = ?""",
            (avg_score, session_id),
        )
        await db.commit()

        return {"message": "Session ended", "overall_score": avg_score}
    finally:
        await db.close()
