/** Response from POST /analyze */
export interface AnalysisResponse {
  match_score: number;
  overlapping_skills: string[];
  missing_skills: string[];
  suggested_next_steps: string[];
  mode: "baseline" | "llm";
}
