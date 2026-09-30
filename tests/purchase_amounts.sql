SELECT user_id, converted, checkout_amount
FROM {{ ref('fct_ab_test_users') }}
WHERE (converted = 1 AND checkout_amount <= 0)
   OR (converted = 0 AND checkout_amount != 0)
