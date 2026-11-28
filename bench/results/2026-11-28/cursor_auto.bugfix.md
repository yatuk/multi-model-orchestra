<!-- mmo provider=cursor model=auto mode=rw status=ok exit=0 seconds=156 base=fba01b306 changed=3 committed=yes -->
I'll read `durations.py` and `test_durations.py`, then fix `parse_duration` to match all docstring rules.The current parser skips empty input, trailing numbers, duplicate units, and unit order. I'll fix those so all five docstring rules hold.The shell hook rejected that run; retrying the tests.An otomode hook is intercepting the shell — checking what's configured.Retrying the test run with smart-mode approval after the hook block.Updated `parse_duration` for all five docstring rules: empty input, trailing numbers, duplicate units, h→m→s order, and invalid characters.

FAILED: could not run `python -m unittest test_durations` (otomode shell hook syntax error)
