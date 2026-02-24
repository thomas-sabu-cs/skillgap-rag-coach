"""
SQLAlchemy schema for analysis runs.
"""
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AnalysisRun(Base):
    """Stored analysis run (resume vs job)."""

    __tablename__ = "analysis_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    resume_summary: Mapped[str] = mapped_column(String(100), nullable=False)
    job_title_guess: Mapped[str] = mapped_column(String(200), nullable=False)
    match_score: Mapped[int] = mapped_column(Integer, nullable=False)
    result_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
