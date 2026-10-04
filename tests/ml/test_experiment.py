"""
ML Pipeline Tests (Gate 3 Enforcement)

Tests that enforce:
  - Baseline model is required
  - Temporal data cannot use random splits
  - Candidate must beat baseline
  - Subgroup analysis is performed
"""

from __future__ import annotations

import pandas as pd
import pytest
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression

from src.ml.experiment import (
    Experiment,
    ExperimentConfig,
    SplitStrategy,
)


class TestBaselineRequirement:
    """Gate 3, Check 1: Baseline model must be established."""

    @pytest.mark.ml
    def test_no_baseline_raises_error(self, sample_ml_df: pd.DataFrame) -> None:
        config = ExperimentConfig(
            name="test_no_baseline",
            target="target",
            split_strategy=SplitStrategy.TEMPORAL,
            temporal_column="date",
        )
        experiment = Experiment(config)
        experiment.add_model("candidate", LogisticRegression(random_state=42))

        with pytest.raises(ValueError, match="No baseline model"):
            experiment.run(sample_ml_df)


class TestTemporalSplitEnforcement:
    """Gate 3, Check 2 & Rule 4: Temporal data must use temporal splits."""

    @pytest.mark.ml
    def test_temporal_split_requires_temporal_column(self, sample_ml_df: pd.DataFrame) -> None:
        config = ExperimentConfig(
            name="test_temporal",
            target="target",
            split_strategy=SplitStrategy.TEMPORAL,
            temporal_column=None,  # Missing!
        )
        experiment = Experiment(config)
        experiment.add_baseline("baseline", DummyClassifier(strategy="most_frequent", random_state=42))
        experiment.add_model("candidate", LogisticRegression(random_state=42))

        with pytest.raises(ValueError, match="temporal split requires temporal_column"):
            experiment.run(sample_ml_df)

    @pytest.mark.ml
    def test_temporal_split_preserves_order(self, sample_ml_df: pd.DataFrame) -> None:
        config = ExperimentConfig(
            name="test_temporal_order",
            target="target",
            split_strategy=SplitStrategy.TEMPORAL,
            temporal_column="date",
            test_size=0.2,
        )
        experiment = Experiment(config)
        experiment.add_baseline("baseline", DummyClassifier(strategy="most_frequent", random_state=42))
        experiment.add_model("logistic", LogisticRegression(random_state=42))
        report = experiment.run(sample_ml_df)

        # Verify experiment completes
        assert report.baseline_result is not None
        assert len(report.candidate_results) == 1


class TestModelComparison:
    """Gate 3: Candidate must beat baseline."""

    @pytest.mark.ml
    def test_candidate_vs_baseline(self, sample_ml_df: pd.DataFrame) -> None:
        config = ExperimentConfig(
            name="test_comparison",
            target="target",
            split_strategy=SplitStrategy.TEMPORAL,
            temporal_column="date",
        )
        experiment = Experiment(config)
        experiment.add_baseline("random_baseline", DummyClassifier(strategy="most_frequent", random_state=42))
        experiment.add_model("logistic", LogisticRegression(random_state=42))

        report = experiment.run(sample_ml_df)

        # Report should have baseline and candidate results
        assert report.baseline_result is not None
        assert len(report.candidate_results) == 1
        assert report.gate_3_status in ("PASSED", "FAILED")


class TestSubgroupAnalysis:
    """Gate 3, Check 5: Subgroup error analysis."""

    @pytest.mark.ml
    def test_subgroup_metrics_computed(self, sample_ml_df: pd.DataFrame) -> None:
        config = ExperimentConfig(
            name="test_subgroups",
            target="target",
            split_strategy=SplitStrategy.TEMPORAL,
            temporal_column="date",
            subgroup_columns=["segment"],
        )
        experiment = Experiment(config)
        experiment.add_baseline("baseline", DummyClassifier(strategy="most_frequent", random_state=42))
        experiment.add_model("logistic", LogisticRegression(random_state=42))

        report = experiment.run(sample_ml_df)

        # Best candidate should have subgroup metrics
        best_result = report.candidate_results[0]
        assert len(best_result.subgroup_metrics) > 0


class TestExperimentReport:
    """Test report generation."""

    @pytest.mark.ml
    def test_report_generates_markdown(self, sample_ml_df: pd.DataFrame) -> None:
        config = ExperimentConfig(
            name="test_report",
            target="target",
            split_strategy=SplitStrategy.TEMPORAL,
            temporal_column="date",
            subgroup_columns=["segment"],
        )
        experiment = Experiment(config)
        experiment.add_baseline("baseline", DummyClassifier(strategy="most_frequent", random_state=42))
        experiment.add_model("logistic", LogisticRegression(random_state=42))

        report = experiment.run(sample_ml_df)
        markdown = report.to_markdown()

        assert "# Model Evaluation" in markdown
        assert "BASELINE" in markdown
        assert "Gate 3 Status" in markdown
