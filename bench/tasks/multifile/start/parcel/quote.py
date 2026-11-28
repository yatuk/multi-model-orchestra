"""Quotes: what a parcel costs to ship."""
import math

from .rates import bracket_price, extra_per_kg, table_for
from .surcharge import apply_fuel
from .units import QuoteError


def quote(order, fuel_percent=0):
    """Return the shipping price of `order` in cents.

    1. The weight is order.total_grams(). A weight of 0 g raises QuoteError.
    2. The zone's table gets the fuel surcharge (see surcharge.py).
    3. The price is that of the first bracket that holds the weight (see rates.py).
    4. Above the last bracket: the last bracket's price (with fuel) plus the zone's
       extra fee for every started kilogram above it, without fuel.
    Quoting has no side effects: the same order and percent always give the same price.
    """
    grams = order.total_grams()
    if grams <= 0:
        raise QuoteError("empty parcel")
    table = apply_fuel(table_for(order.zone), fuel_percent)
    price = bracket_price(table, grams)
    if price is not None:
        return price
    max_grams, last_price = table[-1]
    started_kg = math.ceil((grams - max_grams) / 1000)
    return last_price + started_kg * extra_per_kg(order.zone)


def format_cents(cents):
    """12345 -> "123.45"."""
    return f"{cents // 100}.{cents % 100:02d}"


def quote_text(order, fuel_percent=0):
    """One line for the order page, for example "EU 12.50 EUR (1.240 kg)".

    The zone code is always shown in capitals.
    """
    cents = quote(order, fuel_percent)
    grams = order.total_grams()
    return f"{order.zone} {format_cents(cents)} EUR ({grams // 1000}.{grams % 1000:03d} kg)"
