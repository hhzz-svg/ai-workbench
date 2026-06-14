from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import Artifact, Job, ProviderProfile, UploadedFile, utc_now
from .utils import new_id


class Store:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                create table if not exists providers (
                    id text primary key,
                    name text not null,
                    provider text not null,
                    base_url text not null,
                    model text not null,
                    wire_api text not null,
                    api_key_env text not null,
                    has_api_key integer not null,
                    created_at text not null
                );
                create table if not exists files (
                    id text primary key,
                    name text not null,
                    path text not null,
                    size integer not null,
                    content_type text,
                    created_at text not null
                );
                create table if not exists jobs (
                    id text primary key,
                    skill_type text not null,
                    prompt text not null,
                    options text not null,
                    file_ids text not null,
                    provider_profile_id text,
                    status text not null,
                    workspace text,
                    created_at text not null,
                    updated_at text not null,
                    error text
                );
                create table if not exists artifacts (
                    id text primary key,
                    job_id text not null,
                    name text not null,
                    path text not null,
                    kind text not null,
                    size integer not null,
                    created_at text not null
                );
                """
            )

    def create_provider(self, *, name: str, provider: str, base_url: str, model: str, wire_api: str) -> ProviderProfile:
        profile = ProviderProfile(
            id=new_id("provider"),
            name=name,
            provider=provider,
            base_url=base_url,
            model=model,
            wire_api=wire_api,  # type: ignore[arg-type]
            has_api_key=True,
        )
        with self._connect() as conn:
            conn.execute(
                """
                insert into providers values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile.id,
                    profile.name,
                    profile.provider,
                    profile.base_url,
                    profile.model,
                    profile.wire_api,
                    profile.api_key_env,
                    1,
                    profile.created_at,
                ),
            )
        return profile

    def list_providers(self) -> list[ProviderProfile]:
        with self._connect() as conn:
            rows = conn.execute("select * from providers order by created_at desc").fetchall()
        return [self._provider_from_row(row) for row in rows]

    def get_provider(self, provider_id: str | None) -> ProviderProfile | None:
        if not provider_id:
            return None
        with self._connect() as conn:
            row = conn.execute("select * from providers where id = ?", (provider_id,)).fetchone()
        return self._provider_from_row(row) if row else None

    def delete_provider(self, provider_id: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("delete from providers where id = ?", (provider_id,))
        return cursor.rowcount > 0

    def save_file(self, *, name: str, path: str, size: int, content_type: str | None) -> UploadedFile:
        file = UploadedFile(id=new_id("file"), name=name, path=path, size=size, content_type=content_type)
        with self._connect() as conn:
            conn.execute(
                "insert into files values (?, ?, ?, ?, ?, ?)",
                (file.id, file.name, file.path, file.size, file.content_type, file.created_at),
            )
        return file

    def get_files(self, file_ids: list[str]) -> list[UploadedFile]:
        if not file_ids:
            return []
        marks = ",".join("?" for _ in file_ids)
        with self._connect() as conn:
            rows = conn.execute(f"select * from files where id in ({marks})", file_ids).fetchall()
        by_id = {row["id"]: self._file_from_row(row) for row in rows}
        return [by_id[file_id] for file_id in file_ids if file_id in by_id]

    def create_job(
        self,
        skill_type: str,
        prompt: str,
        options: dict[str, Any],
        file_ids: list[str],
        provider_profile_id: str | None,
    ) -> Job:
        job = Job(
            id=new_id("job"),
            skill_type=skill_type,
            prompt=prompt,
            options=options,
            file_ids=file_ids,
            provider_profile_id=provider_profile_id,
        )
        with self._connect() as conn:
            conn.execute(
                "insert into jobs values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    job.id,
                    job.skill_type,
                    job.prompt,
                    json.dumps(job.options),
                    json.dumps(job.file_ids),
                    job.provider_profile_id,
                    job.status,
                    job.workspace,
                    job.created_at,
                    job.updated_at,
                    job.error,
                ),
            )
        return job

    def set_job_workspace(self, job_id: str, workspace: str) -> Job:
        with self._connect() as conn:
            conn.execute(
                "update jobs set workspace = ?, updated_at = ? where id = ?",
                (workspace, utc_now(), job_id),
            )
        return self.get_job(job_id)

    def update_job_status(self, job_id: str, status: str, error: str | None = None) -> Job:
        with self._connect() as conn:
            conn.execute(
                "update jobs set status = ?, error = ?, updated_at = ? where id = ?",
                (status, error, utc_now(), job_id),
            )
        return self.get_job(job_id)

    def fail_interrupted_jobs(self, message: str) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                update jobs
                set status = 'failed', error = ?, updated_at = ?
                where status in ('pending', 'running')
                """,
                (message, utc_now()),
            )
        return cursor.rowcount

    def get_job(self, job_id: str) -> Job:
        with self._connect() as conn:
            row = conn.execute("select * from jobs where id = ?", (job_id,)).fetchone()
        if not row:
            raise KeyError(job_id)
        return self._job_from_row(row)

    def list_jobs(self) -> list[Job]:
        with self._connect() as conn:
            rows = conn.execute("select * from jobs order by created_at desc").fetchall()
        return [self._job_from_row(row) for row in rows]

    def delete_job(self, job_id: str) -> bool:
        with self._connect() as conn:
            conn.execute("delete from artifacts where job_id = ?", (job_id,))
            cursor = conn.execute("delete from jobs where id = ?", (job_id,))
        return cursor.rowcount > 0

    def delete_jobs_by_status(self, statuses: list[str]) -> list[Job]:
        jobs = [job for job in self.list_jobs() if job.status in statuses]
        for job in jobs:
            self.delete_job(job.id)
        return jobs

    def add_artifact(self, *, job_id: str, name: str, path: str, kind: str, size: int) -> Artifact:
        artifact = Artifact(id=new_id("artifact"), job_id=job_id, name=name, path=path, kind=kind, size=size)
        with self._connect() as conn:
            conn.execute(
                "insert into artifacts values (?, ?, ?, ?, ?, ?, ?)",
                (artifact.id, artifact.job_id, artifact.name, artifact.path, artifact.kind, artifact.size, artifact.created_at),
            )
        return artifact

    def clear_artifacts(self, job_id: str) -> None:
        with self._connect() as conn:
            conn.execute("delete from artifacts where job_id = ?", (job_id,))

    def list_artifacts(self, job_id: str) -> list[Artifact]:
        with self._connect() as conn:
            rows = conn.execute("select * from artifacts where job_id = ? order by created_at, name", (job_id,)).fetchall()
        return [self._artifact_from_row(row) for row in rows]

    def get_artifact(self, artifact_id: str) -> Artifact:
        with self._connect() as conn:
            row = conn.execute("select * from artifacts where id = ?", (artifact_id,)).fetchone()
        if not row:
            raise KeyError(artifact_id)
        return self._artifact_from_row(row)

    @staticmethod
    def _provider_from_row(row: sqlite3.Row) -> ProviderProfile:
        return ProviderProfile(
            id=row["id"],
            name=row["name"],
            provider=row["provider"],
            base_url=row["base_url"],
            model=row["model"],
            wire_api=row["wire_api"],
            api_key_env=row["api_key_env"],
            has_api_key=bool(row["has_api_key"]),
            created_at=row["created_at"],
        )

    @staticmethod
    def _file_from_row(row: sqlite3.Row) -> UploadedFile:
        return UploadedFile(
            id=row["id"],
            name=row["name"],
            path=row["path"],
            size=row["size"],
            content_type=row["content_type"],
            created_at=row["created_at"],
        )

    @staticmethod
    def _job_from_row(row: sqlite3.Row) -> Job:
        return Job(
            id=row["id"],
            skill_type=row["skill_type"],
            prompt=row["prompt"],
            options=json.loads(row["options"]),
            file_ids=json.loads(row["file_ids"]),
            provider_profile_id=row["provider_profile_id"],
            status=row["status"],
            workspace=row["workspace"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            error=row["error"],
        )

    @staticmethod
    def _artifact_from_row(row: sqlite3.Row) -> Artifact:
        return Artifact(
            id=row["id"],
            job_id=row["job_id"],
            name=row["name"],
            path=row["path"],
            kind=row["kind"],
            size=row["size"],
            created_at=row["created_at"],
        )
