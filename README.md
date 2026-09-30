# Autonomous Data Intelligence Operating System (ADI-OS)
> **Level-4 Enterprise-Grade Multi-Agent Operating System for Data Engineering, Analytics Engineering, Data Science, AI/ML, and Decision Intelligence.**

[![Architecture: 6 Planes](https://img.shields.io/badge/Architecture-6%20Planes-blue.svg)](#-system-architecture)
[![Agent Domains: 7](https://img.shields.io/badge/Agent%20Domains-7%20Domains%20%7C%2026%20Roles-emerald.svg)](#-agent-domains--specialized-roles)
[![Quality Gates: 7](https://img.shields.io/badge/Quality%20Gates-Gates%201--7%20Active-brightgreen.svg)](#-the-7-mandatory-quality-gates)
[![Evidence Policy](https://img.shields.io/badge/Evidence%20Policy-Strict%20No--Fabrication-crimson.svg)](#-evidence-tagging--zero-fabrication-policy)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](#-license)

---

## 📖 Overview

The **Autonomous Data Intelligence Operating System (ADI-OS)** is an integrated organization of specialized AI agents, deterministic workflows, quality gates, governance mechanisms, and decision-intelligence capabilities. It operates to the engineering rigor of a principal-level data & AI team.

Instead of operating as an unconstrained single chatbot, ADI-OS enforces a strict lifecycle:
```text
QUESTION → EVIDENCE → DATA → QUALITY (GATE 1) → ENGINEERING → ANALYTICS 
  → SCIENCE → MODEL → REVIEW (GATES 2–6) → DECISION → DELIVERY (GATE 7)
```

---

## 🏛️ System Architecture: 6 Major Planes

```text
┌───────────────────────────────────────────────────────────┐
│                     EXPERIENCE PLANE                      │
│ User / Business / Decisions / Dashboards / Reports / APIs │
└─────────────────────────────┬─────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────┐
│                    INTELLIGENCE PLANE                     │
│ Analytics / BI / ML / Forecasting / Optimization / Causal │
│         Experimentation / Decision Intelligence           │
└─────────────────────────────┬─────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────┐
│                       AGENT PLANE                         │
│    Orchestrator + Specialized Domain Agent Collectives    │
└─────────────────────────────┬─────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────┐
│                     DATA FOUNDATION                       │
│    Ingestion / Storage / Bronze-Silver-Gold / Serving     │
└─────────────────────────────┬─────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────┐
│                      CONTROL PLANE                        │
│ Metadata / Catalog / Contracts / Lineage / Quality Gates  │
│ Policies / Permissions / State / Memory / Audit Logging   │
└─────────────────────────────┬─────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────┐
│               OBSERVABILITY & LEARNING PLANE              │
│ Monitoring / Drift / Evaluation / Incidents / Playbooks   │
│           Self-Healing / Continuous Learning              │
└───────────────────────────────────────────────────────────┘
```

---

## 👥 Agent Domains & Specialized Roles

ADI-OS organizes 26 specialized roles across 7 functional domains:

| Domain | Roles | Key Responsibilities |
|---|---|---|
| **Domain A: Data Foundation** | Data Architect, Senior Data Engineer, Database Engineer, Analytics Engineer, Streaming Engineer | Lakehouse architecture, ETL/ELT pipelines, streaming, dbt/semantic models, physical indexing |
| **Domain B: Analytics & BI** | Senior Data Analyst, BI Engineer, Decision Analyst | Exploratory analysis (EDA), KPI metric tracking, segmentation, cohorts, dashboard systems |
| **Domain C: Statistics & Science** | Statistician, Experimentation Scientist, Causal Inference Agent, Forecasting Scientist, Optimization Scientist | Hypothesis tests, A/B experiments, Do-calculus/causal DAGs, multi-horizon forecasting, linear/integer programming |
| **Domain D: AI & Machine Learning** | Senior Data Scientist, ML Engineer, MLOps Engineer, Model Reviewer | Target formulation, feature engineering, baselines, model serving, CI/CD, adversarial validation |
| **Domain E: Quality, Governance & Security** | Data Quality Engineer, Data Observability Agent, Data Governance Agent, Security Agent, Compliance Reviewer | Automated data profiling, schema drift, PII scrubbing, access control, audit trail |
| **Domain F: Knowledge & Research** | Research Agent, Knowledge Agent, Documentation Agent | SOTA method synthesis, playbooks, artifact management, data dictionaries |
| **Domain G: Orchestration** | Data Tech Lead / Orchestrator | Problem decomposition, DAG routing, quality gate enforcement, consensus arbitration |

---

## ⚡ The 11 Absolute Maxims

1. **DATA BEFORE CONCLUSION** — Never hypothesize or conclude before examining source data.
2. **EVIDENCE BEFORE CLAIM** — Every assertion must carry an evidence classification tag.
3. **VALIDATION BEFORE DELIVERY** — No output is delivered without passing quality gates.
4. **BASELINE BEFORE OPTIMIZATION** — Always establish a naive or simple baseline prior to complex modeling.
5. **TEST BEFORE DEPLOYMENT** — Code and pipelines must be tested; execution does not imply correctness.
6. **REVIEW BEFORE PRODUCTION** — Independent review by a dedicated reviewer agent is mandatory.
7. **PERMISSION BEFORE PRIVILEGED ACTION** — High-impact, destructive, or external operations require approval.
8. **REPRODUCIBILITY BEFORE TRUST** — Determinism, seeds, environment specs, and data versions must be captured.
9. **SECURITY BEFORE AUTONOMY** — Sensitive data, PII, credentials, and least privilege override convenience.
10. **QUALITY BEFORE SCALE** — Clean, verified small-scale data precedes large-scale distributed runs.
11. **CORRECTNESS BEFORE SPEED** — Thoroughness and rigor always supersede premature task completion.

---

## 🚦 The 7 Mandatory Quality Gates

```text
  [SOURCE DATA]
        │
        ▼
┌───────────────────────┐
│ GATE 1: DATA QUALITY  │  Schema invariants, 0% null keys, range checks, zero future leakage
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ GATE 2: ANALYTICS     │  Canonical metric registry alignment, distribution assumption tests
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ GATE 3: MODEL/SCIENCE │  Baseline model benchmarked, leak-free temporal split, error analysis
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ GATE 4: ENGINEERING   │  Pipeline idempotency, deterministic test assertions, observable logging
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ GATE 5: GOVERNANCE    │  Zero hardcoded credentials, PII masked, asset classification tagged
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ GATE 6: INDEPENDENT   │  Adversarial review by dedicated reviewer agent (No self-approval)
│         REVIEW        │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ GATE 7: DELIVERY      │  Durable artifacts created, seeds & versions pinned, 16-point standard
└───────────┬───────────┘
            │
            ▼
   [PRODUCTION / USER]
```

---

## 🏷️ Evidence Tagging & Zero-Fabrication Policy

Every substantive statement in ADI-OS deliverables must be categorized:
- `[FACT]` — Supported by raw source data or official documentation.
- `[OBSERVATION]` — Directly inspected in raw tables, logs, or profiles.
- `[MEASURED_RESULT]` — Directly computed output from deterministic code.
- `[STATISTICAL_RESULT]` — Backed by hypothesis tests, confidence bounds, or power calculations.
- `[MODEL_RESULT]` — Generated by a trained, validated, and reviewed algorithm.
- `[EXPERIMENTAL_RESULT]` — Produced by randomized controlled trials or A/B experiments.
- `[ASSUMPTION]` — Explicit operational assumption required to proceed.
- `[HYPOTHESIS]` — Unverified proposition awaiting empirical testing.
- `[INTERPRETATION]` — Reasoned inference derived from verified evidence.
- `[RECOMMENDATION]` — Actionable proposal evaluated against trade-offs and operational risks.

*Prohibition:* Never present assumptions as facts, correlation as causation, estimates as measurements, or unvalidated model predictions as absolute truth.

---

## 📂 Repository Structure & Phase 0 Protocols

```text
DATA-SCIENCE-SKILL/
├── README.md                                  # Repository overview and master specification
└── .agents/
    ├── skills/
    │   └── autonomous-data-org/
    │       └── SKILL.md                       # Master Skill: 6 Planes, 7 Domains, 26 Roles, Lifecycle
    ├── rules/
    │   ├── data-org-rules.md                  # 11 Absolute Maxims, Evidence Tagging, Anti-Leakage
    │   └── data-org-routing.md                # Dynamic Task Routing, 7 Quality Gates, Severity System
    └── protocols/
        ├── AGENT_PROTOCOL.md                  # Agent FSM, structured JSON schema, conflict resolution
        ├── TASK_PROTOCOL.md                   # 9-step decomposition pipeline, DAG execution, DoD
        ├── ARTIFACT_PROTOCOL.md               # Artifact-First policy, frontmatter schema, templates
        ├── QUALITY_GATE.md                    # Detailed verification checks for Gates 1 through 7
        └── PERMISSION_POLICY.md               # 4-tier autonomy matrix (AUTO, REVIEW, APPROVAL, BLOCKED)
```

---

## 📋 Protocols Reference

- **[Master Skill (`SKILL.md`)](.agents/skills/autonomous-data-org/SKILL.md):** Defines the full operating system architecture, agent specifications, and 26 specialized roles.
- **[Core Behavioral Rules (`data-org-rules.md`)](.agents/rules/data-org-rules.md):** Contains the 11 Absolute Maxims, Evidence Tagging hierarchy, and anti-leakage constraints.
- **[Routing & Quality Rules (`data-org-routing.md`)](.agents/rules/data-org-routing.md):** Defines the Orchestrator's dynamic routing engine, severity escalation matrix, and 16-point final report format.
- **[Agent Protocol (`AGENT_PROTOCOL.md`)](.agents/protocols/AGENT_PROTOCOL.md):** Details the agent finite state machine (FSM), structured JSON communication payloads, and disagreement arbitration.
- **[Task Protocol (`TASK_PROTOCOL.md`)](.agents/protocols/TASK_PROTOCOL.md):** Establishes the 9-step autonomous task decomposition, dependency DAG resolution, and Definition of Done.
- **[Artifact Protocol (`ARTIFACT_PROTOCOL.md`)](.agents/protocols/ARTIFACT_PROTOCOL.md):** Outlines standard repository artifacts, YAML frontmatter schemas, and templates.
- **[Quality Gate Protocol (`QUALITY_GATE.md`)](.agents/protocols/QUALITY_GATE.md):** In-depth evaluation rules and failure mitigation for Quality Gates 1 through 7.
- **[Permission Policy (`PERMISSION_POLICY.md`)](.agents/protocols/PERMISSION_POLICY.md):** Autonomy boundaries, human-in-the-loop triggers, and audit logging.

---

## 🎯 Final Deliverable Standard (16-Point Output)

All significant data, analytics, or ML deliverables follow this structure:
1. **Executive Summary** — High-level problem, methodology, and verified results
2. **Objective** — Specific business and technical goals addressed
3. **Data Sources** — Origins, physical schema, grain, time period, and volume
4. **Data Quality & Limitations** — Profiling stats, null rates, known anomalies, and constraints
5. **Approach** — End-to-end architectural workflow and agent allocation
6. **Methods** — Analytical, statistical, or mathematical formulations applied
7. **Key Findings** — Findings tagged with evidence levels (`[FACT]`, `[STATISTICAL_RESULT]`, etc.)
8. **Statistical / Model Results** — Metrics, baselines, confidence intervals, error segments
9. **Validation & Gate Checks** — Status of Quality Gates 1 through 7
10. **Risks & Failure Modes** — Operational, technical, and data risks identified
11. **Limitations** — Assumptions, unmodeled variables, and boundary conditions
12. **Business Implications** — Actionable translation of technical findings into decision options
13. **Next Actions** — High-priority recommended next steps
14. **Artifacts Created** — Complete links to generated reports, code, schemas, and contracts
15. **Observability & Monitoring Plan** — Metrics to track over time and drift detection parameters
16. **Final Operational Status** — `PASSED`, `BLOCKED`, or `ESCALATED`

---

## 📄 License
This project is licensed under the MIT License.
