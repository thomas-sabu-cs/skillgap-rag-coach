import type { AnalysisResponse, HistoryItem } from "@/types";

const getApiUrl = (): string => {
  if (typeof window !== "undefined") {
    return (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\/$/, "") || "http://localhost:8000";
  }
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
};

export async function analyze(resumeText: string, jobDescription: string): Promise<AnalysisResponse> {
  const base = getApiUrl();
  const res = await fetch(`${base}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      resume_text: resumeText,
      job_description: jobDescription,
    }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const message = (body as { detail?: string })?.detail ?? res.statusText;
    throw new Error(message);
  }
  return res.json() as Promise<AnalysisResponse>;
}

export async function getHistory(): Promise<HistoryItem[]> {
  const base = getApiUrl();
  const res = await fetch(`${base}/history`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const message = (body as { detail?: string })?.detail ?? res.statusText;
    throw new Error(message);
  }
  return res.json() as Promise<HistoryItem[]>;
}

export async function clearHistory(): Promise<void> {
  const base = getApiUrl();
  const res = await fetch(`${base}/history`, { method: "DELETE" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const message = (body as { detail?: string })?.detail ?? res.statusText;
    throw new Error(message);
  }
}

export async function deleteHistoryItem(id: number): Promise<void> {
  const base = getApiUrl();
  const res = await fetch(`${base}/history/${id}`, { method: "DELETE" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const message = (body as { detail?: string })?.detail ?? res.statusText;
    throw new Error(message);
  }
}

