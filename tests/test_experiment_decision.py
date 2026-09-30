import unittest

from experiment_decision import ALPHA, conversion_conclusion


class ConversionConclusionTests(unittest.TestCase):
    def test_significant_variant_improvement(self):
        self.assertEqual(
            conversion_conclusion(0.01, 0.02),
            "Variant has a statistically significant higher conversion rate.",
        )

    def test_significant_control_improvement(self):
        self.assertEqual(
            conversion_conclusion(0.01, -0.02),
            "Control has a statistically significant higher conversion rate.",
        )

    def test_nonsignificant_difference(self):
        expected = "No statistically significant conversion-rate difference."
        self.assertEqual(conversion_conclusion(0.20, 0.02), expected)
        self.assertEqual(conversion_conclusion(ALPHA, -0.02), expected)

    def test_invalid_test_result_fails(self):
        with self.assertRaises(ValueError):
            conversion_conclusion(float("nan"), 0.02)
        with self.assertRaises(ValueError):
            conversion_conclusion(0.01, 0.0)


if __name__ == "__main__":
    unittest.main()
