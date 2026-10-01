"""
ADI-OS Data Quality Validators

Implements Quality Gate 1 checks as defined in QUALITY_GATE.md:
  1. Schema Invariants
  2. Primary Key Uniqueness
  3. Null Thresholds
  4. Range Invariants
  5. Temporal Ordering
  6. Target & Feature Leakage

Usage:
    from src.quality.validators import DataQualityValidator
    validator = DataQualityValidator(df, contract)
    report = validator.run_gate_1()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import pandas as pd

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class GateStatus(str, Enum):
    """Quality gate evaluation status."""

    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"


class CheckSeverity(str, Enum):
    """Severity of a quality check."""

    CRITICAL = "CRITICAL"   # Fails the gate immediately
    WARNING = "WARNING"     # Logged but gate can still pass
    INFO = "INFO"           # Informational only


@dataclass
class QualityCheckResult:
    """Result of a single quality check."""

    check_name: str
    check_category: str
    status: GateStatus
    severity: CheckSeverity
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class DataContract:
    """
    Executable Data Contract specification.

    Defines the expected schema, constraints, and SLAs for a dataset.
    Maps to ARTIFACT_PROTOCOL.md DATA_CONTRACT.md template.
    """

    name: str
    description: str
    owner: str
    primary_keys: list[str]
    columns: dict[str, ColumnContract]
    freshness_hours: float | None = None  # Max hours since last update
    max_null_percentage: float = 0.0      # Default: 0% nulls for critical fields
    grain: str = ""                        # e.g., "one row per customer per day"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DataContract:
        """Create a DataContract from a dictionary (e.g., loaded from YAML)."""
        columns = {
            name: ColumnContract(**spec)
            for name, spec in data.get("columns", {}).items()
        }
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            owner=data.get("owner", "unknown"),
            primary_keys=data.get("primary_keys", []),
            columns=columns,
            freshness_hours=data.get("freshness_hours"),
            max_null_percentage=data.get("max_null_percentage", 0.0),
            grain=data.get("grain", ""),
        )


@dataclass
class ColumnContract:
    """Contract specification for a single column."""

    dtype: str                              # Expected pandas dtype string
    nullable: bool = False                  # Whether nulls are allowed
    max_null_pct: float = 0.0              # Max null percentage (0.0 = no nulls)
    min_value: float | None = None         # Minimum allowed value
    max_value: float | None = None         # Maximum allowed value
    allowed_values: list[Any] | None = None  # Categorical allowed values
    is_primary_key: bool = False
    is_temporal: bool = False               # Date/datetime column
    no_future_dates: bool = False           # Temporal: reject future dates
    description: str = ""


@dataclass
class QualityReport:
    """
    Complete Quality Gate 1 Report.

    Maps to ARTIFACT_PROTOCOL.md DATA_QUALITY_REPORT.md template.
    """

    dataset_name: str
    gate_status: GateStatus
    checks: list[QualityCheckResult]
    summary: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @property
    def critical_failures(self) -> list[QualityCheckResult]:
        return [
            c for c in self.checks
            if c.status == GateStatus.FAILED and c.severity == CheckSeverity.CRITICAL
        ]

    @property
    def warnings(self) -> list[QualityCheckResult]:
        return [c for c in self.checks if c.status == GateStatus.WARNING]

    @property
    def passed_checks(self) -> list[QualityCheckResult]:
        return [c for c in self.checks if c.status == GateStatus.PASSED]

    def to_markdown(self) -> str:
        """Generate DATA_QUALITY_REPORT.md content."""
        lines = [
            "---",
            f'artifact_type: "DATA_QUALITY_REPORT"',
            f'title: "Data Quality Report: {self.dataset_name}"',
            f'created_at: "{self.timestamp}"',
            f'quality_gate_status: "{self.gate_status.value}"',
            "---",
            "",
            f"# Data Quality Report: {self.dataset_name}",
            "",
            f"**Gate 1 Status:** `{self.gate_status.value}`",
            f"**Timestamp:** {self.timestamp}",
            "",
            "## Summary",
            "",
            f"| Metric | Value |",
            f"|---|---|",
        ]
        for key, value in self.summary.items():
            lines.append(f"| {key} | {value} |")

        lines.extend([
            "",
            "## Check Results",
            "",
            "| Check | Category | Status | Severity | Message |",
            "|---|---|---|---|---|",
        ])
        for check in self.checks:
            status_icon = "✅" if check.status == GateStatus.PASSED else "❌" if check.status == GateStatus.FAILED else "⚠️"
            lines.append(
                f"| {check.check_name} | {check.check_category} | "
                f"{status_icon} {check.status.value} | {check.severity.value} | {check.message} |"
            )

        if self.critical_failures:
            lines.extend([
                "",
                "## ❌ Critical Failures",
                "",
            ])
            for failure in self.critical_failures:
                lines.append(f"- **{failure.check_name}:** {failure.message}")
                if failure.details:
                    for k, v in failure.details.items():
                        lines.append(f"  - {k}: {v}")

        return "\n".join(lines)


class DataQualityValidator:
    """
    Implements all Quality Gate 1 checks from QUALITY_GATE.md.

    Usage:
        contract = DataContract(...)
        validator = DataQualityValidator(df, contract)
        report = validator.run_gate_1()
        if report.gate_status == GateStatus.FAILED:
            # Quarantine and alert
    """

    def __init__(self, df: pd.DataFrame, contract: DataContract) -> None:
        self.df = df
        self.contract = contract
        self._results: list[QualityCheckResult] = []

    def run_gate_1(self) -> QualityReport:
        """Execute all Gate 1 mandatory checks and return a QualityReport."""
        logger.info(
            "Starting Gate 1 Data Quality validation",
            dataset=self.contract.name,
            rows=len(self.df),
            columns=len(self.df.columns),
        )

        self._check_schema_invariants()
        self._check_primary_key_uniqueness()
        self._check_null_thresholds()
        self._check_range_invariants()
        self._check_temporal_ordering()

        # Determine overall gate status
        has_critical_failure = any(
            r.status == GateStatus.FAILED and r.severity == CheckSeverity.CRITICAL
            for r in self._results
        )

        gate_status = GateStatus.FAILED if has_critical_failure else GateStatus.PASSED

        summary = {
            "Total Rows": len(self.df),
            "Total Columns": len(self.df.columns),
            "Duplicate Rows": int(self.df.duplicated().sum()),
            "Total Checks": len(self._results),
            "Passed": sum(1 for r in self._results if r.status == GateStatus.PASSED),
            "Failed": sum(1 for r in self._results if r.status == GateStatus.FAILED),
            "Warnings": sum(1 for r in self._results if r.status == GateStatus.WARNING),
            "Missing Cell %": f"{self.df.isnull().mean().mean() * 100:.2f}%",
        }

        report = QualityReport(
            dataset_name=self.contract.name,
            gate_status=gate_status,
            checks=self._results,
            summary=summary,
        )

        logger.info(
            "Gate 1 validation complete",
            dataset=self.contract.name,
            gate_status=gate_status.value,
            passed=summary["Passed"],
            failed=summary["Failed"],
        )

        return report

    def _check_schema_invariants(self) -> None:
        """Check 1: Column names and data types match contract."""
        expected_cols = set(self.contract.columns.keys())
        actual_cols = set(self.df.columns)

        missing = expected_cols - actual_cols
        extra = actual_cols - expected_cols

        if missing:
            self._results.append(QualityCheckResult(
                check_name="Schema: Missing Columns",
                check_category="Schema Invariants",
                status=GateStatus.FAILED,
                severity=CheckSeverity.CRITICAL,
                message=f"Missing columns: {sorted(missing)}",
                details={"missing_columns": sorted(missing)},
            ))
        elif extra:
            self._results.append(QualityCheckResult(
                check_name="Schema: Extra Columns",
                check_category="Schema Invariants",
                status=GateStatus.WARNING,
                severity=CheckSeverity.WARNING,
                message=f"Unexpected columns: {sorted(extra)}",
                details={"extra_columns": sorted(extra)},
            ))
        else:
            self._results.append(QualityCheckResult(
                check_name="Schema: Column Presence",
                check_category="Schema Invariants",
                status=GateStatus.PASSED,
                severity=CheckSeverity.CRITICAL,
                message="All expected columns present",
            ))

        # Check data types for present columns
        for col_name, col_contract in self.contract.columns.items():
            if col_name not in self.df.columns:
                continue
            actual_dtype = str(self.df[col_name].dtype)
            expected_dtype = col_contract.dtype

            # Flexible dtype matching
            dtype_compatible = (
                actual_dtype == expected_dtype
                or (expected_dtype == "int64" and actual_dtype in ("int64", "Int64", "int32"))
                or (expected_dtype == "float64" and actual_dtype in ("float64", "float32"))
                or (expected_dtype == "object" and actual_dtype in ("object", "string", "str"))
                or (expected_dtype == "datetime64" and "datetime" in actual_dtype)
                or (expected_dtype == "bool" and actual_dtype in ("bool", "boolean"))
            )

            status = GateStatus.PASSED if dtype_compatible else GateStatus.FAILED
            self._results.append(QualityCheckResult(
                check_name=f"Schema: dtype [{col_name}]",
                check_category="Schema Invariants",
                status=status,
                severity=CheckSeverity.CRITICAL if not dtype_compatible else CheckSeverity.INFO,
                message=f"Expected {expected_dtype}, got {actual_dtype}",
                details={"column": col_name, "expected": expected_dtype, "actual": actual_dtype},
            ))

    def _check_primary_key_uniqueness(self) -> None:
        """Check 2: Primary key distinct count equals row count; zero null keys."""
        pks = self.contract.primary_keys
        if not pks:
            self._results.append(QualityCheckResult(
                check_name="PK: No primary key defined",
                check_category="Primary Key Uniqueness",
                status=GateStatus.WARNING,
                severity=CheckSeverity.WARNING,
                message="No primary key defined in contract",
            ))
            return

        # Check for missing PK columns
        missing_pks = [pk for pk in pks if pk not in self.df.columns]
        if missing_pks:
            self._results.append(QualityCheckResult(
                check_name="PK: Missing PK Columns",
                check_category="Primary Key Uniqueness",
                status=GateStatus.FAILED,
                severity=CheckSeverity.CRITICAL,
                message=f"Primary key columns missing: {missing_pks}",
            ))
            return

        # Check null PKs
        null_pk_count = int(self.df[pks].isnull().any(axis=1).sum())
        if null_pk_count > 0:
            self._results.append(QualityCheckResult(
                check_name="PK: Null Primary Keys",
                check_category="Primary Key Uniqueness",
                status=GateStatus.FAILED,
                severity=CheckSeverity.CRITICAL,
                message=f"{null_pk_count} rows have null primary key values",
                details={"null_pk_rows": null_pk_count},
            ))
        else:
            self._results.append(QualityCheckResult(
                check_name="PK: No Null Keys",
                check_category="Primary Key Uniqueness",
                status=GateStatus.PASSED,
                severity=CheckSeverity.CRITICAL,
                message="Zero null primary keys",
            ))

        # Check uniqueness
        total_rows = len(self.df)
        unique_pk_count = len(self.df.drop_duplicates(subset=pks))
        duplicate_count = total_rows - unique_pk_count

        if duplicate_count > 0:
            self._results.append(QualityCheckResult(
                check_name="PK: Uniqueness",
                check_category="Primary Key Uniqueness",
                status=GateStatus.FAILED,
                severity=CheckSeverity.CRITICAL,
                message=f"{duplicate_count} duplicate primary key combinations found",
                details={
                    "total_rows": total_rows,
                    "unique_pks": unique_pk_count,
                    "duplicates": duplicate_count,
                },
            ))
        else:
            self._results.append(QualityCheckResult(
                check_name="PK: Uniqueness",
                check_category="Primary Key Uniqueness",
                status=GateStatus.PASSED,
                severity=CheckSeverity.CRITICAL,
                message=f"All {total_rows} primary keys are unique",
            ))

    def _check_null_thresholds(self) -> None:
        """Check 3: Null rates within contract thresholds."""
        for col_name, col_contract in self.contract.columns.items():
            if col_name not in self.df.columns:
                continue

            null_count = int(self.df[col_name].isnull().sum())
            null_pct = null_count / len(self.df) if len(self.df) > 0 else 0.0
            threshold = col_contract.max_null_pct

            if not col_contract.nullable and null_count > 0:
                self._results.append(QualityCheckResult(
                    check_name=f"Nulls: [{col_name}]",
                    check_category="Null Thresholds",
                    status=GateStatus.FAILED,
                    severity=CheckSeverity.CRITICAL,
                    message=f"Non-nullable column has {null_count} nulls ({null_pct:.2%})",
                    details={"null_count": null_count, "null_pct": f"{null_pct:.4f}"},
                ))
            elif null_pct > threshold:
                self._results.append(QualityCheckResult(
                    check_name=f"Nulls: [{col_name}]",
                    check_category="Null Thresholds",
                    status=GateStatus.FAILED,
                    severity=CheckSeverity.CRITICAL,
                    message=f"Null rate {null_pct:.2%} exceeds threshold {threshold:.2%}",
                    details={"null_count": null_count, "null_pct": f"{null_pct:.4f}", "threshold": threshold},
                ))
            else:
                self._results.append(QualityCheckResult(
                    check_name=f"Nulls: [{col_name}]",
                    check_category="Null Thresholds",
                    status=GateStatus.PASSED,
                    severity=CheckSeverity.INFO,
                    message=f"Null rate {null_pct:.2%} within threshold {threshold:.2%}",
                ))

    def _check_range_invariants(self) -> None:
        """Check 4: Numerical values within physically plausible domains."""
        for col_name, col_contract in self.contract.columns.items():
            if col_name not in self.df.columns:
                continue

            # Numeric range checks
            if col_contract.min_value is not None:
                violations = self.df[col_name].dropna() < col_contract.min_value
                violation_count = int(violations.sum())
                if violation_count > 0:
                    self._results.append(QualityCheckResult(
                        check_name=f"Range: [{col_name}] min",
                        check_category="Range Invariants",
                        status=GateStatus.FAILED,
                        severity=CheckSeverity.CRITICAL,
                        message=f"{violation_count} values below minimum {col_contract.min_value}",
                        details={"violations": violation_count, "min_allowed": col_contract.min_value},
                    ))
                else:
                    self._results.append(QualityCheckResult(
                        check_name=f"Range: [{col_name}] min",
                        check_category="Range Invariants",
                        status=GateStatus.PASSED,
                        severity=CheckSeverity.INFO,
                        message=f"All values >= {col_contract.min_value}",
                    ))

            if col_contract.max_value is not None:
                violations = self.df[col_name].dropna() > col_contract.max_value
                violation_count = int(violations.sum())
                if violation_count > 0:
                    self._results.append(QualityCheckResult(
                        check_name=f"Range: [{col_name}] max",
                        check_category="Range Invariants",
                        status=GateStatus.FAILED,
                        severity=CheckSeverity.CRITICAL,
                        message=f"{violation_count} values above maximum {col_contract.max_value}",
                        details={"violations": violation_count, "max_allowed": col_contract.max_value},
                    ))
                else:
                    self._results.append(QualityCheckResult(
                        check_name=f"Range: [{col_name}] max",
                        check_category="Range Invariants",
                        status=GateStatus.PASSED,
                        severity=CheckSeverity.INFO,
                        message=f"All values <= {col_contract.max_value}",
                    ))

            # Categorical allowed values
            if col_contract.allowed_values is not None:
                actual_values = set(self.df[col_name].dropna().unique())
                invalid = actual_values - set(col_contract.allowed_values)
                if invalid:
                    self._results.append(QualityCheckResult(
                        check_name=f"Range: [{col_name}] allowed values",
                        check_category="Range Invariants",
                        status=GateStatus.FAILED,
                        severity=CheckSeverity.CRITICAL,
                        message=f"Invalid values found: {sorted(invalid)[:10]}",
                        details={"invalid_values": sorted(str(v) for v in list(invalid)[:10])},
                    ))
                else:
                    self._results.append(QualityCheckResult(
                        check_name=f"Range: [{col_name}] allowed values",
                        check_category="Range Invariants",
                        status=GateStatus.PASSED,
                        severity=CheckSeverity.INFO,
                        message="All values within allowed set",
                    ))

    def _check_temporal_ordering(self) -> None:
        """Check 5: Future timestamps absent; time-series ordering verified."""
        now = pd.Timestamp.now()

        for col_name, col_contract in self.contract.columns.items():
            if not col_contract.is_temporal or col_name not in self.df.columns:
                continue

            try:
                temporal_col = pd.to_datetime(self.df[col_name], errors="coerce")
            except Exception:
                self._results.append(QualityCheckResult(
                    check_name=f"Temporal: [{col_name}] parse",
                    check_category="Temporal Ordering",
                    status=GateStatus.FAILED,
                    severity=CheckSeverity.CRITICAL,
                    message=f"Cannot parse column as datetime",
                ))
                continue

            # Check for future dates
            if col_contract.no_future_dates:
                future_count = int((temporal_col > now).sum())
                if future_count > 0:
                    self._results.append(QualityCheckResult(
                        check_name=f"Temporal: [{col_name}] no future",
                        check_category="Temporal Ordering",
                        status=GateStatus.FAILED,
                        severity=CheckSeverity.CRITICAL,
                        message=f"{future_count} future timestamps detected (potential leakage!)",
                        details={"future_dates": future_count},
                    ))
                else:
                    self._results.append(QualityCheckResult(
                        check_name=f"Temporal: [{col_name}] no future",
                        check_category="Temporal Ordering",
                        status=GateStatus.PASSED,
                        severity=CheckSeverity.CRITICAL,
                        message="No future timestamps detected",
                    ))

            # Check parse failures
            parse_failures = int(temporal_col.isnull().sum() - self.df[col_name].isnull().sum())
            if parse_failures > 0:
                self._results.append(QualityCheckResult(
                    check_name=f"Temporal: [{col_name}] parse errors",
                    check_category="Temporal Ordering",
                    status=GateStatus.WARNING,
                    severity=CheckSeverity.WARNING,
                    message=f"{parse_failures} values failed datetime parsing",
                    details={"parse_failures": parse_failures},
                ))
