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
from ..services.conversation_engine import generate_next_question, should_add_followup
from ..services.response_analyzer import analyze_response
from ..services.answer_coach import generate_improved_answer

router = APIRouter(tags=["interview"])

PROFILE_JSON_FIELDS = (
    "education", "skills", "experience", "projects", "target_programs",
    "target_universities", "achievements", "interests", "personality_traits",
)


def _load_profile(row: dict) -> dict:
    """Load profile from DB row, parsing JSON fields."""
    result = {}
    for field in PROFILE_JSON_FIELDS:
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


async def _load_exchanges(db, session_id: int) -> list[dict]:
    """Load all exchanges for a session."""
    rows = await db.execute_fetchall(
        "SELECT * FROM exchanges WHERE session_id = ? ORDER BY question_number",
        (session_id,),
    )
    return [dict(r) for r in rows]


@router.post("/interview/start", response_model=InterviewStartResponse)
async def start_interview(data: InterviewStartRequest):
    db = await get_db()
    try:
        profile_rows = await db.execute_fetchall(
            "SELECT * FROM profiles WHERE user_id = ?", (data.user_id,)
        )
        if not profile_rows:
            raise HTTPException(
                status_code=400,
                detail="Please create a profile first by recording your introduction.",
            )

        profile = _load_profile(dict(profile_rows[0]))
        mode = getattr(data, "mode", "practice") or "practice"
        difficulty = getattr(data, "difficulty", "medium") or "medium"
        program = getattr(data, "target_program", None)
        max_q = settings.max_questions_per_session

        # Create session
        cursor = await db.execute(
            "INSERT INTO sessions (user_id, target_university, target_program, mode, difficulty, max_questions) VALUES (?, ?, ?, ?, ?, ?)",
            (data.user_id, data.target_university, program, mode, difficulty, max_q),
        )
        await db.commit()
        session_id = cursor.lastrowid

        # Generate first question using conversation engine
        question_text, question_type = await generate_next_question(
            profile=profile,
            university=data.target_university,
            program=program,
            question_number=1,
            max_questions=max_q,
            exchanges=[],
            difficulty=difficulty,
        )

        # Store exchange with question type
        await db.execute(
            "INSERT INTO exchanges (session_id, question_number, question_text, question_type, started_at) VALUES (?, ?, ?, ?, datetime('now'))",
            (session_id, 1, question_text, question_type),
        )
        await db.commit()

        return InterviewStartResponse(
            session_id=session_id,
            question_number=1,
            question_text=question_text,
            question_type=question_type,
            max_questions=max_q,
            mode=mode,
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

        mode = session.get("mode", "practice")
        program = session.get("target_program")

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
        response_time = getattr(data, "response_time_seconds", None)
        analysis = await analyze_response(
            question=exchange["question_text"],
            answer=data.answer_text,
            profile=profile,
            university=session["target_university"],
            program=program,
            response_time=response_time,
            mode=mode,
        )

        # Update exchange with answer and all scores
        await db.execute(
            """UPDATE exchanges
            SET answer_text = ?, content_score = ?, relevance_score = ?, clarity_score = ?,
                values_alignment_score = ?, self_awareness_score = ?, time_management_score = ?,
                feedback = ?, response_time_seconds = ?
            WHERE id = ?""",
            (
                data.answer_text,
                analysis["content_score"],
                analysis["relevance_score"],
                analysis["clarity_score"],
                analysis.get("values_alignment_score"),
                analysis.get("self_awareness_score"),
                analysis.get("time_management_score"),
                analysis["feedback"],
                response_time,
                exchange["id"],
            ),
        )
        await db.commit()

        feedback = AnswerFeedback(
            content_score=analysis["content_score"],
            relevance_score=analysis["relevance_score"],
            clarity_score=analysis["clarity_score"],
            values_alignment_score=analysis.get("values_alignment_score"),
            self_awareness_score=analysis.get("self_awareness_score"),
            time_management_score=analysis.get("time_management_score"),
            feedback=analysis["feedback"],
        )

        # Load all exchanges for conversation context
        all_exchanges = await _load_exchanges(db, session_id)
        current_q = exchange["question_number"]
        max_q = session.get("max_questions") or settings.max_questions_per_session

        # Check if session should be extended with follow-up
        if current_q >= max_q and should_add_followup(all_exchanges, max_q):
            max_q += 1
            await db.execute(
                "UPDATE sessions SET max_questions = ? WHERE id = ?",
                (max_q, session_id),
            )
            await db.commit()

        if current_q < max_q:
            # Generate next question with full conversation context
            next_question_text, next_question_type = await generate_next_question(
                profile=profile,
                university=session["target_university"],
                program=program,
                question_number=current_q + 1,
                max_questions=max_q,
                exchanges=all_exchanges,
                difficulty=session.get("difficulty", "medium"),
            )
            await db.execute(
                "INSERT INTO exchanges (session_id, question_number, question_text, question_type, started_at) VALUES (?, ?, ?, ?, datetime('now'))",
                (session_id, current_q + 1, next_question_text, next_question_type),
            )
            await db.commit()

            return AnswerResponse(
                feedback=feedback,
                next_question=InterviewStartResponse(
                    session_id=session_id,
                    question_number=current_q + 1,
                    question_text=next_question_text,
                    question_type=next_question_type,
                    max_questions=max_q,
                    mode=mode,
                ),
            )
        else:
            # Session complete
            answered = [e for e in all_exchanges if e.get("content_score") is not None]
            avg_score = sum(
                (e["content_score"] + e["relevance_score"] + e["clarity_score"]) / 3
                for e in answered
            ) / max(len(answered), 1)

            from ..services import ollama
            summary_prompt = f"""Summarize this student's CUHK {program or ''} admission interview performance in 3-4 sentences.
Overall average score: {avg_score:.1f}/10. They answered {len(answered)} questions.
Provide encouragement and 2-3 key areas for improvement. Be specific, referencing patterns from their answers."""

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


@router.post("/interview/{session_id}/exchange/{exchange_id}/improve")
async def improve_answer(session_id: int, exchange_id: int):
    """Generate an improved version of the student's answer (on-demand)."""
    db = await get_db()
    try:
        exchange_rows = await db.execute_fetchall(
            "SELECT * FROM exchanges WHERE id = ? AND session_id = ?",
            (exchange_id, session_id),
        )
        if not exchange_rows:
            raise HTTPException(status_code=404, detail="Exchange not found")

        exchange = dict(exchange_rows[0])
        if not exchange.get("answer_text"):
            raise HTTPException(status_code=400, detail="No answer to improve")

        # Return cached if already generated
        if exchange.get("improved_answer"):
            return {
                "improved_answer": exchange["improved_answer"],
                "key_changes": json.loads(exchange["key_changes"]) if exchange.get("key_changes") else [],
                "star_breakdown": json.loads(exchange["star_breakdown"]) if exchange.get("star_breakdown") else None,
            }

        # Get profile
        session_rows = await db.execute_fetchall(
            "SELECT user_id FROM sessions WHERE id = ?", (session_id,)
        )
        profile_rows = await db.execute_fetchall(
            "SELECT * FROM profiles WHERE user_id = ?", (dict(session_rows[0])["user_id"],)
        )
        profile = _load_profile(dict(profile_rows[0])) if profile_rows else {}

        result = await generate_improved_answer(
            question=exchange["question_text"],
            answer=exchange["answer_text"],
            profile=profile,
            scores={
                "content_score": exchange.get("content_score"),
                "relevance_score": exchange.get("relevance_score"),
                "clarity_score": exchange.get("clarity_score"),
            },
        )

        # Cache the result
        await db.execute(
            "UPDATE exchanges SET improved_answer = ?, key_changes = ?, star_breakdown = ? WHERE id = ?",
            (
                result["improved_answer"],
                json.dumps(result["key_changes"]),
                json.dumps(result["star_breakdown"]) if result["star_breakdown"] else None,
                exchange_id,
            ),
        )
        await db.commit()

        return result
    finally:
        await db.close()


@router.post("/interview/{session_id}/replay/{exchange_id}")
async def replay_answer(session_id: int, exchange_id: int, data: AnswerRequest):
    """Re-answer a question and get re-scored with delta comparison."""
    db = await get_db()
    try:
        exchange_rows = await db.execute_fetchall(
            "SELECT * FROM exchanges WHERE id = ? AND session_id = ?",
            (exchange_id, session_id),
        )
        if not exchange_rows:
            raise HTTPException(status_code=404, detail="Exchange not found")

        exchange = dict(exchange_rows[0])

        session_rows = await db.execute_fetchall(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        )
        session = dict(session_rows[0])

        profile_rows = await db.execute_fetchall(
            "SELECT * FROM profiles WHERE user_id = ?", (session["user_id"],)
        )
        profile = _load_profile(dict(profile_rows[0])) if profile_rows else {}

        # Analyze the new answer
        analysis = await analyze_response(
            question=exchange["question_text"],
            answer=data.answer_text,
            profile=profile,
            university=session["target_university"],
            program=session.get("target_program"),
        )

        # Get attempt number
        retries = await db.execute_fetchall(
            "SELECT MAX(attempt_number) as max_attempt FROM exchange_retries WHERE exchange_id = ?",
            (exchange_id,),
        )
        attempt = (dict(retries[0])["max_attempt"] or 0) + 1

        # Store retry
        await db.execute(
            """INSERT INTO exchange_retries
            (exchange_id, attempt_number, answer_text, content_score, relevance_score, clarity_score, feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                exchange_id, attempt, data.answer_text,
                analysis["content_score"], analysis["relevance_score"],
                analysis["clarity_score"], analysis["feedback"],
            ),
        )
        await db.commit()

        # Compute deltas from original
        return {
            "attempt_number": attempt,
            "scores": {
                "content_score": analysis["content_score"],
                "relevance_score": analysis["relevance_score"],
                "clarity_score": analysis["clarity_score"],
            },
            "deltas": {
                "content": round(analysis["content_score"] - (exchange.get("content_score") or 0), 1),
                "relevance": round(analysis["relevance_score"] - (exchange.get("relevance_score") or 0), 1),
                "clarity": round(analysis["clarity_score"] - (exchange.get("clarity_score") or 0), 1),
            },
            "feedback": analysis["feedback"],
        }
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
