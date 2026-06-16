from __future__ import annotations

import queue
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from .adapters import get_adapter
from .api_runner import ApiRunner
from .key_store import KeyStore
from .models import Artifact, Job
from .provider_validation import first_shape_error, shape_from_profile
from .runner import CodexRunner, redact_secrets
from .store import Store


class JobManager:
    def __init__(self, store: Store, key_store: KeyStore, data_dir: Path, max_workers: int = 1) -> None:
        self.store = store
        self.key_store = key_store
        self.data_dir = data_dir
        self.jobs_dir = data_dir / "jobs"
        self.uploads_dir = data_dir / "uploads"
        self.runner = CodexRunner()
        self.api_runner = ApiRunner()
        self.max_run_seconds = 30 * 60
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.events: dict[str, queue.Queue[dict[str, Any]]] = {}
        self.canceled: set[str] = set()
        self.lock = threading.Lock()
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)

    def enqueue(self, job: Job) -> None:
        self.executor.submit(self._run_job, job.id)

    def cancel(self, job_id: str) -> Job:
        self.canceled.add(job_id)
        self._emit(job_id, {"type": "job.canceled", "message": "Cancellation requested."})
        return self.store.update_job_status(job_id, "canceled")

    def get_queue(self, job_id: str) -> queue.Queue[dict[str, Any]]:
        with self.lock:
            return self.events.setdefault(job_id, queue.Queue())

    def _emit(self, job_id: str, event: dict[str, Any]) -> None:
        event["job_id"] = job_id
        self.get_queue(job_id).put(event)

    def _run_job(self, job_id: str) -> None:
        try:
            job = self.store.get_job(job_id)
            if job.status == "canceled":
                return
            job = self.store.update_job_status(job_id, "running")
            self._emit(job_id, {"type": "job.started", "message": "Job started."})

            workspace = self.jobs_dir / job.id
            workspace.mkdir(parents=True, exist_ok=True)
            self.store.set_job_workspace(job.id, str(workspace))

            files = self._copy_files_to_workspace(job, workspace)
            adapter = get_adapter(job.skill_type)
            context = adapter.prepare(job.id, job.prompt, job.options, files, workspace)
            prompt_file = workspace / "prompt.txt"
            prompt_file.write_text(context.prompt, encoding="utf-8")

            provider = self.store.get_provider(job.provider_profile_id)
            api_key = self.key_store.get(provider.id) if provider else None
            provider_shape = shape_from_profile(provider, api_key) if provider else None
            if provider:
                provider_error = first_shape_error(provider_shape, require_api_key=True)
                if provider_error:
                    self.store.update_job_status(job.id, "failed", error=provider_error)
                    self._emit(job.id, {"type": "job.failed", "message": provider_error})
                    return

            if provider_shape:
                result = self.api_runner.run(
                    prompt=context.prompt,
                    workspace=workspace,
                    provider=provider_shape,
                    expected_outputs=context.expected_outputs,
                    on_event=lambda event: self._emit(job.id, event),
                )
            else:
                result = self.runner.run(
                    prompt_file=prompt_file,
                    workspace=workspace,
                    provider=None,
                    api_key=None,
                    on_event=lambda event: self._emit(job.id, event),
                    should_cancel=lambda: job.id in self.canceled,
                    max_seconds=self.max_run_seconds,
                )

            if job.id in self.canceled:
                self.store.update_job_status(job.id, "canceled")
                self._emit(job.id, {"type": "job.finished", "message": "Job canceled."})
                return

            artifacts = self._record_artifacts(job, adapter.scan_artifacts(workspace))
            if result.code != 0:
                detail = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else ""
                error = f"Codex exited with code {result.code}" + (f": {detail}" if detail else "")
                self.store.update_job_status(job.id, "failed", error=error)
                self._emit(job.id, {"type": "job.failed", "message": error})
                return
            if self._needs_input(workspace):
                self.store.update_job_status(job.id, "needs_input")
                self._emit(job.id, {"type": "job.needs_input", "message": "The skill needs more input."})
                return
            self.store.update_job_status(job.id, "succeeded")
            self._emit(job.id, {"type": "job.succeeded", "message": f"Generated {len(artifacts)} artifact(s)."})
        except Exception as exc:
            message = redact_secrets(str(exc))
            self.store.update_job_status(job_id, "failed", error=message)
            self._emit(job_id, {"type": "job.failed", "message": message})
        finally:
            self._emit(job_id, {"type": "stream.end", "message": "Event stream ended."})

    def _copy_files_to_workspace(self, job: Job, workspace: Path) -> list[Path]:
        files = self.store.get_files(job.file_ids)
        target_dir = workspace / "input"
        target_dir.mkdir(parents=True, exist_ok=True)
        copied: list[Path] = []
        for file in files:
            source = Path(file.path)
            target = target_dir / file.name
            if source.exists():
                shutil.copy2(source, target)
                copied.append(target)
        return copied

    def _record_artifacts(self, job: Job, artifacts: list[Artifact]) -> list[Artifact]:
        self.store.clear_artifacts(job.id)
        recorded: list[Artifact] = []
        for artifact in artifacts:
            artifact = self._publish_artifact(job, artifact)
            recorded.append(
                self.store.add_artifact(
                    job_id=job.id,
                    name=artifact.name,
                    path=artifact.path,
                    kind=artifact.kind,
                    size=artifact.size,
                )
            )
        return recorded

    def _publish_artifact(self, job: Job, artifact: Artifact) -> Artifact:
        output_path = job.options.get("outputPath")
        if not isinstance(output_path, str) or not output_path.strip():
            return artifact
        output_dir = Path(output_path).expanduser()
        if not output_dir.is_absolute():
            return artifact

        source = Path(artifact.path)
        if not source.exists():
            return artifact

        relative_path = Path(artifact.name)
        if job.workspace:
            try:
                relative_path = source.resolve().relative_to(Path(job.workspace).resolve())
            except ValueError:
                relative_path = Path(artifact.name)
        target = output_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)
        return artifact.model_copy(update={"path": str(target), "size": target.stat().st_size})

    @staticmethod
    def _needs_input(workspace: Path) -> bool:
        for path in workspace.glob("**/*"):
            if path.is_file() and path.suffix.lower() in {".txt", ".md", ".log"}:
                if path.name == "prompt.txt":
                    continue
                try:
                    if "NEEDS_INPUT" in path.read_text(encoding="utf-8", errors="ignore"):
                        return True
                except OSError:
                    continue
        return False
