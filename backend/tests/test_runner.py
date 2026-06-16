import json
import os
import sys
import time
from pathlib import Path

from app.models import ProviderProfile
from app.runner import CodexRunner, redact_secrets


def test_redact_secrets_removes_api_keys_and_bearer_tokens():
    text = "Authorization: Bearer sk-test123 and OPENAI_API_KEY=abc123"
    redacted = redact_secrets(text, ["abc123", "sk-test123"])

    assert "abc123" not in redacted
    assert "sk-test123" not in redacted
    assert "[REDACTED]" in redacted


def test_runner_builds_codex_exec_command_with_provider_overrides(tmp_path):
    provider = ProviderProfile(
        id="provider_1",
        name="Local proxy",
        provider="proxy",
        base_url="http://localhost:4000/v1",
        model="gpt-5.5",
        wire_api="responses",
        api_key_env="SKILL_WORKBENCH_API_KEY",
        has_api_key=True,
    )
    runner = CodexRunner(codex_bin="codex")

    command, env = runner.build_command(
        prompt_file=tmp_path / "prompt.txt",
        workspace=tmp_path,
        provider=provider,
        api_key="secret-key",
    )

    command_text = " ".join(command)
    assert command[:2] == ["codex", "exec"]
    assert "--json" in command
    assert "--skip-git-repo-check" in command
    assert "--ask-for-approval" not in command
    assert "--dangerously-bypass-approvals-and-sandbox" not in command
    assert "-C" in command
    assert str(tmp_path) in command
    assert "model=\"gpt-5.5\"" in command_text
    assert "model_provider=\"skill_workbench\"" in command_text
    assert "model_providers.skill_workbench.base_url=\"http://localhost:4000/v1\"" in command_text
    assert env["SKILL_WORKBENCH_API_KEY"] == "secret-key"
    assert os.environ.get("SKILL_WORKBENCH_API_KEY") is None


def test_runner_parses_jsonl_events():
    line = json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "done"}})
    event = CodexRunner.parse_event(line)

    assert event["type"] == "item.completed"
    assert event["message"] == "done"


def test_runner_cancels_silent_process_without_waiting_for_more_output(tmp_path):
    fake_codex = tmp_path / "fake_codex.py"
    fake_codex.write_text(
        "\n".join(
            [
                "import json, sys, time",
                "sys.stdin.read()",
                "print(json.dumps({'type': 'started', 'message': 'running'}), flush=True)",
                "time.sleep(30)",
            ]
        ),
        encoding="utf-8",
    )
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("run", encoding="utf-8")
    runner = CodexRunner(codex_bin=sys.executable)
    runner.codex_command = [sys.executable, str(fake_codex)]
    cancel_requested = False

    def on_event(_event):
        nonlocal cancel_requested
        cancel_requested = True

    started = time.monotonic()
    result = runner.run(
        prompt_file=prompt_file,
        workspace=tmp_path,
        provider=None,
        api_key=None,
        on_event=on_event,
        should_cancel=lambda: cancel_requested,
    )
    elapsed = time.monotonic() - started

    # 取消生效就应远早于子进程的 30s 睡眠结束；放宽到 15s 以容忍
    # CI 共享 runner 上较慢的子进程冷启动与线程调度，同时仍能抓住
    # “取消未生效、傻等满睡眠”的回归。
    assert elapsed < 15
    assert result.code != 0
