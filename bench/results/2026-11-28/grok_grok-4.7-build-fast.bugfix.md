<!-- mmo provider=grok model=grok-4.7-build-fast mode=rw status=ok exit=0 seconds=37 base=b1124a89c changed=1 -->
I'll read `durations.py` and its tests first, then fix `parse_duration` so every docstring rule holds.

The current parser ignores trailing numbers, repeated units, and bad order. I'll implement the five docstring rules and run the tests.

DONE: `parse_duration` enforces all five docstring rules and `python -m unittest test_durations` passes.
