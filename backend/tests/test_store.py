from pathlib import Path

from app.store import Store


def test_store_creates_job_and_transitions_status(tmp_path):
    store = Store(tmp_path / "app.db")
    job = store.create_job(
        skill_type="nature-polishing",
        prompt="Polish this abstract",
        options={"language": "en"},
        file_ids=[],
        provider_profile_id=None,
    )

    assert job.status == "pending"

    updated = store.update_job_status(job.id, "running")
    assert updated.status == "running"
    assert store.get_job(job.id).status == "running"


def test_store_persists_artifacts(tmp_path):
    store = Store(tmp_path / "app.db")
    job = store.create_job("nature-polishing", "Prompt", {}, [], None)

    artifact = store.add_artifact(
        job_id=job.id,
        name="polished.md",
        path=str(tmp_path / "polished.md"),
        kind="markdown",
        size=12,
    )

    assert artifact.job_id == job.id
    assert store.list_artifacts(job.id)[0].name == "polished.md"
