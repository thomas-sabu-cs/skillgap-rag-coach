"""
Deterministic baseline: extract skills via keyword dictionary and compute match score.
No external API keys required.
"""
import re
from typing import List, Set

from services.models import AnalysisResult
from services.skill_dict import SKILL_KEYWORDS, SKILL_WORDS


def normalize_text(text: str) -> str:
    """Lowercase and replace punctuation with spaces for tokenization."""
    if not text or not text.strip():
        return ""
    lower = text.lower().strip()
    # Replace punctuation with space, keep alphanumeric and spaces
    normalized = re.sub(r"[^\w\s]", " ", lower)
    return " ".join(normalized.split())


def tokenize(text: str) -> Set[str]:
    """Return set of lowercase tokens (words and bigrams for phrases)."""
    normalized = normalize_text(text)
    tokens = set(normalized.split())
    # Add bigrams for "machine learning", "data science", etc.
    words = normalized.split()
    for i in range(len(words) - 1):
        bigram = f"{words[i]} {words[i+1]}"
        tokens.add(bigram)
    return tokens


def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract skills present in text using deterministic keyword dictionary.
    Returns sorted list of matched skill strings (canonical form where applicable).
    """
    if not text or not text.strip():
        return []
    tokens = tokenize(text)
    found: Set[str] = set()
    # Check multi-word keywords first
    for kw in SKILL_KEYWORDS:
        if " " in kw and kw in normalize_text(text):
            found.add(kw)
    # Then single words
    for word in tokens:
        if word in SKILL_WORDS or word in SKILL_KEYWORDS:
            found.add(word)
    return sorted(found)


def compute_match_score(resume_skills: List[str], job_skills: List[str]) -> int:
    """
    Match score 0–100: percentage of job skills found in resume.
    If job has no skills, return 100 to avoid division by zero.
    """
    if not job_skills:
        return 100
    resume_set = set(s.lower() for s in resume_skills)
    job_set = set(s.lower() for s in job_skills)
    overlap = len(job_set & resume_set)
    return min(100, round(100 * overlap / len(job_set)))


def suggest_next_steps_baseline(
    missing_skills: List[str],
    overlapping_skills: List[str],
) -> List[str]:
    """Generate a simple bullet plan from missing and overlapping skills."""
    steps: List[str] = []
    if missing_skills:
        steps.append(f"Focus on building or highlighting these skills: {', '.join(missing_skills[:5])}.")
        if len(missing_skills) > 5:
            steps.append(f"Plus {len(missing_skills) - 5} more job-relevant skills to consider.")
    else:
        steps.append("Your resume already covers the main skills mentioned in the job.")
    if overlapping_skills:
        steps.append("Emphasize your experience with: " + ", ".join(overlapping_skills[:5]) + " in your summary or top bullet points.")
    steps.append("Add concrete outcomes (metrics, impact) for your top 3 matching skills.")
    steps.append("Tailor your resume header and summary to mirror keywords from the job description.")
    return steps


def run_baseline_analysis(resume_text: str, job_description: str) -> AnalysisResult:
    """Run full baseline analysis: extract skills, score, suggest steps."""
    resume_skills = extract_skills_from_text(resume_text)
    job_skills = extract_skills_from_text(job_description)
    overlap = sorted(set(s.lower() for s in resume_skills) & set(s.lower() for s in job_skills))
    missing = sorted(set(s.lower() for s in job_skills) - set(s.lower() for s in resume_skills))
    score = compute_match_score(resume_skills, job_skills)
    steps = suggest_next_steps_baseline(missing, overlap)
    return AnalysisResult(
        match_score=score,
        overlapping_skills=overlap,
        missing_skills=missing,
        suggested_next_steps=steps,
        mode="baseline",
    )
