import unittest

import numpy as np
import pandas as pd

from validate_data import validate_experiment_data


class ExperimentValidationTests(unittest.TestCase):
    def setUp(self):
        self.rows = pd.DataFrame(
            {
                "user_id": ["U_1", "U_2"],
                "variant": ["Control", "Variant"],
                "device": ["Mobile", "Desktop"],
                "event_time": ["2024-01-01 00:00:00", "2024-01-30 23:59:00"],
                "converted": [1, 0],
                "checkout_amount": [10.0, 0.0],
            }
        )

    def test_valid_paid_purchase_and_nonconverter(self):
        validate_experiment_data(self.rows)

    def test_duplicate_user_with_conflicting_assignments(self):
        extra = self.rows.iloc[[0]].copy()
        extra.loc[:, "variant"] = "Variant"
        extra.loc[:, "device"] = "Tablet"
        duplicated = pd.concat([self.rows, extra], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "user_id must occur exactly once"):
            validate_experiment_data(duplicated)

    def test_rejects_invalid_purchase_amounts(self):
        cases = [
            (0, 0.0, "positive paid purchase"),
            (1, 1.0, "zero checkout_amount"),
            (0, -1.0, "cannot be negative"),
            (0, np.inf, "must be finite"),
        ]
        for row, value, message in cases:
            with self.subTest(row=row, value=value):
                bad = self.rows.copy()
                bad.loc[row, "checkout_amount"] = value
                with self.assertRaisesRegex(ValueError, message):
                    validate_experiment_data(bad)

    def test_rejects_invalid_assignment_outcome_or_timestamp(self):
        cases = [
            ("user_id", None, "user_id must be present"),
            ("variant", "Other", "variant must be"),
            ("device", "Other", "device must be"),
            ("event_time", "2024-01-31 00:00:00", "event_time must be"),
            ("converted", 2, "converted must be"),
        ]
        for field, value, message in cases:
            with self.subTest(field=field):
                bad = self.rows.copy()
                bad.loc[0, field] = value
                with self.assertRaisesRegex(ValueError, message):
                    validate_experiment_data(bad)


if __name__ == "__main__":
    unittest.main()
