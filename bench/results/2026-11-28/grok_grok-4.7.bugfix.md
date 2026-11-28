<!-- mmo provider=grok model=grok-4.7 mode=rw status=ok exit=0 seconds=50 base=b1124a89c changed=1 -->
I'll read `durations.py` and `test_durations.py`, then fix `parse_duration` so every docstring rule holds.

The parser accepts empty input, leftover numbers, repeated units, and out-of-order units. I'll enforce all five docstring rules.

DONE: `parse_duration` follows docstring rules 1-5 and `python -m unittest test_durations` passes.
