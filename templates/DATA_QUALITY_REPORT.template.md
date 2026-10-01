---
artifact_id: "ART-YYYYMMDD-DQ-NNN"
artifact_type: "DATA_QUALITY_REPORT"
title: "Data Quality Report: [Dataset Name]"
version: "1.0.0"
created_at: "YYYY-MM-DDTHH:MM:SSZ"
owner_agent: "data_quality_engineer"
review_agent: "model_reviewer"
quality_gate_status: "PENDING"
---

# Data Quality Report: [Dataset Name]

## 1. Summary

| Metric | Value |
|---|---|
| **Total Rows** | |
| **Total Columns** | |
| **Duplicate Rows** | |
| **Missing Cell %** | |
| **Memory Usage** | |
| **Data Period** | YYYY-MM-DD to YYYY-MM-DD |

---

## 2. Quality Scorecard

| Dimension | Score | Threshold | Status |
|---|---|---|---|
| **Completeness** | % | >= 99% | ☐ PASS / ☐ FAIL |
| **Validity** | % | >= 99% | ☐ PASS / ☐ FAIL |
| **Uniqueness** | % | >= 99.9% | ☐ PASS / ☐ FAIL |
| **Consistency** | % | >= 99% | ☐ PASS / ☐ FAIL |
| **Freshness** | hours | <= SLA | ☐ PASS / ☐ FAIL |
| **Overall** | % | >= 95% | ☐ PASS / ☐ FAIL |

---

## 3. Column Profiling

| Column | Type | Non-Null | Null% | Distinct | Mean | Std | Min | Q25 | Median | Q75 | Max |
|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | |

---

## 4. Gate 1 Integrity Rule Results

| Rule | Category | Status | Severity | Details |
|---|---|---|---|---|
| Schema: Column Presence | Schema Invariants | | CRITICAL | |
| Schema: Data Types | Schema Invariants | | CRITICAL | |
| PK: Uniqueness | Primary Key | | CRITICAL | |
| PK: No Nulls | Primary Key | | CRITICAL | |
| Null Thresholds | Completeness | | CRITICAL | |
| Range Invariants | Validity | | CRITICAL | |
| Temporal: No Future Dates | Temporal | | CRITICAL | |
| Temporal: Sequence Gaps | Temporal | | WARNING | |

---

## 5. Temporal Integrity

| Check | Result |
|---|---|
| **Date Range** | [earliest] to [latest] |
| **Future Dates** | 0 found ✅ |
| **Sequence Gaps** | [number] gaps detected |
| **Date Coverage** | [X/Y days covered] |

---

## 6. Anomalies Detected

| Column | Anomaly Type | Count | Details |
|---|---|---|---|
| | Outlier | | |
| | Unexpected Nulls | | |
| | Invalid Values | | |

---

## 7. Gate 1 Verdict

**Overall Status:** ☐ `PASSED` / ☐ `FAILED`

**Critical Failures:** [Count]
**Warnings:** [Count]

### Quarantine Actions
- Rows quarantined: [count]
- Quarantine location: `data/quarantine/[dataset]/`
- Reason: [description]

---

## 8. Recommendations

1. [Recommendation based on findings]
2. [Data contract update needed]
3. [Pipeline fix required]
