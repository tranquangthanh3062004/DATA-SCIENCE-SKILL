# TASK PROTOCOL
## Autonomous Data Intelligence Operating System (ADI-OS) — Phase 0 Core

---

## 1. PURPOSE & SCOPE
The **Task Protocol** defines how user requests are ingested, classified, decomposed into dependency graphs (DAGs), executed across specialized agents, validated against quality gates, and verified against the Definition of Done.

---

## 2. TASK CLASSIFICATION TAXONOMY

Every incoming task must be tagged with one or more canonical task classes:
- `DATA_DISCOVERY` — Cataloging, profiling, schema inference, lineage mapping.
- `DATA_ENGINEERING` — Ingestion, ELT/ETL, transformation, partitioning, pipeline design.
- `DATA_ARCHITECTURE` — Lakehouse/warehouse design, data contract formulation.
- `DATA_ANALYTICS` — EDA, KPI exploration, cohort segmentation, trend analysis.
- `BUSINESS_INTELLIGENCE` — Dashboard design, semantic layer definitions, visual marts.
- `STATISTICAL_ANALYSIS` — Hypothesis tests, confidence bounds, power calculations.
- `EXPERIMENTATION` — A/B test design, randomization, sample size estimation.
- `CAUSAL_INFERENCE` — Quasi-experiments, propensity matching, instrumental variables.
- `MACHINE_LEARNING` — Supervised/unsupervised modeling, feature engineering, baselines.
- `FORECASTING` — Time-series decomposition, backtesting, prediction intervals.
- `ANOMALY_DETECTION` — Distribution outlier identification, drift detection.
- `OPTIMIZATION` — Constraint programming, LP/MIP, simulation optimization.
- `ML_PRODUCTION` — Model serving, packaging, inference optimization, CI/CD.
- `DATA_QUALITY` — Profiling, test suite execution, anomaly flagging.
- `DATA_GOVERNANCE` — Access control verification, classification, data contracts.
- `DATA_SECURITY` — PII scrubbing, credential protection, query sanitization.
- `RESEARCH` — Literature review, algorithmic benchmarking.
- `DECISION_INTELLIGENCE` — Multi-criteria evaluation, trade-off analysis, simulation.
- `INCIDENT_RESPONSE` — Failure diagnosis, safe recovery, postmortem generation.

---

## 3. AUTONOMOUS TASK DECOMPOSITION PIPELINE

When an ambiguous or high-level request is received, the Orchestrator executes this decomposition before calling domain agents:

```text
[AMBIGUOUS USER REQUEST]
           │
           ▼
1. GOAL & SUCCESS CRITERIA        — What business or technical outcome defines success?
           │
           ▼
2. BUSINESS QUESTION FORMULATION  — Formalize into falsifiable or measurable questions.
           │
           ▼
3. DATA REQUIREMENTS SPECIFICATION— What entities, granularities, and horizons are required?
           │
           ▼
4. DATA SOURCE IDENTIFICATION     — Locate raw files, warehouse tables, APIs, or streams.
           │
           ▼
5. DATA QUALITY PRE-ASSESSMENT    — Identify known missingness, skew, or contract gaps.
           │
           ▼
6. ANALYTICAL / SCIENTIFIC METHOD — Select statistical test, baseline model, or metric logic.
           │
           ▼
7. MODEL / PIPELINE REQUIREMENTS  — Establish performance, latency, and operational bounds.
           │
           ▼
8. VALIDATION & QUALITY GATES     — Define which of Gates 1-7 apply and their passing criteria.
           │
           ▼
9. DELIVERABLE SPECIFICATION      — List durable markdown artifacts and code components.
```

---

## 4. TASK DEPENDENCY GRAPH (DAG) EXECUTION

Tasks are organized as directed acyclic graphs where downstream tasks execute only upon successful completion and validation of parent tasks.

### Example: Predictive Modeling DAG
```text
Task 1: Ingestion & Schema Profiling (Data Engineer)
   │
   ▼
Task 2: Data Quality Audit & Leakage Check (Data Quality Engineer) [GATE 1]
   │
   ├──► Task 3A: Exploratory Data Analysis (Data Analyst) [GATE 2]
   │       │
   │       ▼
   │    Task 4A: Statistical Driver Analysis (Statistician)
   │
   └──► Task 3B: Feature Engineering & Baseline Model (Data Scientist)
           │
           ▼
        Task 4B: Model Comparison & Tuning (Data Scientist)
           │
           ▼
        Task 5: Independent Model Review & Error Analysis (Model Reviewer) [GATE 3]
           │
           ▼
        Task 6: Pipeline Packaging & Serving Spec (ML Engineer) [GATE 4]
           │
           ▼
        Task 7: Business Impact & Trade-Off Synthesis (Business Reviewer) [GATE 6]
           │
           ▼
        Task 8: Final Artifact Delivery & Documentation (Documentation Agent) [GATE 7]
```

---

## 5. DEFINITION OF DONE (DoD)

No task may be marked `COMPLETED` until all checklist criteria are satisfied:
- [x] **Objective Understood:** Explicit scope, questions, and success metrics recorded.
- [x] **Data Inspected:** Schema, row/column counts, and grain verified against source.
- [x] **Data Quality Validated:** Quality gate 1 evaluated and signed off.
- [x] **Data Contract Defined / Verified:** Primary keys, null rules, and types documented.
- [x] **Method Documented:** Mathematical, statistical, or algorithmic formulation stated.
- [x] **Baseline Model Evaluated:** Simple heuristic or baseline verified before complex models.
- [x] **Leakage Checked:** Temporal and feature leakage explicitly verified as absent.
- [x] **Tests Executed:** Code executed and verified deterministically with test assertions.
- [x] **Independent Review Completed:** Dedicated reviewer agent performed audit.
- [x] **Risks & Limitations Recorded:** Unmodeled factors and boundary conditions listed.
- [x] **Artifacts Generated:** Durable markdown files persisted in repository.
- [x] **Reproducibility Verified:** Random seeds, dependencies, and code versions captured.
- [x] **Final Response Formatted:** Complete 16-point executive synthesis delivered.
