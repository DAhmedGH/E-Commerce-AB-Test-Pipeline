{{ config(materialized='table') }}

WITH raw_data AS (
    SELECT 
        user_id,
        CAST(timestamp AS DATETIME) AS event_time,
        variant_group,
        device_type,
        CAST(converted AS INT64) AS is_converted,
        CAST(checkout_amount AS FLOAT64) AS revenue
    FROM `ab-test-portfolio-508122.ecommerce_data.raw_events`
),

aggregated AS (
    SELECT 
        variant_group,
        device_type,
        COUNT(DISTINCT user_id) AS total_users,
        SUM(is_converted) AS total_conversions,
        SUM(revenue) AS total_revenue,
        ROUND(SUM(is_converted) / COUNT(DISTINCT user_id), 4) AS conversion_rate,
        ROUND(SUM(revenue) / NULLIF(SUM(is_converted), 0), 2) AS average_order_value
    FROM raw_data
    GROUP BY variant_group, device_type
)

SELECT * FROM aggregated