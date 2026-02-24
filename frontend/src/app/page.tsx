"use client";

import { useState, useCallback } from "react";
import { analyze } from "@/lib/api";
import type { AnalysisResponse } from "@/types";
import styles from "./page.module.css";

const PLACEHOLDER_RESUME = "Paste your resume text here...\n\nExample: Software engineer with 5 years of experience in Python, React, and PostgreSQL. Built APIs with FastAPI and deployed on AWS.";
const PLACEHOLDER_JOB = "Paste the job description here...\n\nExample: We are looking for a backend engineer. Required: Python, REST APIs, PostgreSQL, Docker. Nice to have: Kubernetes, AWS.";

export default function Home() {
  const [resumeText, setResumeText] = useState("");
  const [jobText, setJobText] = useState("");
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, [resumeText, jobText]);

  return (
    <main className={styles.page}>
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

      {error && (
        <div className={`${styles.message} ${styles.messageError}`} role="alert">
          {error}
        </div>
      )}

      {result && (
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
                <ul>
                  {result.overlapping_skills.map((s) => (
                    <li key={s}>{s}</li>
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
  );
}
