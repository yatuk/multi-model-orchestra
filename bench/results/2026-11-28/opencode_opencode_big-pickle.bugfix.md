<!-- mmo provider=opencode model=opencode/big-pickle mode=rw status=ok exit=0 seconds=34 base=0c54c1f8b changed=1 -->
`durations.py` now enforces all five rules: strictly increasing unit order (which also prevents repeats), a number before every unit, a unit after every number, non-empty input, and ASCII digits/valid characters only. Only `durations.py` was modified. `python -m unittest test_durations` passes (4 tests), and additional checks of uncovered edge cases passed.

DONE
