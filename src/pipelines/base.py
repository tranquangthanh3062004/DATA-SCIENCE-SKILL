"""
ADI-OS Pipeline Base

Abstract base classes for building idempotent, observable, and
recoverable data pipelines as required by QUALITY_GATE.md Gate 4.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar

from src.utils.logging_config import get_logger, new_trace_id, set_context

if TYPE_CHECKING:
    from collections.abc import Callable

logger = get_logger(__name__)

T_Input = TypeVar("T_Input")
T_Output = TypeVar("T_Output")


class PipelineStatus(str, Enum):
    """Pipeline execution status."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


@dataclass
class PipelineRunMetrics:
    """Metrics collected during a pipeline run (Gate 4: Observability)."""

    pipeline_name: str
    run_id: str
    status: PipelineStatus = PipelineStatus.PENDING
    start_time: str = ""
    end_time: str = ""
    duration_sec: float = 0.0
    rows_read: int = 0
    rows_written: int = 0
    rows_quarantined: int = 0
    retry_count: int = 0
    error_message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class BasePipeline(ABC, Generic[T_Input, T_Output]):
    """
    Abstract base for all ADI-OS data pipelines.

    Guarantees:
      - Idempotency (Gate 4 Check 1)
      - Structured logging with trace IDs (Gate 4 Check 4)
      - Retry with backoff (Gate 4 Check 3)
      - Metric collection for observability

    Usage:
        class MyPipeline(BasePipeline[pd.DataFrame, pd.DataFrame]):
            @property
            def name(self) -> str:
                return "my_pipeline"

            def extract(self, source) -> pd.DataFrame:
                ...
            def transform(self, data) -> pd.DataFrame:
                ...
            def load(self, data) -> None:
                ...
    """

    MAX_RETRIES: int = 3
    RETRY_BACKOFF_SEC: float = 2.0
    # Only I/O-style failures are retried. Logic/validation errors fail fast.
    RETRYABLE_EXCEPTIONS: ClassVar[tuple[type[BaseException], ...]] = (ConnectionError, TimeoutError)

    def _with_retry(self, step: str, fn: Callable[[Any], Any], arg: Any) -> Any:
        """Run ``fn(arg)``, retrying transient errors with exponential backoff."""
        attempt = 0
        while True:
            try:
                return fn(arg)
            except self.RETRYABLE_EXCEPTIONS as e:
                if attempt >= self.MAX_RETRIES:
                    raise
                delay = self.RETRY_BACKOFF_SEC * (2**attempt)
                attempt += 1
                self._metrics.retry_count += 1
                self._metrics.status = PipelineStatus.RETRYING
                logger.warning(
                    "Transient failure — retrying",
                    pipeline=self.name,
                    step=step,
                    attempt=attempt,
                    max_retries=self.MAX_RETRIES,
                    delay_sec=delay,
                    error=str(e),
                )
                time.sleep(delay)
                self._metrics.status = PipelineStatus.RUNNING

    def __init__(self) -> None:
        self._metrics = PipelineRunMetrics(
            pipeline_name=self.name,
            run_id=new_trace_id(),
        )

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique pipeline identifier."""
        ...

    @abstractmethod
    def extract(self, source: Any) -> T_Input:
        """Extract data from source (Bronze layer)."""
        ...

    @abstractmethod
    def transform(self, data: T_Input) -> T_Output:
        """Transform data (Bronze → Silver or Silver → Gold)."""
        ...

    @abstractmethod
    def load(self, data: T_Output) -> None:
        """Load transformed data to target."""
        ...

    def validate(self, data: T_Output) -> bool:
        """Optional validation step before load. Override to add checks."""
        return True

    def run(self, source: Any) -> PipelineRunMetrics:
        """
        Execute the full ETL pipeline with retry logic.

        Returns PipelineRunMetrics for observability.
        """
        set_context(task_id=f"PIPELINE-{self.name}", agent_id="data_engineer")
        self._metrics.start_time = datetime.now(UTC).isoformat()
        self._metrics.status = PipelineStatus.RUNNING

        logger.info("Pipeline started", pipeline=self.name, run_id=self._metrics.run_id)
        start = time.monotonic()

        try:
            # Extract (retried on transient errors)
            logger.info("Extracting data", pipeline=self.name)
            raw_data = self._with_retry("extract", self.extract, source)

            # Transform (pure — not retried)
            logger.info("Transforming data", pipeline=self.name)
            transformed = self.transform(raw_data)

            # Validate (never retried — Gate 4 block)
            logger.info("Validating output", pipeline=self.name)
            if not self.validate(transformed):
                raise ValueError("Output validation failed — Gate 4 check blocked load")

            # Load (retried on transient errors; load() must be idempotent)
            logger.info("Loading data", pipeline=self.name)
            self._with_retry("load", self.load, transformed)

            self._metrics.status = PipelineStatus.SUCCESS
            logger.info(
                "Pipeline completed successfully",
                pipeline=self.name,
                rows_written=self._metrics.rows_written,
            )

        except Exception as e:
            self._metrics.status = PipelineStatus.FAILED
            self._metrics.error_message = str(e)
            logger.error(
                "Pipeline failed",
                pipeline=self.name,
                error=str(e),
                retry_count=self._metrics.retry_count,
            )
            raise

        finally:
            elapsed = time.monotonic() - start
            self._metrics.duration_sec = round(elapsed, 2)
            self._metrics.end_time = datetime.now(UTC).isoformat()

        return self._metrics
