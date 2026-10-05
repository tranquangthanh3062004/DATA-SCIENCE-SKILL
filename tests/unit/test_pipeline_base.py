"""
Unit Tests — Base Pipeline (src.pipelines.base)

Tests:
  - Successful run: extract -> transform -> validate -> load
  - Validation failure: Gate 4 block
  - Pipeline error handling and status=FAILED
  - Runtime metrics collection (duration, run_id, timestamps)
"""

from __future__ import annotations

from typing import Any

import pytest

from src.pipelines.base import BasePipeline, PipelineStatus


class SimpleWorkingPipeline(BasePipeline[dict[str, Any], dict[str, Any]]):
    """Test implementation of BasePipeline."""

    @property
    def name(self) -> str:
        return "test_working_pipeline"

    def extract(self, source: Any) -> dict[str, Any]:
        return {"data": list(source)}

    def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        return {"data": [x * 2 for x in data["data"]]}

    def load(self, data: dict[str, Any]) -> None:
        self._metrics.rows_written = len(data["data"])


class FailingValidationPipeline(BasePipeline[list[int], list[int]]):
    """Pipeline that fails output validation."""

    @property
    def name(self) -> str:
        return "test_failing_validation_pipeline"

    def extract(self, source: Any) -> list[int]:
        return list(source)

    def transform(self, data: list[int]) -> list[int]:
        return data

    def validate(self, data: list[int]) -> bool:
        # Fails Gate 4 validation check
        return False

    def load(self, data: list[int]) -> None:
        pass


class BrokenPipeline(BasePipeline[list[int], list[int]]):
    """Pipeline that throws an unhandled exception."""

    @property
    def name(self) -> str:
        return "test_broken_pipeline"

    def extract(self, source: Any) -> list[int]:
        raise RuntimeError("Source extraction failed")

    def transform(self, data: list[int]) -> list[int]:
        return data

    def load(self, data: list[int]) -> None:
        pass


class TestBasePipeline:
    """Test execution lifecycle and guarantees of BasePipeline."""

    @pytest.mark.unit
    def test_successful_pipeline_execution(self) -> None:
        pipeline = SimpleWorkingPipeline()
        metrics = pipeline.run([1, 2, 3])

        assert metrics.status == PipelineStatus.SUCCESS
        assert metrics.pipeline_name == "test_working_pipeline"
        assert metrics.rows_written == 3
        assert metrics.duration_sec >= 0.0
        assert metrics.run_id != ""
        assert metrics.start_time != ""
        assert metrics.end_time != ""

    @pytest.mark.unit
    def test_validation_failure_blocks_load(self) -> None:
        pipeline = FailingValidationPipeline()
        with pytest.raises(ValueError, match="Output validation failed"):
            pipeline.run([1, 2, 3])

        assert pipeline._metrics.status == PipelineStatus.FAILED
        assert "Output validation failed" in pipeline._metrics.error_message

    @pytest.mark.unit
    def test_runtime_exception_tracked_in_metrics(self) -> None:
        pipeline = BrokenPipeline()
        with pytest.raises(RuntimeError, match="Source extraction failed"):
            pipeline.run([1, 2, 3])

        assert pipeline._metrics.status == PipelineStatus.FAILED
        assert "Source extraction failed" in pipeline._metrics.error_message


class FlakyPipeline(BasePipeline[list[int], list[int]]):
    """Extract fails with a transient error ``failures`` times, then succeeds."""

    RETRY_BACKOFF_SEC = 0.0

    def __init__(self, failures: int, exc: type[Exception] = ConnectionError) -> None:
        super().__init__()
        self.failures = failures
        self.exc = exc
        self.extract_calls = 0
        self.load_calls = 0

    @property
    def name(self) -> str:
        return "test_flaky_pipeline"

    def extract(self, source: Any) -> list[int]:
        self.extract_calls += 1
        if self.extract_calls <= self.failures:
            raise self.exc("transient")
        return list(source)

    def transform(self, data: list[int]) -> list[int]:
        return data

    def load(self, data: list[int]) -> None:
        self.load_calls += 1


class TestRetry:
    """Gate 4 Check 3: retry with backoff for transient failures only."""

    @pytest.mark.unit
    def test_transient_failure_is_retried_then_succeeds(self) -> None:
        pipeline = FlakyPipeline(failures=2)
        metrics = pipeline.run([1, 2])

        assert metrics.status == PipelineStatus.SUCCESS
        assert metrics.retry_count == 2
        assert pipeline.extract_calls == 3
        assert pipeline.load_calls == 1

    @pytest.mark.unit
    def test_gives_up_after_max_retries(self) -> None:
        pipeline = FlakyPipeline(failures=10)
        with pytest.raises(ConnectionError):
            pipeline.run([1])

        assert pipeline.extract_calls == pipeline.MAX_RETRIES + 1
        assert pipeline._metrics.retry_count == pipeline.MAX_RETRIES
        assert pipeline._metrics.status == PipelineStatus.FAILED

    @pytest.mark.unit
    def test_non_transient_error_is_not_retried(self) -> None:
        pipeline = FlakyPipeline(failures=1, exc=ValueError)
        with pytest.raises(ValueError):
            pipeline.run([1])

        assert pipeline.extract_calls == 1
        assert pipeline._metrics.retry_count == 0

    @pytest.mark.unit
    def test_validation_failure_is_not_retried(self) -> None:
        pipeline = FailingValidationPipeline()
        with pytest.raises(ValueError):
            pipeline.run([1])
        assert pipeline._metrics.retry_count == 0
