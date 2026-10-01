"""
ADI-OS Structured Logging

Enterprise-grade structured logging using structlog.
Every log entry includes: timestamp, level, agent_id, task_id, and trace_id
as required by QUALITY_GATE.md Gate 4 (Observability).
"""

from __future__ import annotations

import uuid
from contextvars import ContextVar
from typing import Any

import structlog

from src.utils.config import get_settings

# ── Context Variables for Distributed Tracing ──
_trace_id: ContextVar[str] = ContextVar("trace_id", default="")
_task_id: ContextVar[str] = ContextVar("task_id", default="")
_agent_id: ContextVar[str] = ContextVar("agent_id", default="")


def set_context(
    *,
    trace_id: str | None = None,
    task_id: str | None = None,
    agent_id: str | None = None,
) -> None:
    """Set logging context for the current execution scope."""
    if trace_id is not None:
        _trace_id.set(trace_id)
    if task_id is not None:
        _task_id.set(task_id)
    if agent_id is not None:
        _agent_id.set(agent_id)


def new_trace_id() -> str:
    """Generate a new trace ID and set it in context."""
    tid = str(uuid.uuid4())[:12]
    _trace_id.set(tid)
    return tid


def _inject_context(
    logger: Any, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Structlog processor: inject trace/task/agent context into every log."""
    trace = _trace_id.get("")
    task = _task_id.get("")
    agent = _agent_id.get("")

    if trace:
        event_dict["trace_id"] = trace
    if task:
        event_dict["task_id"] = task
    if agent:
        event_dict["agent_id"] = agent

    return event_dict


def _add_severity_emoji(
    logger: Any, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add visual severity indicators for console output."""
    emojis = {
        "debug": "🔍",
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "critical": "🔥",
    }
    event_dict["severity"] = emojis.get(method_name, "")
    return event_dict


def configure_logging() -> None:
    """
    Configure structured logging for the entire application.

    Call once at application startup.
    """
    settings = get_settings()

    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        _inject_context,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.is_production:
        # JSON output for production log aggregation
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Pretty console output for development
        processors.append(_add_severity_emoji)
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.

    Usage:
        from src.utils.logging_config import get_logger
        logger = get_logger(__name__)
        logger.info("Pipeline started", rows=1000, source="api")
    """
    return structlog.get_logger(name)
