from app.api_runner import write_api_artifacts


def test_write_api_artifacts_saves_fenced_file_blocks(tmp_path):
    response = """Done.

```file path=polished.md
Polished text
```

```file path=revision_notes.md
- tightened logic
```
"""

    written = write_api_artifacts(response, tmp_path, ["polished.md", "revision_notes.md"])

    assert written == 2
    assert (tmp_path / "polished.md").read_text(encoding="utf-8") == "Polished text\n"
    assert (tmp_path / "revision_notes.md").read_text(encoding="utf-8") == "- tightened logic\n"


def test_write_api_artifacts_falls_back_to_first_text_contract(tmp_path):
    written = write_api_artifacts("Plain model answer", tmp_path, ["final.pptx", "qa_report.md"])

    assert written == 1
    assert (tmp_path / "qa_report.md").read_text(encoding="utf-8") == "Plain model answer\n"


def test_write_api_artifacts_ignores_unsafe_or_binary_paths(tmp_path):
    response = """```file path=../outside.md
bad
```

```file path=deck.pptx
not real binary
```
"""

    written = write_api_artifacts(response, tmp_path, ["polished.md"])

    assert written == 0
    assert not (tmp_path.parent / "outside.md").exists()
    assert not (tmp_path / "deck.pptx").exists()
