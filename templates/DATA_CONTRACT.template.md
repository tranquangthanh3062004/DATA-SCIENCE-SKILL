---
artifact_id: "ART-YYYYMMDD-DC-NNN"
artifact_type: "DATA_CONTRACT"
title: "Data Contract: [Dataset Name]"
version: "1.0.0"
created_at: "YYYY-MM-DDTHH:MM:SSZ"
owner_agent: "data_architect"
review_agent: "data_quality_engineer"
quality_gate_status: "PENDING"
---

# Data Contract: [Dataset Name]

## 1. Producer & Consumer

| Field | Value |
|---|---|
| **Producer System** | [Source system name] |
| **Producer Team** | [Team/owner responsible for producing data] |
| **Consumer Systems** | [List of downstream systems] |
| **Consumer Teams** | [List of downstream teams] |

---

## 2. Schema & Grain

**Grain:** [e.g., "One row per customer per day"]

| Column Name | Physical Type | Logical Type | Description |
|---|---|---|---|
| `column_1` | INT64 | identifier | Primary key |
| `column_2` | STRING | categorical | Product category |
| `column_3` | FLOAT64 | measure | Transaction amount (USD) |
| `column_4` | TIMESTAMP | temporal | Event timestamp (UTC) |

---

## 3. Primary Key & Uniqueness

| Constraint | Specification |
|---|---|
| **Primary Key** | `[column_1]` or `[column_1, column_2]` (composite) |
| **Uniqueness** | Primary key combination must be unique |
| **Null Policy** | Primary key columns must have 0% nulls |

---

## 4. Value Range & Allowed Categories

| Column | Constraint Type | Specification |
|---|---|---|
| `amount` | Range | `>= 0.0` |
| `age` | Range | `[0, 125]` |
| `category` | Enum | `['electronics', 'clothing', 'food', 'other']` |
| `status` | Enum | `['active', 'inactive', 'pending']` |
| `event_date` | Temporal | No future dates; no dates before 2020-01-01 |

---

## 5. Null Thresholds

| Column | Max Null % | Severity if Breached |
|---|---|---|
| `primary_key_col` | 0.0% | CRITICAL — Gate 1 fail |
| `required_field` | 0.0% | CRITICAL |
| `optional_field` | 5.0% | WARNING |
| `optional_field_2` | 10.0% | INFO |

---

## 6. Freshness & Latency SLA

| SLA Metric | Threshold | Alert Channel |
|---|---|---|
| **Max Staleness** | 4 hours | Slack + PagerDuty |
| **Expected Update Frequency** | Every 1 hour | Monitoring dashboard |
| **Max Ingestion Latency** | 15 minutes | Slack |

---

## 7. Quality Score Targets

| Dimension | Target | Formula |
|---|---|---|
| Completeness | >= 99% | 1 - (null_cells / total_cells) |
| Validity | >= 99% | (rows passing range + enum checks) / total_rows |
| Uniqueness | >= 99.9% | 1 - (duplicate_rows / total_rows) |
| Consistency | >= 99% | Cross-source match rate |
| Freshness | <= SLA | hours since last update |

---

## 8. Breach Action Protocol

| Breach Type | Severity | Automated Action |
|---|---|---|
| Schema drift | P1 | HALT pipeline, alert Data Architect |
| PK null/duplicate | P0 | HALT pipeline, quarantine rows |
| Null threshold exceeded | P1 | Quarantine rows, alert owner |
| Range violation | P1 | Quarantine rows, log incident |
| Freshness SLA breach | P1 | Trigger re-ingestion, alert |

---

## 9. Sign-Off

| Role | Name | Date | Status |
|---|---|---|---|
| Data Architect | | | ☐ APPROVED |
| Data Quality Engineer | | | ☐ APPROVED |
| Consumer Lead | | | ☐ APPROVED |
