from fastapi import APIRouter
from ..database import get_db
from ..services.analytics import get_progress_summary, detect_weakness_patterns, get_strengths

router = APIRouter(tags=["analytics"])


@router.get("/analytics/{user_id}")
async def get_analytics(user_id: int):
    db = await get_db()
    try:
        summary = await get_progress_summary(db, user_id)
        weaknesses = await detect_weakness_patterns(db, user_id) if summary["sessions_completed"] >= 1 else []
        strengths = await get_strengths(db, user_id) if summary["sessions_completed"] >= 1 else []

        return {
            **summary,
            "weaknesses": weaknesses,
            "strengths": strengths,
        }
    finally:
        await db.close()
