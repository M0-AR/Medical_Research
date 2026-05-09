from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Medical Research Portal API"
    API_V1_STR: str = "/api"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    REPORTS_DIR: Path = BASE_DIR / "app" / "reports"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

# Ensure reports directory exists
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
