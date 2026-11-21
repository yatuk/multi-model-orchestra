# Four tasks

Python 3 standard library only. Run all visible tests with `python -m unittest`.
Do not edit or delete the existing `test_*.py` files. Do not add dependencies.
The tasks are independent of each other. Hidden tests will check every rule below,
including rules the visible tests do not cover.

## Task 1 (bugfix): `intervals.py`

`merge()` does not follow its docstring. Fix it so every rule 1-7 in the docstring holds.
Input items may be tuples or lists; output items are tuples.

## Task 2 (feature): TTL for `cache.py`

Add optional expiry to `LRUCache`: `LRUCache(capacity, ttl=None, clock=None)`.

- `clock` is a zero-argument callable returning seconds; default `time.monotonic`. Store it as `self.clock`.
- `ttl=None` means entries never expire. A `ttl` that is not None must be > 0, else `ValueError`.
- An entry put at time `t` is expired when `clock() - t >= ttl`.
- `put` on an existing key replaces the value and restarts its TTL. `get` does not restart the TTL
  (it still marks the key as most recently used).
- An expired entry behaves as absent everywhere: `get` returns the default, `in` is False,
  `len()` does not count it, and it does not take up capacity (a `put` evicts expired entries
  before it evicts the least recently used live one).
- Everything that works today keeps working.

## Task 3 (refactor with tests): `report.py`

`summarize()` is one long function. Split it into these module-level helpers and make
`summarize()` a short function that uses them (at most 12 non-blank, non-comment lines in its body):

- `group_totals(orders) -> dict`: `{customer: (net_cents, order_count)}`. Cancelled orders are skipped;
  refunded orders subtract their amount and still count as an order.
- `rank(totals) -> list`: customer names from a `group_totals` result, by net total descending, ties by name ascending.
- `format_cents(cents) -> str`: `-305 -> "-3.05"`, `7 -> "0.07"`.

The output of `summarize()` must stay exactly the same for every input.
Add a new test file `test_report_parts.py` with at least three passing tests for the helpers.

## Task 4 (parser): `query.py`

Implement `parse(text)` and `matches(text, record)` for this filter language:

```
expr       := or_expr
or_expr    := and_expr ("OR" and_expr)*          left-associative
and_expr   := not_expr ("AND" not_expr)*         left-associative
not_expr   := "NOT" not_expr | primary
primary    := "(" expr ")" | comparison
comparison := FIELD OP VALUE
FIELD      := [A-Za-z_][A-Za-z0-9_]* ("." [A-Za-z_][A-Za-z0-9_]*)*
OP         := "=" | "!=" | "<" | "<=" | ">" | ">="
VALUE      := integer (optional leading "-") | string | true | false | null
string     := double-quoted; \" is a quote and \\ is a backslash
```

- `AND`, `OR`, `NOT`, `true`, `false`, `null` are case-insensitive. Whitespace between tokens is optional and ignored.
- AST nodes are tuples: `("cmp", field, op, value)`, `("not", node)`, `("and", left, right)`, `("or", left, right)`.
  Values are Python `int`, `str`, `True`, `False` or `None`.
- Any error raises `ParseError(message, pos)` (already defined). `pos` is the 0-based index of the first
  character of the offending token; if input ended too early, `pos = len(text)`. An unterminated string
  is reported at its opening quote. Examples: `"" -> 0`, `"a = " -> 4`, `"a == 1" -> 3`, `"a = 1)" -> 5`,
  `"(a = 1" -> 6`, `"a = 1 b = 2" -> 6`.

`matches(text, record)` parses `text` and evaluates it against the dict `record`:

- A dotted field walks nested dicts. If any part is missing, the comparison is False (and `NOT` of it is True).
- `= null` is True when the value is None; `!= null` is True when the field exists and is not None.
- Numbers compare with numbers (int and float mix). Strings compare with strings. `bool` is not a number:
  `True = 1` is False. Any other type mix makes the comparison False, for every operator.
