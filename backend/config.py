import os
from pydantic import BaseModel
from typing import Optional

class Settings(BaseModel):
    app_name: str = "CampusMind AI"
    version: str = "1.0.0"
    debug: bool = True
    sqlite_db_path: str = os.getenv("SQLITE_DB_PATH", "campusmind.db")
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    default_llm_provider: str = os.getenv("DEFAULT_LLM_PROVIDER", "auto") # auto, gemini, openai, fallback
    model_name_gemini: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    model_name_openai: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

settings = Settings()
