# ARTIFACT PROTOCOL
## Autonomous Data Intelligence Operating System (ADI-OS) — Phase 0 Core

---

## 1. PURPOSE & PRINCIPLE
The **Artifact Protocol** enforces the system's **Artifact-First Policy**:
> Chat output is ephemeral. High-value data engineering, analytical, and machine-learning intelligence must be captured in durable, versionable, and reproducible markdown artifacts persisted directly in the repository.

---

## 2. REPOSITORY ARTIFACT DIRECTORY STRUCTURE

Project deliverables adhere to standard locations:

```text
project_root/
├── README.md                     # High-level system & repository guide
├── PROJECT_BRIEF.md              # Scope, objectives, stakeholders, constraints
├── DATA_CATALOG.md               # Registry of all data assets, schemas, origins
├── DATA_DICTIONARY.md            # Column-level definitions, datatypes, valid ranges
├── DATA_CONTRACT.md              # Formal producer-consumer schema and SLA contract
├── DATA_QUALITY_REPORT.md        # Profiling stats, null rates, validation pass/fail
├── DATA_LINEAGE.md               # Upstream to downstream transformation graph
├── METRIC_DEFINITIONS.md         # Canonical mathematical formulas and metric registry
├── ANALYSIS_PLAN.md              # Hypotheses, analytical methodologies, validation strategy
├── ANALYSIS_REPORT.md            # Detailed EDA, segmentations, and business findings
├── STATISTICAL_REPORT.md         # Statistical hypothesis tests, power, and significance
├── EXPERIMENT_REPORT.md          # A/B or causal experimentation design and results
├── MODEL_CARD.md                 # ML architecture, training data, metrics, intended use
├── MODEL_EVALUATION.md           # Benchmark comparisons, error analysis, calibration
├── ARCHITECTURE.md               # Infrastructure, medallion layers, pipeline blueprints
├── DECISION_LOG.md               # Chronological architectural and analytical ADRs
├── RISKS.md                      # Operational, data quality, security, and modeling risks
├── ASSUMPTIONS.md                # Explicit assumptions required for execution
├── INCIDENT_REPORT.md            # Postmortem analysis for pipeline or model failures
└── FINAL_REPORT.md               # Comprehensive executive synthesis (16-point standard)
```

---

## 3. MANDATORY ARTIFACT HEADER SCHEMA

Every generated artifact must begin with standard YAML frontmatter for traceability:

```yaml
---
artifact_id: "ART-20260930-DQ-001"
artifact_type: "DATA_QUALITY_REPORT"
title: "Data Quality & Profiling Audit: Customer Transactions"
version: "1.0.0"
created_at: "2026-09-30T17:15:00Z"
owner_agent: "data_quality_engineer"
review_agent: "model_reviewer"
data_assets_evaluated:
  - "urn:data_os:asset:dataset:raw_customer_transactions:v1"
quality_gate_status: "PASSED"
reproducibility:
  seed: 42
  environment_hash: "env-prod-2026a"
  code_reference: "src/transformation/clean_transactions.py"
---
```

---

## 4. CORE ARTIFACT TEMPLATE STANDARDS

### A. DATA_CONTRACT.md
Must define:
1. **Producer & Consumer:** Systems and owning teams.
2. **Schema & Grain:** Exact column names, physical types, and row grain.
3. **Primary Key & Uniqueness:** Non-null primary key specification.
4. **Value Range & Allowed Categories:** Invariants and enum values.
5. **Freshness & Latency SLA:** Expected update frequency and alert threshold.
6. **Breach Action:** Automated quarantine or alert protocol.

### B. DATA_QUALITY_REPORT.md
Must define:
1. **Summary Table:** Total rows, column count, duplicate rows, missing cell percentage.
2. **Column Profiling:** Distribution stats (mean, median, IQR, min, max, null count, distinct count).
3. **Integrity Rule Results:** Pass/Fail evaluation for each rule.
4. **Temporal Integrity:** Date range coverage, sequence gaps, future leakage verification.
5. **Quality Scorecard:** Dimension scores (Completeness, Validity, Uniqueness, Consistency, Freshness).

### C. MODEL_CARD.md
Must define:
1. **Model Details:** Architecture, algorithm, hyperparameter configuration, framework version.
2. **Intended Use & Non-Goals:** Target domain, expected inputs, explicit out-of-scope usages.
3. **Training Data & Split Strategy:** Data version, temporal/stratified split parameters.
4. **Baseline Performance:** Naive/heuristic model metrics vs candidate model metrics.
5. **Evaluation Metrics:** Classification (ROC-AUC, PR-AUC, F1, Log Loss) or Regression (MAE, RMSE, R²).
6. **Subgroup & Error Analysis:** Performance broken down across demographic/temporal cohorts.
7. **Ethical, Fairness & Operational Considerations:** Known biases, drift risks, monitoring plan.

### D. DECISION_LOG.md (Architecture Decision Record - ADR)
Must record:
- **Decision ID & Title**
- **Context & Problem Statement**
- **Decision Drivers & Constraints**
- **Options Considered (Pros & Cons)**
- **Chosen Option & Justification**
- **Consequences (Positive, Negative, Neutral)**
- **Reviewer Sign-off**
