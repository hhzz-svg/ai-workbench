from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse

from .adapters import classify_skill_type, list_skills
from .jobs import JobManager
from .key_store import KeyStore
from .models import JobCreate, JobReply, ProviderCreate, ProviderValidate, ProviderValidationResult
from .provider_validation import (
    first_shape_error,
    shape_from_create,
    shape_from_profile,
    shape_from_validate,
    validate_custom_provider_connection,
)
from .runner import default_codex_command
from .store import Store
from .utils import new_id


def default_data_dir() -> Path:
    return Path.home() / ".skill-workbench"


def create_app(data_dir: Path | None = None, start_worker: bool = True) -> FastAPI:
    root = data_dir or default_data_dir()
    root.mkdir(parents=True, exist_ok=True)
    store = Store(root / "app.db")
    store.fail_interrupted_jobs("后台服务已重启，之前未完成的任务已中断。请重新创建任务。")
    key_store = KeyStore(root)
    manager = JobManager(store, key_store, root)

    app = FastAPI(title="Skill Workbench", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.store = store
    app.state.key_store = key_store
    app.state.manager = manager
    app.state.start_worker = start_worker

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        codex = shutil.which("codex")
        version = None
        if codex:
            try:
                version = subprocess.check_output([*default_codex_command(), "--version"], text=True, timeout=15).strip()
            except Exception as exc:
                version = f"unavailable: {type(exc).__name__}"
        return {"ok": True, "codex_available": bool(codex), "codex_version": version, "data_dir": str(root)}

    @app.get("/api/skills")
    def skills():
        return [skill.model_dump() for skill in list_skills()]

    @app.post("/api/providers")
    def create_provider(payload: ProviderCreate):
        shape = shape_from_create(payload)
        shape_error = first_shape_error(shape, require_api_key=True)
        if shape_error:
            raise HTTPException(status_code=400, detail=shape_error)
        profile = store.create_provider(
            name=shape.name,
            provider=shape.provider,
            base_url=shape.base_url,
            model=shape.model,
            wire_api=shape.wire_api,
        )
        key_store.set(profile.id, shape.api_key or "")
        return profile.model_dump()

    @app.get("/api/providers")
    def providers():
        return [provider.model_dump() for provider in store.list_providers()]

    @app.post("/api/providers/validate")
    def validate_provider(payload: ProviderValidate):
        result = validate_custom_provider_connection(shape_from_validate(payload))
        return result.model_dump()

    @app.post("/api/providers/default/validate")
    def validate_default_provider():
        codex = shutil.which("codex")
        if not codex:
            return ProviderValidationResult(ok=False, message="未找到 Codex CLI，请先确认 codex 已安装并在 PATH 中。").model_dump()
        try:
            version = subprocess.check_output([*default_codex_command(), "--version"], text=True, timeout=15).strip()
        except Exception as exc:
            return ProviderValidationResult(ok=False, message=f"Codex CLI 不可用：{type(exc).__name__}").model_dump()
        return ProviderValidationResult(ok=True, message=f"本机 Codex 可用：{version}").model_dump()

    @app.post("/api/providers/{provider_id}/validate")
    def validate_saved_provider(provider_id: str):
        profile = store.get_provider(provider_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Provider not found")
        api_key = key_store.get(profile.id)
        result = validate_custom_provider_connection(shape_from_profile(profile, api_key))
        return result.model_dump()

    @app.delete("/api/providers/{provider_id}")
    def delete_provider(provider_id: str):
        deleted = store.delete_provider(provider_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Provider not found")
        key_store.delete(provider_id)
        return {"deleted": True}

    @app.post("/api/files")
    async def upload_file(file: UploadFile = File(...)):
        upload_dir = root / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_id = new_id("upload")
        safe_name = Path(file.filename or file_id).name
        path = upload_dir / f"{file_id}-{safe_name}"
        size = 0
        with path.open("wb") as handle:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                handle.write(chunk)
        record = store.save_file(name=safe_name, path=str(path), size=size, content_type=file.content_type)
        return record.model_dump()

    @app.post("/api/jobs")
    def create_job(payload: JobCreate):
        skill_type = classify_skill_type(payload.prompt) if payload.skill_type == "auto" else payload.skill_type
        if skill_type not in {skill.id for skill in list_skills()}:
            raise HTTPException(status_code=400, detail=f"Unknown skill type: {skill_type}")

        # 处理自定义输出路径
        options = payload.options.copy()
        if "outputPath" in options:
            output_path = Path(options["outputPath"])
            # 验证路径
            if not output_path.is_absolute():
                raise HTTPException(status_code=400, detail="输出路径必须是绝对路径")
            # 确保目录存在
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"无法创建输出目录：{str(e)}")

        job = store.create_job(
            skill_type=skill_type,
            prompt=payload.prompt,
            options=options,
            file_ids=payload.file_ids,
            provider_profile_id=payload.provider_profile_id,
        )
        if start_worker:
            manager.enqueue(job)
        return job.model_dump()

    @app.get("/api/jobs")
    def jobs():
        return [job.model_dump() for job in store.list_jobs()]

    @app.post("/api/jobs/clear-failed")
    def clear_failed_jobs():
        removed = store.delete_jobs_by_status(["failed", "canceled"])
        for job in removed:
            _remove_job_workspace(root, job.workspace)
        return {"deleted": len(removed)}

    @app.get("/api/jobs/{job_id}")
    def job_detail(job_id: str):
        try:
            return store.get_job(job_id).model_dump()
        except KeyError:
            raise HTTPException(status_code=404, detail="Job not found") from None

    @app.delete("/api/jobs/{job_id}")
    def delete_job(job_id: str):
        try:
            job = store.get_job(job_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Job not found") from None
        if job.status in {"pending", "running"}:
            raise HTTPException(status_code=409, detail="Cannot delete a running job. Cancel it first.")
        deleted = store.delete_job(job.id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Job not found")
        _remove_job_workspace(root, job.workspace)
        return {"deleted": True}

    @app.get("/api/jobs/{job_id}/events")
    def job_events(job_id: str):
        try:
            store.get_job(job_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Job not found") from None

        def stream():
            q = manager.get_queue(job_id)
            while True:
                event = q.get()
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("type") == "stream.end":
                    break

        return StreamingResponse(stream(), media_type="text/event-stream")

    @app.post("/api/jobs/{job_id}/cancel")
    def cancel_job(job_id: str):
        try:
            return manager.cancel(job_id).model_dump()
        except KeyError:
            raise HTTPException(status_code=404, detail="Job not found") from None

    @app.post("/api/jobs/{job_id}/reply")
    def reply_to_job(job_id: str, payload: JobReply):
        try:
            job = store.get_job(job_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Job not found") from None
        new_prompt = f"{job.prompt}\n\nAdditional user input:\n{payload.prompt}"
        followup = store.create_job(job.skill_type, new_prompt, job.options, job.file_ids, job.provider_profile_id)
        if start_worker:
            manager.enqueue(followup)
        return followup.model_dump()

    @app.get("/api/jobs/{job_id}/artifacts")
    def artifacts(job_id: str):
        try:
            store.get_job(job_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Job not found") from None
        return [artifact.model_dump() for artifact in store.list_artifacts(job_id)]

    @app.get("/api/artifacts/{artifact_id}/download")
    def download_artifact(artifact_id: str):
        try:
            artifact = store.get_artifact(artifact_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Artifact not found") from None
        path = Path(artifact.path)
        if not path.exists():
            raise HTTPException(status_code=404, detail="Artifact file is missing")
        return FileResponse(path, filename=artifact.name)

    @app.post("/api/artifacts/{artifact_id}/annotate")
    def annotate_artifact(artifact_id: str, payload: dict):
        """
        对已生成的产物进行 AI 二次处理

        请求体：
        {
            "annotation": "处理指令，如：将配色改为蓝色系"
        }
        """
        try:
            artifact = store.get_artifact(artifact_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Artifact not found") from None

        annotation = payload.get("annotation", "").strip()
        if not annotation:
            raise HTTPException(status_code=400, detail="注释内容不能为空")

        # 获取原始任务信息
        try:
            original_job = store.get_job(artifact.job_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Original job not found") from None

        # 构建二次处理的提示词
        new_prompt = f"""基于已生成的文件进行修改：

原始需求：{original_job.prompt}

已生成文件：{artifact.name} ({artifact.kind})
文件路径：{artifact.path}

修改要求：{annotation}

请读取上述文件，根据修改要求进行调整，并生成新的文件。"""

        # 创建新的任务
        new_job = store.create_job(
            skill_type=original_job.skill_type,
            prompt=new_prompt,
            options={
                **original_job.options,
                "based_on_artifact": artifact_id,
                "annotation": annotation,
            },
            file_ids=[],  # 不需要重新上传文件，直接引用已有的
            provider_profile_id=original_job.provider_profile_id,
        )

        if start_worker:
            manager.enqueue(new_job)

        return {
            "new_job_id": new_job.id,
            "message": "二次处理任务已创建，请在任务列表中查看进度",
        }

    return app


app = create_app()


def _remove_job_workspace(root: Path, workspace: str | None) -> None:
    if not workspace:
        return
    jobs_root = (root / "jobs").resolve()
    path = Path(workspace).resolve()
    try:
        path.relative_to(jobs_root)
    except ValueError:
        return
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)
