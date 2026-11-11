<!-- mmo provider=deepseek model=deepseek/deepseek-flash mode=rw status=ok exit=0 seconds=14 -->
Fixed `parse_duration` in `durations.py:7`. The parser now tracks the position of the last seen unit and enforces the docstring rules the original code skipped:

- Duplicate or out-of-order units (`1h1h`, `1m1h`, `1s1m`) now raise `ValueError` (rules 1–2).
- A unit with no preceding number (`h`, `1hh`) now raises instead of silently adding 0, and a trailing number is rejected at end-of-string rather than being dropped (rule 3).
- Empty input is rejected explicitly (rule 4).
- Digit detection is restricted to ASCII `0-9`, so exotic Unicode digits and any other stray character are rejected (rule 5).

Verified: `python -m unittest test_durations` passes 4/4, and a separate ad-hoc check of the uncovered cases (out-of-order/duplicate units, bare units, `-1h`, `1.5h`, spaces/tabs, other letters) behaves per the docstring.

DONE — all five docstring rules enforced and the test suite passes.
