-- ╔══════════════════════════════════════════════════════════════════════╗
-- ║  ADI-OS dbt — Gold Mart Example                                     ║
-- ║  Silver → Gold: Daily Revenue Summary                               ║
-- ║  Layer: Marts (Gold)                                                ║
-- ║  Metric: gross_revenue (from metric_registry.yml)                   ║
-- ╚══════════════════════════════════════════════════════════════════════╝

{{
    config(
        materialized='table',
        schema='gold',
        tags=['marts', 'gold', 'revenue']
    )
}}

WITH transactions AS (
    SELECT *
    FROM {{ ref('stg_customer_transactions') }}
    -- Canonical filter for gross_revenue / average_order_value (configs/metric_registry.yml)
    WHERE transaction_status = 'completed'
),

daily_summary AS (
    SELECT
        transaction_date,
        product_category,
        store_id,

        -- Metric: gross_revenue (canonical definition from metric_registry.yml)
        -- Formula: SUM(transaction_amount) WHERE transaction_status = 'completed'
        SUM(transaction_amount) AS gross_revenue,

        -- Metric: average_order_value
        -- Formula: SUM(transaction_amount) / COUNT(DISTINCT transaction_id)
        SUM(transaction_amount) / NULLIF(COUNT(DISTINCT transaction_id), 0) AS average_order_value,

        -- Volume metrics
        COUNT(DISTINCT transaction_id) AS transaction_count,
        COUNT(DISTINCT customer_id) AS unique_customers,

        -- Audit
        CURRENT_TIMESTAMP AS _computed_at

    FROM transactions
    GROUP BY
        transaction_date,
        product_category,
        store_id
)

SELECT * FROM daily_summary
