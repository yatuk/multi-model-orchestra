<!-- mmo provider=opencode model=opencode/hy4-flash-free mode=rw status=ok exit=0 seconds=55 base=99f973a1a changed=1 -->
Only `durations.py` was changed. The fix enforces all five docstring rules: non-empty ASCII-digit input, numbers always followed by a unit, units in strict `h → m → s` order with no repeats, and `ValueError` for anything else (including non-string input).

`python -m unittest test_durations` passes (4/4), and extra checks for the uncovered rules pass as well.

DONE
