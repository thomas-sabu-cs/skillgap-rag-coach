/** One overlapping skill with evidence snippet from resume */
export interface SkillWithEvidence {
  skill: string;
  evidence: string;
}

/** Response from POST /analyze */
export interface AnalysisResponse {
  match_score: number;
  overlapping_skills: SkillWithEvidence[];
  missing_skills: string[];
  suggested_next_steps: string[];
  mode: "baseline" | "llm";
}

/** One item from GET /history */
export interface HistoryItem {
  id: number;
  timestamp: string;
  resume_summary: string;
  job_title_guess: string;
  match_score: number;
  result: AnalysisResponse;
}
