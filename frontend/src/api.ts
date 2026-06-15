import type {
  Artifact,
  Job,
  ProviderPayload,
  ProviderProfile,
  ProviderValidationResult,
  SkillInfo,
  UploadedFile
} from "./types";

export const API_BASE = import.meta.env.VITE_API_BASE || "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: init?.body instanceof FormData ? undefined : { "Content-Type": "application/json" },
    ...init
  });
  if (!response.ok) {
    const detail = await response.text();
    let message = detail;
    try {
      const parsed = JSON.parse(detail) as { detail?: string };
      message = parsed.detail || detail;
    } catch {
      message = detail;
    }
    throw new Error(message || response.statusText);
  }
  return response.json() as Promise<T>;
}

export const api = {
  skills: () => request<SkillInfo[]>("/api/skills"),
  jobs: () => request<Job[]>("/api/jobs"),
  providers: () => request<ProviderProfile[]>("/api/providers"),
  artifacts: (jobId: string) => request<Artifact[]>(`/api/jobs/${jobId}/artifacts`),
  createProvider: (payload: ProviderPayload) =>
    request<ProviderProfile>("/api/providers", { method: "POST", body: JSON.stringify(payload) }),
  validateProvider: (payload: ProviderPayload) =>
    request<ProviderValidationResult>("/api/providers/validate", { method: "POST", body: JSON.stringify(payload) }),
  validateDefaultProvider: () =>
    request<ProviderValidationResult>("/api/providers/default/validate", { method: "POST" }),
  validateSavedProvider: (providerId: string) =>
    request<ProviderValidationResult>(`/api/providers/${providerId}/validate`, { method: "POST" }),
  deleteProvider: (providerId: string) => request<{ deleted: boolean }>(`/api/providers/${providerId}`, { method: "DELETE" }),
  deleteJob: (jobId: string) => request<{ deleted: boolean }>(`/api/jobs/${jobId}`, { method: "DELETE" }),
  clearFailedJobs: () => request<{ deleted: number }>("/api/jobs/clear-failed", { method: "POST" }),
  uploadFile: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<UploadedFile>("/api/files", { method: "POST", body: form });
  },
  createJob: (payload: {
    skillType: string;
    prompt: string;
    fileIds: string[];
    options: Record<string, unknown>;
    providerProfileId: string | null;
  }) => request<Job>("/api/jobs", { method: "POST", body: JSON.stringify(payload) }),
  cancelJob: (jobId: string) => request<Job>(`/api/jobs/${jobId}/cancel`, { method: "POST" }),
  downloadUrl: (artifactId: string) => `/api/artifacts/${artifactId}/download`,
  annotateArtifact: (artifactId: string, annotation: string) =>
    request<{ new_job_id: string; message: string }>(`/api/artifacts/${artifactId}/annotate`, {
      method: "POST",
      body: JSON.stringify({ annotation }),
    }),
};
