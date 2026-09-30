# QUALITY GATE PROTOCOL
## Autonomous Data Intelligence Operating System (ADI-OS) — Phase 0 Core

---

## 1. PURPOSE & PRINCIPLE
The **Quality Gate Protocol** establishes non-negotiable verification checkpoints across the data, analytics, machine-learning, and engineering lifecycles.
> A critical gate failure halts downstream processing immediately. High aggregate quality scores never override a critical violation.

---

## 2. THE 7 MANDATORY QUALITY GATES

```text
  [SOURCE DATA]
        │
        ▼
┌───────────────────────┐
│ GATE 1: DATA QUALITY  │  Evaluated by: Data Quality Engineer
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ GATE 2: ANALYTICS     │  Evaluated by: Analytics Engineer & Statistician
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ GATE 3: MODEL/SCIENCE │  Evaluated by: Model Reviewer
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ GATE 4: ENGINEERING   │  Evaluated by: Senior Data Engineer & ML Engineer
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ GATE 5: GOVERNANCE    │  Evaluated by: Data Governance & Security Agent
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ GATE 6: INDEPENDENT   │  Evaluated by: Business Reviewer & Technical Lead
│         REVIEW        │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ GATE 7: DELIVERY      │  Evaluated by: Documentation Agent & Orchestrator
└───────────┬───────────┘
            │
            ▼
   [PRODUCTION / USER]
```

---

## 3. DETAILED GATE SPECIFICATIONS

### GATE 1: DATA QUALITY
- **Evaluator:** Data Quality Engineer
- **Mandatory Checks:**
  1. *Schema Invariants:* Column names, physical data types match data contract.
  2. *Primary Key Uniqueness:* Primary key distinct count equals row count; zero null keys.
  3. *Null Thresholds:* Critical operational fields have 0% nulls; optional fields within contract limits.
  4. *Range Invariants:* Numerical values within physically plausible domains (e.g., age ∈ [0, 125], price ≥ 0).
  5. *Temporal Ordering:* Future timestamps absent; time-series ordering verified.
  6. *Target & Feature Leakage:* No proxy variables derived from post-outcome events.
- **Passing Criteria:** 100% pass on critical invariant rules; data quality score ≥ 95%.
- **Failure Action:** HALT pipeline. Quarantine failing rows into `data/quarantine/`. Generate incident alert.

---

### GATE 2: ANALYTICAL VALIDITY
- **Evaluator:** Analytics Engineer & Statistician
- **Mandatory Checks:**
  1. *Metric Registry Alignment:* All KPIs use approved, canonical mathematical formulas.
  2. *Distributional Verification:* Skewness, kurtosis, and zero-inflation inspected.
  3. *Statistical Assumptions:* Normality, homoscedasticity, or independence evaluated before parametric tests.
  4. *Confounding Assessment:* Potential lurking variables identified before correlational claims.
- **Passing Criteria:** Metrics traceable to canonical registry; statistical tests appropriate for distribution.
- **Failure Action:** Block reporting. Revert to exploratory phase for data transformation or non-parametric methods.

---

### GATE 3: MODEL & SCIENCE VALIDITY
- **Evaluator:** Independent Model Reviewer
- **Mandatory Checks:**
  1. *Baseline Presence:* A simple baseline (e.g., majority class, mean, logistic regression, rule-based) is benchmarked.
  2. *Split Isolation:* Train/Validation/Test splits strictly separated before any feature transformation or imputation.
  3. *Temporal Leakage Check:* Time-series tasks use strictly forward-chaining / walk-forward splits.
  4. *Metric Alignment:* Evaluation metric directly reflects the operational loss function (e.g., PR-AUC for imbalanced fraud).
  5. *Subgroup Analysis:* Model performance verified across demographic, regional, or customer segments to detect hidden failure pockets.
- **Passing Criteria:** Candidate beats baseline with statistical significance; zero feature leakage detected; subgroup degradation within acceptable bounds.
- **Failure Action:** Reject model candidate. Document failure modes in `MODEL_EVALUATION.md`.

---

### GATE 4: ENGINEERING & RELIABILITY
- **Evaluator:** Senior Data Engineer & ML Engineer
- **Mandatory Checks:**
  1. *Idempotency:* Pipeline produces identical output when executed repeatedly with identical inputs.
  2. *Test Coverage:* Unit and data integration tests pass (100% pass on pipeline assertions).
  3. *Fault Tolerance:* Checkpoints, retries with exponential backoff, and timeouts configured.
  4. *Observability:* Structured logging with trace IDs and runtime metrics instrumented.
- **Passing Criteria:** Zero unhandled exceptions; deterministic execution verified across two consecutive test runs.
- **Failure Action:** Reject pipeline deployment. Refactor code in staging branch.

---

### GATE 5: GOVERNANCE & SECURITY
- **Evaluator:** Security Agent & Compliance Reviewer
- **Mandatory Checks:**
  1. *Secret Scrubbing:* Zero hardcoded API keys, database passwords, or auth tokens in code or logs.
  2. *PII Protection:* Sensitive personal identifiers (SSN, credit cards, emails) hashed, masked, or tokenized.
  3. *Classification Tagging:* Data assets tagged with correct security tier (`PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, `RESTRICTED`).
  4. *Access Authorization:* Agent permissions verified against policy.
- **Passing Criteria:** Zero P0 security violations; all data assets classified.
- **Failure Action:** Immediate P0 security incident. Quash artifact. Scrub credentials immediately.

---

### GATE 6: INDEPENDENT MULTI-AGENT REVIEW
- **Evaluator:** Business Reviewer & Technical Lead
- **Mandatory Checks:**
  1. *Adversarial Scrutiny:* Active inspection of assumptions, limitations, and potential edge-case failures.
  2. *Business Relevance:* Do findings or model outcomes answer the foundational business question?
  3. *Trade-Off Quantification:* Cost of false positives vs false negatives clearly articulated.
- **Passing Criteria:** Explicit sign-off with recorded checklist. ("Looks good" is rejected).
- **Failure Action:** Re-route to specific agent domain with corrective feedback.

---

### GATE 7: DELIVERY & REPRODUCIBILITY
- **Evaluator:** Documentation Agent & Orchestrator
- **Mandatory Checks:**
  1. *Artifact Completeness:* All required markdown documents generated and linked.
  2. *Deterministic Reproducibility:* Random seeds recorded, dependencies pinned, data version locked.
  3. *Final Response Synthesis:* 16-point executive standard fully populated.
- **Passing Criteria:** All artifacts present and verified; zero missing sections in final delivery.
- **Failure Action:** Complete missing documentation before release to user.
