<!-- mmo provider=agy model=claude-opus-5-5-high mode=rw status=ok exit=0 seconds=25 base=5993ac539 changed=1 -->
I rewrote `parse_duration` in [durations.py](<workdir>/durations.py), and `python -m unittest test_durations` passes (4/4). I also ran an ad-hoc edge-case check outside the test file: it rejected every invalid input I tried and returned the right values for the valid ones.

The function now checks the whole string against one pattern that only allows `<digits>h`, then `<digits>m`, then `<digits>s`, each optional. Here's how that covers the rules:

- **Rules 1 and 2 (at most once, in h-m-s order):** `1m1h` and `1h1h` now raise `ValueError`. The old code accepted both.
- **Rule 3 (every number needs a unit):** `90` and `1h30` are rejected. A unit with no number in front, like `h` or `1hm`, is also rejected; before, it was quietly counted as 0.
- **Rule 4 (empty string):** `""` raises `ValueError`.
- **Rule 5 (anything else):** spaces, signs, other letters and a trailing newline are all rejected. Only ASCII digits 0–9 count as numbers, so characters like `²` or Arabic-Indic digits, which `str.isdigit()` would have accepted, are now refused.

One addition you didn't ask for: input that isn't a string also raises `ValueError`.

DONE — all five docstring rules are enforced and the tests pass.
