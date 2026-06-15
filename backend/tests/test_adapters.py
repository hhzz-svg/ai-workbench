from pathlib import Path

import pytest

from app.adapters import SKILL_TYPES, classify_skill_type, get_adapter


def test_registry_exposes_five_core_skills():
    assert set(SKILL_TYPES) == {
        "nature-paper2ppt",
        "nature-polishing",
        "guizang-ppt-skill",
        "make-poster",
        "mondo-poster-design",
    }


@pytest.mark.parametrize(
    ("skill_type", "expected_outputs"),
    [
        ("nature-paper2ppt", ["final_presentation_cn.pptx", "qa_report.md"]),
        ("nature-polishing", ["polished.md", "revision_notes.md"]),
        ("guizang-ppt-skill", ["ppt/index.html"]),
        ("make-poster", ["poster/index.html", "poster.pdf", "poster-config.json"]),
        ("mondo-poster-design", ["outputs", "prompt"]),
    ],
)
def test_each_adapter_builds_skill_prompt_with_output_contract(skill_type, expected_outputs, tmp_path):
    adapter = get_adapter(skill_type)
    context = adapter.prepare(
        job_id="job_123",
        prompt="Create the requested artifact from my material.",
        options={"language": "zh-CN", "size": "16:9"},
        files=[],
        workspace=tmp_path,
    )

    assert skill_type in context.prompt
    for output in expected_outputs:
        assert output in context.prompt
    assert str(tmp_path) in context.prompt


@pytest.mark.parametrize(
    ("prompt", "expected"),
    [
        ("帮我把这篇 Nature 论文做成中文组会 PPT", "nature-paper2ppt"),
        ("polish this abstract into Nature style English", "nature-polishing"),
        ("做一个电子杂志风格横向网页 PPT", "guizang-ppt-skill"),
        ("根据论文和项目页做一个 conference academic poster", "make-poster"),
        ("generate a Mondo style English movie poster", "mondo-poster-design"),
        ("生成一个3页的英文 how to make student campus life easier 英语海报", "mondo-poster-design"),
        ("做一张校园生活主题英语海报", "mondo-poster-design"),
        ("根据论文做一张学术海报", "make-poster"),
    ],
)
def test_classifier_maps_prompt_to_known_adapter(prompt, expected):
    assert classify_skill_type(prompt) == expected


def test_adapter_scans_expected_artifacts(tmp_path):
    adapter = get_adapter("nature-polishing")
    (tmp_path / "polished.md").write_text("Polished", encoding="utf-8")
    (tmp_path / "revision_notes.md").write_text("Notes", encoding="utf-8")

    artifacts = adapter.scan_artifacts(tmp_path)

    assert [artifact.name for artifact in artifacts] == ["polished.md", "revision_notes.md"]
    assert {artifact.kind for artifact in artifacts} == {"markdown"}


def test_adapter_rejects_empty_prompt(tmp_path):
    adapter = get_adapter("nature-polishing")
    with pytest.raises(ValueError, match="prompt"):
        adapter.prepare("job_123", "   ", {}, [], tmp_path)


def test_adapter_prompt_names_skill_without_template_marker(tmp_path):
    adapter = get_adapter("nature-polishing")
    context = adapter.prepare("job_123", "Polish this abstract.", {}, [], tmp_path)

    assert "Use the nature-polishing skill" in context.prompt
    assert "$nature-polishing" not in context.prompt
