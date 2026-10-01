"""
ADI-OS Data Profiler

Automated data profiling engine that generates comprehensive
DATA_QUALITY_REPORT.md artifacts per ARTIFACT_PROTOCOL.md standards.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ColumnProfile:
    """Statistical profile for a single column."""

    name: str
    dtype: str
    count: int
    null_count: int
    null_pct: float
    distinct_count: int
    distinct_pct: float

    # Numeric stats (None for non-numeric)
    mean: float | None = None
    std: float | None = None
    min_val: float | None = None
    q25: float | None = None
    median: float | None = None
    q75: float | None = None
    max_val: float | None = None
    iqr: float | None = None
    skewness: float | None = None
    kurtosis: float | None = None

    # Categorical stats
    top_values: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class DataProfile:
    """Complete dataset profile."""

    dataset_name: str
    row_count: int
    column_count: int
    duplicate_rows: int
    total_missing_pct: float
    memory_usage_mb: float
    columns: list[ColumnProfile]

    # Quality dimensions (0.0 to 1.0)
    completeness: float = 0.0
    validity: float = 0.0
    uniqueness: float = 0.0

    def to_markdown(self) -> str:
        """Generate markdown report."""
        lines = [
            "---",
            f'artifact_type: "DATA_QUALITY_REPORT"',
            f'title: "Data Profile: {self.dataset_name}"',
            "---",
            "",
            f"# Data Profile: {self.dataset_name}",
            "",
            "## Summary",
            "",
            "| Metric | Value |",
            "|---|---|",
            f"| Total Rows | {self.row_count:,} |",
            f"| Total Columns | {self.column_count} |",
            f"| Duplicate Rows | {self.duplicate_rows:,} |",
            f"| Missing Cells | {self.total_missing_pct:.2%} |",
            f"| Memory Usage | {self.memory_usage_mb:.2f} MB |",
            "",
            "## Quality Scorecard",
            "",
            "| Dimension | Score |",
            "|---|---|",
            f"| Completeness | {self.completeness:.2%} |",
            f"| Validity | {self.validity:.2%} |",
            f"| Uniqueness | {self.uniqueness:.2%} |",
            "",
            "## Column Profiles",
            "",
            "| Column | Type | Non-Null | Null% | Distinct | Mean | Std | Min | Max |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for col in self.columns:
            mean_str = f"{col.mean:.2f}" if col.mean is not None else "—"
            std_str = f"{col.std:.2f}" if col.std is not None else "—"
            min_str = f"{col.min_val:.2f}" if col.min_val is not None else "—"
            max_str = f"{col.max_val:.2f}" if col.max_val is not None else "—"
            lines.append(
                f"| {col.name} | {col.dtype} | {col.count - col.null_count:,} | "
                f"{col.null_pct:.1%} | {col.distinct_count:,} | "
                f"{mean_str} | {std_str} | {min_str} | {max_str} |"
            )

        return "\n".join(lines)


class DataProfiler:
    """
    Automated data profiling engine.

    Usage:
        profiler = DataProfiler()
        profile = profiler.profile(df, "customer_transactions")
        markdown = profile.to_markdown()
    """

    def profile(self, df: pd.DataFrame, dataset_name: str = "dataset") -> DataProfile:
        """Generate a comprehensive profile for the given DataFrame."""
        logger.info("Profiling dataset", dataset=dataset_name, rows=len(df), cols=len(df.columns))

        column_profiles = [self._profile_column(df, col) for col in df.columns]

        total_cells = len(df) * len(df.columns)
        total_missing = int(df.isnull().sum().sum())
        completeness = 1.0 - (total_missing / total_cells) if total_cells > 0 else 0.0

        profile = DataProfile(
            dataset_name=dataset_name,
            row_count=len(df),
            column_count=len(df.columns),
            duplicate_rows=int(df.duplicated().sum()),
            total_missing_pct=total_missing / total_cells if total_cells > 0 else 0.0,
            memory_usage_mb=df.memory_usage(deep=True).sum() / (1024 * 1024),
            columns=column_profiles,
            completeness=completeness,
            uniqueness=1.0 - (int(df.duplicated().sum()) / len(df)) if len(df) > 0 else 0.0,
            validity=1.0,  # Requires contract for accurate assessment
        )

        logger.info(
            "Profiling complete",
            dataset=dataset_name,
            completeness=f"{completeness:.2%}",
            duplicate_rows=profile.duplicate_rows,
        )

        return profile

    def _profile_column(self, df: pd.DataFrame, col: str) -> ColumnProfile:
        """Profile a single column."""
        series = df[col]
        count = len(series)
        null_count = int(series.isnull().sum())
        distinct_count = int(series.nunique())

        profile = ColumnProfile(
            name=col,
            dtype=str(series.dtype),
            count=count,
            null_count=null_count,
            null_pct=null_count / count if count > 0 else 0.0,
            distinct_count=distinct_count,
            distinct_pct=distinct_count / count if count > 0 else 0.0,
        )

        # Numeric statistics
        if pd.api.types.is_numeric_dtype(series):
            desc = series.describe()
            profile.mean = float(desc.get("mean", 0))
            profile.std = float(desc.get("std", 0))
            profile.min_val = float(desc.get("min", 0))
            profile.q25 = float(desc.get("25%", 0))
            profile.median = float(desc.get("50%", 0))
            profile.q75 = float(desc.get("75%", 0))
            profile.max_val = float(desc.get("max", 0))
            profile.iqr = (profile.q75 or 0) - (profile.q25 or 0)
            try:
                profile.skewness = float(series.skew())
                profile.kurtosis = float(series.kurtosis())
            except Exception:
                pass

        # Top values for categorical
        if pd.api.types.is_object_dtype(series) or pd.api.types.is_categorical_dtype(series):
            top = series.value_counts().head(10)
            profile.top_values = [
                {"value": str(val), "count": int(cnt), "pct": f"{cnt / count:.2%}"}
                for val, cnt in top.items()
            ]

        return profile
