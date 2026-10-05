-- ╔══════════════════════════════════════════════════════════════════════╗
-- ║  ADI-OS dbt — Staging Model Example                                 ║
-- ║  Bronze → Silver: Customer Transactions                             ║
-- ║  Layer: Staging (Silver)                                            ║
-- ╚══════════════════════════════════════════════════════════════════════╝

-- This model demonstrates the Bronze-to-Silver transformation pattern:
--   1. Rename columns to business-friendly names
--   2. Cast data types explicitly
--   3. Add audit columns
--   4. Apply basic data quality filters

{{
    config(
        materialized='view',
        schema='silver',
        tags=['staging', 'silver', 'transactions']
    )
}}

WITH source AS (
    SELECT *
    FROM {{ source('bronze', 'raw_customer_transactions') }}
),

-- Step 1: Rename and cast
renamed AS (
    SELECT
        -- Primary Key
        CAST(transaction_id AS BIGINT) AS transaction_id,

        -- Foreign Keys
        CAST(customer_id AS BIGINT) AS customer_id,
        CAST(store_id AS INTEGER) AS store_id,

        -- Measures
        CAST(amount AS NUMERIC(12, 2)) AS transaction_amount,

        -- Dimensions
        LOWER(TRIM(category)) AS product_category,
        LOWER(TRIM(payment_method)) AS payment_method,
        LOWER(TRIM(transaction_status)) AS transaction_status,

        -- Temporal
        CAST(transaction_date AS TIMESTAMP) AS transaction_at,
        CAST(transaction_date AS DATE) AS transaction_date,

        -- Audit
        CURRENT_TIMESTAMP AS _loaded_at,
        '{{ invocation_id }}' AS _dbt_invocation_id

    FROM source
),

-- Step 2: Apply data quality filters (Gate 1 inline)
filtered AS (
    SELECT *
    FROM renamed
    WHERE
        -- PK not null
        transaction_id IS NOT NULL
        -- No future dates
        AND transaction_date <= CURRENT_DATE
        -- Valid amounts
        AND transaction_amount >= 0
        -- Valid category
        AND product_category IN ('electronics', 'clothing', 'food', 'other')
)

SELECT * FROM filtered
