"""Database engine/session setup. Reads DATABASE_URL (Postgres in
production, e.g. Neon) and falls back to a local SQLite file for dev."""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DEFAULT_SQLITE_URL = f"sqlite:///{BASE_DIR / 'data' / 'app.db'}"

DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_SQLITE_URL)
if DATABASE_URL.startswith("postgres://"):
    # Render/Heroku-style URLs use the old "postgres://" scheme; SQLAlchemy needs "postgresql://"
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, future=True)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    from models import Company, SeenJob  # noqa: F401 - registers models on Base

    Base.metadata.create_all(engine)
