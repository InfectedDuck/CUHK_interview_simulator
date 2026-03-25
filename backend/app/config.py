from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    database_path: str = "interview_tester.db"
    cors_origins: list[str] = ["http://localhost:5173"]
    max_questions_per_session: int = 5

    model_config = {"env_prefix": "INTERVIEW_"}


settings = Settings()
