# Autonomous Data Intelligence Operating System — Routing & Workflow Rules

## 1. Autonomous Dynamic Routing Cases

The Orchestrator determines the minimum sufficient agent team for each task type:

### Case 1: Exploratory & Business Analytics
`Goal: Understand trends, performance, correlations, or driver analysis.`
```text
Orchestrator → Data Quality Engineer → Data Analyst → Statistician → Business Reviewer → Documentation Agent
```

### Case 2: Machine Learning & Predictive Modeling
`Goal: Supervised or unsupervised learning, ranking, or recommendation.`
```text
Orchestrator → Data Engineer → Data Quality Engineer → Data Analyst → Statistician → Data Scientist → ML Engineer → Model Reviewer → Business Reviewer → Documentation Agent
```

### Case 3: Data Foundation, Lakehouse & Pipeline Engineering
`Goal: Schema design, ETL/ELT pipelines, ingestion, and metric layer building.`
```text
Orchestrator → Data Architect → Data Engineer → Analytics Engineer → Data Quality Engineer → Security Agent → Architecture Reviewer → Documentation Agent
```

### Case 4: Diagnostic & Root Cause Analysis (e.g., Revenue Decline)
`Goal: Investigate metric anomalies and breakdown factors.`
```text
Orchestrator → Analytics Engineer (Metric Validation) → Data Analyst (Slicing/Segmentation) → Statistician (Significance of Change) → Causal Inference Agent → Business Reviewer → Documentation Agent
```

### Case 5: Time-Series Forecasting & Demand Planning
`Goal: Multi-horizon forecasting with uncertainty bounds.`
```text
Orchestrator → Data Engineer → Data Quality Engineer → Forecasting Scientist → Model Reviewer → Business Reviewer → Documentation Agent
```

### Case 6: Operational Pipeline Failure / Self-Healing
`Goal: Fix broken ETL or batch processing job.`
```text
Orchestrator → Data Observability Agent → Data Engineer → Data Quality Engineer → Security Agent → Documentation Agent
```

### Case 7: Model Drift & Retraining
`Goal: Address model performance degradation.`
```text
Orchestrator → Data Observability Agent → Data Scientist → ML Engineer → Model Reviewer → Documentation Agent
```

---

## 2. Standard Quality Gates (Mandatory Verification)

| Gate | Focus | Mandatory Checks |
|---|---|---|
| **Gate 1: Data Quality** | Data Foundation | Schema validation, null counts, duplicate detection, range checks, temporal ordering, zero future leakage |
| **Gate 2: Analytical Rigor** | Analytics & BI | Canonical metric registry validation, distributional assumptions verified, confounding analyzed |
| **Gate 3: Model & Science** | AI/ML & Stats | Baseline established, train/val/test split isolated, metric alignment with loss, error analysis across cohorts, independent review passed |
| **Gate 4: Engineering** | Reliability | Idempotency verified, unit/data tests passed, logging instrumented, recovery/retry logic configured |
| **Gate 5: Governance & Security** | Compliance | Secrets & PII masked, least privilege verified, asset classification tagged, data contract verified |
| **Gate 6: Independent Review** | Multi-Agent Audit | Technical reviewer + business reviewer adversarial verification. No self-approval. |
| **Gate 7: Delivery** | Reproducibility | Versioned artifacts generated, code reproducible from clean environment, limitations explicitly stated |

---

## 3. Severity Matrix & Incident Levels

| Severity | Definition | Autonomous Action | Escalation |
|---|---|---|---|
| **P0 — Critical** | Data corruption, active security vulnerability, severe target leakage in production | **HALT IMMEDIATELY**. Rollback to last known good checkpoint. | Immediate human notification. |
| **P1 — High** | Invalid model validation split, broken pipeline run, major data contract breach | Pause downstream jobs. Diagnose root cause and attempt safe recovery in staging. | Notify if automated recovery fails. |
| **P2 — Medium** | Suboptimal model performance, pipeline latency degradation, minor drift | Flag metric in Observability plane, queue optimization ticket. | Autonomous remediation. |
| **P3 — Low** | Documentation gap, cosmetic dashboard defect, non-blocking warning | Log in documentation backlog. | Autonomous remediation. |
| **P4 — Enhancement** | Architectural refactoring, feature engineering ideas, performance tuning | Record in organizational memory backlog. | None. |

---

## 4. Final Answer Standard (16-Point Deliverable)

For every significant deliverable, structure the final delivery as follows:
```text
1. EXECUTIVE SUMMARY          — Concise, high-level summary of problem, methodology, and outcome
2. OBJECTIVE                  — Specific business and technical goals addressed
3. DATA SOURCES               — Origins, schema, grain, time period, and volume of data used
4. DATA QUALITY & LIMITATIONS — Data profiling metrics, null rates, known anomalies, and constraints
5. APPROACH                   — End-to-end architectural workflow and agent allocation
6. METHODS                    — Analytical, statistical, or mathematical formulations applied
7. KEY FINDINGS               — Findings classified with evidence tags ([FACT], [STATISTICAL_RESULT], etc.)
8. STATISTICAL / MODEL RESULTS— Comprehensive metrics, baselines, confidence intervals, error segments
9. VALIDATION & GATE CHECKS   — Status of Gates 1 through 7
10. RISKS & FAILURE MODES     — Operational, technical, and data risks identified
11. LIMITATIONS               — Assumptions, unmodeled variables, and non-generalizable aspects
12. BUSINESS IMPLICATIONS     — Actionable translation of technical results into decision alternatives
13. NEXT ACTIONS              — High-priority recommended next steps
14. ARTIFACTS CREATED         — Complete file links to created reports, code, schemas, and contracts
15. OBSERVABILITY & MONITORING— Metrics to track over time and drift detection parameters
16. FINAL OPERATIONAL STATUS  — PASSED, BLOCKED, or ESCALATED
```
