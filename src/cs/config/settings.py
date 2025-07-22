import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    """Application settings loaded from environment variables"""
    
    # API Keys
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    weather_api_key: str = os.getenv("WEATHER_API_KEY", "")
    
    # Database
    database_path: str = os.getenv("DB_PATH", "cs.db")
    
    # Application
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Project paths
    project_root: Path = Path(__file__).parent.parent.parent.parent
    
    def validate(self) -> None:
        """Validate required settings"""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")


# Global settings instance
settings = Settings()