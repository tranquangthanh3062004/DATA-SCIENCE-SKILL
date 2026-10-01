# 🚀 ADI-OS — New Data Engineer Onboarding Guide

Welcome to the Autonomous Data Intelligence Operating System (ADI-OS) team!
This guide will get you up and running quickly.

---

## 📋 Day 1 Checklist

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-org/data-science-skill.git
cd data-science-skill

# Install uv (Python package manager)
pip install uv

# Install all dependencies
uv sync --all-extras

# Copy environment config
cp .env.example .env
# Edit .env with your local settings

# Start local infrastructure
docker compose up -d

# Verify everything works
make test
```

### 2. Verify Local Stack
After `docker compose up -d`, verify:
- **PostgreSQL**: `localhost:5432` (user: `adi_user`, db: `adi_os`)
- **Jupyter**: `http://localhost:8888` (token: `adi-os-dev`)
- **MLflow**: `http://localhost:5000`
- **Grafana**: `http://localhost:3000` (admin/admin)

### 3. Key Commands
```bash
make help           # See all available commands
make test           # Run all tests
make lint           # Check code quality
make format         # Auto-format code
make quality-check  # Run data quality gates
make serve          # Start model serving API
```

---

## 🏛️ Architecture Overview

ADI-OS operates across 6 architectural planes:

```
Experience → Intelligence → Agent → Data Foundation → Control → Observability
```

Data flows through the **Medallion Architecture**:
```
RAW → BRONZE → SILVER → GOLD → METRIC → DASHBOARD/MODEL → DECISION
```

---

## 📚 Must-Read Documents

Read these in order during your first week:

| Priority | Document | What You'll Learn |
|---|---|---|
| 1 | `README.md` | System overview, architecture, quality gates |
| 2 | `.agents/skills/autonomous-data-org/SKILL.md` | Full system specification, 26 roles |
| 3 | `.agents/protocols/QUALITY_GATE.md` | The 7 mandatory quality gates |
| 4 | `.agents/protocols/TASK_PROTOCOL.md` | How tasks are decomposed and executed |
| 5 | `.agents/rules/data-org-rules.md` | Core behavioral rules & maxims |
| 6 | `.agents/protocols/PERMISSION_POLICY.md` | What you can/can't do autonomously |

---

## 🔑 Core Principles (Memorize These)

1. **DATA BEFORE CONCLUSION** — Always inspect data first
2. **EVIDENCE BEFORE CLAIM** — Tag every claim with evidence level
3. **BASELINE BEFORE OPTIMIZATION** — Simple model first, always
4. **VALIDATION BEFORE DELIVERY** — Quality gates are non-negotiable
5. **CORRECTNESS BEFORE SPEED** — Take time to be right

---

## 📁 Project Structure

```
DATA-SCIENCE-SKILL/
├── src/                    # Core Python code
│   ├── pipelines/          # ETL/ELT pipeline framework
│   ├── analytics/          # Analysis and metric engines
│   ├── ml/                 # ML experiment framework
│   ├── quality/            # Data quality validators
│   └── utils/              # Config, logging, secrets
├── dbt_project/            # Analytics engineering (SQL)
├── tests/                  # Test suites (unit, ML, quality)
├── configs/                # Environment & metric configs
├── contracts/              # Data contracts & schemas
├── templates/              # Artifact templates
├── governance/             # Data governance rules
├── monitoring/             # Dashboards & alert rules
├── infrastructure/         # Docker, Terraform, K8s
└── .agents/                # AI agent specifications
```

---

## 🧪 Running Your First Data Quality Check

```python
import pandas as pd
from src.quality.validators import DataQualityValidator, DataContract, ColumnContract

# Load your data
df = pd.read_csv("data.csv")

# Define a contract
contract = DataContract(
    name="my_dataset",
    description="Sample dataset",
    owner="your_name",
    primary_keys=["id"],
    columns={
        "id": ColumnContract(dtype="int64", nullable=False, is_primary_key=True),
        "value": ColumnContract(dtype="float64", min_value=0.0, max_value=1000.0),
    },
)

# Run Gate 1
validator = DataQualityValidator(df, contract)
report = validator.run_gate_1()
print(f"Gate 1: {report.gate_status.value}")
print(report.to_markdown())
```

---

## 🤖 Running Your First ML Experiment

```python
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from src.ml.experiment import Experiment, ExperimentConfig, SplitStrategy, TaskType

config = ExperimentConfig(
    name="my_first_experiment",
    target="label",
    task_type=TaskType.CLASSIFICATION,
    split_strategy=SplitStrategy.TEMPORAL,
    temporal_column="date",
    subgroup_columns=["segment"],
)

experiment = Experiment(config)

# Gate 3 requires a baseline FIRST
experiment.add_baseline("majority_class", DummyClassifier(strategy="most_frequent"))
experiment.add_model("logistic", LogisticRegression())

report = experiment.run(df)
print(f"Gate 3: {report.gate_3_status}")
print(report.to_markdown())
```

---

## ❓ FAQs

**Q: Can I skip quality gates in development?**
A: Gate 6 (Independent Review) is disabled in dev. All other gates are always active.

**Q: Where do I put new data sources?**
A: Add to `configs/data_sources.yml` and create a matching Data Contract in `contracts/`.

**Q: How do I add a new metric?**
A: Add it to `configs/metric_registry.yml` with a canonical formula, grain, and owner.

**Q: What if my pipeline fails?**
A: Check logs, create an `INCIDENT_REPORT.md` from the template, and follow the self-healing protocol.

---

*Last updated: 2026-10-01*
