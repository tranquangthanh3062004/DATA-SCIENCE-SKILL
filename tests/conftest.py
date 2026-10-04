"""
ADI-OS Test Configuration

Shared fixtures for all test categories:
  - unit tests
  - integration tests
  - data quality gate tests
  - ML pipeline tests
"""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from src.quality.validators import ColumnContract, DataContract

# ── Sample Data Fixtures ──


@pytest.fixture
def sample_transactions_df() -> pd.DataFrame:
    """Generate a synthetic customer transactions dataset."""
    np.random.seed(42)
    n = 1000

    base_date = datetime(2025, 1, 1)
    dates = [base_date + timedelta(days=int(d)) for d in np.random.randint(0, 365, n)]

    return pd.DataFrame(
        {
            "transaction_id": range(1, n + 1),
            "customer_id": np.random.randint(100, 500, n),
            "transaction_date": dates,
            "amount": np.round(np.random.exponential(50, n), 2),
            "category": np.random.choice(["electronics", "clothing", "food", "other"], n),
            "store_id": np.random.randint(1, 20, n),
        }
    )


@pytest.fixture
def sample_transactions_contract() -> DataContract:
    """Data contract for the sample transactions dataset."""
    return DataContract(
        name="sample_transactions",
        description="Synthetic customer transactions for testing",
        owner="data_quality_engineer",
        primary_keys=["transaction_id"],
        grain="one row per transaction",
        columns={
            "transaction_id": ColumnContract(
                dtype="int64",
                nullable=False,
                is_primary_key=True,
                description="Unique transaction identifier",
            ),
            "customer_id": ColumnContract(
                dtype="int64",
                nullable=False,
                min_value=1,
                description="Customer identifier",
            ),
            "transaction_date": ColumnContract(
                dtype="datetime64",
                nullable=False,
                is_temporal=True,
                no_future_dates=True,
                description="Date of transaction",
            ),
            "amount": ColumnContract(
                dtype="float64",
                nullable=False,
                min_value=0.0,
                description="Transaction amount in USD",
            ),
            "category": ColumnContract(
                dtype="object",
                nullable=False,
                allowed_values=["electronics", "clothing", "food", "other"],
                description="Product category",
            ),
            "store_id": ColumnContract(
                dtype="int64",
                nullable=False,
                min_value=1,
                max_value=100,
                description="Store identifier",
            ),
        },
    )


@pytest.fixture
def sample_ml_df() -> pd.DataFrame:
    """Generate a synthetic ML dataset with a binary target."""
    np.random.seed(42)
    n = 500

    base_date = datetime(2025, 1, 1)
    dates = sorted([base_date + timedelta(days=int(d)) for d in np.random.randint(0, 365, n)])

    X1 = np.random.randn(n)
    X2 = np.random.randn(n)
    X3 = np.random.randn(n)
    noise = np.random.randn(n) * 0.5

    # Simple linear decision boundary
    logit = 0.5 * X1 + 0.3 * X2 - 0.2 * X3 + noise
    target = (logit > 0).astype(int)

    return pd.DataFrame(
        {
            "date": dates,
            "feature_1": np.round(X1, 4),
            "feature_2": np.round(X2, 4),
            "feature_3": np.round(X3, 4),
            "segment": np.random.choice(["A", "B", "C"], n),
            "target": target,
        }
    )
