"""
Unit Tests — Data Quality Validators (Gate 1)

Tests the DataQualityValidator against all 5 mandatory checks:
  1. Schema Invariants (presence, extra columns, data types)
  2. Primary Key Uniqueness (nulls, duplicates, distinctness)
  3. Null Thresholds (strict non-nullable, configurable tolerance)
  4. Range Invariants (min, max, allowed categorical values)
  5. Temporal Ordering (future timestamps, parse errors)
And tests DataContract parsing and QualityReport aggregation.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import pytest

from src.quality.validators import (
    ColumnContract,
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
        assert all(c.status == GateStatus.PASSED for c in schema_checks)
        assert report.gate_status == GateStatus.PASSED

    @pytest.mark.unit
    def test_missing_column_fails(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        df_missing = sample_transactions_df.drop(columns=["amount"])
        validator = DataQualityValidator(df_missing, sample_transactions_contract)
        report = validator.run_gate_1()
        assert report.gate_status == GateStatus.FAILED
        failed_checks = [c for c in report.checks if c.status == GateStatus.FAILED]
        assert any("Missing Columns" in c.check_name for c in failed_checks)

    @pytest.mark.unit
    def test_extra_column_yields_warning(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        df_extra = sample_transactions_df.copy()
        df_extra["unexpected_column"] = 123
        validator = DataQualityValidator(df_extra, sample_transactions_contract)
        report = validator.run_gate_1()
        warning_checks = [c for c in report.checks if c.status == GateStatus.WARNING]
        assert any("Extra Columns" in c.check_name for c in warning_checks)

    @pytest.mark.unit
    def test_incompatible_dtype_fails(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        df_bad_type = sample_transactions_df.copy()
        df_bad_type["amount"] = df_bad_type["amount"].astype(str)  # Should be float64
        validator = DataQualityValidator(df_bad_type, sample_transactions_contract)
        report = validator.run_gate_1()
        assert report.gate_status == GateStatus.FAILED
        dtype_fails = [c for c in report.checks if "dtype [amount]" in c.check_name]
        assert len(dtype_fails) == 1
        assert dtype_fails[0].status == GateStatus.FAILED


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
        df_dup = pd.concat([sample_transactions_df, sample_transactions_df.head(5)], ignore_index=True)
        df_dup.loc[len(sample_transactions_df) :, "transaction_id"] = range(1, 6)
        validator = DataQualityValidator(df_dup, sample_transactions_contract)
        report = validator.run_gate_1()
        assert report.gate_status == GateStatus.FAILED
        dup_fails = [c for c in report.checks if "duplicate primary key" in c.message]
        assert len(dup_fails) > 0

    @pytest.mark.unit
    def test_null_pk_fails(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        df_null_pk = sample_transactions_df.copy()
        df_null_pk.loc[0, "transaction_id"] = None
        validator = DataQualityValidator(df_null_pk, sample_transactions_contract)
        report = validator.run_gate_1()
        assert report.gate_status == GateStatus.FAILED
        null_pk_fails = [c for c in report.checks if "null primary key" in c.message]
        assert len(null_pk_fails) > 0


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

    @pytest.mark.unit
    def test_nulls_within_contract_limit_passes(self, sample_transactions_df: pd.DataFrame) -> None:
        contract = DataContract(
            name="tolerance_test",
            description="Testing null thresholds",
            owner="analytics",
            primary_keys=["transaction_id"],
            columns={
                "transaction_id": ColumnContract(dtype="int64", nullable=False),
                "amount": ColumnContract(dtype="float64", nullable=True, max_null_pct=0.10, min_value=0.0),
            },
        )
        df = sample_transactions_df[["transaction_id", "amount"]].copy()
        # Set 5% nulls (within 10% limit)
        df.loc[: int(len(df) * 0.05), "amount"] = None
        validator = DataQualityValidator(df, contract)
        report = validator.run_gate_1()
        null_checks = [c for c in report.checks if "Nulls: [amount]" in c.check_name]
        assert len(null_checks) == 1
        assert null_checks[0].status == GateStatus.PASSED
        assert report.gate_status == GateStatus.PASSED

    @pytest.mark.unit
    def test_nulls_exceeding_contract_limit_fails(self, sample_transactions_df: pd.DataFrame) -> None:
        contract = DataContract(
            name="tolerance_test",
            description="Testing null thresholds",
            owner="analytics",
            primary_keys=["transaction_id"],
            columns={
                "transaction_id": ColumnContract(dtype="int64", nullable=False),
                "amount": ColumnContract(dtype="float64", nullable=True, max_null_pct=0.05, min_value=0.0),
            },
        )
        df = sample_transactions_df[["transaction_id", "amount"]].copy()
        # Set 20% nulls (exceeds 5% limit)
        df.loc[: int(len(df) * 0.20), "amount"] = None
        validator = DataQualityValidator(df, contract)
        report = validator.run_gate_1()
        assert report.gate_status == GateStatus.FAILED
        null_checks = [c for c in report.checks if "Nulls: [amount]" in c.check_name]
        assert len(null_checks) == 1
        assert null_checks[0].status == GateStatus.FAILED


class TestRangeInvariants:
    """Gate 1, Check 4: Range invariants."""

    @pytest.mark.unit
    def test_valid_ranges_pass(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        validator = DataQualityValidator(sample_transactions_df, sample_transactions_contract)
        report = validator.run_gate_1()
        range_checks = [c for c in report.checks if c.check_category == "Range Invariants"]
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
        assert report.gate_status == GateStatus.FAILED

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


class TestDataContractAndReport:
    """Test DataContract.from_dict and QualityReport properties."""

    @pytest.mark.unit
    def test_contract_from_dict(self) -> None:
        data = {
            "name": "orders",
            "version": "2.1.0",
            "owner": "team_lead",
            "primary_keys": ["order_id"],
            "columns": {
                "order_id": {"name": "order_id", "dtype": "int64", "nullable": False},
                "total_price": {"name": "total_price", "dtype": "float64", "min_value": 0.0},
            },
        }
        contract = DataContract.from_dict(data)
        assert contract.name == "orders"
        assert contract.primary_keys == ["order_id"]
        assert "total_price" in contract.columns
        assert contract.columns["total_price"].min_value == 0.0

    @pytest.mark.unit
    def test_report_generates_markdown_and_filters(
        self, sample_transactions_df: pd.DataFrame, sample_transactions_contract: DataContract
    ) -> None:
        df_with_issue = sample_transactions_df.copy()
        df_with_issue.loc[0, "amount"] = -10.0  # Critical failure
        validator = DataQualityValidator(df_with_issue, sample_transactions_contract)
        report = validator.run_gate_1()

        assert len(report.critical_failures) > 0
        assert len(report.passed_checks) > 0
        markdown = report.to_markdown()
        assert "# Data Quality Report" in markdown
        assert "Gate 1 Status" in markdown
        assert "Total Rows" in markdown
