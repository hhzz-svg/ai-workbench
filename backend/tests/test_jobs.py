from pathlib import Path

from app.api_runner import ApiRunResult
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


def test_job_with_provider_uses_api_runner_instead_of_codex(tmp_path):
    store = Store(tmp_path / "app.db")
    key_store = KeyStore(tmp_path)
    provider = store.create_provider(
        name="OpenAI compatible",
        provider="proxy",
        base_url="https://api.example.com/v1",
        model="gpt-5.5",
        wire_api="responses",
    )
    key_store.set(provider.id, "secret-key")
    job = store.create_job("nature-polishing", "Polish this abstract.", {}, [], provider.id)
    manager = JobManager(store, key_store, tmp_path)

    def fake_api_run(*, workspace: Path, **_kwargs):
        (workspace / "polished.md").write_text("Polished via API", encoding="utf-8")
        (workspace / "revision_notes.md").write_text("Notes", encoding="utf-8")
        return ApiRunResult(code=0)

    manager.api_runner.run = fake_api_run  # type: ignore[method-assign]
    manager.runner.run = lambda **_kwargs: (_ for _ in ()).throw(AssertionError("Codex runner should not run"))  # type: ignore[method-assign]

    manager._run_job(job.id)

    finished = store.get_job(job.id)
    artifacts = store.list_artifacts(job.id)
    assert finished.status == "succeeded"
    assert [artifact.name for artifact in artifacts] == ["polished.md", "revision_notes.md"]


def test_needs_input_scan_ignores_runner_prompt_file(tmp_path):
    (tmp_path / "prompt.txt").write_text("Write a NEEDS_INPUT message if inputs are missing.", encoding="utf-8")

    assert JobManager._needs_input(tmp_path) is False
