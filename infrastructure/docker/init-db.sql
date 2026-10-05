-- ╔══════════════════════════════════════════════════════════════════════╗
-- ║  ADI-OS — Database Initialization Script                            ║
-- ║  Creates medallion architecture schemas (bronze/silver/gold)        ║
-- ╚══════════════════════════════════════════════════════════════════════╝

-- Medallion Architecture Schemas
CREATE SCHEMA IF NOT EXISTS bronze;    -- Raw ingested data
CREATE SCHEMA IF NOT EXISTS silver;    -- Cleaned, validated, conformed
CREATE SCHEMA IF NOT EXISTS gold;      -- Business-ready aggregates & marts
CREATE SCHEMA IF NOT EXISTS quarantine; -- Failed quality gate records
CREATE SCHEMA IF NOT EXISTS staging;   -- Temporary staging area

-- Audit & Observability
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- ── Audit Log Table ──
CREATE TABLE IF NOT EXISTS audit.agent_actions (
    action_id       BIGSERIAL PRIMARY KEY,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    task_id         TEXT NOT NULL,
    agent_id        TEXT NOT NULL,
    action_type     TEXT NOT NULL,        -- AUTO | REVIEW | APPROVAL | BLOCKED
    tool_name       TEXT,
    parameters      JSONB,
    result_status   TEXT NOT NULL,        -- SUCCESS | FAILED | BLOCKED
    error_message   TEXT,
    execution_ms    INTEGER,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_task ON audit.agent_actions(task_id);
CREATE INDEX IF NOT EXISTS idx_audit_agent ON audit.agent_actions(agent_id);
CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit.agent_actions(timestamp);

-- ── Bronze: raw customer transactions (source for dbt staging) ──
-- Raw layer keeps loose types (TEXT) so ingestion never fails on malformed input;
-- casting and validation happen in stg_customer_transactions (Silver).
CREATE TABLE IF NOT EXISTS bronze.raw_customer_transactions (
    transaction_id      TEXT,
    customer_id         TEXT,
    store_id            TEXT,
    amount              TEXT,
    category            TEXT,
    payment_method      TEXT,
    transaction_status  TEXT,
    transaction_date    TEXT,
    _ingested_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    _source_file        TEXT
);

-- ── Data Quality Scores Table ──
CREATE TABLE IF NOT EXISTS monitoring.data_quality_scores (
    score_id        BIGSERIAL PRIMARY KEY,
    dataset_name    TEXT NOT NULL,
    schema_name     TEXT NOT NULL,
    check_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completeness    NUMERIC(5,4),     -- 0.0000 to 1.0000
    validity        NUMERIC(5,4),
    uniqueness      NUMERIC(5,4),
    consistency     NUMERIC(5,4),
    freshness       NUMERIC(5,4),
    overall_score   NUMERIC(5,4),
    gate_status     TEXT NOT NULL,     -- PASSED | FAILED | WARNING
    details         JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Pipeline Run Tracking ──
CREATE TABLE IF NOT EXISTS monitoring.pipeline_runs (
    run_id          BIGSERIAL PRIMARY KEY,
    pipeline_name   TEXT NOT NULL,
    run_timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status          TEXT NOT NULL,       -- RUNNING | SUCCESS | FAILED | RETRYING
    rows_read       BIGINT,
    rows_written    BIGINT,
    rows_quarantined BIGINT DEFAULT 0,
    duration_sec    NUMERIC(10,2),
    error_message   TEXT,
    retry_count     INTEGER DEFAULT 0,
    metadata        JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Model Registry Table ──
CREATE TABLE IF NOT EXISTS monitoring.model_registry (
    model_id        BIGSERIAL PRIMARY KEY,
    model_name      TEXT NOT NULL,
    model_version   TEXT NOT NULL,
    algorithm       TEXT NOT NULL,
    training_date   TIMESTAMPTZ NOT NULL,
    metrics         JSONB NOT NULL,       -- {"auc": 0.85, "f1": 0.78, ...}
    baseline_metrics JSONB,               -- baseline comparison
    gate_3_status   TEXT NOT NULL,        -- PASSED | FAILED
    gate_6_status   TEXT NOT NULL,        -- PASSED | FAILED (independent review)
    deployed        BOOLEAN DEFAULT FALSE,
    deployed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(model_name, model_version)
);

COMMENT ON SCHEMA bronze IS 'Raw ingested data — no transformations applied';
COMMENT ON SCHEMA silver IS 'Cleaned, validated, and conformed data';
COMMENT ON SCHEMA gold IS 'Business-ready aggregates, metrics, and analytical marts';
COMMENT ON SCHEMA quarantine IS 'Records that failed data quality gates';
