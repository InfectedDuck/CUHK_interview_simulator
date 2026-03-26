from pydantic import BaseModel


class InterviewStartRequest(BaseModel):
    user_id: int
    target_university: str
    target_program: str | None = None
    mode: str = "practice"  # "practice" or "simulation"
    difficulty: str = "medium"  # "easy", "medium", or "hard"


class InterviewStartResponse(BaseModel):
    session_id: int
    question_number: int
    question_text: str
    question_type: str | None = None
    max_questions: int = 5
    mode: str = "practice"


class AnswerRequest(BaseModel):
    answer_text: str
    response_time_seconds: float | None = None


class AnswerFeedback(BaseModel):
    content_score: float
    relevance_score: float
    clarity_score: float
    values_alignment_score: float | None = None
    self_awareness_score: float | None = None
    time_management_score: float | None = None
    feedback: str


class AnswerResponse(BaseModel):
    feedback: AnswerFeedback
    next_question: InterviewStartResponse | None = None
    session_complete: bool = False
    overall_score: float | None = None
    summary_feedback: str | None = None
