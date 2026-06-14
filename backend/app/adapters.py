from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import AdapterContext, Artifact, SkillInfo
from .utils import new_id


SKILL_TYPES = [
    "nature-paper2ppt",
    "nature-polishing",
    "guizang-ppt-skill",
    "make-poster",
    "mondo-poster-design",
]


KIND_BY_SUFFIX = {
    ".md": "markdown",
    ".markdown": "markdown",
    ".html": "html",
    ".htm": "html",
    ".pptx": "presentation",
    ".pdf": "pdf",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
    ".json": "json",
}


@dataclass(frozen=True)
class SkillAdapter:
    skill_type: str
    name: str
    description: str
    required_inputs: list[str]
    output_contract: list[str]
    prompt_template: str

    def info(self) -> SkillInfo:
        return SkillInfo(
            id=self.skill_type,
            name=self.name,
            description=self.description,
            required_inputs=self.required_inputs,
            output_contract=self.output_contract,
        )

    def prepare(
        self,
        job_id: str,
        prompt: str,
        options: dict[str, Any],
        files: list[Path],
        workspace: Path,
    ) -> AdapterContext:
        if not prompt.strip():
            raise ValueError("prompt is required")
        workspace.mkdir(parents=True, exist_ok=True)
        file_lines = "\n".join(f"- {path}" for path in files) or "- No uploaded files."
        option_lines = "\n".join(f"- {key}: {value}" for key, value in sorted(options.items())) or "- No extra options."
        expected_lines = "\n".join(f"- {item}" for item in self.output_contract)
        full_prompt = self.prompt_template.format(
            skill_type=self.skill_type,
            job_id=job_id,
            user_prompt=prompt.strip(),
            workspace=workspace,
            files=file_lines,
            options=option_lines,
            outputs=expected_lines,
        )
        return AdapterContext(
            skill_type=self.skill_type,
            prompt=full_prompt,
            expected_outputs=self.output_contract,
        )

    def scan_artifacts(self, workspace: Path) -> list[Artifact]:
        artifacts: list[Artifact] = []
        for pattern in self.output_contract:
            if pattern == "outputs":
                candidates = [p for p in (workspace / "outputs").glob("*") if p.is_file()] if (workspace / "outputs").exists() else []
            elif pattern == "prompt":
                candidates = list(workspace.glob("*prompt*.*")) + list(workspace.glob("*design*.*"))
            else:
                target = workspace / pattern
                candidates = [target] if target.exists() and target.is_file() else []
                if not candidates and "*" in pattern:
                    candidates = [p for p in workspace.glob(pattern) if p.is_file()]
            for path in candidates:
                artifacts.append(_artifact_from_path(path))
        seen: set[str] = set()
        unique: list[Artifact] = []
        for artifact in artifacts:
            if artifact.path not in seen:
                seen.add(artifact.path)
                unique.append(artifact)
        return sorted(unique, key=lambda artifact: artifact.name)


def _artifact_from_path(path: Path) -> Artifact:
    return Artifact(
        id=new_id("artifact"),
        job_id="",
        name=path.name,
        path=str(path),
        kind=KIND_BY_SUFFIX.get(path.suffix.lower(), "file"),
        size=path.stat().st_size,
    )


BASE_TEMPLATE = """Use the ${skill_type} skill for this job.

Job ID: {job_id}
Workspace: {workspace}

User request:
{user_prompt}

Uploaded source files:
{files}

Options:
{options}

Required output contract:
{outputs}

Instructions:
- Work only inside the workspace above.
- Copy or create every final deliverable inside the workspace using the exact paths in the output contract when applicable.
- If required information is missing, write a concise NEEDS_INPUT message explaining exactly what is missing.
- Do not expose API keys or environment variables in logs or output files.
"""


ADAPTERS: dict[str, SkillAdapter] = {
    "nature-paper2ppt": SkillAdapter(
        skill_type="nature-paper2ppt",
        name="Nature Paper to PPT",
        description="Create a Chinese Nature-style PPTX deck from a scientific paper or paper notes.",
        required_inputs=["paper PDF, paper text, or structured reading notes"],
        output_contract=["final_presentation_cn.pptx", "qa_report.md", "assets/figures/*", "asset_manifest.md"],
        prompt_template=BASE_TEMPLATE + "\nPrimary deliverable must be a real PPTX deck, not just an outline.\n",
    ),
    "nature-polishing": SkillAdapter(
        skill_type="nature-polishing",
        name="Nature Polishing",
        description="Polish, restructure, or translate academic prose into Nature-leaning English.",
        required_inputs=["academic text, abstract, section draft, or manuscript notes"],
        output_contract=["polished.md", "revision_notes.md"],
        prompt_template=BASE_TEMPLATE + "\nSave polished prose to polished.md and concise revision notes to revision_notes.md.\n",
    ),
    "guizang-ppt-skill": SkillAdapter(
        skill_type="guizang-ppt-skill",
        name="Guizang Web PPT",
        description="Generate an editorial magazine and e-ink style horizontal HTML slide deck.",
        required_inputs=["topic, audience, duration, source material, optional images"],
        output_contract=["ppt/index.html", "ppt/images/*"],
        prompt_template=BASE_TEMPLATE + "\nCreate the single-file web PPT at ppt/index.html with relative image assets in ppt/images/.\n",
    ),
    "make-poster": SkillAdapter(
        skill_type="make-poster",
        name="Academic Poster",
        description="Generate an interactive HTML conference poster and optional PDF from paper materials.",
        required_inputs=["paper source or PDF, project URL, formatting notes, optional references"],
        output_contract=["poster/index.html", "poster/poster.pdf", "poster/poster-config.json"],
        prompt_template=BASE_TEMPLATE + "\nCreate a self-contained poster website and PDF under poster/.\n",
    ),
    "mondo-poster-design": SkillAdapter(
        skill_type="mondo-poster-design",
        name="Mondo Poster Design",
        description="Create Mondo-style English poster, cover, or visual prompt packages, with image output when provider keys are available.",
        required_inputs=["subject, format, style preference, aspect ratio, optional reference image"],
        output_contract=["outputs", "prompt", "mondo_prompt.md"],
        prompt_template=BASE_TEMPLATE + "\nSave a prompt/design package as mondo_prompt.md and generated images under outputs/ when available.\n",
    ),
}


def get_adapter(skill_type: str) -> SkillAdapter:
    try:
        return ADAPTERS[skill_type]
    except KeyError as exc:
        raise ValueError(f"Unknown skill type: {skill_type}") from exc


def list_skills() -> list[SkillInfo]:
    return [ADAPTERS[skill_type].info() for skill_type in SKILL_TYPES]


def classify_skill_type(prompt: str) -> str:
    text = prompt.lower()
    academic_poster_tokens = ["conference poster", "academic poster", "scientific poster", "research poster", "学术海报", "科研海报", "会议海报"]
    general_poster_tokens = ["mondo", "movie poster", "book cover", "cover design", "poster", "海报", "英语海报", "英文海报", "封面"]
    if any(token in text for token in academic_poster_tokens):
        return "make-poster"
    if any(token in text for token in ["网页 ppt", "web ppt", "电子杂志", "guizang", "横向"]):
        return "guizang-ppt-skill"
    if any(token in text for token in ["ppt", "pptx", "组会", "paper", "论文"]):
        return "nature-paper2ppt"
    if any(token in text for token in general_poster_tokens):
        return "mondo-poster-design"
    if any(token in text for token in ["polish", "润色", "abstract", "nature style english", "manuscript"]):
        return "nature-polishing"
    return "nature-polishing"
