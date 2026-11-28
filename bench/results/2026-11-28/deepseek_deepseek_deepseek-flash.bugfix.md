<!-- mmo provider=deepseek model=deepseek/deepseek-flash mode=rw status=ok exit=0 seconds=15 base=d2afe8054 changed=1 -->
Visible tests pass, all invalid edge cases from rules 1–5 are rejected, and valid durations return the right totals.

`durations.py` now: rejects empty input, trailing numbers (`"90"`, `"1h30"`), units without a number (`"h"`), repeated or out-of-order units (`"1h1h"`, `"1m1h"`), non-ASCII digits (`"٣s"`), and any other stray character; `"1h30m15s"` → 5415.

DONE — all five docstring rules enforced in `durations.py`; `python -m unittest test_durations` passes (4 tests OK).
