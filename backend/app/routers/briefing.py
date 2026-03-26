import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..database import get_db
from ..services.strategy_briefing import generate_briefing, get_format_briefing
from ..services.analytics import get_progress_summary
from ..services.cuhk_knowledge import get_all_programs

router = APIRouter(tags=["briefing"])


class BriefingRequest(BaseModel):
    university: str
    program: str | None = None


PROFILE_JSON_FIELDS = (
    "education", "skills", "experience", "projects", "target_programs",
    "target_universities", "achievements", "interests", "personality_traits",
)


@router.post("/briefing/{user_id}")
async def create_briefing(user_id: int, data: BriefingRequest):
    db = await get_db()
    try:
        profile_rows = await db.execute_fetchall(
            "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
        )
        if not profile_rows:
            raise HTTPException(status_code=400, detail="No profile found")

        row = dict(profile_rows[0])
        profile = {}
        for field in PROFILE_JSON_FIELDS:
            val = row.get(field)
            if val and isinstance(val, str):
                try:
                    profile[field] = json.loads(val)
                except json.JSONDecodeError:
                    profile[field] = val
            else:
                profile[field] = val
        profile["goals"] = row.get("goals")

        # Get past performance summary
        summary = await get_progress_summary(db, user_id)
        perf = f"Sessions completed: {summary['sessions_completed']}."
        if summary["category_averages"]:
            perf += f" Average scores: content={summary['category_averages']['content']}, relevance={summary['category_averages']['relevance']}, clarity={summary['category_averages']['clarity']}."
        if summary.get("improvement_velocity"):
            perf += f" Improvement velocity: {summary['improvement_velocity']}."

        briefing = await generate_briefing(
            profile=profile,
            university=data.university,
            program=data.program,
            past_performance=perf,
        )

        # Cache it
        await db.execute(
            "INSERT INTO briefings (user_id, university, program, content) VALUES (?, ?, ?, ?)",
            (user_id, data.university, data.program, json.dumps(briefing)),
        )
        await db.commit()

        return briefing
    finally:
        await db.close()


@router.get("/briefing/format")
async def get_interview_format(university: str, program: str | None = None):
    return get_format_briefing(university, program or "General / Undecided")


@router.get("/briefing/programs")
async def list_programs():
    return {"programs": get_all_programs()}
