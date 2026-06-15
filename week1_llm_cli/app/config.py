from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

@dataclass(frozen=True)
class Settings:
    api_key:str
    base_url:str
    model:str

def load_settings(env_path: Path=Path(".env")) -> Settings:
    """读取本地环境变量,并返回项目配置"""
    load_dotenv(env_path)

    api_key = os.getenv("API_KEY")
    if not api_key:
        raise RuntimeError("缺少 API_KEY, 请检查 .env 文件是否存在并正确拼写")
    
    base_url=os.getenv("BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/").rstrip("/")

    model=os.getenv("MODEL", "gemini-3-flash-preview")

    return Settings(api_key=api_key, base_url=base_url, model=model)
