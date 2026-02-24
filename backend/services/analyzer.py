"""
Orchestrator: choose baseline vs LLM and run analysis.
"""
from config import settings

from services.baseline import run_baseline_analysis
from services.llm_service import is_llm_available, run_llm_analysis
from services.models import AnalysisResult


def analyze_resume_vs_job(resume_text: str, job_description: str) -> AnalysisResult:
    """
    Analyze resume against job description.
    Uses LLM mode only if OPENAI_API_KEY is set and USE_LLM_MODE is true; otherwise baseline.
    """
    if settings.use_llm_mode and is_llm_available():
        return run_llm_analysis(resume_text, job_description)
    return run_baseline_analysis(resume_text, job_description)
