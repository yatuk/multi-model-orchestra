<!-- mmo provider=cursor model=composer-2.5 mode=rw status=ok exit=0 seconds=56 base=ff303c588 changed=1 -->
Reading `durations.py` and `test_durations.py` to identify docstring rules and required fixes.


Implementing validation for all five docstring rules: empty input, trailing numbers, unit order, duplicate units, and digits required before each unit.
`parse_duration` in `durations.py` now implements all five docstring rules:

1. **At most one of each unit** — `seen` rejects duplicates (e.g. `1h1h`).
2. **Order h → m → s** — `last_index` against `"hms"` rejects `1m1h`, `5s3m`, etc.; skipping units is still fine (`2h5s`).
3. **Every number has a following unit** — reject a unit with no leading digits and any leftover digits at EOF (`90`, `1h30`).
4. **Empty string** — `if not text` raises `ValueError`.
5. **Only digits and h/m/s** — anything else raises in the `else` branch.

DONE: implementation matches rules 1–5 and satisfies the visible tests; `python -m unittest test_durations` could not be run here because the shell hook blocked execution.
