from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

from exceptions import ConfigError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

@dataclass(frozen=True)
class Settings:
    api_key:str
    base_url:str
    model:str

def load_settings() -> Settings:
    """
    Read the.env configuration and validate the key fields needed for the big model call
    """
    if not ENV_PATH.exists():
        raise ConfigError(f"env file not found: {ENV_PATH}")
    
    load_dotenv(ENV_PATH)

    api_key = os.getenv("LLM_API_KEY","").strip()
    base_url = os.getenv("LLM_BASE_URL","").strip()
    model = os.getenv("LLM_MODEL","").strip()

    if not api_key:
        raise ConfigError("LLM_API_KEY is not set in the .env file")

    if not base_url:
        raise ConfigError("LLM_BASE_URL is not set in the .env file")

    if not model:
        raise ConfigError("LLM_MODEL is not set in the .env file")

    return Settings(
        api_key=api_key, 
        base_url=base_url, 
        model=model,
    )
