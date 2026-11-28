<!-- mmo provider=opencode model=opencode/seaglass-alpha-free mode=rw status=ok exit=0 seconds=94 base=006b5b96d changed=1 -->
All checks passed: `python -m unittest test_durations` → OK (4 tests), plus my own edge-case verification of rules 1–5 (repeated/out-of-order units, missing numbers, empty string, spaces/signs/other letters/Unicode digits, non-string input, huge numbers). Only `durations.py` was modified; no test files, no new dependencies, nothing committed.

DONE
