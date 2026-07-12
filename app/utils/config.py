import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.0"))
    IBM_API_KEY: str = os.getenv("IBM_API_KEY", "")
    IBM_PROJECT_ID: str = os.getenv("IBM_PROJECT_ID", "")
    IBM_URL: str = os.getenv("IBM_URL", "https://us-south.ml.cloud.ibm.com")
    IBM_MODEL: str = os.getenv("IBM_MODEL", "ibm/granite-13b-chat-v2")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "memory.db")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "3"))
    KNOWLEDGE_BASE_DIR: str = os.getenv("KNOWLEDGE_BASE_DIR", "knowledge_base")
    FASTAPI_HOST: str = os.getenv("FASTAPI_HOST", "0.0.0.0")
    FASTAPI_PORT: int = int(os.getenv("FASTAPI_PORT", "8000"))


settings = Settings()
