"""
Integration Tests — Warehouse bootstrap (infrastructure/docker/init-db.sql)

Runs against a real PostgreSQL (CI `integration-tests` service). Skipped
automatically when no database is configured or `psql` is unavailable.

Checks:
  - init-db.sql applies cleanly on an empty database
  - init-db.sql is idempotent (second run does not fail)
  - the bronze source table required by dbt exists with transaction_status
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

INIT_SQL = Path(__file__).resolve().parents[2] / "infrastructure" / "docker" / "init-db.sql"

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(shutil.which("psql") is None, reason="psql client not installed"),
    pytest.mark.skipif("DWH_PASSWORD" not in os.environ, reason="no warehouse configured (DWH_* env)"),
]


def _psql(*args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PGPASSWORD": os.environ["DWH_PASSWORD"]}
    cmd = [
        "psql",
        "-v",
        "ON_ERROR_STOP=1",
        "-h",
        os.environ.get("DWH_HOST", "localhost"),
        "-p",
        os.environ.get("DWH_PORT", "5432"),
        "-U",
        os.environ.get("DWH_USER", "adi_user"),
        "-d",
        os.environ.get("DWH_DATABASE", "adi_os"),
        *args,
    ]
    return subprocess.run(cmd, env=env, capture_output=True, text=True, check=False, timeout=60)


def test_init_db_is_idempotent() -> None:
    for attempt in (1, 2):
        result = _psql("-f", str(INIT_SQL))
        assert result.returncode == 0, f"run {attempt} failed:\n{result.stderr}"


def test_bronze_source_table_has_status_column() -> None:
    _psql("-f", str(INIT_SQL))
    result = _psql(
        "-tAc",
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema='bronze' AND table_name='raw_customer_transactions'",
    )
    assert result.returncode == 0, result.stderr
    columns = set(result.stdout.split())
    assert {"transaction_id", "amount", "transaction_status", "transaction_date"} <= columns
