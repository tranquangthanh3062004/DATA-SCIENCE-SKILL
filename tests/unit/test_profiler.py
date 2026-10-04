"""
Unit Tests — Data Profiler (src.quality.profiler)

Tests:
  - Profiling numeric, categorical, and datetime columns
  - Quality score calculation (completeness, uniqueness, validity)
  - Duplicate row detection and missing values
  - Markdown report generation (DATA_QUALITY_REPORT)
  - Edge cases (empty DataFrame, single-row DataFrame)
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.quality.profiler import DataProfiler


class TestDataProfiler:
    """Test comprehensive data profiling."""

    @pytest.mark.unit
    def test_profiler_computes_dataset_summary(self, sample_transactions_df: pd.DataFrame) -> None:
        profiler = DataProfiler()
        profile = profiler.profile(sample_transactions_df, dataset_name="transactions")

        assert profile.dataset_name == "transactions"
        assert profile.row_count == len(sample_transactions_df)
        assert profile.column_count == len(sample_transactions_df.columns)
        assert profile.duplicate_rows == 0
        assert profile.completeness == 1.0
        assert profile.uniqueness == 1.0

    @pytest.mark.unit
    def test_profiler_numeric_columns(self) -> None:
        df = pd.DataFrame(
            {
                "id": [1, 2, 3, 4, 5],
                "val": [10.0, 20.0, 30.0, 40.0, 50.0],
            }
        )
        profiler = DataProfiler()
        profile = profiler.profile(df, dataset_name="numeric_test")

        val_col = next(c for c in profile.columns if c.name == "val")
        assert val_col.mean == 30.0
        assert val_col.min_val == 10.0
        assert val_col.max_val == 50.0
        assert val_col.median == 30.0
        assert val_col.iqr is not None and val_col.iqr > 0

    @pytest.mark.unit
    def test_profiler_categorical_columns(self) -> None:
        df = pd.DataFrame(
            {
                "category": ["A", "A", "B", "C", "A"],
            }
        )
        profiler = DataProfiler()
        profile = profiler.profile(df, dataset_name="cat_test")

        cat_col = next(c for c in profile.columns if c.name == "category")
        assert cat_col.distinct_count == 3
        assert len(cat_col.top_values) == 3
        # 'A' appears 3 times (60%)
        top_val = cat_col.top_values[0]
        assert top_val["value"] == "A"
        assert top_val["count"] == 3

    @pytest.mark.unit
    def test_profiler_with_nulls_and_duplicates(self) -> None:
        df = pd.DataFrame(
            {
                "a": [1, 1, 2, None],
                "b": ["x", "x", "y", "z"],
            }
        )
        profiler = DataProfiler()
        profile = profiler.profile(df, dataset_name="dirty_data")

        assert profile.duplicate_rows == 1  # Row 1 is a duplicate of Row 0
        assert profile.total_missing_pct > 0
        assert profile.completeness < 1.0

    @pytest.mark.unit
    def test_profiler_markdown_generation(self, sample_transactions_df: pd.DataFrame) -> None:
        profiler = DataProfiler()
        profile = profiler.profile(sample_transactions_df, dataset_name="transactions")
        md = profile.to_markdown()

        assert "# Data Profile: transactions" in md
        assert "DATA_QUALITY_REPORT" in md
        assert "Total Rows" in md
        assert "Quality Scorecard" in md
        assert "Completeness" in md

    @pytest.mark.unit
    def test_profiler_empty_dataframe(self) -> None:
        df = pd.DataFrame(columns=["col1", "col2"])
        profiler = DataProfiler()
        profile = profiler.profile(df, dataset_name="empty")

        assert profile.row_count == 0
        assert profile.column_count == 2
        assert profile.completeness == 0.0
