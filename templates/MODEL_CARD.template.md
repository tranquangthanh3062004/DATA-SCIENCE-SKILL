---
artifact_id: "ART-YYYYMMDD-MC-NNN"
artifact_type: "MODEL_CARD"
title: "Model Card: [Model Name]"
version: "1.0.0"
created_at: "YYYY-MM-DDTHH:MM:SSZ"
owner_agent: "data_scientist"
review_agent: "model_reviewer"
quality_gate_status: "PENDING"
reproducibility:
  seed: 42
  environment_hash: ""
  code_reference: ""
---

# Model Card: [Model Name]

## 1. Model Details

| Field | Value |
|---|---|
| **Model Name** | |
| **Version** | 1.0.0 |
| **Algorithm** | |
| **Framework** | scikit-learn / XGBoost / PyTorch / etc. |
| **Framework Version** | |
| **Owner** | |
| **Created** | YYYY-MM-DD |

### Hyperparameters
```yaml
# List all hyperparameters
learning_rate: 0.1
max_depth: 6
n_estimators: 100
```

---

## 2. Intended Use & Non-Goals

### Intended Use
- **Primary Use Case:** [Describe the business problem this model solves]
- **Target Users:** [Who will use the model's predictions]
- **Expected Inputs:** [Description of input features]
- **Expected Outputs:** [Description of output predictions]

### Non-Goals (Explicitly Out of Scope)
- [ ] [Use case this model should NOT be used for]
- [ ] [Population this model was NOT trained on]

---

## 3. Training Data & Split Strategy

| Field | Value |
|---|---|
| **Data Source** | |
| **Data Version** | |
| **Date Range** | YYYY-MM-DD to YYYY-MM-DD |
| **Total Samples** | |
| **Train Size** | |
| **Validation Size** | |
| **Test Size** | |
| **Split Strategy** | Temporal / Grouped / Stratified |

### Feature Leakage Check
- [x] No features derived from post-outcome events
- [x] No proxy variables for the target
- [x] Preprocessing fitted on training data only
- [x] Temporal ordering preserved (if applicable)

---

## 4. Baseline Performance

| Model | Metric 1 | Metric 2 | Metric 3 |
|---|---|---|---|
| **Baseline (Naive/Heuristic)** | | | |
| **Candidate Model** | | | |
| **Improvement** | | | |

> **Gate 3 Check 1:** Baseline ☐ PASSED / ☐ FAILED

---

## 5. Evaluation Metrics

### Classification Metrics
| Metric | Train | Validation | Test |
|---|---|---|---|
| Accuracy | | | |
| F1 Score | | | |
| Precision | | | |
| Recall | | | |
| ROC-AUC | | | |
| PR-AUC | | | |
| Log Loss | | | |

### Calibration
[Describe calibration assessment — are predicted probabilities well-calibrated?]

---

## 6. Subgroup & Error Analysis

### Performance by Segment
| Segment | Metric 1 | Metric 2 | Sample Size |
|---|---|---|---|
| Segment A | | | |
| Segment B | | | |
| Segment C | | | |

### Error Analysis
- **Most Common False Positives:** [Pattern description]
- **Most Common False Negatives:** [Pattern description]
- **High-Error Subgroups:** [Segments with degraded performance]

> **Gate 3 Check 5:** Subgroup Analysis ☐ PASSED / ☐ FAILED

---

## 7. Ethical, Fairness & Operational Considerations

### Known Biases
- [ ] [Describe any known biases in training data or predictions]

### Fairness Assessment
- [ ] Performance parity across protected groups evaluated
- [ ] Disparate impact ratio assessed

### Drift & Monitoring Plan
| Monitor | Metric | Threshold | Action |
|---|---|---|---|
| Feature Drift | PSI | > 0.2 | Trigger retraining |
| Prediction Drift | PSI | > 0.2 | Alert + investigate |
| Performance | Primary Metric | < baseline * 0.95 | Alert + retrain |

---

## 8. Limitations & Assumptions

### Assumptions
- [ASSUMPTION] [List explicit assumptions]

### Limitations
- [List known limitations and boundary conditions]
- [Populations or scenarios where the model may not generalize]

---

## 9. Review Sign-Off

| Reviewer | Role | Date | Status |
|---|---|---|---|
| | Model Reviewer | | ☐ APPROVED / ☐ REJECTED |
| | Business Reviewer | | ☐ APPROVED / ☐ REJECTED |
