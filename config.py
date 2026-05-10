# src/config.py
"""Configuration settings for video analyzer"""

from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    VIDEO_UPLOAD_DIR: Path = PROJECT_ROOT / "uploads"
    OUTPUT_DIR: Path = PROJECT_ROOT / "outputs"
    TEMP_DIR: Path = PROJECT_ROOT / "temp"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    
    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    # Model Settings
    USE_LOCAL_OLLAMA: bool = True
    OLLAMA_MODEL: str = "mistral:7b"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    WHISPER_MODEL: str = "base"  # tiny, base, small, medium, large
    
    # Processing Settings
    FRAMES_PER_MINUTE: int = 2
    MAX_VIDEO_SIZE_MB: int = 500
    SUPPORTED_FORMATS: list = ["mp4", "webm", "mov", "avi", "mkv"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Feature Flags
    ENABLE_FRAME_EXTRACTION: bool = True
    ENABLE_VISUAL_ANALYSIS: bool = True
    ENABLE_TRANSCRIPTION: bool = True
    ENABLE_SUMMARIZATION: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.VIDEO_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Create global settings instance
settings = Settings()
