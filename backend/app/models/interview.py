from pydantic import BaseModel


class InterviewStartRequest(BaseModel):
    user_id: int
    target_university: str


class InterviewStartResponse(BaseModel):
    session_id: int
    question_number: int
    question_text: str


class AnswerRequest(BaseModel):
    answer_text: str


class AnswerFeedback(BaseModel):
    content_score: float
    relevance_score: float
    clarity_score: float
    feedback: str


class AnswerResponse(BaseModel):
    feedback: AnswerFeedback
    next_question: InterviewStartResponse | None = None
    session_complete: bool = False
    overall_score: float | None = None
    summary_feedback: str | None = None
