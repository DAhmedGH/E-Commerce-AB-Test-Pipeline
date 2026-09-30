{{ config(materialized='table') }}

SELECT
    variant AS variant_group,
    device AS device_type,
    COUNT(DISTINCT user_id) AS total_users,
    SUM(converted) AS total_conversions,
    SUM(checkout_amount) AS total_revenue,
    ROUND(SUM(converted) / COUNT(DISTINCT user_id), 4) AS conversion_rate,
    ROUND(SUM(checkout_amount) / NULLIF(SUM(converted), 0), 2) AS average_order_value
FROM {{ ref('fct_ab_test_users') }}
GROUP BY variant, device
