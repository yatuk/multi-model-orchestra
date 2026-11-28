<!-- mmo provider=grok model=grok-4.5 mode=rw status=ok exit=0 seconds=50 base=b1124a89c changed=1 -->
The current parser ignores trailing numbers, empty input, duplicate units, and unit order. I'll fix those against the docstring rules.

DONE — `parse_duration` now enforces all five docstring rules and `python -m unittest test_durations` passes.
