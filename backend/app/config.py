import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "qwen3.5-27b")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "tongyi-embedding-vision-flash")
    OPENAI_EMBEDDING_API_KEY: str = os.getenv("OPENAI_EMBEDDING_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    OPENAI_EMBEDDING_BASE_URL: str = os.getenv("OPENAI_EMBEDDING_BASE_URL", "") or os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/knowledge.db")


settings = Settings()
