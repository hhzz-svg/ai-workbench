from pathlib import Path

from app.jobs import JobManager
from app.key_store import KeyStore
from app.models import Artifact
from app.store import Store


def test_record_artifacts_copies_outputs_to_custom_output_path(tmp_path):
    store = Store(tmp_path / "app.db")
    output_dir = tmp_path / "published"
    job = store.create_job(
        "nature-polishing",
        "Prompt",
        {"outputPath": str(output_dir)},
        [],
        None,
    )
    workspace = tmp_path / "jobs" / job.id
    source = workspace / "nested" / "polished.md"
    source.parent.mkdir(parents=True)
    source.write_text("Polished text", encoding="utf-8")
    store.set_job_workspace(job.id, str(workspace))
    manager = JobManager(store, KeyStore(tmp_path), tmp_path)

    recorded = manager._record_artifacts(
        store.get_job(job.id),
        [
            Artifact(
                id="artifact_1",
                job_id=job.id,
                name="polished.md",
                path=str(source),
                kind="markdown",
                size=source.stat().st_size,
            )
        ],
    )

    published = output_dir / "nested" / "polished.md"
    assert published.read_text(encoding="utf-8") == "Polished text"
    assert recorded[0].path == str(published)
