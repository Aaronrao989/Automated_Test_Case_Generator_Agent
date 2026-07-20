import type { AnalysisResult, RecentJob, StartResponse } from "./types";

// Strip any trailing slash so we never build "https://host//api/v1/...".
const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/+$/, "");

async function parseError(res: Response): Promise<string> {
  try {
    const data = await res.json();
    return typeof data?.detail === "string" ? data.detail : `Request failed (${res.status})`;
  } catch {
    return `Request failed (${res.status})`;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers as Record<string, string>) },
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json() as Promise<T>;
}

export const api = {
  startAnalysis(sourceType: string, sourceData: string): Promise<StartResponse> {
    return request<StartResponse>("/api/v1/analysis/start", {
      method: "POST",
      body: JSON.stringify({ source_type: sourceType, source_data: sourceData }),
    });
  },

  uploadZip(file: File, onProgress?: (pct: number) => void): Promise<StartResponse> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", `${API_URL}/api/v1/analysis/upload`);
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable && onProgress) onProgress(Math.round((e.loaded / e.total) * 100));
      };
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(JSON.parse(xhr.responseText));
        } else {
          try {
            reject(new Error(JSON.parse(xhr.responseText).detail || "Upload failed"));
          } catch {
            reject(new Error(`Upload failed (${xhr.status})`));
          }
        }
      };
      xhr.onerror = () => reject(new Error("Upload failed"));
      const formData = new FormData();
      formData.append("file", file);
      xhr.send(formData);
    });
  },

  getResult(jobId: string): Promise<AnalysisResult> {
    return request<AnalysisResult>(`/api/v1/analysis/${jobId}`);
  },

  listRecent(limit = 20): Promise<RecentJob[]> {
    return request<RecentJob[]>(`/api/v1/analysis?limit=${limit}`);
  },

  deleteJob(jobId: string): Promise<{ message: string }> {
    return request(`/api/v1/analysis/${jobId}`, { method: "DELETE" });
  },
};
