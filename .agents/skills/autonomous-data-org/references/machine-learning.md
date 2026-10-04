# Machine Learning Standard

Load for any modeling task (Gate 3) and for drift/retraining work.

## 1. Problem Framing (before any code)

State: prediction target and its exact definition, prediction time (when is the score used), label availability delay, population, unit of prediction, action taken on the score, and the **cost matrix** (FP vs FN). If any is unknown, record `[ASSUMPTION]`.

## 2. Split Strategy Matrix

| Data property | Split | Never |
|---|---|---|
| Time-ordered | Forward-chaining / walk-forward, with a gap equal to label delay | Random split |
| Repeated entities (users, stores) | Group split by entity | Same entity in train and test |
| i.i.d., classification | Stratified random | - |
| Spatial autocorrelation | Spatial block CV | Random |

Order of operations: split first, then fit imputers/scalers/encoders/selectors on **train only** (use a `Pipeline`). Hyperparameter tuning on validation/CV; the test set is used once for the final report.

## 3. Leakage Checklist (fails Gate 1/3 immediately)

- [ ] Features computed using data after the prediction time (aggregates over full history, "last status", post-event flags)
- [ ] Target-derived or proxy columns (IDs that encode outcome, refund flags for fraud labels)
- [ ] Preprocessing fitted before the split
- [ ] Duplicates/near-duplicates across train and test
- [ ] Group or entity overlap across splits
- [ ] Feature importance dominated by a single suspicious feature (investigate AUC > 0.98 on hard problems)
- [ ] Time-travel joins (dimension tables joined at current value instead of as-of date)

## 4. Baselines (must be beaten)

| Task | Minimum baselines |
|---|---|
| Classification | Majority class, prior-rate, logistic regression, simple rule |
| Regression | Mean/median, last value, linear model |
| Forecasting | Seasonal naive, moving average |
| Ranking/recsys | Popularity, recency |

Candidate must beat the strongest baseline with an interval, not a single point: repeated CV or multiple seeds, report mean and 95% CI, and paired comparison where possible.

## 5. Metric Selection

| Situation | Primary metric | Also report |
|---|---|---|
| Balanced classification | F1 / accuracy / ROC-AUC | Confusion matrix |
| Imbalanced (fraud, churn) | PR-AUC, recall@precision | Calibration, cost-weighted loss |
| Probability used for decisions | Log loss / Brier | Calibration curve, ECE |
| Regression | MAE (robust) or RMSE | Bias, residual plots |
| Ranking | NDCG@k, MAP | Coverage |

Choose the metric from the cost matrix **before** training. Select a decision threshold on validation data to optimize expected cost, not default 0.5.

## 6. Calibration, Imbalance, Uncertainty

- Check calibration (reliability curve, ECE); recalibrate (isotonic/Platt) on a separate calibration fold.
- Imbalance: prefer class weights/threshold tuning over naive oversampling; if resampling, apply inside training folds only.
- Provide prediction intervals for regression/forecasts when decisions depend on risk.

## 7. Error Analysis (mandatory)

Break down errors by: key segments (region, tenure, product), time slices, confidence buckets, and the worst-k residuals. Report subgroup minimum sample size (the repo uses >10) and flag groups with degraded metrics. Document failure modes in `MODEL_EVALUATION.md`.

## 8. Interpretability and Fairness

SHAP/permutation importance on held-out data (not train). Check for protected-attribute proxies; report subgroup performance gaps. Importance is `[INTERPRETATION]`, never causation.

## 9. Reproducibility

Record: seed, library versions (lockfile), data snapshot/version hash, split definition, feature list, hyperparameters, run id in MLflow. Same inputs must reproduce metrics within a declared tolerance.

## 10. Monitoring and Retraining

| Signal | Default threshold (see `configs/alert_rules.yml`) | Action |
|---|---|---|
| PSI on score/feature | > 0.1 watch, > 0.2 alert | Investigate drift |
| Metric vs baseline | < 95% of baseline | Flag retraining evaluation |
| Data freshness/schema change | SLA breach / any change | Halt and notify |

Delayed labels: monitor input and score drift immediately; evaluate true performance when labels mature. Retrain only through the full gate path; the new model must beat the current champion on the same holdout.

## 11. Model Card and Release

`MODEL_CARD.md` and `MODEL_EVALUATION.md` (with baseline comparison) plus an independent sign-off are required before any deploy (`deploy.yml` enforces file presence; a human or separate reviewer provides the actual review).
