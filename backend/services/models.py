"""Domain models for analysis results."""
from dataclasses import dataclass


@dataclass
class AnalysisResult:
    """Result of resume vs job description analysis."""

    match_score: int  # 0–100
    overlapping_skills: list[str]
    missing_skills: list[str]
    suggested_next_steps: list[str]
    mode: str  # "baseline" | "llm"
