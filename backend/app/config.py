from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM provider: "ollama" (local) or "openrouter" (cloud)
    llm_provider: str = "ollama"
    # Ollama settings (local)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral:7b-instruct-q4_0"
    # OpenRouter settings (cloud)
    openrouter_api_key: str = ""
    openrouter_model: str = "mistralai/mistral-7b-instruct:free"
    # General
    database_path: str = "interview_tester.db"
    cors_origins: list[str] = ["http://localhost:5173"]
    max_questions_per_session: int = 5
    whisper_model: str = "base"
    whisper_language: str = "en"

    model_config = {"env_prefix": "INTERVIEW_"}


settings = Settings()
