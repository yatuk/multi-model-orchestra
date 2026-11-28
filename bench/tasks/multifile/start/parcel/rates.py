"""Rate tables per zone.

A table is a list of (max_grams, price_cents) brackets with max_grams ascending.
A parcel goes in the first bracket whose max_grams is greater than or equal to its
weight: a parcel of exactly 500 g is in the 500 g bracket, 501 g is in the next one.
"""
from .units import QuoteError

_ZONES = {
    "DOM": [(500, 450), (1000, 625), (2000, 890), (5000, 1225)],
    "EU": [(500, 990), (1000, 1250), (2000, 1690), (10000, 2450)],
    "WORLD": [(500, 1890), (2000, 3125), (10000, 5290)],
}

# Fee for every started kilogram above the last bracket (1 g over counts as 1 kg).
_EXTRA_PER_KG = {"DOM": 180, "EU": 260, "WORLD": 640}

# Built tables, one per zone. Building is cheap here; in the real service it reads a file.
_CACHE = {}


def table_for(zone):
    """Return the bracket table for `zone` ("DOM", "EU" or "WORLD", any case).

    Tables are built once per zone and cached, so callers must treat the list they get
    as read-only. An unknown zone raises QuoteError.
    """
    key = zone.upper() if isinstance(zone, str) else zone
    if key not in _ZONES:
        raise QuoteError(f"unknown zone {zone!r}")
    if key not in _CACHE:
        _CACHE[key] = [tuple(b) for b in _ZONES[key]]
    return _CACHE[key]


def extra_per_kg(zone):
    """Fee in cents for every started kilogram above the zone's last bracket."""
    if zone not in _EXTRA_PER_KG:
        raise QuoteError(f"unknown zone {zone!r}")
    return _EXTRA_PER_KG[zone]


def bracket_price(table, grams):
    """Price of the bracket for `grams`, or None when the parcel is above the last bracket."""
    for max_grams, price in table:
        if grams <= max_grams:
            return price
    return None
