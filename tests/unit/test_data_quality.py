"""
Unit Tests — Data Quality Validators (Gate 1)

Tests the DataQualityValidator against all 5 mandatory checks:
  1. Schema Invariants
  2. Primary Key Uniqueness
  3. Null Thresholds
  4. Range Invariants
  5. Temporal Ordering
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import pytest

from src.quality.validators import (
    DataContract,
    DataQualityValidator,
    GateStatus,
)


class TestSchemaInvariants:
    """Gate 1, Check 1: Schema invariants."""

    @pytest.mark.unit
    def test_all_columns_present_passes(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        validator = DataQualityValidator(sample_transactions_df, sample_transactions_contract)
        report = validator.run_gate_1()
        schema_checks = [c for c in report.checks if c.check_category == "Schema Invariants"]
        assert any(c.status == GateStatus.PASSED for c in schema_checks)

    @pytest.mark.unit
    def test_missing_column_fails(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        df_missing = sample_transactions_df.drop(columns=["amount"])
        validator = DataQualityValidator(df_missing, sample_transactions_contract)
        report = validator.run_gate_1()
        assert report.gate_status == GateStatus.FAILED


class TestPrimaryKeyUniqueness:
    """Gate 1, Check 2: Primary key uniqueness."""

    @pytest.mark.unit
    def test_unique_pks_pass(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        validator = DataQualityValidator(sample_transactions_df, sample_transactions_contract)
        report = validator.run_gate_1()
        pk_checks = [c for c in report.checks if c.check_category == "Primary Key Uniqueness"]
        assert all(c.status == GateStatus.PASSED for c in pk_checks)

    @pytest.mark.unit
    def test_duplicate_pks_fail(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        # Introduce duplicate PKs
        df_dup = pd.concat([sample_transactions_df, sample_transactions_df.head(5)], ignore_index=True)
        # Reset transaction_id to create real duplicates
        df_dup.loc[len(sample_transactions_df) :, "transaction_id"] = range(1, 6)
        validator = DataQualityValidator(df_dup, sample_transactions_contract)
        report = validator.run_gate_1()
        assert report.gate_status == GateStatus.FAILED

    @pytest.mark.unit
    def test_null_pk_fails(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        df_null_pk = sample_transactions_df.copy()
        df_null_pk.loc[0, "transaction_id"] = None
        validator = DataQualityValidator(df_null_pk, sample_transactions_contract)
        report = validator.run_gate_1()
        assert report.gate_status == GateStatus.FAILED


class TestNullThresholds:
    """Gate 1, Check 3: Null thresholds."""

    @pytest.mark.unit
    def test_no_nulls_passes(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        validator = DataQualityValidator(sample_transactions_df, sample_transactions_contract)
        report = validator.run_gate_1()
        null_checks = [c for c in report.checks if c.check_category == "Null Thresholds"]
        assert all(c.status == GateStatus.PASSED for c in null_checks)

    @pytest.mark.unit
    def test_nulls_in_nonnullable_fails(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        df_nulls = sample_transactions_df.copy()
        df_nulls.loc[0:10, "amount"] = None
        validator = DataQualityValidator(df_nulls, sample_transactions_contract)
        report = validator.run_gate_1()
        assert report.gate_status == GateStatus.FAILED


class TestRangeInvariants:
    """Gate 1, Check 4: Range invariants."""

    @pytest.mark.unit
    def test_valid_ranges_pass(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        validator = DataQualityValidator(sample_transactions_df, sample_transactions_contract)
        report = validator.run_gate_1()
        range_checks = [c for c in report.checks if c.check_category == "Range Invariants"]
        # All amount values are positive (generated with exponential)
        assert all(c.status == GateStatus.PASSED for c in range_checks)

    @pytest.mark.unit
    def test_negative_amount_fails(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        df_neg = sample_transactions_df.copy()
        df_neg.loc[0, "amount"] = -100.0
        validator = DataQualityValidator(df_neg, sample_transactions_contract)
        report = validator.run_gate_1()
        range_fails = [
            c for c in report.checks if c.check_category == "Range Invariants" and c.status == GateStatus.FAILED
        ]
        assert len(range_fails) > 0

    @pytest.mark.unit
    def test_invalid_category_fails(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        df_bad_cat = sample_transactions_df.copy()
        df_bad_cat.loc[0, "category"] = "INVALID_CATEGORY"
        validator = DataQualityValidator(df_bad_cat, sample_transactions_contract)
        report = validator.run_gate_1()
        assert report.gate_status == GateStatus.FAILED


class TestTemporalOrdering:
    """Gate 1, Check 5: Temporal ordering."""

    @pytest.mark.unit
    def test_no_future_dates_passes(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        validator = DataQualityValidator(sample_transactions_df, sample_transactions_contract)
        report = validator.run_gate_1()
        temporal_checks = [c for c in report.checks if c.check_category == "Temporal Ordering"]
        assert all(c.status == GateStatus.PASSED for c in temporal_checks)

    @pytest.mark.unit
    def test_future_dates_fail(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        df_future = sample_transactions_df.copy()
        df_future.loc[0, "transaction_date"] = datetime.now() + timedelta(days=365)
        validator = DataQualityValidator(df_future, sample_transactions_contract)
        report = validator.run_gate_1()
        temporal_fails = [
            c for c in report.checks if c.check_category == "Temporal Ordering" and c.status == GateStatus.FAILED
        ]
        assert len(temporal_fails) > 0


class TestQualityReport:
    """Test report generation."""

    @pytest.mark.unit
    def test_report_generates_markdown(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        validator = DataQualityValidator(sample_transactions_df, sample_transactions_contract)
        report = validator.run_gate_1()
        markdown = report.to_markdown()
        assert "# Data Quality Report" in markdown
        assert "Gate 1 Status" in markdown
        assert "Total Rows" in markdown
