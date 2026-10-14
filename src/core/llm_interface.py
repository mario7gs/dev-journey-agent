"""Structured LLM seam with deterministic mocks and model fallback."""
from __future__ import annotations

import json
from typing import Any, TypeVar

from pydantic import BaseModel

from config.settings import Settings, load_settings
from core.telemetry import active_recorder

T = TypeVar("T", bound=BaseModel)

_MOCK_REGISTRY: dict[str, dict[str, Any]] = {}


class LLMGenerationError(RuntimeError):
    """Raised when every configured LLM model fails to produce valid output."""


def register_mock(schema_name: str, payload: dict[str, Any]) -> None:
    _MOCK_REGISTRY[schema_name] = payload


def generate_structured(
    prompt: str,
    schema: type[T],
    use_mock: bool = True,
    settings: Settings | None = None,
) -> T:
    if use_mock:
        payload = _mock_payload(prompt, schema)
        output = schema.model_validate(payload)
        recorder = active_recorder()
        if recorder is not None:
            recorder.record_llm_attempt("mock", "ok")
        return output
    recorder = active_recorder()
    if recorder is not None:
        recorder.raise_if_budget_exceeded()
    output = _real_generate(prompt, schema, settings or load_settings())
    if recorder is not None:
        recorder.raise_if_budget_exceeded()
    return output


def _mock_payload(prompt: str, schema: type[T]) -> dict[str, Any]:
    name = schema.__name__
    if name in _MOCK_REGISTRY:
        return _MOCK_REGISTRY[name]
    # Generic deterministic fallback: empty-but-valid for stub schemas
    fields = schema.model_fields
    payload: dict[str, Any] = {}
    for fname, finfo in fields.items():
        ann = str(finfo.annotation)
        if "list" in ann.lower() or "tuple" in ann.lower():
            payload[fname] = []
        elif "bool" in ann:
            payload[fname] = False
        elif "int" in ann:
            payload[fname] = 0
        elif "dict" in ann.lower():
            payload[fname] = {}
        else:
            payload[fname] = f"mock-{fname}"
    return payload


def _call_model(
    model: str,
    prompt: str,
    schema: type[T],
    settings: Settings,
) -> Any:
    """Call LiteLLM in JSON mode; kept separate for deterministic tests."""
    from litellm import completion

    kwargs: dict[str, Any] = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Return only a JSON object valid against the supplied schema. "
                    "Do not add markdown fences or commentary."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
        "timeout": settings.llm_timeout_seconds,
    }
    if settings.openai_api_key and not model.startswith("ollama/"):
        kwargs["api_key"] = settings.openai_api_key
    return completion(**kwargs)


def _content_from_response(response: Any) -> str:
    choices = getattr(response, "choices", None) or []
    if not choices:
        raise ValueError("LLM response contained no choices")
    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", None) if message is not None else None
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return json.dumps(content)
    if isinstance(content, list):
        parts = [part.get("text", "") for part in content if isinstance(part, dict)]
        return "".join(parts)
    raise ValueError("LLM response contained no textual JSON content")


def _real_generate(prompt: str, schema: type[T], settings: Settings) -> T:
    schema_hint = json.dumps(schema.model_json_schema(), ensure_ascii=False)
    enriched_prompt = (
        f"{prompt}\n\nRequired Pydantic JSON schema for {schema.__name__}:\n{schema_hint}"
    )
    models = [settings.primary_model, settings.fallback_model, settings.local_model]
    failures: list[str] = []
    for model in dict.fromkeys(m for m in models if m):
        recorder = active_recorder()
        if recorder is not None:
            recorder.raise_if_budget_exceeded()
        response = None
        try:
            response = _call_model(model, enriched_prompt, schema, settings)
            payload = json.loads(_content_from_response(response))
            output = schema.model_validate(payload)
            recorder = active_recorder()
            if recorder is not None:
                recorder.record_llm_attempt(model, "ok", response=response)
            return output
        except Exception as exc:  # noqa: BLE001 - provider SDKs expose heterogeneous errors
            recorder = active_recorder()
            if recorder is not None:
                recorder.record_llm_attempt(model, "error", response=response, error=exc)
            failures.append(f"{model}: {type(exc).__name__}: {exc}")
    details = "; ".join(failures) or "no models configured"
    raise LLMGenerationError(
        f"All configured LLM models failed for {schema.__name__}: {details}"
    )
