<!-- mmo provider=agy model=claude-sonnet-5-5-high mode=rw status=ok exit=0 seconds=30 base=5993ac539 changed=1 -->
PowerShell mangled the quoting, so the edit didn't apply. I'll edit the file directly instead.
File unchanged. Rewriting it.
DONE: `parse_duration` in `durations.py` now follows rules 1–5, and `python -m unittest test_durations` passes. I also checked cases the visible tests don't cover (`1m1h`, `1h1h`, `1h30`, signs, spaces, uppercase, non-ASCII digits, a trailing newline, a bare `h`), and all of them raise `ValueError`.
