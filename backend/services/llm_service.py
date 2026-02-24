"""
Optional LLM mode: use OpenAI to enrich skill extraction and suggestions.
Only active when OPENAI_API_KEY is set and USE_LLM_MODE=true.
"""
import os
from typing import List

from services.baseline import run_baseline_analysis
from services.models import AnalysisResult


def is_llm_available() -> bool:
    """True if OpenAI API key is set and non-empty."""
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    return bool(key)


def run_llm_analysis(resume_text: str, job_description: str) -> AnalysisResult:
    """
    Run baseline first, then optionally call OpenAI to improve suggestions.
    Falls back to baseline if LLM call fails.
    """
    baseline = run_baseline_analysis(resume_text, job_description)
    try:
        import openai
        client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        # Build a short prompt for next steps only (keep score/skills from baseline for consistency)
        prompt = f"""You are a career coach. Given:
- Job description (excerpt): {job_description[:1500]}
- Resume skills we detected: {baseline.overlapping_skills}
- Missing skills for the job: {baseline.missing_skills}
- Current match score: {baseline.match_score}/100

Provide 4-5 short, actionable bullet points as "Suggested next steps" for the candidate. Be specific and practical. One line per bullet. No preamble."""
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
        )
        content = (resp.choices[0].message.content or "").strip()
        steps: List[str] = []
        for line in content.split("\n"):
            line = line.strip()
            if not line:
                continue
            # Strip common bullets
            for prefix in ("- ", "* ", "• ", "1. ", "2. ", "3. ", "4. ", "5. "):
                if line.startswith(prefix):
                    line = line[len(prefix):].strip()
                    break
            if line:
                steps.append(line)
        if steps:
            return AnalysisResult(
                match_score=baseline.match_score,
                overlapping_skills=baseline.overlapping_skills,
                missing_skills=baseline.missing_skills,
                suggested_next_steps=steps[:6],
                mode="llm",
            )
    except Exception:
        pass
    return baseline
