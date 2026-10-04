"""
Unit Tests — App Settings & Configuration (src.utils.config)

Tests:
  - Database connection string generation
  - Safe connection string masking password
  - Data lake path resolution (bronze, silver, gold, quarantine)
  - Environment validator and is_production flag
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import SecretStr

from src.utils.config import (
    AppSettings,
    DatabaseSettings,
    DataLakeSettings,
    Environment,
)


class TestConfig:
    """Test configuration models and security protections."""

    @pytest.mark.unit
    def test_database_connection_string(self) -> None:
        db = DatabaseSettings(
            host="db.example.com",
            port=5432,
            database="analytics",
            user="app_user",
            password=SecretStr("super_secret_pw"),
        )
        assert db.connection_string == "postgresql://app_user:super_secret_pw@db.example.com:5432/analytics"

    @pytest.mark.unit
    def test_database_safe_connection_string_masks_password(self) -> None:
        db = DatabaseSettings(
            host="db.example.com",
            port=5432,
            database="analytics",
            user="app_user",
            password=SecretStr("super_secret_pw"),
        )
        safe = db.safe_connection_string
        assert "super_secret_pw" not in safe
        assert safe == "postgresql://app_user:***@db.example.com:5432/analytics"

    @pytest.mark.unit
    def test_data_lake_paths(self) -> None:
        lake = DataLakeSettings(path="./my_data")
        assert lake.bronze_path == Path("my_data/bronze")
        assert lake.silver_path == Path("my_data/silver")
        assert lake.gold_path == Path("my_data/gold")
        assert lake.quarantine_path == Path("my_data/quarantine")

    @pytest.mark.unit
    def test_app_settings_environment(self) -> None:
        settings_dev = AppSettings(environment=Environment.DEVELOPMENT)
        assert not settings_dev.is_production
        assert settings_dev.project_root.exists()

        settings_prod = AppSettings(environment=Environment.PRODUCTION)
        assert settings_prod.is_production
