"""
ADI-OS Configuration Manager

Centralized, type-safe configuration management using Pydantic Settings.
Loads from environment variables and .env files following the
PERMISSION_POLICY.md principle: secrets never hardcoded.
"""

from __future__ import annotations

from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Deployment environment tiers."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Structured log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DataLakeProvider(str, Enum):
    """Supported object storage backends."""

    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"
    ADLS = "adls"


# ── Project Root Detection ──
def _find_project_root() -> Path:
    """Walk up from this file to find the project root (contains pyproject.toml)."""
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return current.parent.parent  # fallback


PROJECT_ROOT = _find_project_root()


class DatabaseSettings(BaseSettings):
    """Data Warehouse connection settings."""

    model_config = SettingsConfigDict(env_prefix="DWH_")

    host: str = "localhost"
    port: int = 5432
    database: str = "adi_os"
    schema_: str = Field(default="public", alias="DWH_SCHEMA")
    user: str = "adi_user"
    password: SecretStr = SecretStr("changeme")

    @property
    def connection_string(self) -> str:
        """Generate SQLAlchemy connection string (password masked in logs)."""
        pwd = self.password.get_secret_value()
        return f"postgresql://{self.user}:{pwd}@{self.host}:{self.port}/{self.database}"

    @property
    def safe_connection_string(self) -> str:
        """Connection string safe for logging (password redacted)."""
        return f"postgresql://{self.user}:***@{self.host}:{self.port}/{self.database}"


class DataLakeSettings(BaseSettings):
    """Object storage / data lake settings."""

    model_config = SettingsConfigDict(env_prefix="DATA_LAKE_")

    provider: DataLakeProvider = DataLakeProvider.LOCAL
    bucket: str = "adi-os-datalake"
    path: str = "./data"

    @property
    def bronze_path(self) -> Path:
        return Path(self.path) / "bronze"

    @property
    def silver_path(self) -> Path:
        return Path(self.path) / "silver"

    @property
    def gold_path(self) -> Path:
        return Path(self.path) / "gold"

    @property
    def quarantine_path(self) -> Path:
        return Path(self.path) / "quarantine"


class MLflowSettings(BaseSettings):
    """Experiment tracking settings."""

    model_config = SettingsConfigDict(env_prefix="MLFLOW_")

    tracking_uri: str = "http://localhost:5000"
    experiment_name: str = "adi-os-default"
    artifact_root: str = "./mlruns"


class SecuritySettings(BaseSettings):
    """Security and PII protection settings."""

    model_config = SettingsConfigDict(env_prefix="")

    pii_detection_enabled: bool = True
    encryption_key: SecretStr = SecretStr("")
    audit_log_path: str = "./logs/audit"


class AppSettings(BaseSettings):
    """
    Master application configuration.

    Loads from .env file and environment variables.
    Hierarchy: env vars > .env file > defaults
    """

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── General ──
    environment: Environment = Environment.DEVELOPMENT
    log_level: LogLevel = LogLevel.INFO
    project_name: str = "adi-os"

    # ── Sub-configs ──
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    data_lake: DataLakeSettings = Field(default_factory=DataLakeSettings)
    mlflow: MLflowSettings = Field(default_factory=MLflowSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION

    @property
    def project_root(self) -> Path:
        return PROJECT_ROOT

    @field_validator("environment", mode="before")
    @classmethod
    def validate_environment(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.lower()
        return v


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """
    Singleton settings instance.

    Usage:
        from src.utils.config import get_settings
        settings = get_settings()
        print(settings.db.safe_connection_string)
    """
    return AppSettings()
