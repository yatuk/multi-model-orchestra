<!-- mmo provider=opencode model=opencode/deepseek-v4.1-flash-free mode=rw status=ok exit=0 seconds=22 base=0c54c1f8b changed=1 -->
Only `durations.py` changed. The parser now rejects duplicates, out-of-order units, missing numbers/units, empty input, and any stray characters (including unicode digits, signs, and whitespace), while keeping the signature.

DONE — `parse_duration` enforces all rules 1–5 and `python -m unittest test_durations` passes (4 tests OK).
