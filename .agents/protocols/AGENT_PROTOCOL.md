# AGENT PROTOCOL
## Autonomous Data Intelligence Operating System (ADI-OS) — Phase 0 Core

---

## 1. PURPOSE & SCOPE
The **Agent Protocol** governs how specialized AI agents within ADI-OS initialize, transition state, exchange structured messages, collaborate across domain boundaries, surface disagreements, and maintain accountability.

---

## 2. AGENT DOMAIN ALLOCATION

Agents belong to one of seven core functional domains:
- **Domain A (Data Foundation):** Data Architect, Data Engineer, Database Engineer, Analytics Engineer, Streaming Engineer
- **Domain B (Analytics & BI):** Data Analyst, BI Engineer, Decision Analyst
- **Domain C (Statistics & Science):** Statistician, Experimentation Scientist, Causal Inference Agent, Forecasting Scientist, Optimization Scientist
- **Domain D (AI / Machine Learning):** Data Scientist, ML Engineer, MLOps Engineer, Model Reviewer
- **Domain E (Quality, Governance & Security):** Data Quality Engineer, Data Observability Agent, Data Governance Agent, Security Agent, Compliance Reviewer
- **Domain F (Knowledge & Research):** Research Agent, Knowledge Agent, Documentation Agent
- **Domain G (Orchestration):** Data Tech Lead / Orchestrator

---

## 3. AGENT FINITE STATE MACHINE (FSM)

Every agent lifecycle adheres to the following state transitions:

```text
[IDLE]
  │
  ▼ (Task Assigned by Orchestrator)
[ASSIGNED]
  │
  ▼ (Parse Contract, Inputs, Preconditions)
[PLANNING]
  │
  ▼ (Execute Tool Calls, Queries, Transformations, Models)
[EXECUTING] ───────────► [FAILED]
  │                        │
  │                        ▼ (Inspect Logs, Inputs, Safe Remediation)
  │                      [DIAGNOSING]
  │                        │
  │                        ├─────────► [RETRY / RECOVER] (Within Max 3 Attempts)
  │                        │                 │
  │                        │                 ▼
  │                        │           [VALIDATING]
  │                        │
  │                        ▼ (Max Retries Exceeded or Unsafe)
  │                      [BLOCKED] ──► [ESCALATED_TO_HUMAN]
  ▼
[VALIDATING] (Internal Self-Check vs Quality Gates)
  │
  ▼
[REVIEWING] (Handed to Independent Auditor Agent)
  │
  ▼
[COMPLETED] (Artifacts Persisted, Memory Updated)
```

---

## 4. STRUCTURED AGENT COMMUNICATION SCHEMA

Agents do not communicate using unstructured chatter alone. Structured state payloads are required for all inter-agent messages and handoffs:

```json
{
  "$schema": "https://data-os.internal/schemas/agent_message_v1.json",
  "task_id": "TASK-20260930-001",
  "sender_agent_id": "data_engineer",
  "recipient_agent_id": "data_quality_engineer",
  "timestamp": "2026-09-30T17:15:00Z",
  "status": "VALIDATING",
  "input_assets": [
    "urn:data_os:asset:dataset:raw_customer_transactions:v1"
  ],
  "output_assets": [
    "urn:data_os:asset:dataset:silver_customer_transactions:v1"
  ],
  "execution_summary": "Ingested raw CSVs, cast data types, partitioned by transaction_date.",
  "findings": [
    {
      "type": "OBSERVATION",
      "summary": "1,420 rows had negative transaction amounts indicating refunds/returns."
    }
  ],
  "metrics": {
    "rows_processed": 1450200,
    "rows_quarantined": 12,
    "pipeline_execution_sec": 42.1
  },
  "assumptions": [
    "Negative transactions represent legitimate refunds and should be preserved in silver layer."
  ],
  "risks": [
    {
      "severity": "P2",
      "description": "Upstream source may occasionally produce duplicate transaction_ids."
    }
  ],
  "quality_gate_status": {
    "gate_id": "GATE_1_DATA_QUALITY",
    "status": "PENDING_AUDIT"
  },
  "next_action": "PERFORM_DATA_QUALITY_AUDIT"
}
```

---

## 5. AGENT DISAGREEMENT & ADVERSARIAL REVIEW

When two agents reach divergent interpretations or conclusions from the same data:
1. **No Suppression:** Neither agent may overwrite or silence the other.
2. **Evidence Comparison:** Both agents must submit their specific claims tagged with Evidence Hierarchy levels (`[OBSERVATION]`, `[STATISTICAL_RESULT]`, `[MODEL_RESULT]`).
3. **Arbitration by Tech Lead / Orchestrator:** The Orchestrator conducts an empirical test or requires additional ablation/sensitivity analysis.
4. **Resolution Recording:** The conflict, debate, and empirical resolution are documented in `DECISION_LOG.md`.
