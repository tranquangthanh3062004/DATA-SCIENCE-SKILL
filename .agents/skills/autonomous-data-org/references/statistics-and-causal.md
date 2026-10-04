# Statistics, Experimentation & Causal Standard

Load for any hypothesis test, A/B test, forecast evaluation, or causal claim (Gate 2).

## 1. Reporting Contract

Every statistical result states: **estimate, uncertainty (CI), effect size, n, test/assumptions, and practical significance**. A bare p-value is invalid. Tag: `[STATISTICAL_RESULT]`.

## 2. Test Selection

| Question | Data | Default test | If assumptions fail |
|---|---|---|---|
| Two group means | Continuous, independent | Welch t-test | Mann-Whitney U / bootstrap |
| Paired difference | Continuous, paired | Paired t-test | Wilcoxon signed-rank |
| >2 groups | Continuous | One-way ANOVA (Welch) | Kruskal-Wallis |
| Two proportions | Binary | Two-proportion z / chi-square | Fisher exact (small counts) |
| Association | Two categorical | Chi-square + Cramer's V | Fisher exact |
| Correlation | Continuous | Pearson | Spearman |
| Distribution shift | Any | KS test, PSI | - |
| Time-to-event | Censored | Kaplan-Meier + log-rank | Cox PH |

Check before parametric tests: independence, approximate normality of residuals (or large n), variance homogeneity, outliers. Inspect distributions (skew, kurtosis, zero-inflation) first.

## 3. Effect Size and CI Defaults

- Means: Cohen's d / Hedges' g with 95% CI. Proportions: absolute and relative lift with CI. Correlation: r with CI.
- Prefer bootstrap CIs (>=2000 resamples, fixed seed) for skewed metrics (revenue, latency).
- Distinguish **statistical** from **practical** significance using a pre-declared minimum detectable/important effect (MDE).

## 4. Power and Sample Size

- Fix alpha (default 0.05 two-sided), power (default 0.80), and MDE **before** collecting data.
- Report required n per arm; compute with `statsmodels.stats.power`. For ratio metrics or clustering, use delta-method or cluster-robust variance, or simulation.
- Post-hoc "observed power" is not evidence; report CI instead.

## 5. Multiple Comparisons

- Declare the test family up front. Use Holm (FWER) for confirmatory, Benjamini-Hochberg (FDR) for exploratory screening.
- Subgroup analyses are exploratory unless pre-registered; label as `[HYPOTHESIS]`.

## 6. A/B Test Checklist

1. Unit of randomization = unit of analysis (else cluster-robust errors).
2. **Sample ratio mismatch (SRM)** chi-square on assignment counts; p < 0.001 -> invalidate and investigate.
3. A/A check or historical variance for baseline sanity.
4. Fixed horizon or a sequential method with alpha-spending; **no peeking** with fixed-horizon tests.
5. Primary metric + guardrail metrics declared in advance; novelty/primacy effects checked by time slices.
6. Interference (network effects, shared inventory) assessed; use cluster/switchback designs if present.
7. Decision rule written before looking at results.

## 7. Causal Inference Ladder

Default claim: **"X is associated with Y in this dataset."** Upgrade only with the matching design:

| Evidence | Allowed language | Required |
|---|---|---|
| Observational correlation | associated with | Confounder discussion |
| Adjusted observational | associated, after adjusting for Z | Pre-specified DAG, no colliders/mediators adjusted |
| Quasi-experiment (DiD, RDD, IV, synthetic control) | estimated effect under assumptions | Assumption tests (parallel trends, continuity, instrument validity), placebo checks |
| Randomized experiment | causal effect of treatment | Integrity checks (SRM, balance) |

Always list untestable assumptions as `[ASSUMPTION]` and run a sensitivity analysis where possible (e.g. E-value).

## 8. Forecasting Evaluation

- Rolling-origin (walk-forward) backtest; never shuffle. Horizon-aligned splits.
- Baselines first: seasonal naive, moving average. Report MASE/sMAPE/WAPE (avoid MAPE with zeros) and interval coverage (e.g. 80% interval should cover ~80%).
- Decompose trend/seasonality; check stationarity where model requires it; document holiday/promo regressors and whether they are known at forecast time (leakage otherwise).

## 9. Metric Governance

All KPIs use one definition from `configs/metric_registry.yml` (formula, grain, filters, owner). A report that recomputes a KPI differently fails Gate 2 until reconciled.
