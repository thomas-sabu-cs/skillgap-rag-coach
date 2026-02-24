"""Domain models for analysis results."""
from dataclasses import dataclass


@dataclass
class SkillWithEvidence:
    """A skill found in the resume with a snippet of where it appeared."""

    skill: str
    evidence: str


@dataclass
class AnalysisResult:
    """Result of resume vs job description analysis."""

    match_score: int  # 0–100
    overlapping_skills: list[SkillWithEvidence]
    missing_skills: list[str]
    suggested_next_steps: list[str]
    mode: str  # "baseline" | "llm"
