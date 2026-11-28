"""parcel: shipping quotes for small parcels.

Public API (names and signatures are fixed; other modules import them):
    parse_weight(text) -> int            grams, see units.py
    Item(sku, weight, qty=1)             see order.py
    Order(zone, items=())                see order.py
    table_for(zone) -> list              see rates.py
    apply_fuel(table, percent) -> list   see surcharge.py
    fuel_amount(price_cents, percent)    see surcharge.py
    quote(order, fuel_percent=0) -> int  cents, see quote.py
    quote_text(order, fuel_percent=0)    see quote.py
    QuoteError                           raised for every invalid input
"""
from .units import QuoteError, parse_weight
from .order import Item, Order
from .rates import table_for, extra_per_kg
from .surcharge import apply_fuel, fuel_amount
from .quote import quote, quote_text, format_cents

__all__ = [
    "QuoteError", "parse_weight", "Item", "Order", "table_for", "extra_per_kg",
    "apply_fuel", "fuel_amount", "quote", "quote_text", "format_cents",
]
