import json
from fastapi import APIRouter, HTTPException
from ..database import get_db
from ..models.session import SessionResponse, SessionDetail, ExchangeResponse

router = APIRouter(tags=["sessions"])


@router.get("/sessions/{user_id}", response_model=list[SessionResponse])
async def list_sessions(user_id: int):
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT * FROM sessions WHERE user_id = ? ORDER BY started_at DESC",
            (user_id,),
        )
        return [dict(row) for row in rows]
    finally:
        await db.close()


@router.get("/sessions/{user_id}/{session_id}", response_model=SessionDetail)
async def get_session_detail(user_id: int, session_id: int):
    db = await get_db()
    try:
        session_rows = await db.execute_fetchall(
            "SELECT * FROM sessions WHERE id = ? AND user_id = ?",
            (session_id, user_id),
        )
        if not session_rows:
            raise HTTPException(status_code=404, detail="Session not found")

        session = dict(session_rows[0])

        exchange_rows = await db.execute_fetchall(
            "SELECT * FROM exchanges WHERE session_id = ? ORDER BY question_number",
            (session_id,),
        )
        session["exchanges"] = [dict(row) for row in exchange_rows]

        return session
    finally:
        await db.close()
