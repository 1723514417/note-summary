import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "embedding-3")
    OPENAI_EMBEDDING_API_KEY: str = os.getenv("OPENAI_EMBEDDING_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    OPENAI_EMBEDDING_BASE_URL: str = os.getenv("OPENAI_EMBEDDING_BASE_URL", "") or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/knowledge.db")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")


settings = Settings()
