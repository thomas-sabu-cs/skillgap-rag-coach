"""
Deterministic baseline: extract skills via keyword dictionary and compute match score.
Includes evidence (sentence/context) where each skill was found in the resume.
No external API keys required.
"""
import re
from typing import List, Set

from services.models import AnalysisResult, SkillWithEvidence
from services.skill_dict import SKILL_KEYWORDS, SKILL_WORDS

# Max length for evidence snippet
EVIDENCE_MAX_LEN = 120


def normalize_text(text: str) -> str:
    """Lowercase and replace punctuation with spaces for tokenization."""
    if not text or not text.strip():
        return ""
    lower = text.lower().strip()
    normalized = re.sub(r"[^\w\s]", " ", lower)
    return " ".join(normalized.split())


def tokenize(text: str) -> Set[str]:
    """Return set of lowercase tokens (words and bigrams for phrases)."""
    normalized = normalize_text(text)
    tokens = set(normalized.split())
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
    for kw in SKILL_KEYWORDS:
        if " " in kw and kw in normalize_text(text):
            found.add(kw)
    for word in tokens:
        if word in SKILL_WORDS or word in SKILL_KEYWORDS:
            found.add(word)
    return sorted(found)


def _sentences(text: str) -> List[str]:
    """Split text into sentences (simple split on . ! ?)."""
    if not text or not text.strip():
        return []
    raw = text.strip()
    parts = re.split(r"(?<=[.!?])\s+", raw)
    return [p.strip() for p in parts if p.strip()]


def _find_evidence_for_skill(resume_text: str, skill: str) -> str:
    """
    Find a snippet from resume_text where the skill appears (sentence or surrounding context).
    """
    if not resume_text or not skill:
        return ""
    lower_resume = resume_text.lower()
    lower_skill = skill.lower()
    # Prefer sentence containing the skill
    for sent in _sentences(resume_text):
        if lower_skill in sent.lower():
            snippet = sent.strip()
            if len(snippet) > EVIDENCE_MAX_LEN:
                snippet = snippet[: EVIDENCE_MAX_LEN - 3].rsplit(maxsplit=1)[0] + "..."
            return snippet
    # Fallback: find first occurrence and take surrounding chars
    idx = lower_resume.find(lower_skill)
    if idx == -1:
        return ""
    start = max(0, idx - 40)
    end = min(len(resume_text), idx + len(skill) + 50)
    snippet = resume_text[start:end].strip()
    if start > 0:
        snippet = "..." + snippet
    if end < len(resume_text):
        snippet = snippet + "..."
    if len(snippet) > EVIDENCE_MAX_LEN:
        snippet = snippet[: EVIDENCE_MAX_LEN - 3] + "..."
    return snippet


def extract_overlapping_skills_with_evidence(
    resume_text: str,
    job_skills: List[str],
    resume_skills: List[str],
) -> List[SkillWithEvidence]:
    """
    For each job skill that appears in the resume, build SkillWithEvidence with a snippet.
    """
    overlap = sorted(set(s.lower() for s in resume_skills) & set(s.lower() for s in job_skills))
    result: List[SkillWithEvidence] = []
    for skill in overlap:
        evidence = _find_evidence_for_skill(resume_text, skill)
        result.append(SkillWithEvidence(skill=skill, evidence=evidence or f"(mentioned: {skill})"))
    return result


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
    overlapping_skill_names: List[str],
) -> List[str]:
    """Generate a simple bullet plan from missing and overlapping skills."""
    steps: List[str] = []
    if missing_skills:
        steps.append(f"Focus on building or highlighting these skills: {', '.join(missing_skills[:5])}.")
        if len(missing_skills) > 5:
            steps.append(f"Plus {len(missing_skills) - 5} more job-relevant skills to consider.")
    else:
        steps.append("Your resume already covers the main skills mentioned in the job.")
    if overlapping_skill_names:
        steps.append("Emphasize your experience with: " + ", ".join(overlapping_skill_names[:5]) + " in your summary or top bullet points.")
    steps.append("Add concrete outcomes (metrics, impact) for your top 3 matching skills.")
    steps.append("Tailor your resume header and summary to mirror keywords from the job description.")
    return steps


def run_baseline_analysis(resume_text: str, job_description: str) -> AnalysisResult:
    """Run full baseline analysis: extract skills, score, suggest steps, with evidence."""
    resume_skills = extract_skills_from_text(resume_text)
    job_skills = extract_skills_from_text(job_description)
    overlapping = extract_overlapping_skills_with_evidence(resume_text, job_skills, resume_skills)
    missing = sorted(set(s.lower() for s in job_skills) - set(s.lower() for s in resume_skills))
    score = compute_match_score(resume_skills, job_skills)
    overlap_names = [s.skill for s in overlapping]
    steps = suggest_next_steps_baseline(missing, overlap_names)
    return AnalysisResult(
        match_score=score,
        overlapping_skills=overlapping,
        missing_skills=missing,
        suggested_next_steps=steps,
        mode="baseline",
    )
