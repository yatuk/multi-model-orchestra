"""Orders and their items."""
from .units import QuoteError, parse_weight

PACKAGING_GRAMS = 40


class Item:
    """One line of an order.

    weight is either a weight text for parse_weight ("1.2kg") or a whole number of grams.
    qty is a whole number, at least 1.
    """

    def __init__(self, sku, weight, qty=1):
        if not isinstance(qty, int) or isinstance(qty, bool) or qty < 1:
            raise QuoteError(f"bad quantity {qty!r} for {sku}")
        if isinstance(weight, str):
            grams = parse_weight(weight)
        elif isinstance(weight, int) and not isinstance(weight, bool) and weight >= 0:
            grams = weight
        else:
            raise QuoteError(f"bad weight {weight!r} for {sku}")
        self.sku = sku
        self.grams = grams
        self.qty = qty

    def total_grams(self):
        return self.grams * self.qty


class Order:
    """A parcel to one zone.

    zone is a zone code and is case-insensitive: "eu", "Eu" and "EU" are the same zone.

    total_grams() is the sum of every item's weight times its quantity, plus
    PACKAGING_GRAMS once per order. An order with no items weighs 0 g (no packaging).
    """

    def __init__(self, zone, items=()):
        self.zone = zone
        self.items = list(items)

    def add(self, item):
        self.items.append(item)
        return self

    def total_grams(self):
        if not self.items:
            return 0
        return sum(i.total_grams() for i in self.items) + PACKAGING_GRAMS
