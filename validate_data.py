"""Check the one-row-per-user experiment data used throughout the pipeline."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = (
    "user_id", "variant", "device", "event_time", "converted", "checkout_amount"
)
VARIANTS = {"Control", "Variant"}
DEVICES = {"Mobile", "Desktop", "Tablet"}
PERIOD_START = pd.Timestamp("2024-01-01", tz="UTC")
PERIOD_END = pd.Timestamp("2024-01-31", tz="UTC")


def validate_experiment_data(df: pd.DataFrame) -> None:
    """Raise ValueError if the canonical user-level experiment is invalid."""
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if df.empty:
        raise ValueError("Experiment data has no users")

    if df["user_id"].isna().any() or df["user_id"].astype(str).str.strip().eq("").any():
        raise ValueError("user_id must be present for every row")
    # A unique user row also enforces one treatment and one device per user.
    if df["user_id"].duplicated().any():
        raise ValueError("user_id must occur exactly once (one variant and device per user)")

    if df["variant"].isna().any() or not df["variant"].isin(VARIANTS).all():
        raise ValueError("variant must be Control or Variant for every user")
    if df["device"].isna().any() or not df["device"].isin(DEVICES).all():
        raise ValueError("device must be Mobile, Desktop, or Tablet for every user")

    event_time = pd.to_datetime(df["event_time"], errors="coerce", utc=True)
    if event_time.isna().any() or not event_time.between(PERIOD_START, PERIOD_END, inclusive="left").all():
        raise ValueError("event_time must be within January 1-30, 2024 UTC")

    converted = pd.to_numeric(df["converted"], errors="coerce")
    if not converted.isin([0, 1]).all():
        raise ValueError("converted must be 0 or 1 for every user")

    amount = pd.to_numeric(df["checkout_amount"], errors="coerce")
    if not np.isfinite(amount.to_numpy(dtype=float)).all():
        raise ValueError("checkout_amount must be finite for every user")
    if (amount < 0).any():
        raise ValueError("checkout_amount cannot be negative")
    if ((converted == 1) & (amount <= 0)).any():
        raise ValueError("converted users must have a positive paid purchase")
    if ((converted == 0) & (amount != 0)).any():
        raise ValueError("nonconverted users must have zero checkout_amount")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, help="User-level CSV to validate")
    args = parser.parse_args()
    data = pd.read_csv(args.csv)
    validate_experiment_data(data)
    print(f"Validated {len(data)} user rows in {args.csv}")
