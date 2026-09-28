from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@dataclass(frozen=True)
class Settings:
    app_name: str = "Sistema de reservas de salas"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./salas.db")
    test_database_url: str = os.getenv("TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:")


@lru_cache
def get_settings() -> Settings:
    return Settings()
