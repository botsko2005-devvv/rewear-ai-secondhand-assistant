import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "mock")
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4o-mini")
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_TIMEOUT_SEC: float = float(os.getenv("AI_TIMEOUT_SEC", "10.0"))


settings = Settings()
