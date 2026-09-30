"""Export dbt user and aggregate models for the notebook and Tableau."""

import argparse
import csv
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

import pandas as pd

from validate_data import validate_experiment_data


FIELDS = ("user_id", "variant", "device", "event_time", "converted", "checkout_amount")
DASHBOARD_FIELDS = (
    "variant_group",
    "device_type",
    "total_users",
    "total_conversions",
    "total_revenue",
    "conversion_rate",
    "average_order_value",
)


def validate_dashboard_rows(rows):
    """Check the six-group aggregate before writing the Tableau CSV."""
    if not rows:
        raise ValueError("Dashboard export has no rows")

    pairs = set()
    variants = set()
    devices = set()

    for row in rows:
        missing = set(DASHBOARD_FIELDS) - set(row.keys())
        if missing:
            raise ValueError(
                f"Dashboard export is missing columns: {', '.join(sorted(missing))}"
            )

        def finite_number(field):
            try:
                value = Decimal(str(row[field]))
            except (InvalidOperation, TypeError, ValueError) as exc:
                raise ValueError(
                    f"Dashboard {field} must be a finite number"
                ) from exc
            if not value.is_finite():
                raise ValueError(f"Dashboard {field} must be a finite number")
            return value

        variant = row["variant_group"]
        device = row["device_type"]

        if variant not in {"Control", "Variant"}:
            raise ValueError("Dashboard variant_group must be Control or Variant")

        if device not in {"Desktop", "Mobile", "Tablet"}:
            raise ValueError("Dashboard device_type must be Desktop, Mobile, or Tablet")

        pair = (variant, device)
        if pair in pairs:
            raise ValueError(
                "Dashboard export has a duplicate variant_group and device_type"
            )

        pairs.add(pair)
        variants.add(variant)
        devices.add(device)

        users = finite_number("total_users")
        conversions = finite_number("total_conversions")
        revenue = finite_number("total_revenue")
        if users <= 0 or users != users.to_integral_value():
            raise ValueError("Dashboard total_users must be a positive integer")
        if conversions < 0 or conversions != conversions.to_integral_value():
            raise ValueError("Dashboard total_conversions must be a nonnegative integer")
        if conversions > users:
            raise ValueError("Dashboard total_conversions cannot exceed total_users")
        if revenue < 0:
            raise ValueError("Dashboard total_revenue has an invalid total")

        conversion_rate = finite_number("conversion_rate")
        expected_rate = (conversions / users).quantize(
            Decimal("0.0001"), rounding=ROUND_HALF_UP
        )
        if not 0 <= conversion_rate <= 1 or conversion_rate != expected_rate:
            raise ValueError("Dashboard conversion_rate disagrees with totals")

        if conversions == 0:
            if revenue != 0 or row["average_order_value"] is not None:
                raise ValueError(
                    "Dashboard zero conversions require zero total_revenue and null average_order_value"
                )
        else:
            aov = finite_number("average_order_value")
            expected_aov = (revenue / conversions).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            if aov < 0 or aov != expected_aov:
                raise ValueError("Dashboard average_order_value disagrees with totals")

    if variants != {"Control", "Variant"}:
        raise ValueError("Dashboard export must include Control and Variant")

    if devices != {"Desktop", "Mobile", "Tablet"}:
        raise ValueError("Dashboard export must include Desktop, Mobile, and Tablet")

    expected_pairs = {
        ("Control", "Desktop"),
        ("Control", "Mobile"),
        ("Control", "Tablet"),
        ("Variant", "Desktop"),
        ("Variant", "Mobile"),
        ("Variant", "Tablet"),
    }

    if pairs != expected_pairs:
        raise ValueError(
            "Dashboard export must contain exactly one row for each variant and device combination"
        )


def main():
    from google.cloud import bigquery

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
    client = bigquery.Client(project=args.project, location=args.location)
    rows = client.query(query).result()

    count = 0
    with args.output.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in FIELDS})
            count += 1

    validate_experiment_data(pd.read_csv(args.output))
    print(f"Exported {count} users to {args.output}")

    dashboard_table = f"{args.project}.{args.dataset}.fct_ab_test_results"
    dashboard_columns = ", ".join(DASHBOARD_FIELDS)
    dashboard_query = (
        f"SELECT {dashboard_columns} FROM `{dashboard_table}` "
        "ORDER BY variant_group, device_type"
    )
    dashboard_rows = list(client.query(dashboard_query).result())
    validate_dashboard_rows(dashboard_rows)

    dashboard_output = Path("dashboard_data.csv")
    with dashboard_output.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=DASHBOARD_FIELDS)
        writer.writeheader()
        for row in dashboard_rows:
            writer.writerow({field: row[field] for field in DASHBOARD_FIELDS})
    print(f"Exported {len(dashboard_rows)} dashboard rows to {dashboard_output}")


if __name__ == "__main__":
    main()
