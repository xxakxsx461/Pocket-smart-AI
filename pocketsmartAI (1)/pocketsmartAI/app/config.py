import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

class Settings:
    PROJECT_NAME: str = os.getenv('PROJECT_NAME', 'PocketSmart AI')
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
    HOST: str = os.getenv('HOST', '127.0.0.1')
    PORT: int = int(os.getenv('PORT', '8000'))
    
    # Security
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'pocketsmart_default_secret_key_change_me')
    ALGORITHM: str = os.getenv('ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '1440'))
    
    # AI Engine
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL: str = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    
    # Directories
    APP_DIR: Path = BASE_DIR / 'app'
    STATIC_DIR: Path = APP_DIR / 'static'
    TEMPLATES_DIR: Path = APP_DIR / 'templates'
    DATA_DIR: Path = BASE_DIR / os.getenv('DATA_DIR', 'data')
    UPLOADS_DIR: Path = STATIC_DIR / 'uploads'

    @property
    def has_gemini_key(self) -> bool:
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.strip())

settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
