<!-- mmo provider=deepseek model=deepseek/deepseek-flash mode=rw status=ok exit=0 seconds=17 -->
`parse_duration` now validates the whole string against `(?:[0-9]+h)?(?:[0-9]+m)?(?:[0-9]+s)?` with `fullmatch`, so:

- Rules 1-2: the ordered, non-repeating optional groups reject `"1h1h"`, `"1m1h"`, `"1s1m"`.
- Rule 3: digits are only matched inside a `<number><unit>` group, rejecting `"90"`, `"1h30"`, and bare units like `"h"`.
- Rule 4: an explicit check rejects `""` before matching (an all-optional pattern would otherwise match it).
- Rule 5: `[0-9]` (not `\d` or `str.isdigit`) rejects non-ASCII digits, and full-match rejects spaces, signs, other letters, and suffixes.

Verified: `python -m unittest test_durations` passes (4/4), plus a manual sweep of valid and invalid edge cases all behaved correctly.

DONE — all rules 1-5 enforced, only `durations.py` changed, tests pass.
