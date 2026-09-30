import csv
import io
import sys
import types
import unittest
from contextlib import nullcontext
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd

from export_analysis import DASHBOARD_FIELDS, main, validate_dashboard_rows


def dashboard_rows():
    return [
        {
            "variant_group": variant,
            "device_type": device,
            "total_users": 1,
            "total_conversions": 1,
            "total_revenue": Decimal("10.00"),
            "conversion_rate": 1.0,
            "average_order_value": 10.0,
        }
        for variant in ("Control", "Variant")
        for device in ("Desktop", "Mobile", "Tablet")
    ]


class DashboardExportTests(unittest.TestCase):
    def test_dashboard_validation(self):
        validate_dashboard_rows(dashboard_rows())

        cases = (
            (lambda rows: rows.clear(), "no rows"),
            (lambda rows: rows[0].pop("average_order_value"), "missing columns"),
            (lambda rows: rows.append(rows[0].copy()), "duplicate"),
            (lambda rows: rows[0].update(variant_group="Other"), "variant_group"),
            (lambda rows: rows[0].update(device_type="Other"), "device_type"),
            (
                lambda rows: rows.__setitem__(slice(0, 3), []),
                "Control and Variant",
            ),
            (
                lambda rows: (rows.pop(5), rows.pop(2)),
                "Desktop, Mobile, and Tablet",
            ),
            (
                lambda rows: rows.pop(0),
                "exactly one row for each variant and device combination",
            ),
            (lambda rows: rows[0].update(total_users=None), "total_users"),
            (lambda rows: rows[0].update(total_users=0), "total_users"),
            (
                lambda rows: rows[0].update(total_conversions=-1),
                "total_conversions",
            ),
            (lambda rows: rows[0].update(total_revenue=-1), "total_revenue"),
            (
                lambda rows: rows[0].update(total_revenue=float("nan")),
                "total_revenue",
            ),
        )

        for change, message in cases:
            with self.subTest(message=message, change=change):
                rows = dashboard_rows()
                change(rows)

                with self.assertRaisesRegex(ValueError, message):
                    validate_dashboard_rows(rows)

    def test_one_invocation_exports_both_csvs(self):
        users = [
            {
                "user_id": f"U_{number}",
                "variant": variant,
                "device": "Desktop",
                "event_time": "2024-01-01 00:00:00",
                "converted": 1,
                "checkout_amount": Decimal("10.00"),
            }
            for number, variant in ((1, "Control"), (2, "Variant"))
        ]

        aggregates = dashboard_rows()
        client = Mock()

        def query(sql):
            rows = users if "fct_ab_test_users" in sql else aggregates
            return types.SimpleNamespace(result=lambda: rows)

        client.query.side_effect = query

        bigquery = types.ModuleType("google.cloud.bigquery")
        bigquery.Client = Mock(return_value=client)

        google = types.ModuleType("google")
        cloud = types.ModuleType("google.cloud")
        google.cloud = cloud
        cloud.bigquery = bigquery

        outputs = {
            "clean_data_for_stats.csv": io.StringIO(),
            "dashboard_data.csv": io.StringIO(),
        }

        read_csv = pd.read_csv

        with (
            patch.dict(
                sys.modules,
                {
                    "google": google,
                    "google.cloud": cloud,
                    "google.cloud.bigquery": bigquery,
                },
            ),
            patch.object(
                sys,
                "argv",
                [
                    "export_analysis.py",
                    "--project",
                    "sample-project",
                    "--dataset",
                    "sample_data",
                ],
            ),
            patch.object(
                Path,
                "open",
                lambda path, *args, **kwargs: nullcontext(outputs[path.name]),
            ),
            patch.object(
                pd,
                "read_csv",
                side_effect=lambda path: read_csv(
                    io.StringIO(outputs[Path(path).name].getvalue())
                ),
            ),
        ):
            main()

        user_export = list(
            csv.DictReader(
                io.StringIO(outputs["clean_data_for_stats.csv"].getvalue())
            )
        )

        dashboard_reader = csv.DictReader(
            io.StringIO(outputs["dashboard_data.csv"].getvalue())
        )

        self.assertEqual(
            dashboard_reader.fieldnames,
            list(DASHBOARD_FIELDS),
        )

        dashboard_export = list(dashboard_reader)

        self.assertEqual(len(user_export), 2)
        self.assertEqual(user_export[0]["user_id"], "U_1")

        self.assertEqual(
            [
                (row["variant_group"], row["device_type"])
                for row in dashboard_export
            ],
            [
                (row["variant_group"], row["device_type"])
                for row in aggregates
            ],
        )

        self.assertEqual(
            dashboard_export[0]["total_revenue"],
            "10.00",
        )

        self.assertEqual(client.query.call_count, 2)

        self.assertIn(
            "ORDER BY user_id",
            client.query.call_args_list[0].args[0],
        )

        self.assertIn(
            "`sample-project.sample_data.fct_ab_test_results`",
            client.query.call_args_list[1].args[0],
        )

        self.assertIn(
            "ORDER BY variant_group, device_type",
            client.query.call_args_list[1].args[0],
        )


if __name__ == "__main__":
    unittest.main()