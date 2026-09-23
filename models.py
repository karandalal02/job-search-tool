"""SQLAlchemy models for the company list and the seen-jobs recency tracker."""

from datetime import date

from sqlalchemy import Boolean, Date, String
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    career_url: Mapped[str] = mapped_column(String, default="")
    ats_type: Mapped[str] = mapped_column(String, default="unknown")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class SeenJob(Base):
    __tablename__ = "seen_jobs"

    job_url: Mapped[str] = mapped_column(String, primary_key=True)
    first_seen: Mapped[date] = mapped_column(Date)
