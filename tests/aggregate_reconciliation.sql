WITH users AS (
    SELECT
        variant,
        COUNT(*) AS total_users,
        SUM(converted) AS total_conversions,
        SUM(checkout_amount) AS total_revenue
    FROM {{ ref('fct_ab_test_users') }}
    GROUP BY variant
),
results AS (
    SELECT
        variant_group AS variant,
        SUM(total_users) AS total_users,
        SUM(total_conversions) AS total_conversions,
        SUM(total_revenue) AS total_revenue
    FROM {{ ref('fct_ab_test_results') }}
    GROUP BY variant_group
)
SELECT COALESCE(u.variant, r.variant) AS variant
FROM users AS u
FULL OUTER JOIN results AS r ON u.variant = r.variant
WHERE u.variant IS NULL
   OR r.variant IS NULL
   OR u.total_users != r.total_users
   OR u.total_conversions != r.total_conversions
   OR u.total_revenue != r.total_revenue
