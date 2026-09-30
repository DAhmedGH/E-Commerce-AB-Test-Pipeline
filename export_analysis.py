"""Export the dbt user-level model to the CSV read by the notebook."""

import argparse
import csv
import re
from pathlib import Path

import pandas as pd
from google.cloud import bigquery

from validate_data import validate_experiment_data


FIELDS = ("user_id", "variant", "device", "event_time", "converted", "checkout_amount")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="BigQuery project ID")
    parser.add_argument("--dataset", required=True, help="Dataset containing dbt models")
    parser.add_argument("--location", default="US", help="BigQuery dataset location")
    parser.add_argument("--output", type=Path, default=Path("clean_data_for_stats.csv"))
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]*", args.project):
        parser.error("--project must be a BigQuery project ID")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", args.dataset):
        parser.error("--dataset must be a BigQuery dataset ID")

    table = f"{args.project}.{args.dataset}.fct_ab_test_users"
    fields = ", ".join(FIELDS)
    query = f"SELECT {fields} FROM `{table}` ORDER BY user_id"
    rows = bigquery.Client(project=args.project, location=args.location).query(query).result()

    count = 0
    with args.output.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in FIELDS})
            count += 1

    validate_experiment_data(pd.read_csv(args.output))
    print(f"Exported {count} users to {args.output}")


if __name__ == "__main__":
    main()
