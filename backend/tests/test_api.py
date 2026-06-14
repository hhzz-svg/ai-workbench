from fastapi.testclient import TestClient

import app.main as main_module
from app.main import create_app


def test_skills_endpoint_lists_core_skills(tmp_path):
    app = create_app(data_dir=tmp_path, start_worker=False)
    client = TestClient(app)

    response = client.get("/api/skills")

    assert response.status_code == 200
    skill_types = {skill["id"] for skill in response.json()}
    assert "nature-paper2ppt" in skill_types
    assert "mondo-poster-design" in skill_types


def test_create_provider_masks_key(tmp_path):
    app = create_app(data_dir=tmp_path, start_worker=False)
    client = TestClient(app)

    response = client.post(
        "/api/providers",
        json={
            "name": "OpenAI proxy",
            "provider": "proxy",
            "base_url": "https://api.example.com/v1",
            "model": "gpt-5.5",
            "wire_api": "responses",
            "api_key": "secret",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["has_api_key"] is True
    assert "api_key" not in body


def test_create_provider_requires_a_human_name(tmp_path):
    app = create_app(data_dir=tmp_path, start_worker=False)
    client = TestClient(app)

    response = client.post(
        "/api/providers",
        json={
            "name": "  ",
            "provider": "proxy",
            "base_url": "https://api.example.com/v1",
            "model": "gpt-5.5",
            "wire_api": "responses",
            "api_key": "secret",
        },
    )

    assert response.status_code == 400
    assert "名称" in response.json()["detail"]


def test_create_provider_rejects_api_key_in_base_url(tmp_path):
    app = create_app(data_dir=tmp_path, start_worker=False)
    client = TestClient(app)

    response = client.post(
        "/api/providers",
        json={
            "name": "Proxy",
            "provider": "proxy",
            "base_url": "sk-wrong-field",
            "model": "gpt-5.5",
            "wire_api": "responses",
            "api_key": "secret",
        },
    )

    assert response.status_code == 400
    assert "Base URL" in response.json()["detail"]


def test_validate_provider_reports_shape_errors_without_saving(tmp_path):
    app = create_app(data_dir=tmp_path, start_worker=False)
    client = TestClient(app)

    response = client.post(
        "/api/providers/validate",
        json={
            "name": "Proxy",
            "provider": "proxy",
            "base_url": "sk-wrong-field",
            "model": "gpt-5.5",
            "wire_api": "responses",
            "api_key": "secret",
        },
    )

    assert response.status_code == 200
    assert response.json()["ok"] is False
    assert client.get("/api/providers").json() == []


def test_validate_default_provider_checks_codex_cli(tmp_path, monkeypatch):
    monkeypatch.setattr(main_module.shutil, "which", lambda name: "codex" if name == "codex" else None)
    monkeypatch.setattr(main_module.subprocess, "check_output", lambda *args, **kwargs: "codex 1.2.3")
    app = create_app(data_dir=tmp_path, start_worker=False)
    client = TestClient(app)

    response = client.post("/api/providers/default/validate")

    assert response.status_code == 200
    assert response.json() == {"ok": True, "message": "本机 Codex 可用：codex 1.2.3"}


def test_delete_provider_removes_saved_profile(tmp_path):
    app = create_app(data_dir=tmp_path, start_worker=False)
    client = TestClient(app)
    created = client.post(
        "/api/providers",
        json={
            "name": "Custom proxy",
            "provider": "proxy",
            "base_url": "https://api.example.com/v1",
            "model": "gpt-5.5",
            "wire_api": "responses",
            "api_key": "secret",
        },
    ).json()

    response = client.delete(f"/api/providers/{created['id']}")

    assert response.status_code == 200
    assert response.json()["deleted"] is True
    assert client.get("/api/providers").json() == []


def test_create_job_enqueues_pending_job(tmp_path):
    app = create_app(data_dir=tmp_path, start_worker=False)
    client = TestClient(app)

    response = client.post(
        "/api/jobs",
        json={
            "skillType": "auto",
            "prompt": "polish this abstract into Nature style English",
            "fileIds": [],
            "options": {},
            "providerProfileId": None,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["skill_type"] == "nature-polishing"
    assert body["status"] == "pending"


def test_app_marks_interrupted_jobs_failed_on_startup(tmp_path):
    app = create_app(data_dir=tmp_path, start_worker=False)
    store = app.state.store
    running = store.create_job("nature-polishing", "Prompt", {}, [], None)
    store.update_job_status(running.id, "running")

    restarted = create_app(data_dir=tmp_path, start_worker=False)
    client = TestClient(restarted)

    job = client.get(f"/api/jobs/{running.id}").json()
    assert job["status"] == "failed"
    assert "后台服务已重启" in job["error"]


def test_delete_failed_job_removes_record_and_workspace(tmp_path):
    app = create_app(data_dir=tmp_path, start_worker=False)
    store = app.state.store
    job = store.create_job("nature-polishing", "Prompt", {}, [], None)
    workspace = tmp_path / "jobs" / job.id
    workspace.mkdir(parents=True)
    (workspace / "prompt.txt").write_text("prompt", encoding="utf-8")
    store.set_job_workspace(job.id, str(workspace))
    store.update_job_status(job.id, "failed", "nope")
    client = TestClient(app)

    response = client.delete(f"/api/jobs/{job.id}")

    assert response.status_code == 200
    assert response.json() == {"deleted": True}
    assert client.get(f"/api/jobs/{job.id}").status_code == 404
    assert not workspace.exists()


def test_delete_running_job_is_rejected(tmp_path):
    app = create_app(data_dir=tmp_path, start_worker=False)
    store = app.state.store
    job = store.create_job("nature-polishing", "Prompt", {}, [], None)
    store.update_job_status(job.id, "running")
    client = TestClient(app)

    response = client.delete(f"/api/jobs/{job.id}")

    assert response.status_code == 409


def test_clear_failed_jobs_removes_only_failed_and_canceled(tmp_path):
    app = create_app(data_dir=tmp_path, start_worker=False)
    store = app.state.store
    failed = store.create_job("nature-polishing", "Failed", {}, [], None)
    canceled = store.create_job("nature-polishing", "Canceled", {}, [], None)
    succeeded = store.create_job("nature-polishing", "Succeeded", {}, [], None)
    store.update_job_status(failed.id, "failed", "bad")
    store.update_job_status(canceled.id, "canceled")
    store.update_job_status(succeeded.id, "succeeded")
    client = TestClient(app)

    response = client.post("/api/jobs/clear-failed")

    assert response.status_code == 200
    assert response.json() == {"deleted": 2}
    remaining_ids = {job["id"] for job in client.get("/api/jobs").json()}
    assert remaining_ids == {succeeded.id}
