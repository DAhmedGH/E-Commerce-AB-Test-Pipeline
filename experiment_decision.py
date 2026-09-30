"""Decision rule for the checkout experiment's primary conversion metric."""

from math import isfinite


ALPHA = 0.05


def conversion_conclusion(p_value: float, variant_minus_control: float) -> str:
    """Interpret a two-sided conversion test using its p-value and effect direction."""
    if not isfinite(p_value) or not 0 <= p_value <= 1:
        raise ValueError("Conversion p-value must be between 0 and 1")
    if not isfinite(variant_minus_control):
        raise ValueError("Conversion-rate difference must be finite")
    if p_value >= ALPHA:
        return "No statistically significant conversion-rate difference."
    if variant_minus_control > 0:
        return "Variant has a statistically significant higher conversion rate."
    if variant_minus_control < 0:
        return "Control has a statistically significant higher conversion rate."
    raise ValueError("A significant test must have a nonzero conversion-rate difference")
