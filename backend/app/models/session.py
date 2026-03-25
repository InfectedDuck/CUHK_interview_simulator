from pydantic import BaseModel


class SessionResponse(BaseModel):
    id: int
    user_id: int
    target_university: str
    status: str
    overall_score: float | None = None
    summary_feedback: str | None = None
    started_at: str
    completed_at: str | None = None


class SessionDetail(SessionResponse):
    exchanges: list["ExchangeResponse"] = []


class ExchangeResponse(BaseModel):
    id: int
    session_id: int
    question_number: int
    question_text: str
    answer_text: str | None = None
    content_score: float | None = None
    relevance_score: float | None = None
    clarity_score: float | None = None
    feedback: str | None = None
    created_at: str
