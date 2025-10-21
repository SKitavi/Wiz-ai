import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path


# --- Load environment variables from .env ---
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def is_running_in_docker() -> bool:
    """Detect if running inside a Docker container."""
    if os.path.exists("/.dockerenv"):
        return True
    return os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true"


RUNNING_IN_DOCKER = is_running_in_docker()
DB_HOST = "host.docker.internal" if RUNNING_IN_DOCKER else "localhost"


class Settings(BaseSettings):
    # Database components
    POSTGRES_USER: str = "sharonkitavi"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "wizai"
    POSTGRES_PORT: int = 5432

    # Construct full connection URL
    DATABASE_URL: str = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Paths & Config
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    GOOGLE_CALENDAR_CREDENTIALS: str = "./credentials.json"
    GOOGLE_CALENDAR_TOKEN: str = "./token.json"
    N8N_WEBHOOK_URL: str = "https://your-n8n-instance.com/webhook/wizai"
    RATE_LIMIT_PER_MINUTE: int = 60

    # Portal credentials
    PORTAL_USERNAME: str = os.getenv("PORTAL_USERNAME", "encrypted_or_env_var")
    PORTAL_PASSWORD: str = os.getenv("PORTAL_PASSWORD", "encrypted_or_env_var")

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore any additional .env vars not defined here


def get_cors_origins() -> List[str]:
    """Return allowed CORS origins based on environment."""
    if settings.ENVIRONMENT == "development":
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
    return ["https://yourdomain.com"]


settings = Settings()

print(f"🟢 Running in {'Docker' if RUNNING_IN_DOCKER else 'Local'} mode")
print(f"🗄️  Database URL: {settings.DATABASE_URL}")
