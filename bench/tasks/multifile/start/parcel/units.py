"""Weights. Inside the package every weight is a whole number of grams."""
import math
import re
from fractions import Fraction


class QuoteError(ValueError):
    """Any invalid input to the package."""


# Exact factors, so "1lb" is 453.59237 g before rounding and never 453.5923699999.
GRAMS_PER_UNIT = {
    "g": Fraction(1),
    "kg": Fraction(1000),
    "lb": Fraction(45359237, 100000),
    "oz": Fraction(45359237, 1600000),
}

_WEIGHT = re.compile(r"(\d+(?:\.\d+)?)(kg|g|lb|oz)")


def parse_weight(text):
    """Return the weight written in `text` as whole grams, rounded up.

    Rules:
    1. The text is a plain decimal number followed directly by a unit: g, kg, lb or oz
       (lower case). No sign, no exponent, no spaces, no thousands separator.
    2. The value is converted exactly and rounded UP to a whole gram:
       "250g" -> 250, "1.2kg" -> 1200, "1lb" -> 454, "0.5oz" -> 15, "0.1g" -> 1.
    3. Zero is a valid weight ("0g" -> 0).
    Anything else raises QuoteError.
    """
    if not isinstance(text, str):
        raise QuoteError(f"weight must be text, got {type(text).__name__}")
    m = _WEIGHT.fullmatch(text)
    if not m:
        raise QuoteError(f"bad weight {text!r}")
    grams = Fraction(m.group(1)) * GRAMS_PER_UNIT[m.group(2)]
    return math.ceil(grams)
