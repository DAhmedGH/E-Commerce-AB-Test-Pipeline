import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

from validate_data import validate_experiment_data


SEED = 42
np.random.seed(SEED)
random.seed(SEED)

n_users = 50000

# One synthetic observation timestamp per user in January 1-30, 2024 (UTC).
# The naive datetime is stored as BigQuery DATETIME; it is not a purchase time.
user_ids = [f"U_{i:05d}" for i in range(n_users)]
start_date = datetime(2024, 1, 1)
timestamps = [start_date + timedelta(minutes=random.randrange(30 * 24 * 60)) for _ in range(n_users)]

# 50/50 split between Control (A) and Variant (B)
groups = np.random.choice(['Control', 'Variant'], size=n_users, p=[0.5, 0.5])

# Simulate Conversion Rates (Control: ~12%, Variant: ~14.5%)
conversions = []
revenues = []

for group in groups:
    if group == 'Control':
        converted = np.random.choice([0, 1], p=[0.88, 0.12])
        mean_amount = 50
    else:
        converted = np.random.choice([0, 1], p=[0.855, 0.145])
        mean_amount = 55

    revenue = 0.0
    if converted:
        revenue = round(np.random.normal(mean_amount, 15), 2)
        while revenue <= 0:
            revenue = round(np.random.normal(mean_amount, 15), 2)

    conversions.append(converted)
    revenues.append(revenue)

# Create DataFrame
df = pd.DataFrame({
    'user_id': user_ids,
    'variant': groups,
    'device': np.random.choice(['Mobile', 'Desktop', 'Tablet'], size=n_users, p=[0.6, 0.3, 0.1]),
    'event_time': timestamps,
    'converted': conversions,
    'checkout_amount': revenues
})

validate_experiment_data(df)

# Save to CSV
df.to_csv('raw_experiment_logs.csv', index=False)
print("Data generated! Check your folder for 'raw_experiment_logs.csv'")
