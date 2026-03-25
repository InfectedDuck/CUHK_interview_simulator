from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str


class UserResponse(BaseModel):
    id: int
    name: str
    created_at: str


class ProfileExtractRequest(BaseModel):
    user_id: int
    transcript: str


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    raw_transcript: str
    education: dict | None = None
    skills: list[str] | None = None
    experience: list[dict] | None = None
    goals: str | None = None
    target_programs: list[str] | None = None
    target_universities: list[str] | None = None
    updated_at: str


class ProfileUpdate(BaseModel):
    education: dict | None = None
    skills: list[str] | None = None
    experience: list[dict] | None = None
    goals: str | None = None
    target_programs: list[str] | None = None
    target_universities: list[str] | None = None
