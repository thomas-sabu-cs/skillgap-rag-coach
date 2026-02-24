"""Tests for baseline skill extraction and scoring."""
import pytest

from services.baseline import (
    compute_match_score,
    extract_skills_from_text,
    run_baseline_analysis,
    suggest_next_steps_baseline,
)


def test_extract_skills_single_words() -> None:
    text = "I know Python, JavaScript and React."
    skills = extract_skills_from_text(text)
    assert "python" in skills
    assert "javascript" in skills
    assert "react" in skills


def test_extract_skills_bigrams() -> None:
    text = "Experience with machine learning and data science."
    skills = extract_skills_from_text(text)
    assert "machine learning" in skills
    assert "data science" in skills


def test_extract_skills_empty() -> None:
    assert extract_skills_from_text("") == []
    assert extract_skills_from_text("   ") == []


def test_compute_match_score_full_match() -> None:
    job = ["python", "react", "sql"]
    resume = ["python", "react", "sql", "docker"]
    assert compute_match_score(resume, job) == 100


def test_compute_match_score_partial() -> None:
    job = ["python", "react", "sql"]
    resume = ["python", "react"]
    # 2/3 * 100 = 67 rounded
    assert compute_match_score(resume, job) == 67


def test_compute_match_score_no_match() -> None:
    job = ["python", "react"]
    resume = ["java", "c++"]
    assert compute_match_score(resume, job) == 0


def test_compute_match_score_empty_job() -> None:
    assert compute_match_score(["python"], []) == 100


def test_suggest_next_steps_has_missing() -> None:
    steps = suggest_next_steps_baseline(
        missing_skills=["python", "aws"],
        overlapping_skill_names=["git", "sql"],
    )
    assert len(steps) >= 3
    assert any("python" in s.lower() or "aws" in s.lower() for s in steps)


def test_run_baseline_analysis_full_flow() -> None:
    resume = "Software engineer with Python, React, and PostgreSQL. Used Docker and AWS."
    job = "We need Python, React, Kubernetes, and AWS. Experience with REST APIs."
    result = run_baseline_analysis(resume, job)
    assert 0 <= result.match_score <= 100
    overlap_skills = [s.skill for s in result.overlapping_skills]
    assert "python" in overlap_skills or "react" in overlap_skills
    assert "kubernetes" in result.missing_skills or "k8s" in result.missing_skills
    assert len(result.suggested_next_steps) >= 3
    assert result.mode == "baseline"
    # Evidence: each overlapping skill should have a non-empty evidence snippet
    for item in result.overlapping_skills:
        assert item.skill
        assert item.evidence
