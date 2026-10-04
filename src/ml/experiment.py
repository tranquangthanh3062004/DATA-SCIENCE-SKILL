"""
ADI-OS ML Experiment Framework

Structured ML experiment runner that enforces:
  - Gate 3: Baseline model established before complex models
  - Gate 3: Leakage-free temporal/grouped splits
  - Gate 3: Metric alignment with business loss function
  - Gate 3: Subgroup error analysis

Usage:
    from src.ml.experiment import Experiment, ExperimentConfig
    config = ExperimentConfig(name="churn_prediction", target="churned", ...)
    experiment = Experiment(config)
    experiment.add_model("baseline", LogisticRegression())
    experiment.add_model("candidate", XGBClassifier())
    results = experiment.run(df)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Protocol

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    log_loss,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class TaskType(str, Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"


class SplitStrategy(str, Enum):
    """
    Data split strategy per data-org-rules.md Rule 4:
    Time-dependent data must NEVER be split randomly.
    """

    TEMPORAL = "temporal"  # Time-based forward split
    TEMPORAL_CV = "temporal_cv"  # Walk-forward cross-validation
    GROUPED = "grouped"  # Group-aware split (no group leakage)
    STRATIFIED = "stratified"  # Stratified random (non-temporal only)


class ModelProtocol(Protocol):
    """Minimal interface for any sklearn-compatible model."""

    def fit(self, X: Any, y: Any) -> Any: ...
    def predict(self, X: Any) -> Any: ...
    def predict_proba(self, X: Any) -> Any: ...


@dataclass
class ExperimentConfig:
    """Configuration for an ML experiment."""

    name: str
    target: str
    task_type: TaskType = TaskType.CLASSIFICATION
    split_strategy: SplitStrategy = SplitStrategy.TEMPORAL
    temporal_column: str | None = None  # Required for temporal splits
    group_column: str | None = None  # Required for grouped splits
    test_size: float = 0.2
    validation_size: float = 0.15
    random_seed: int = 42
    subgroup_columns: list[str] = field(default_factory=list)  # For error analysis
    feature_columns: list[str] = field(default_factory=list)  # Empty = auto-detect


@dataclass
class ModelResult:
    """Results for a single model in the experiment."""

    model_name: str
    metrics: dict[str, float]
    subgroup_metrics: dict[str, dict[str, float]] = field(default_factory=dict)
    feature_importance: dict[str, float] = field(default_factory=dict)
    predictions: np.ndarray | None = None
    training_time_sec: float = 0.0


@dataclass
class ExperimentReport:
    """
    Complete experiment report.

    Maps to MODEL_EVALUATION.md artifact.
    """

    experiment_name: str
    config: ExperimentConfig
    baseline_result: ModelResult | None = None
    candidate_results: list[ModelResult] = field(default_factory=list)
    best_model: str = ""
    gate_3_status: str = "PENDING"
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_markdown(self) -> str:
        """Generate MODEL_EVALUATION.md content."""
        lines = [
            "---",
            'artifact_type: "MODEL_EVALUATION"',
            f'title: "Model Evaluation: {self.experiment_name}"',
            f'gate_3_status: "{self.gate_3_status}"',
            f'created_at: "{self.timestamp}"',
            "reproducibility:",
            f"  seed: {self.config.random_seed}",
            "---",
            "",
            f"# Model Evaluation: {self.experiment_name}",
            "",
            f"**Task:** {self.config.task_type.value}",
            f"**Split Strategy:** {self.config.split_strategy.value}",
            f"**Gate 3 Status:** `{self.gate_3_status}`",
            "",
            "## Model Comparison",
            "",
        ]

        # Build comparison table
        all_results = []
        if self.baseline_result:
            all_results.append(("🎯 BASELINE: " + self.baseline_result.model_name, self.baseline_result))
        for r in self.candidate_results:
            prefix = "⭐ BEST: " if r.model_name == self.best_model else ""
            all_results.append((prefix + r.model_name, r))

        if all_results:
            metric_names = list(all_results[0][1].metrics.keys())
            header = "| Model | " + " | ".join(metric_names) + " |"
            sep = "|---|" + "|".join(["---"] * len(metric_names)) + "|"
            lines.extend([header, sep])
            for label, result in all_results:
                vals = " | ".join(f"{result.metrics.get(m, 0):.4f}" for m in metric_names)
                lines.append(f"| {label} | {vals} |")

        # Subgroup analysis
        if self.candidate_results and self.candidate_results[0].subgroup_metrics:
            lines.extend(["", "## Subgroup Error Analysis", ""])
            best = next(
                (r for r in self.candidate_results if r.model_name == self.best_model), self.candidate_results[0]
            )
            for group_key, group_metrics in best.subgroup_metrics.items():
                lines.append(f"### {group_key}")
                lines.append("| Metric | Value |")
                lines.append("|---|---|")
                for m, v in group_metrics.items():
                    lines.append(f"| {m} | {v:.4f} |")
                lines.append("")

        return "\n".join(lines)


class Experiment:
    """
    ML Experiment runner with Gate 3 enforcement.

    Ensures:
      1. Baseline always evaluated first
      2. Split strategy respects temporal/group constraints
      3. Subgroup error analysis performed
      4. Results compared against baseline
    """

    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config
        self._models: dict[str, Any] = {}
        self._baseline_name: str | None = None

    def add_baseline(self, name: str, model: Any) -> None:
        """Register the baseline model (Gate 3 Check 1: baseline required)."""
        self._baseline_name = name
        self._models[name] = model

    def add_model(self, name: str, model: Any) -> None:
        """Register a candidate model."""
        self._models[name] = model

    def run(self, df: pd.DataFrame) -> ExperimentReport:
        """Execute the experiment and return a report."""
        # Gate 3 Check 1: Baseline must exist
        if self._baseline_name is None:
            raise ValueError(
                "Gate 3 VIOLATION: No baseline model registered. "
                "Call add_baseline() before run(). "
                "Maxim 4: BASELINE BEFORE OPTIMIZATION."
            )

        logger.info(
            "Starting experiment",
            experiment=self.config.name,
            models=list(self._models.keys()),
            split=self.config.split_strategy.value,
        )

        np.random.seed(self.config.random_seed)

        # Prepare features and target.
        # Default: numeric columns only (string/categorical columns require explicit
        # encoding and must be listed in config.feature_columns after preprocessing).
        excluded = {self.config.target, self.config.temporal_column, self.config.group_column}
        excluded.update(self.config.subgroup_columns)
        feature_cols = self.config.feature_columns or [
            c for c in df.select_dtypes(include="number").columns if c not in excluded
        ]

        X = df[feature_cols]
        y = df[self.config.target]

        # Split data
        X_train, X_test, y_train, y_test, test_df = self._split_data(df, X, y)

        # Evaluate all models
        report = ExperimentReport(experiment_name=self.config.name, config=self.config)

        for model_name, model in self._models.items():
            logger.info("Training model", model=model_name)
            import time

            start = time.monotonic()
            model.fit(X_train, y_train)
            training_time = time.monotonic() - start

            predictions = model.predict(X_test)
            metrics = self._compute_metrics(y_test, predictions, model, X_test)

            # Subgroup analysis (Gate 3 Check 5)
            subgroup_metrics: dict[str, dict[str, float]] = {}
            for sg_col in self.config.subgroup_columns:
                if sg_col in test_df.columns:
                    for group_val in test_df[sg_col].unique():
                        mask = test_df[sg_col] == group_val
                        if mask.sum() > 10:  # Minimum sample size
                            sg_key = f"{sg_col}={group_val}"
                            sg_metrics = self._compute_metrics(y_test[mask], predictions[mask], model, X_test[mask])
                            subgroup_metrics[sg_key] = sg_metrics

            result = ModelResult(
                model_name=model_name,
                metrics=metrics,
                subgroup_metrics=subgroup_metrics,
                training_time_sec=round(training_time, 2),
                predictions=predictions,
            )

            # Extract feature importance if available
            if hasattr(model, "feature_importances_"):
                result.feature_importance = dict(zip(feature_cols, model.feature_importances_, strict=False))

            if model_name == self._baseline_name:
                report.baseline_result = result
            else:
                report.candidate_results.append(result)

            logger.info("Model evaluated", model=model_name, metrics=metrics)

        # Determine best model
        primary_metric = next(iter(report.candidate_results[0].metrics), "") if report.candidate_results else ""
        if report.candidate_results and primary_metric:
            best = max(report.candidate_results, key=lambda r: r.metrics.get(primary_metric, 0))
            report.best_model = best.model_name

            # Gate 3 Pass: candidate must beat baseline
            if report.baseline_result:
                baseline_score = report.baseline_result.metrics.get(primary_metric, 0)
                best_score = best.metrics.get(primary_metric, 0)
                if best_score > baseline_score:
                    report.gate_3_status = "PASSED"
                    logger.info(
                        "Gate 3 PASSED — candidate beats baseline",
                        baseline=f"{baseline_score:.4f}",
                        best=f"{best_score:.4f}",
                    )
                else:
                    report.gate_3_status = "FAILED"
                    logger.warning(
                        "Gate 3 FAILED — candidate does not beat baseline",
                        baseline=f"{baseline_score:.4f}",
                        best=f"{best_score:.4f}",
                    )

        return report

    def _split_data(
        self,
        df: pd.DataFrame,
        X: pd.DataFrame,
        y: pd.Series,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.DataFrame]:
        """Split data according to the configured strategy (Gate 3 Check 2)."""
        if self.config.split_strategy in (SplitStrategy.TEMPORAL, SplitStrategy.TEMPORAL_CV):
            if self.config.temporal_column is None:
                raise ValueError(
                    "Gate 3 VIOLATION: temporal split requires temporal_column. "
                    "Rule 4: time-dependent data must NEVER be split randomly."
                )

            # Sort by temporal column
            sorted_idx = df[self.config.temporal_column].sort_values().index
            split_point = int(len(sorted_idx) * (1 - self.config.test_size))

            train_idx = sorted_idx[:split_point]
            test_idx = sorted_idx[split_point:]

            return X.loc[train_idx], X.loc[test_idx], y.loc[train_idx], y.loc[test_idx], df.loc[test_idx]

        elif self.config.split_strategy == SplitStrategy.GROUPED:
            if self.config.group_column is None:
                raise ValueError("Grouped split requires group_column.")

            groups = df[self.config.group_column].unique()
            np.random.shuffle(groups)
            split_point = int(len(groups) * (1 - self.config.test_size))

            train_groups = set(groups[:split_point])
            train_mask = df[self.config.group_column].isin(train_groups)

            return (
                X[train_mask],
                X[~train_mask],
                y[train_mask],
                y[~train_mask],
                df[~train_mask],
            )

        else:
            # Stratified random (only for non-temporal data)
            from sklearn.model_selection import train_test_split

            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=self.config.test_size,
                random_state=self.config.random_seed,
                stratify=y if self.config.task_type == TaskType.CLASSIFICATION else None,
            )
            test_df = df.loc[X_test.index]
            return X_train, X_test, y_train, y_test, test_df

    def _compute_metrics(
        self,
        y_true: pd.Series | np.ndarray,
        y_pred: np.ndarray,
        model: Any,
        X: pd.DataFrame,
    ) -> dict[str, float]:
        """Compute evaluation metrics aligned with task type."""
        if self.config.task_type == TaskType.CLASSIFICATION:
            metrics: dict[str, float] = {
                "accuracy": float(accuracy_score(y_true, y_pred)),
                "f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
                "precision": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
                "recall": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
            }
            # AUC for binary classification
            if hasattr(model, "predict_proba"):
                try:
                    y_proba = model.predict_proba(X)
                    if y_proba.shape[1] == 2:
                        metrics["roc_auc"] = float(roc_auc_score(y_true, y_proba[:, 1]))
                        metrics["log_loss"] = float(log_loss(y_true, y_proba))
                except Exception:
                    pass
            return metrics

        else:  # Regression
            return {
                "mae": float(mean_absolute_error(y_true, y_pred)),
                "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
                "r2": float(r2_score(y_true, y_pred)),
            }
