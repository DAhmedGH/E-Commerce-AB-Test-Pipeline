SELECT
    user_id,
    variant,
    device,
    event_time,
    converted,
    checkout_amount
FROM {{ source('experiment_raw', 'raw_events') }}
