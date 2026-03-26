import json
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from ..database import get_db
from ..models.user import ProfileExtractRequest, ProfileResponse, ProfileUpdate
from ..services.profile_extractor import extract_profile, extract_from_document, merge_profiles
from ..services.document_parser import parse_document
from ..services.whisper_stt import transcribe, clean_transcript

router = APIRouter(tags=["profile"])


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    context: str = Form(""),
    user_id: int | None = Form(None),
    language: str = Form("en"),
):
    """Transcribe audio using Whisper, then AI-correct using profile context."""
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    raw_text = await transcribe(audio_bytes, language=language)
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not transcribe audio — no speech detected")

    # Build context for AI correction
    full_context = context or ""

    # If user_id provided, load their profile for better context
    if user_id:
        db = await get_db()
        try:
            rows = await db.execute_fetchall(
                "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
            )
            if rows:
                row = dict(rows[0])
                profile_parts = []
                if row.get("education"):
                    profile_parts.append(f"Education: {row['education']}")
                if row.get("skills"):
                    profile_parts.append(f"Skills: {row['skills']}")
                if row.get("projects"):
                    profile_parts.append(f"Projects: {row['projects']}")
                if row.get("experience"):
                    profile_parts.append(f"Experience: {row['experience']}")
                if row.get("goals"):
                    profile_parts.append(f"Goals: {row['goals']}")
                if profile_parts:
                    full_context += "\n\nUser profile:\n" + "\n".join(profile_parts)
        finally:
            await db.close()

    # AI-correct the transcript using context
    corrected = await clean_transcript(raw_text, full_context)

    return {"text": corrected.strip(), "raw_text": raw_text.strip()}

JSON_PROFILE_FIELDS = (
    "education", "skills", "experience", "projects", "target_programs",
    "target_universities", "achievements", "interests", "personality_traits",
)


def _parse_profile_row(row: dict) -> dict:
    """Parse JSON string fields from a profile database row."""
    result = dict(row)
    for field in JSON_PROFILE_FIELDS:
        if result.get(field) and isinstance(result[field], str):
            try:
                result[field] = json.loads(result[field])
            except json.JSONDecodeError:
                pass
    return result


async def _upsert_profile(db, user_id: int, extracted: dict, raw_text: str):
    """Insert or update a profile, merging with existing data if present."""
    existing_rows = await db.execute_fetchall(
        "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
    )

    # If profile exists, merge new data with old
    if existing_rows:
        old_profile = _parse_profile_row(dict(existing_rows[0]))
        old_data = {k: old_profile.get(k) for k in JSON_PROFILE_FIELDS}
        old_data["goals"] = old_profile.get("goals")
        merged = await merge_profiles(old_data, extracted)
        # Append new text to existing transcript
        old_transcript = old_profile.get("raw_transcript", "")
        raw_text = old_transcript + "\n\n---\n\n" + raw_text
    else:
        merged = extracted

    fields = {
        "raw_transcript": raw_text,
        "education": json.dumps(merged.get("education")),
        "skills": json.dumps(merged.get("skills")),
        "experience": json.dumps(merged.get("experience")),
        "projects": json.dumps(merged.get("projects")),
        "goals": merged.get("goals"),
        "target_programs": json.dumps(merged.get("target_programs")),
        "target_universities": json.dumps(merged.get("target_universities")),
        "achievements": json.dumps(merged.get("achievements")),
        "interests": json.dumps(merged.get("interests")),
        "personality_traits": json.dumps(merged.get("personality_traits")),
    }

    if existing_rows:
        sets = ", ".join(f"{k} = ?" for k in fields)
        await db.execute(
            f"UPDATE profiles SET {sets}, updated_at = datetime('now') WHERE user_id = ?",
            (*fields.values(), user_id),
        )
    else:
        cols = ", ".join(["user_id"] + list(fields.keys()))
        placeholders = ", ".join(["?"] * (len(fields) + 1))
        await db.execute(
            f"INSERT INTO profiles ({cols}) VALUES ({placeholders})",
            (user_id, *fields.values()),
        )

    await db.commit()
    rows = await db.execute_fetchall(
        "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
    )
    return _parse_profile_row(rows[0])


@router.post("/profile/extract", response_model=ProfileResponse)
async def extract_user_profile(data: ProfileExtractRequest):
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT * FROM users WHERE id = ?", (data.user_id,)
        )
        if not rows:
            raise HTTPException(status_code=404, detail="User not found")

        extracted = await extract_profile(data.transcript)
        return await _upsert_profile(db, data.user_id, extracted, data.transcript)
    finally:
        await db.close()


@router.post("/profile/upload", response_model=ProfileResponse)
async def upload_document(
    user_id: int = Form(...),
    doc_type: str = Form("document"),
    file: UploadFile = File(...),
):
    # Validate file type
    allowed = {"pdf", "docx", "doc", "txt", "md"}
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. Allowed: {', '.join(allowed)}",
        )

    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        )
        if not rows:
            raise HTTPException(status_code=404, detail="User not found")

        # Parse document to text
        file_bytes = await file.read()
        text_content = parse_document(file_bytes, file.filename)
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from document")

        # Extract profile from document
        extracted = await extract_from_document(text_content, doc_type)
        raw_text = f"[Uploaded {doc_type}: {file.filename}]\n\n{text_content}"
        return await _upsert_profile(db, user_id, extracted, raw_text)
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
