from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .provider_validation import ProviderShape
from .runner import redact_secrets


TEXT_SUFFIXES = {".md", ".markdown", ".html", ".htm", ".json", ".txt", ".csv", ".svg"}
FILE_BLOCK_RE = re.compile(
    r"```(?:file|path)?\s*(?:path=)?[\"']?([^\n\"'`]+)[\"']?\n(.*?)\n```",
    re.IGNORECASE | re.DOTALL,
)


@dataclass(frozen=True)
class ApiRunResult:
    code: int
    stderr: str = ""


class ApiRunner:
    def run(
        self,
        prompt: str,
        workspace: Path,
        provider: ProviderShape,
        expected_outputs: list[str],
        on_event: Callable[[dict[str, Any]], None],
    ) -> ApiRunResult:
        workspace.mkdir(parents=True, exist_ok=True)
        on_event({"type": "api.started", "message": f"正在调用 {provider.name} · {provider.model}"})
        try:
            text = self._call_provider(_api_prompt(prompt, expected_outputs), provider)
            (workspace / "api_response.md").write_text(text, encoding="utf-8")
            written = write_api_artifacts(text, workspace, expected_outputs)
        except Exception as exc:
            message = redact_secrets(str(exc), [provider.api_key or ""])
            return ApiRunResult(code=1, stderr=message)
        on_event({"type": "api.completed", "message": f"API 直连完成，写入 {written} 个产物。"})
        return ApiRunResult(code=0)

    def _call_provider(self, prompt: str, provider: ProviderShape) -> str:
        if provider.wire_api == "chat_completions":
            url = urllib.parse.urljoin(provider.base_url.rstrip("/") + "/", "chat/completions")
            payload = {
                "model": provider.model,
                "messages": [
                    {"role": "system", "content": "You create local deliverable files for AI Workbench."},
                    {"role": "user", "content": prompt},
                ],
            }
        else:
            url = urllib.parse.urljoin(provider.base_url.rstrip("/") + "/", "responses")
            payload = {"model": provider.model, "input": prompt}

        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {provider.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body = response.read(8 * 1024 * 1024).decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            detail = exc.read(4096).decode("utf-8", errors="replace")
            raise RuntimeError(f"API 请求失败：HTTP {exc.code} {detail[:500]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"API 请求失败：{exc.reason}") from exc

        return _extract_text(body)


def write_api_artifacts(text: str, workspace: Path, expected_outputs: list[str]) -> int:
    written = 0
    seen: set[Path] = set()
    for raw_path, content in FILE_BLOCK_RE.findall(text):
        target = _safe_target(workspace, raw_path.strip())
        if not target:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content.rstrip() + "\n", encoding="utf-8")
        seen.add(target.resolve())
        written += 1

    if FILE_BLOCK_RE.search(text):
        return written

    fallback = _first_text_output(expected_outputs) or "api_response.md"
    target = _safe_target(workspace, fallback)
    if target:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text.rstrip() + "\n", encoding="utf-8")
        written += 1
    return written


def _api_prompt(prompt: str, expected_outputs: list[str]) -> str:
    outputs = "\n".join(f"- {item}" for item in expected_outputs)
    return f"""{prompt}

You are running in AI Workbench API-direct mode.
Return final deliverables as fenced file blocks so the app can save them locally.

Required output contract:
{outputs}

File block format:
```file path=relative/path.ext
file content here
```

Use only relative paths. Prefer Markdown, HTML, JSON, SVG, CSV, or plain text files.
If a requested deliverable is a binary file such as PPTX, PDF, or image, provide a complete build-ready Markdown/HTML specification and notes instead of claiming that a binary file was created.
"""


def _extract_text(body: str) -> str:
    data = json.loads(body)
    if isinstance(data, dict):
        output_text = data.get("output_text")
        if isinstance(output_text, str):
            return output_text

        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            message = choices[0].get("message") if isinstance(choices[0], dict) else None
            content = message.get("content") if isinstance(message, dict) else None
            if isinstance(content, str):
                return content

        output = data.get("output")
        if isinstance(output, list):
            parts: list[str] = []
            for item in output:
                if not isinstance(item, dict):
                    continue
                for content in item.get("content", []):
                    if isinstance(content, dict) and isinstance(content.get("text"), str):
                        parts.append(content["text"])
            if parts:
                return "\n".join(parts)
    return body


def _first_text_output(expected_outputs: list[str]) -> str | None:
    for pattern in expected_outputs:
        if "*" in pattern or pattern == "outputs":
            continue
        suffix = Path(pattern).suffix.lower()
        if suffix in TEXT_SUFFIXES:
            return pattern
    return None


def _safe_target(workspace: Path, raw_path: str) -> Path | None:
    candidate = Path(raw_path.strip().replace("\\", "/"))
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    target = (workspace / candidate).resolve()
    try:
        target.relative_to(workspace.resolve())
    except ValueError:
        return None
    if target.suffix.lower() not in TEXT_SUFFIXES:
        return None
    return target
