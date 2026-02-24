"use client";

import { useState, useCallback, useEffect } from "react";
import { analyze, getHistory } from "@/lib/api";
import type { AnalysisResponse, HistoryItem } from "@/types";
import styles from "./page.module.css";

const PLACEHOLDER_RESUME = "Paste your resume text here...\n\nExample: Software engineer with 5 years of experience in Python, React, and PostgreSQL. Built APIs with FastAPI and deployed on AWS.";
const PLACEHOLDER_JOB = "Paste the job description here...\n\nExample: We are looking for a backend engineer. Required: Python, REST APIs, PostgreSQL, Docker. Nice to have: Kubernetes, AWS.";

function formatHistoryDate(iso: string): string {
  try {
    const d = new Date(iso);
    const now = new Date();
    const sameDay = d.toDateString() === now.toDateString();
    if (sameDay) return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    return d.toLocaleDateString([], { month: "short", day: "numeric" });
  } catch {
    return "";
  }
}

export default function Home() {
  const [resumeText, setResumeText] = useState("");
  const [jobText, setJobText] = useState("");
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  const loadHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const data = await getHistory();
      setHistory(data);
    } catch {
      setHistory([]);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleSubmit = useCallback(async () => {
    const r = resumeText.trim();
    const j = jobText.trim();
    if (!r || !j) {
      setError("Please enter both resume and job description.");
      return;
    }
    setError(null);
    setLoading(true);
    setResult(null);
    try {
      const data = await analyze(r, j);
      setResult(data);
      await loadHistory();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, [resumeText, jobText, loadHistory]);

  const handleSelectHistory = useCallback((item: HistoryItem) => {
    setResult(item.result);
    setError(null);
  }, []);

  return (
    <div className={styles.layout}>
      <aside className={styles.sidebar}>
        <h2 className={styles.sidebarTitle}>Recent History</h2>
        {historyLoading ? (
          <p className={styles.muted}>Loading…</p>
        ) : history.length === 0 ? (
          <p className={styles.muted}>No past runs yet.</p>
        ) : (
          <ul className={styles.historyList}>
            {history.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  className={styles.historyItem}
                  onClick={() => handleSelectHistory(item)}
                >
                  <span className={styles.historyScore}>{item.match_score}%</span>
                  <span className={styles.historyJob}>{item.job_title_guess || "Untitled"}</span>
                  <span className={styles.historyResume}>{item.resume_summary}</span>
                  <span className={styles.historyDate}>{formatHistoryDate(item.timestamp)}</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </aside>

      <main className={styles.main}>
        <header className={styles.header}>
          <h1>SkillGap RAG Coach</h1>
          <p className={styles.tagline}>Compare your resume to a job description and get a match score plus an improvement plan.</p>
        </header>

        <section className={styles.formSection}>
          <div className={styles.inputGroup}>
            <label htmlFor="resume">Resume</label>
            <textarea
              id="resume"
              rows={6}
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder={PLACEHOLDER_RESUME}
              disabled={loading}
            />
          </div>
          <div className={styles.inputGroup}>
            <label htmlFor="job">Job description</label>
            <textarea
              id="job"
              rows={6}
              value={jobText}
              onChange={(e) => setJobText(e.target.value)}
              placeholder={PLACEHOLDER_JOB}
              disabled={loading}
            />
          </div>
          <button
            type="button"
            className={styles.submitBtn}
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? "Analyzing…" : "Analyze"}
          </button>
        </section>

        {loading && (
          <div className={styles.loadingWrap} aria-hidden="true">
            <div className={styles.spinner} />
            <p className={styles.loadingText}>Analyzing resume vs job…</p>
          </div>
        )}

        {error && (
          <div className={`${styles.message} ${styles.messageError}`} role="alert">
            {error}
          </div>
        )}

        {result && !loading && (
          <section className={styles.results} aria-label="Analysis results">
            <div className={styles.scoreCard}>
              <span className={styles.scoreLabel}>Match score</span>
              <span className={styles.scoreValue} data-score={result.match_score}>
                {result.match_score}
              </span>
              <span className={styles.scoreSuffix}>/ 100</span>
              <span className={styles.modeBadge}>{result.mode}</span>
            </div>

            <div className={styles.cards}>
              <div className={styles.card}>
                <h2>Overlapping skills</h2>
                {result.overlapping_skills.length === 0 ? (
                  <p className={styles.muted}>None detected.</p>
                ) : (
                  <ul className={styles.skillEvidenceList}>
                    {result.overlapping_skills.map((s) => (
                      <li key={s.skill} className={styles.skillEvidenceItem}>
                        <span className={styles.skillName}>{s.skill}</span>
                        {s.evidence && (
                          <span className={styles.evidenceSnippet} title={s.evidence}>
                            View evidence: {s.evidence}
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              <div className={styles.card}>
                <h2>Missing skills</h2>
                {result.missing_skills.length === 0 ? (
                  <p className={styles.muted}>None — you cover the job skills we detected.</p>
                ) : (
                  <ul>
                    {result.missing_skills.map((s) => (
                      <li key={s}>{s}</li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            <div className={`${styles.card} ${styles.stepsCard}`}>
              <h2>Suggested next steps</h2>
              <ul className={styles.stepsList}>
                {result.suggested_next_steps.map((step, i) => (
                  <li key={i}>{step}</li>
                ))}
              </ul>
            </div>
          </section>
        )}

        <footer className={styles.footer}>
          <p>SkillGap RAG Coach · Deterministic baseline + optional LLM</p>
        </footer>
      </main>
    </div>
  );
}
