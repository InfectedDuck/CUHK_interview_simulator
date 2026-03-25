import json
from fastapi import APIRouter, HTTPException
from ..database import get_db
from ..models.user import ProfileExtractRequest, ProfileResponse, ProfileUpdate
from ..services.profile_extractor import extract_profile

router = APIRouter(tags=["profile"])


def _parse_profile_row(row: dict) -> dict:
    """Parse JSON string fields from a profile database row."""
    result = dict(row)
    for field in ("education", "skills", "experience", "target_programs", "target_universities"):
        if result.get(field) and isinstance(result[field], str):
            try:
                result[field] = json.loads(result[field])
            except json.JSONDecodeError:
                pass
    return result


@router.post("/profile/extract", response_model=ProfileResponse)
async def extract_user_profile(data: ProfileExtractRequest):
    db = await get_db()
    try:
        # Check user exists
        rows = await db.execute_fetchall(
            "SELECT * FROM users WHERE id = ?", (data.user_id,)
        )
        if not rows:
            raise HTTPException(status_code=404, detail="User not found")

        # Extract profile from transcript
        extracted = await extract_profile(data.transcript)

        # Upsert profile
        existing = await db.execute_fetchall(
            "SELECT id FROM profiles WHERE user_id = ?", (data.user_id,)
        )

        fields = {
            "raw_transcript": data.transcript,
            "education": json.dumps(extracted.get("education")),
            "skills": json.dumps(extracted.get("skills")),
            "experience": json.dumps(extracted.get("experience")),
            "goals": extracted.get("goals"),
            "target_programs": json.dumps(extracted.get("target_programs")),
            "target_universities": json.dumps(extracted.get("target_universities")),
        }

        if existing:
            sets = ", ".join(f"{k} = ?" for k in fields)
            await db.execute(
                f"UPDATE profiles SET {sets}, updated_at = datetime('now') WHERE user_id = ?",
                (*fields.values(), data.user_id),
            )
        else:
            cols = ", ".join(["user_id"] + list(fields.keys()))
            placeholders = ", ".join(["?"] * (len(fields) + 1))
            await db.execute(
                f"INSERT INTO profiles ({cols}) VALUES ({placeholders})",
                (data.user_id, *fields.values()),
            )

        await db.commit()

        rows = await db.execute_fetchall(
            "SELECT * FROM profiles WHERE user_id = ?", (data.user_id,)
        )
        return _parse_profile_row(rows[0])
    finally:
        await db.close()


@router.get("/profile/{user_id}", response_model=ProfileResponse)
async def get_profile(user_id: int):
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Profile not found")
        return _parse_profile_row(rows[0])
    finally:
        await db.close()


@router.put("/profile/{user_id}", response_model=ProfileResponse)
async def update_profile(user_id: int, data: ProfileUpdate):
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Profile not found")

        updates = {}
        for field, value in data.model_dump(exclude_unset=True).items():
            if isinstance(value, (dict, list)):
                updates[field] = json.dumps(value)
            else:
                updates[field] = value

        if updates:
            sets = ", ".join(f"{k} = ?" for k in updates)
            await db.execute(
                f"UPDATE profiles SET {sets}, updated_at = datetime('now') WHERE user_id = ?",
                (*updates.values(), user_id),
            )
            await db.commit()

        rows = await db.execute_fetchall(
            "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
        )
        return _parse_profile_row(rows[0])
    finally:
        await db.close()
