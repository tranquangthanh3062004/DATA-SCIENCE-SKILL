# PERMISSION POLICY
## Autonomous Data Intelligence Operating System (ADI-OS) — Phase 0 Core

---

## 1. PURPOSE & PRINCIPLE
The **Permission Policy** defines the boundaries of autonomous agent operation.
> Autonomy exists within strict safety boundaries. Agents possess full autonomy for non-destructive discovery, analysis, experimentation, and staging validation, but must request explicit human approval before executing high-impact, privileged, or irreversible actions.

---

## 2. ACTION CLASSIFICATION MATRIX

All actions performed by agents are categorized into four operational tiers:

```text
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│     AUTO     │     │    REVIEW    │     │   APPROVAL   │     │   BLOCKED    │
│ Fully        │ ──► │ Automated +  │ ──► │ Requires     │ ──► │ Strictly     │
│ Autonomous   │     │ Notification │     │ Explicit     │     │ Prohibited   │
│ Safe Actions │     │ to User      │     │ Human Signoff│     │ Under Any OS │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

| Tier | Description | Typical Operations |
|---|---|---|
| **AUTO** | Read-only, safe computation, local testing, artifact writing | File reads, data profiling, EDA, running local Python calculations, drafting markdown artifacts, training models in sandbox, executing unit tests |
| **REVIEW** | Non-destructive system mutations that alter configuration or state | Registering a candidate model in model registry, publishing a draft data contract, updating an analytics playbook, creating a new feature view |
| **APPROVAL** | High-impact, costly, or externally visible actions | Deploying model to live production endpoint, executing database DDL/schema migrations, modifying production tables, spending cloud compute budget, external API publishing |
| **BLOCKED** | Irreversible, destructive, or high-risk actions | Deleting production data/backups, committing plaintext secrets or passwords, bypassing quality gates, modifying security permissions without authorization |

---

## 3. DETAILED ACTION AUTHORIZATION TABLE

| Action | Tier | Responsible Agent | Verification Required |
|---|---|---|---|
| Inspect dataset / read files | **AUTO** | Any agent | Least privilege path check |
| Execute exploratory data analysis | **AUTO** | Data Analyst | Sandbox compute boundary |
| Train baseline & candidate ML models | **AUTO** | Data Scientist | Resource and memory limits |
| Generate and update documentation artifacts | **AUTO** | Documentation Agent | Version control tracking |
| Run unit & integration tests | **AUTO** | Senior Data Engineer | Isolated test environment |
| Quarantine corrupt rows | **AUTO** | Data Quality Engineer | Non-destructive append to quarantine |
| Register candidate model version | **REVIEW** | MLOps Engineer | Model Card & Gate 3 passing report |
| Update canonical metric definition | **REVIEW** | Analytics Engineer | Impact analysis on existing reports |
| Update organizational playbook | **REVIEW** | Knowledge Agent | Backed by validated postmortem |
| Apply schema migration (DDL) | **APPROVAL** | Database Engineer | Backward compatibility verification |
| Deploy model to production serving | **APPROVAL** | ML Engineer | Model Reviewer sign-off & rollback plan |
| Overwrite / drop database table | **APPROVAL** | Data Architect | Backup verification & lineage check |
| Transmit data to external 3rd-party API | **APPROVAL** | Security Agent | Compliance and PII audit |
| Hard delete production data | **BLOCKED** | N/A | Strictly prohibited autonomously |
| Log raw passwords / secrets | **BLOCKED** | N/A | Strictly prohibited autonomously |

---

## 4. HUMAN-IN-THE-LOOP (HITL) ESCALATION PROTOCOL

When an action requiring `APPROVAL` is encountered:
1. **Execution Freeze:** The agent immediately pauses downstream execution on that branch.
2. **Escalation Dossier Generation:** The agent prepares an escalation proposal containing:
   - Specific action requested and target resource.
   - Justification and business/technical driver.
   - Alternatives considered and trade-off analysis.
   - Rollback / failure recovery plan.
   - Impact assessment (lineage dependencies).
3. **User Prompt:** The system presents the dossier to the human operator and waits for explicit authorization.
4. **Resumption / Abort:** If approved, execution proceeds and the approval token is logged in `DECISION_LOG.md`. If rejected, the agent attempts an alternative safe path or records `OPERATION_REJECTED`.

---

## 5. TOOL EXECUTION AUDIT LOGGING

Every tool call executed by an agent records an audit record in the project observability trail:
```json
{
  "timestamp": "2026-09-30T17:15:30Z",
  "task_id": "TASK-20260930-001",
  "agent_id": "data_engineer",
  "tool_name": "run_command",
  "action_tier": "AUTO",
  "parameters": {
    "command": "python -m pytest tests/test_ingestion.py"
  },
  "execution_result": "SUCCESS",
  "exit_code": 0
}
```
Any attempt to execute an unauthorized tool or access restricted assets generates an immediate P0 security event.
