from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from .models import ProviderCreate, ProviderProfile, ProviderValidate, ProviderValidationResult
from .runner import redact_secrets


@dataclass(frozen=True)
class ProviderShape:
    name: str
    provider: str
    base_url: str
    model: str
    wire_api: str
    api_key: str | None


def shape_from_create(payload: ProviderCreate) -> ProviderShape:
    return ProviderShape(
        name=payload.name.strip(),
        provider=payload.provider.strip() or "proxy",
        base_url=payload.base_url.strip(),
        model=payload.model.strip(),
        wire_api=payload.wire_api,
        api_key=payload.api_key.strip(),
    )


def shape_from_validate(payload: ProviderValidate) -> ProviderShape:
    return ProviderShape(
        name=payload.name.strip(),
        provider=payload.provider.strip() or "proxy",
        base_url=payload.base_url.strip(),
        model=payload.model.strip(),
        wire_api=payload.wire_api,
        api_key=payload.api_key.strip() if payload.api_key else None,
    )


def shape_from_profile(profile: ProviderProfile, api_key: str | None) -> ProviderShape:
    return ProviderShape(
        name=profile.name.strip(),
        provider=profile.provider.strip() or "proxy",
        base_url=profile.base_url.strip(),
        model=profile.model.strip(),
        wire_api=profile.wire_api,
        api_key=api_key.strip() if api_key else None,
    )


def validate_provider_shape(shape: ProviderShape, *, require_api_key: bool) -> list[str]:
    errors: list[str] = []
    if not shape.name:
        errors.append("配置名称不能为空，请给这个配置起一个好认的名字。")
    if not shape.model:
        errors.append("模型名称不能为空。")
    if not shape.base_url:
        errors.append("Base URL 不能为空。")
    elif _looks_like_secret(shape.base_url):
        errors.append("Base URL 里看起来填的是 API Key，请把 sk- 开头的内容放到 API Key。")
    else:
        parsed = urllib.parse.urlparse(shape.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append("Base URL 必须是 http 或 https 开头的完整地址，例如 https://api.example.com/v1。")
    if require_api_key and not shape.api_key:
        errors.append("API Key 不能为空。")
    if shape.api_key and _looks_like_url(shape.api_key):
        errors.append("API Key 里看起来填的是 URL，请把接口地址放到 Base URL。")
    return errors


def first_shape_error(shape: ProviderShape, *, require_api_key: bool) -> str | None:
    errors = validate_provider_shape(shape, require_api_key=require_api_key)
    return "；".join(errors) if errors else None


def validate_custom_provider_connection(shape: ProviderShape) -> ProviderValidationResult:
    shape_error = first_shape_error(shape, require_api_key=True)
    if shape_error:
        return ProviderValidationResult(ok=False, message=shape_error)

    request = urllib.request.Request(_models_url(shape.base_url), method="GET")
    request.add_header("Authorization", f"Bearer {shape.api_key}")
    request.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            body = response.read(512 * 1024).decode("utf-8", errors="replace")
            if response.status < 200 or response.status >= 300:
                return ProviderValidationResult(ok=False, message=f"连接失败：HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        detail = exc.read(2048).decode("utf-8", errors="replace")
        message = f"连接失败：HTTP {exc.code}"
        if detail:
            message = f"{message}，{_compact_detail(detail)}"
        return ProviderValidationResult(ok=False, message=redact_secrets(message, [shape.api_key or ""]))
    except urllib.error.URLError as exc:
        return ProviderValidationResult(ok=False, message=f"连接失败：{redact_secrets(str(exc.reason), [shape.api_key or ''])}")
    except TimeoutError:
        return ProviderValidationResult(ok=False, message="连接超时，请检查 Base URL 或网络代理。")
    except Exception as exc:
        return ProviderValidationResult(ok=False, message=f"连接失败：{redact_secrets(str(exc), [shape.api_key or ''])}")

    model_status = _model_status(body, shape.model)
    if model_status == "found":
        return ProviderValidationResult(ok=True, message=f"连接成功，并在 /models 中找到模型 {shape.model}。")
    if model_status == "missing":
        return ProviderValidationResult(ok=True, message=f"连接成功，但 /models 未列出 {shape.model}，请确认模型名可用。")
    return ProviderValidationResult(ok=True, message="连接成功，但返回的模型列表格式无法识别。")


def _models_url(base_url: str) -> str:
    return urllib.parse.urljoin(base_url.rstrip("/") + "/", "models")


def _looks_like_secret(value: str) -> bool:
    stripped = value.strip()
    return stripped.startswith(("sk-", "sk_", "sk-proj-"))


def _looks_like_url(value: str) -> bool:
    parsed = urllib.parse.urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _compact_detail(detail: str) -> str:
    try:
        data = json.loads(detail)
    except json.JSONDecodeError:
        return detail.strip()[:240]
    if isinstance(data, dict):
        error = data.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if isinstance(message, str):
                return message[:240]
        message = data.get("message")
        if isinstance(message, str):
            return message[:240]
    return detail.strip()[:240]


def _model_status(body: str, model: str) -> str:
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return "unknown"
    rows = data.get("data") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        return "unknown"
    ids = {item.get("id") for item in rows if isinstance(item, dict)}
    return "found" if model in ids else "missing"
