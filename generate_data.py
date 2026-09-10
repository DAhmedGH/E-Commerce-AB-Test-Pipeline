import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

n_users = 50000

# Generate User IDs and timestamp
user_ids = [f"U_{i:05d}" for i in range(n_users)]
start_date = datetime(2024, 1, 1)
timestamps = [start_date + timedelta(minutes=random.randint(0, 43200)) for _ in range(n_users)]

# 50/50 split between Control (A) and Variant (B)
groups = np.random.choice(['Control', 'Variant'], size=n_users, p=[0.5, 0.5])

# Simulate Conversion Rates (Control: ~12%, Variant: ~14.5%)
conversions = []
revenues = []

for group in groups:
    if group == 'Control':
        converted = np.random.choice([0, 1], p=[0.88, 0.12])
        revenue = round(np.random.normal(50, 15), 2) if converted else 0.0
    else:
        converted = np.random.choice([0, 1], p=[0.855, 0.145])
        revenue = round(np.random.normal(55, 15), 2) if converted else 0.0 # Variant also increases cart size slightly
        
    conversions.append(converted)
    # Ensure no negative revenues
    revenues.append(max(0, revenue))

# Create DataFrame
df = pd.DataFrame({
    'user_id': user_ids,
    'timestamp': timestamps,
    'variant_group': groups,
    'device_type': np.random.choice(['Mobile', 'Desktop', 'Tablet'], size=n_users, p=[0.6, 0.3, 0.1]),
    'converted': conversions,
    'checkout_amount': revenues
})

# Save to CSV
df.to_csv('raw_experiment_logs.csv', index=False)
print("Data generated! Check your folder for 'raw_experiment_logs.csv'")