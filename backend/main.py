"""
skillgap-rag-coach — FastAPI backend.
Analyzes resume vs job description and returns match score, skills, and improvement plan.
"""
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import settings
from services.analyzer import analyze_resume_vs_job
from services.models import AnalysisResult


class AnalyzeRequest(BaseModel):
    """Request body for /analyze."""

    resume_text: str = Field(..., min_length=1, description="Raw resume text")
    job_description: str = Field(..., min_length=1, description="Job description text")


class AnalyzeResponse(BaseModel):
    """Response for /analyze — matches AnalysisResult."""

    match_score: int = Field(..., ge=0, le=100)
    overlapping_skills: list[str]
    missing_skills: list[str]
    suggested_next_steps: list[str]
    mode: str = Field(..., description="baseline | llm")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: ensure DB schema if using DB; shutdown: cleanup."""
    # Optional: run DB migrations or create tables here
    yield
    # Cleanup if needed
    pass


app = FastAPI(
    title="SkillGap RAG Coach API",
    description="Analyze resume vs job description: match score, skills gap, improvement plan.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    """Health check for Docker and load balancers."""
    return {"status": "ok", "service": "skillgap-rag-coach"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyze resume text against job description.
    Returns match score (0–100), overlapping skills, missing skills, and suggested next steps.
    """
    try:
        result: AnalysisResult = analyze_resume_vs_job(
            resume_text=request.resume_text.strip(),
            job_description=request.job_description.strip(),
        )
        return AnalyzeResponse(
            match_score=result.match_score,
            overlapping_skills=result.overlapping_skills,
            missing_skills=result.missing_skills,
            suggested_next_steps=result.suggested_next_steps,
            mode=result.mode,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
