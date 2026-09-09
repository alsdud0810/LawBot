from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LawBot 2026"
    environment: str = "development"
    embedding_model: str = "BAAI/bge-m3"
    embedding_batch_size: int = Field(default=1, ge=1)
    embedding_device: str = 'cpu'
    top_k: int = Field(default=3, ge=1, le=20)
    similarity_threshold: float = Field(default=0.35, ge=-1.0, le=1.0)
    data_dir: Path = Path("data")
    vector_index_dir: Path = Path("data/vector_index")
    llm_api_key: str | None = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
