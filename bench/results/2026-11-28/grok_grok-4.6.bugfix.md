<!-- mmo provider=grok model=grok-4.6 mode=rw status=ok exit=0 seconds=33 base=b1124a89c changed=1 -->
I'll read the duration parser and its tests first, then implement every docstring rule.

The current parser ignores trailing numbers, empty input, duplicate units, and unit order. I'll fix those so all five docstring rules hold.

`parse_duration` now rejects empty input, numbers without a unit, duplicate units, out-of-order units, and any character that is not an ASCII digit or `h`/`m`/`s`. Visible tests passed.

DONE all five docstring rules implemented and `python -m unittest test_durations` passed.
