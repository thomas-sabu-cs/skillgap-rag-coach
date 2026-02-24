"use client";

import { useState, useCallback, useEffect } from "react";
import { analyze, clearHistory, deleteHistoryItem, getHistory } from "@/lib/api";
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

  const handleNewAnalysis = useCallback(() => {
    setResumeText("");
    setJobText("");
    setResult(null);
    setError(null);
  }, []);

  const handleSelectHistory = useCallback((item: HistoryItem) => {
    setResult(item.result);
    setResumeText(item.resume_text ?? "");
    setJobText(item.job_description ?? "");
    setError(null);
  }, []);

  const handleClearHistory = useCallback(async () => {
    const ok = window.confirm("Clear all analysis history?");
    if (!ok) return;
    try {
      await clearHistory();
      setHistory([]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to clear history.");
    }
  }, []);

  const handleDeleteHistoryItem = useCallback(
    async (id: number) => {
      try {
        await deleteHistoryItem(id);
        await loadHistory();
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to delete history item.");
      }
    },
    [loadHistory],
  );

  return (
    <div className={styles.layout}>
      <aside className={styles.sidebar}>
        <div className={styles.sidebarHeader}>
          <h2 className={styles.sidebarTitle}>Recent History</h2>
          <button
            type="button"
            className={styles.clearHistoryBtn}
            onClick={handleClearHistory}
            disabled={historyLoading || history.length === 0}
            title="Clear all history"
          >
            Clear
          </button>
        </div>
        {historyLoading ? (
          <p className={styles.muted}>Loading…</p>
        ) : history.length === 0 ? (
          <p className={styles.muted}>No past runs yet.</p>
        ) : (
          <ul className={styles.historyList}>
            {history.map((item) => (
              <li key={item.id}>
                <div className={styles.historyRow}>
                  <button
                    type="button"
                    className={styles.historyItem}
                    onClick={() => handleSelectHistory(item)}
                    title="Load this run"
                  >
                    <span
                      className={`${styles.historyScore} ${
                        item.match_score >= 80
                          ? styles.historyScoreHigh
                          : item.match_score >= 50
                          ? styles.historyScoreMid
                          : styles.historyScoreLow
                      }`}
                    >
                      {item.match_score}%
                    </span>
                    <span className={styles.historyJob}>{item.job_title_guess || "Untitled"}</span>
                    <span className={styles.historyResume}>{item.resume_summary}</span>
                    <span className={styles.historyDate}>{formatHistoryDate(item.timestamp)}</span>
                  </button>
                  <button
                    type="button"
                    className={styles.deleteHistoryBtn}
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      void handleDeleteHistoryItem(item.id);
                    }}
                    title="Delete this run"
                    aria-label={`Delete history item ${item.id}`}
                  >
                    ✕
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </aside>

      <main className={styles.main}>
        <div className={styles.mainInner}>
          <header className={styles.header}>
            <h1>SkillGap AI Coach</h1>
            <p className={styles.tagline}>Compare your resume to a job description and get a match score plus an improvement plan.</p>
          </header>

          <section className={styles.contentRow}>
          <div className={styles.formColumn}>
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
              <div className={styles.formActions}>
                <button
                  type="button"
                  className={styles.submitBtn}
                  onClick={handleSubmit}
                  disabled={loading}
                >
                  {loading ? "Analyzing…" : "Analyze"}
                </button>
                <button
                  type="button"
                  className={styles.secondaryBtn}
                  onClick={handleNewAnalysis}
                  disabled={loading && !result}
                >
                  New analysis
                </button>
              </div>
            </section>

            {error && (
              <div className={`${styles.message} ${styles.messageError}`} role="alert">
                {error}
              </div>
            )}
          </div>

          <div className={styles.resultsColumn}>
            {loading && (
              <div className={styles.loadingWrap} aria-hidden="true">
                <div className={styles.spinner} />
                <p className={styles.loadingText}>Analyzing resume vs job…</p>
              </div>
            )}

            {!loading && result && (
              <section className={styles.results} aria-label="Analysis results">
                <div className={styles.scoreCard}>
                  <span className={styles.scoreLabel}>Match score</span>
                  <span
                    className={`${styles.scoreValue} ${
                      result.match_score >= 80
                        ? styles.scoreValueHigh
                        : result.match_score >= 50
                        ? styles.scoreValueMid
                        : styles.scoreValueLow
                    }`}
                    data-score={result.match_score}
                  >
                    {result.match_score}
                  </span>
                  <span className={styles.scoreSuffix}>/ 100</span>
                  <span className={styles.modeBadge}>{result.mode}</span>
                </div>

                <div className={styles.cards}>
                  <div className={`${styles.card} ${styles.overlapCard}`}>
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
                                {s.evidence}
                              </span>
                            )}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                  <div className={`${styles.card} ${styles.missingCard}`}>
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

            {!loading && !result && (
              <section className={styles.emptyState} aria-label="No analysis yet">
                <div className={styles.emptyStateIcon} aria-hidden="true" />
                <h2 className={styles.emptyStateTitle}>Your analysis will appear here</h2>
                <p className={styles.emptyStateText}>
                  Paste your resume and a job description on the left, then run an analysis to see your match score
                  and skill gaps.
                </p>
              </section>
            )}
          </div>
          </section>

          <footer className={styles.footer}>
            <p>SkillGap AI Coach · Deterministic baseline + optional LLM</p>
          </footer>
        </div>
      </main>
    </div>
  );
}
