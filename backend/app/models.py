from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


JobStatus = Literal["pending", "running", "needs_input", "succeeded", "failed", "canceled"]
WireApi = Literal["responses", "chat_completions"]


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


class ProviderProfile(BaseModel):
    id: str
    name: str
    provider: str
    base_url: str
    model: str
    wire_api: WireApi = "responses"
    api_key_env: str = "SKILL_WORKBENCH_API_KEY"
    has_api_key: bool = False
    created_at: str = Field(default_factory=utc_now)


class ProviderCreate(BaseModel):
    name: str
    provider: str = "proxy"
    base_url: str
    model: str
    wire_api: WireApi = "responses"
    api_key: str


class ProviderValidate(BaseModel):
    name: str
    provider: str = "proxy"
    base_url: str
    model: str
    wire_api: WireApi = "responses"
    api_key: str | None = None


class ProviderValidationResult(BaseModel):
    ok: bool
    message: str


class UploadedFile(BaseModel):
    id: str
    name: str
    path: str
    size: int
    content_type: str | None = None
    created_at: str = Field(default_factory=utc_now)


class Job(BaseModel):
    id: str
    skill_type: str
    prompt: str
    options: dict[str, Any] = Field(default_factory=dict)
    file_ids: list[str] = Field(default_factory=list)
    provider_profile_id: str | None = None
    status: JobStatus = "pending"
    workspace: str | None = None
    created_at: str = Field(default_factory=utc_now)
    updated_at: str = Field(default_factory=utc_now)
    error: str | None = None


class JobCreate(BaseModel):
    skill_type: str = Field(alias="skillType")
    prompt: str
    file_ids: list[str] = Field(default_factory=list, alias="fileIds")
    options: dict[str, Any] = Field(default_factory=dict)
    provider_profile_id: str | None = Field(default=None, alias="providerProfileId")

    model_config = ConfigDict(populate_by_name=True)


class JobReply(BaseModel):
    prompt: str


class Artifact(BaseModel):
    id: str
    job_id: str
    name: str
    path: str
    kind: str
    size: int
    created_at: str = Field(default_factory=utc_now)


class SkillInfo(BaseModel):
    id: str
    name: str
    description: str
    required_inputs: list[str]
    output_contract: list[str]


class AdapterContext(BaseModel):
    skill_type: str
    prompt: str
    expected_outputs: list[str]
