from __future__ import annotations

import json
import os
import queue
import shutil
import re
import subprocess
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import ProviderProfile


SECRET_PATTERNS = [
    re.compile(r"Bearer\s+[A-Za-z0-9._\-]+", re.IGNORECASE),
    re.compile(r"(OPENAI_API_KEY|CODEX_API_KEY|SKILL_WORKBENCH_API_KEY)=([^\s]+)", re.IGNORECASE),
    re.compile(r"sk-[A-Za-z0-9_\-]+"),
]


@dataclass(frozen=True)
class RunResult:
    code: int
    stderr: str = ""


def redact_secrets(text: str, secrets: list[str] | None = None) -> str:
    redacted = text
    for secret in secrets or []:
        if secret:
            redacted = redacted.replace(secret, "[REDACTED]")
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


class CodexRunner:
    def __init__(self, codex_bin: str | None = None) -> None:
        self.codex_command = [codex_bin] if codex_bin else default_codex_command()

    def build_command(
        self,
        prompt_file: Path,
        workspace: Path,
        provider: ProviderProfile | None,
        api_key: str | None,
    ) -> tuple[list[str], dict[str, str]]:
        env = os.environ.copy()
        command = [
            *self.codex_command,
            "exec",
            "--json",
            "--skip-git-repo-check",
            "--sandbox",
            "workspace-write",
            "-C",
            str(workspace),
        ]
        if provider:
            env[provider.api_key_env] = api_key or ""
            provider_id = "skill_workbench"
            command.extend(
                [
                    "-c",
                    f'model="{provider.model}"',
                    "-c",
                    f'model_provider="{provider_id}"',
                    "-c",
                    f'model_providers.{provider_id}.name="{provider.name}"',
                    "-c",
                    f'model_providers.{provider_id}.base_url="{provider.base_url}"',
                    "-c",
                    f'model_providers.{provider_id}.env_key="{provider.api_key_env}"',
                    "-c",
                    f'model_providers.{provider_id}.wire_api="{provider.wire_api}"',
                ]
            )
        command.append("-")
        return command, env

    @staticmethod
    def parse_event(line: str) -> dict[str, Any]:
        try:
            raw = json.loads(line)
        except json.JSONDecodeError:
            return {"type": "log", "message": line}
        message = ""
        item = raw.get("item") if isinstance(raw, dict) else None
        if isinstance(item, dict):
            message = item.get("text") or item.get("command") or item.get("type") or ""
        if not message:
            message = raw.get("message") or raw.get("type") or ""
        return {"type": raw.get("type", "event"), "message": message, "raw": raw}

    def run(
        self,
        prompt_file: Path,
        workspace: Path,
        provider: ProviderProfile | None,
        api_key: str | None,
        on_event: Callable[[dict[str, Any]], None],
        should_cancel: Callable[[], bool] | None = None,
        max_seconds: float | None = None,
    ) -> RunResult:
        command, env = self.build_command(prompt_file, workspace, provider, api_key)
        prompt = prompt_file.read_text(encoding="utf-8")
        process = subprocess.Popen(
            command,
            cwd=str(workspace),
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert process.stdin is not None
        process.stdin.write(prompt)
        process.stdin.close()

        stdout_queue: queue.Queue[str] = queue.Queue()
        stderr_chunks: list[str] = []

        assert process.stdout is not None
        stdout_thread = threading.Thread(target=_read_stdout, args=(process.stdout, stdout_queue), daemon=True)
        stdout_thread.start()

        stderr_thread: threading.Thread | None = None
        if process.stderr is not None:
            stderr_thread = threading.Thread(target=_read_stderr, args=(process.stderr, stderr_chunks), daemon=True)
            stderr_thread.start()

        canceled = False
        timed_out = False
        started_at = time.monotonic()
        while True:
            try:
                line = stdout_queue.get(timeout=0.1)
            except queue.Empty:
                line = None
            if line is not None:
                event = self.parse_event(redact_secrets(line.rstrip(), [api_key or ""]))
                on_event(event)

            if should_cancel and should_cancel():
                canceled = True
                _terminate_process_tree(process)
                break
            if max_seconds is not None and time.monotonic() - started_at > max_seconds:
                timed_out = True
                _terminate_process_tree(process)
                break
            if process.poll() is not None:
                break

        while True:
            try:
                line = stdout_queue.get_nowait()
            except queue.Empty:
                break
            event = self.parse_event(redact_secrets(line.rstrip(), [api_key or ""]))
            on_event(event)

        code = process.wait()
        stdout_thread.join(timeout=1)
        if stderr_thread is not None:
            stderr_thread.join(timeout=1)
        stderr_text = "".join(stderr_chunks)
        if canceled:
            stderr_text = f"{stderr_text}\nCanceled by user.".strip()
        if timed_out:
            stderr_text = f"{stderr_text}\nTimed out after {max_seconds:.0f} seconds.".strip()
        if stderr_text:
            on_event({"type": "stderr", "message": redact_secrets(stderr_text, [api_key or ""])})
        return RunResult(code=code, stderr=redact_secrets(stderr_text, [api_key or ""]))


def default_codex_command() -> list[str]:
    if os.name == "nt":
        return ["cmd.exe", "/c", "codex"]
    path = shutil.which("codex")
    return [path or "codex"]


def _read_stdout(stream, target: queue.Queue[str]) -> None:
    try:
        for line in stream:
            target.put(line)
    finally:
        try:
            stream.close()
        except OSError:
            pass


def _read_stderr(stream, target: list[str]) -> None:
    try:
        text = stream.read()
        if text:
            target.append(text)
    finally:
        try:
            stream.close()
        except OSError:
            pass


def _terminate_process_tree(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5,
            )
        except Exception:
            process.terminate()
    else:
        process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
