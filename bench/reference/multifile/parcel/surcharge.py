"""Fuel surcharge.

The carrier publishes a fuel surcharge as a whole percent from 0 to 50. It is added to
bracket prices only, never to the over-weight fee.
"""
from .units import QuoteError


def check_percent(percent):
    if not isinstance(percent, int) or isinstance(percent, bool) or not 0 <= percent <= 50:
        raise QuoteError(f"fuel percent must be a whole number 0..50, got {percent!r}")
    return percent


def fuel_amount(price_cents, percent):
    """Surcharge on one price: price_cents * percent / 100, rounded half up to a whole cent."""
    check_percent(percent)
    # Integer half up; round() would round halves to even (24.5 -> 24).
    return (price_cents * percent + 50) // 100


def apply_fuel(table, percent):
    """Return a new table with the fuel surcharge added to every bracket price.

    The table passed in is not changed.
    """
    check_percent(percent)
    # A new list: table_for returns the cached table, and changing it would make
    # every later quote for the zone pay the surcharge again.
    return [(max_grams, price + fuel_amount(price, percent)) for max_grams, price in table]
