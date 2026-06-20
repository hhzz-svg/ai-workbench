export type JobStatus = "pending" | "running" | "needs_input" | "succeeded" | "failed" | "canceled";

export type SkillInfo = {
  id: string;
  name: string;
  description: string;
  required_inputs: string[];
  output_contract: string[];
};

export type ProviderProfile = {
  id: string;
  name: string;
  provider: string;
  base_url: string;
  model: string;
  wire_api: "responses" | "chat_completions";
  has_api_key: boolean;
  created_at: string;
};

export type ProviderPayload = {
  name: string;
  provider: string;
  base_url: string;
  model: string;
  wire_api: "responses" | "chat_completions";
  api_key: string;
};

export type ProviderValidationResult = {
  ok: boolean;
  message: string;
};

export type HealthStatus = {
  ok: boolean;
  codex_available: boolean;
  codex_version?: string | null;
  data_dir: string;
};

export type UploadedFile = {
  id: string;
  name: string;
  size: number;
  content_type?: string | null;
};

export type Job = {
  id: string;
  skill_type: string;
  prompt: string;
  options: Record<string, unknown>;
  file_ids: string[];
  provider_profile_id?: string | null;
  status: JobStatus;
  workspace?: string | null;
  created_at: string;
  updated_at: string;
  error?: string | null;
};

export type Artifact = {
  id: string;
  job_id: string;
  name: string;
  path: string;
  kind: "markdown" | "html" | "presentation" | "pdf" | "image" | "json" | "file";
  size: number;
  created_at: string;
};

export type JobEvent = {
  type: string;
  message: string;
  job_id: string;
};

export type DirectoryEntry = {
  name: string;
  path: string;
  is_dir: boolean;
};

export type DirectoryListing = {
  path: string;
  parent: string | null;
  separator: string;
  entries: DirectoryEntry[];
};

export type FilesystemRoot = {
  name: string;
  path: string;
};
