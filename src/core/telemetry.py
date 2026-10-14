"""Optional stage and model telemetry.

The recorder is deliberately fail-open: a missing Phoenix SDK, unavailable
collector, or unwritable telemetry file never interrupts feature planning.
When enabled it writes a local JSONL evidence stream and, when
``arize-phoenix-otel`` is installed, creates matching OpenTelemetry spans for
Phoenix.
"""
from __future__ import annotations

import json
import threading
from collections.abc import Callable
from contextlib import AbstractContextManager
from contextvars import ContextVar
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from types import TracebackType
from typing import Any, Literal, Self

from config.settings import Settings

_ACTIVE_STAGE: ContextVar[_StageContext | None] = ContextVar("dj_active_stage", default=None)


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds")


def _number(value: Any) -> int | float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _usage_dict(response: Any) -> dict[str, int | float]:
    """Extract provider-neutral usage and cost metadata from a LiteLLM response."""
    usage = getattr(response, "usage", None)
    if usage is None and isinstance(response, dict):
        usage = response.get("usage")

    def value(name: str) -> int | float | None:
        raw = usage.get(name) if isinstance(usage, dict) else getattr(usage, name, None)
        parsed = _number(raw)
        return parsed

    output: dict[str, int | float] = {}
    names = {
        "input_tokens": ("prompt_tokens", "input_tokens"),
        "output_tokens": ("completion_tokens", "output_tokens"),
        "total_tokens": ("total_tokens",),
    }
    for target, candidates in names.items():
        for candidate in candidates:
            parsed = value(candidate)
            if parsed is not None:
                output[target] = parsed
                break

    hidden = getattr(response, "_hidden_params", None)
    if isinstance(hidden, dict):
        cost = _number(hidden.get("response_cost"))
        if cost is not None:
            output["cost_usd"] = cost
    if isinstance(response, dict):
        cost = _number(response.get("response_cost"))
        if cost is not None:
            output["cost_usd"] = cost
    return output


class _StageContext(AbstractContextManager["_StageContext"]):
    def __init__(
        self,
        recorder: TelemetryRecorder,
        stage: str,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        self.recorder = recorder
        self.stage = stage
        self.attributes = dict(attributes or {})
        self.started_at = ""
        self._started = 0.0
        self._token: Any = None
        self._attempts: list[dict[str, Any]] = []
        self._status = "ok"
        self._error: dict[str, str] = {}
        self._span: Any = None

    def __enter__(self) -> Self:
        self.started_at = _now()
        self._started = perf_counter()
        self._token = _ACTIVE_STAGE.set(self)
        self._span = self.recorder._start_span(self.stage)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        _traceback: TracebackType | None,
    ) -> Literal[False]:
        if exc is not None:
            self.mark("error", error_type=type(exc).__name__)
        finished_at = _now()
        duration_ms = round((perf_counter() - self._started) * 1000, 3)
        self.recorder._finish_span(self._span, self._status, self.attributes, duration_ms, self._error)
        if self._token is not None:
            _ACTIVE_STAGE.reset(self._token)
        self.recorder._emit_stage(
            self,
            finished_at=finished_at,
            duration_ms=duration_ms,
        )
        return False

    def mark(self, status: str, **attributes: Any) -> None:
        self._status = status
        self.attributes.update(attributes)
        if status == "error":
            self._error.update({key: str(value) for key, value in attributes.items() if value is not None})

    def add_llm_attempt(
        self,
        model: str,
        status: str,
        usage: dict[str, int | float] | None = None,
        error_type: str = "",
    ) -> None:
        attempt: dict[str, Any] = {"model": model, "status": status}
        if usage:
            attempt["usage"] = usage
        if error_type:
            attempt["error_type"] = error_type
        self._attempts.append(attempt)
        if self._span is not None:
            try:
                self._span.add_event("llm.attempt", {"model": model, "status": status})
            except (AttributeError, RuntimeError, TypeError, ValueError):  # pragma: no cover
                return


