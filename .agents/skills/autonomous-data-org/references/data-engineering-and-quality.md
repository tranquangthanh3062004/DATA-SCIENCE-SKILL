# Data Engineering & Quality Standard

Load for pipelines, dbt/SQL models, schemas, ingestion, backfills and data quality (Gates 1, 4, 5).

## 1. Medallion Contract

| Layer | Schema | Rule | Allowed transforms |
|---|---|---|---|
| Bronze | `bronze` | Append-only raw copy, source schema preserved, plus `_ingested_at`, `_source`, `_batch_id` | None (no business logic) |
| Silver | `silver` | Typed, deduplicated, conformed, PK enforced | Cast, rename, dedupe, standardize, filter invalid -> quarantine |
| Gold | `gold` | Business-grain marts and registered metrics | Joins, aggregates, metric formulas |
| Quarantine | `quarantine` | Rejected rows with `reason_code`, `rule_id`, `batch_id` | None |

Never silently drop rows: `rows_in = rows_out + rows_quarantined` must reconcile and be logged to `monitoring.pipeline_runs`.

## 2. Idempotency Patterns

| Load type | Pattern |
|---|---|
| Full refresh | Build to temp table, swap atomically |
| Incremental by key | `MERGE`/`INSERT ... ON CONFLICT DO UPDATE` on the natural key |
| Incremental by partition | Overwrite the partition for the batch window (delete+insert in one transaction) |
| Append-only events | Deduplicate on event id; unique constraint or `QUALIFY ROW_NUMBER()` |

Every run carries a deterministic `batch_id`/window so a re-run produces identical output. Test idempotency by running twice and diffing.

## 3. Reliability

- Retries with exponential backoff and jitter on transient errors only; fail fast on logic/data errors.
- Timeouts, checkpoints, and a dead-letter/quarantine path.
- Late-arriving data: define watermark and allowed lateness; reprocess affected partitions.
- Backfills: run in staging first, bounded windows, idempotent, with row-count reconciliation; destructive backfills need human approval.
- Schema evolution: additive changes allowed; breaking changes require a data-contract version bump and consumer notice. Detect drift automatically and halt on unapproved changes.

## 4. Gate 1 Check Set and Thresholds

| Check | Rule | Severity |
|---|---|---|
| Schema | Names/types match contract | Critical |
| PK | Unique and non-null | Critical |
| Nulls | Critical fields 0%; others within contract (`max_null_pct`) | Critical/Warning |
| Ranges | Domain bounds (amount >= 0, plausible dates) | Critical |
| Temporal | No future timestamps; ordering sane | Critical |
| Referential | FK exists in dimension (or flagged orphan rate) | Warning/Critical |
| Volume | Row count within expected band vs trailing window | Warning |
| Freshness | Age <= SLA | Critical for SLA tables |
| Distribution | Shift vs baseline (PSI/KS) | Warning |

Pass criteria: 100% of critical rules and overall quality score >= 95% (QUALITY_GATE.md). A high aggregate never overrides a critical failure. Implementation: `src/quality/validators.py` (`DataQualityValidator.run_gate_1`) and `src/quality/profiler.py`.

## 5. dbt / SQL Conventions

- `stg_` (1:1 with source, rename/cast only), `int_` (ephemeral logic), `mart_`/`fct_`/`dim_` (gold).
- Every model has `unique` and `not_null` on its key, `accepted_values` for enums (instead of hardcoded `IN` filters that silently drop rows), and relationship tests to dimensions.
- Declare all sources in `sources.yml` with freshness; document grain in the model description.
- Metrics must reference the registry definition (`configs/metric_registry.yml`); the SQL comment is not the source of truth.
- Use a `generate_schema_name` macro so `+schema: silver` yields exactly `silver`, not `<target>_silver`.
- Avoid `SELECT *` in marts; make timestamps UTC; deterministic ordering for dedupe (`ORDER BY updated_at DESC, id`).

## 6. Security and Governance (Gate 5)

- Secrets only via environment/secret manager; `.env` never committed; no credentials in code, compose files, logs or CI output.
- Classify every asset (`PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, `RESTRICTED`) using `governance/data_classification/classification_rules.yml`; mask/hash/tokenize PII before it reaches Silver/Gold or logs.
- Least-privilege roles: pipeline writer, analyst reader, admin separate. Parameterize queries; never interpolate untrusted input into SQL or shell.
- CI/CD: pass untrusted workflow inputs through `env:` and validate with an allow-list regex; never inline `${{ inputs.* }}` into shell.
- Audit every privileged action to `audit.agent_actions`.

## 7. Observability

Structured logs with trace/task/agent ids (`src/utils/logging_config.py`), run metrics (rows read/written/quarantined, duration, retries), freshness/volume/schema monitors, and alerts per `configs/alert_rules.yml`. A status banner must be computed from real results, never hardcoded.

## 8. Synthetic Data Rule

Sample data used for tests or demos must be generated with a fixed seed and labeled `SYNTHETIC`. It may demonstrate mechanics but must never support business conclusions or be mixed into real tables.