class TelemetryRecorder:
    """Fail-open JSONL recorder with an optional Phoenix OpenTelemetry bridge."""

    def __init__(
        self,
        settings: Settings,
        run_id: str,
        mode: str,
        state_provider: Callable[[], dict[str, Any]] | None = None,
    ) -> None:
        self.enabled = settings.phoenix_enabled
        self.run_id = run_id
        self.mode = mode
        self.endpoint = settings.phoenix_endpoint
        self.project_name = settings.phoenix_project_name
        self.telemetry_path = Path(settings.telemetry_path)
        self.state_provider = state_provider
        self._file_lock = threading.Lock()
        self._tracer: Any = None
        self.phoenix_error = ""
        if self.enabled:
            self._configure_phoenix()

    def _configure_phoenix(self) -> None:
        """Load Phoenix lazily so the default install has no observability dependency."""
        try:
            from phoenix.otel import register

            provider = register(
                project_name=self.project_name,
                endpoint=self.endpoint,
                auto_instrument=False,
                batch=False,
            )
            self._tracer = provider.get_tracer("dev-journey-agent")
        except (ImportError, AttributeError, RuntimeError, TypeError, ValueError) as exc:
            self.phoenix_error = f"{type(exc).__name__}: {exc}"

    def stage(
        self, stage: str, attributes: dict[str, Any] | None = None
    ) -> _StageContext:
        return _StageContext(self, stage, attributes)

    def mark_current(self, status: str, **attributes: Any) -> None:
        current = _ACTIVE_STAGE.get()
        if current is not None and current.recorder is self:
            current.mark(status, **attributes)

    def record_event(self, event: str, **attributes: Any) -> None:
        if not self.enabled:
            return
        payload = {
            "event": event,
            "run_id": self.run_id,
            "mode": self.mode,
            "timestamp": _now(),
            "phoenix_endpoint": self.endpoint,
            "phoenix_project": self.project_name,
            **attributes,
        }
        self._write(payload)

    def record_llm_attempt(
        self,
        model: str,
        status: str,
        response: Any = None,
        error: BaseException | None = None,
    ) -> None:
        current = _ACTIVE_STAGE.get()
        if current is None or current.recorder is not self:
            return
        current.add_llm_attempt(
            model,
            status,
            usage=_usage_dict(response) if response is not None else None,
            error_type=type(error).__name__ if error is not None else "",
        )

    def _start_span(self, stage: str) -> Any:
        if self._tracer is None:
            return None
        try:
            span = self._tracer.start_span(stage)
            span.set_attribute("run_id", self.run_id)
            span.set_attribute("mode", self.mode)
            return span
        except (AttributeError, RuntimeError, TypeError, ValueError):  # pragma: no cover
            return None

    @staticmethod
    def _finish_span(
        span: Any,
        status: str,
        attributes: dict[str, Any],
        duration_ms: float,
        error: dict[str, str],
    ) -> None:
        if span is None:
            return
        try:
            for key, value in {**attributes, "duration_ms": duration_ms}.items():
                if isinstance(value, (str, int, float, bool)):
                    span.set_attribute(key, value)
            if status == "error":
                span.record_exception(RuntimeError(error.get("error_message", "stage failed")))
            span.end()
        except (AttributeError, RuntimeError, TypeError, ValueError):  # pragma: no cover
            return

    def _emit_stage(self, context: _StageContext, finished_at: str, duration_ms: float) -> None:
        if not self.enabled:
            return
        usage: dict[str, int | float] = {}
        for attempt in context._attempts:
            for key, value in (attempt.get("usage") or {}).items():
                usage[key] = usage.get(key, 0) + value
        models = [str(attempt["model"]) for attempt in context._attempts]
        attributes = dict(context.attributes)
        attributes.update(
            {
                "models": models,
                "final_model": next(
                    (str(attempt["model"]) for attempt in reversed(context._attempts) if attempt["status"] == "ok"),
                    "",
                ),
                "fallback_attempts": max(0, len(context._attempts) - 1),
                "llm_attempts": context._attempts,
                "usage": usage,
            }
        )
        if self.phoenix_error:
            attributes["phoenix_sdk_error"] = self.phoenix_error
        state = self.state_provider() if self.state_provider is not None else {}
        payload = {
            "event": "stage",
            "run_id": self.run_id,
            "mode": self.mode,
            "stage": context.stage,
            "status": context._status,
            "started_at": context.started_at,
            "finished_at": finished_at,
            "duration_ms": duration_ms,
            "phoenix_endpoint": self.endpoint,
            "phoenix_project": self.project_name,
            "traceability": self._traceability(state),
            "block_reasons": list(state.get("block_reasons", []) or []),
            "attributes": attributes,
        }
        self._write(payload)

    @staticmethod
    def _traceability(state: dict[str, Any]) -> dict[str, list[str]]:
        if not state:
            return {}
        from core.checkpoints import traceability_snapshot

        return traceability_snapshot(state)

    def _write(self, payload: dict[str, Any]) -> None:
        try:
            self.telemetry_path.parent.mkdir(parents=True, exist_ok=True)
            line = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str) + "\n"
            with self._file_lock, self.telemetry_path.open("a", encoding="utf-8") as handle:
                handle.write(line)
        except OSError:
            # Telemetry is diagnostic evidence and must never make a run fail.
            return


def active_recorder() -> TelemetryRecorder | None:
    current = _ACTIVE_STAGE.get()
    return current.recorder if current is not None else None
