<!-- mmo provider=deepseek model=deepseek/deepseek-v4-pro mode=rw status=ok exit=0 seconds=89 base=d2afe8054 changed=1 -->
Fixed `parse_duration` in `durations.py`. The rewrite uses a full-match regex `([0-9]+h)?([0-9]+m)?([0-9]+s)?` that enforces every docstring rule:

- **Rule 1 (each unit at most once)** — a unit can only appear in its single optional group; `"1h1h"` fails the full match.
- **Rule 2 (order h, m, s)** — group order is fixed; `"1m1h"` fails.
- **Rule 3 (every number followed by a unit)** — digits only exist inside a `number+unit` group; `"90"` and `"1h30"` fail.
- **Rule 4 (empty invalid)** — explicit `if not text` check.
- **Rule 5 (spaces/other letters/signs invalid)** — `fullmatch` rejects any stray character, uppercase, spaces, or `+`/`-`.

All 4 visible tests pass, and extra edge cases (`1m1h`, `1h1h`, `1h30`, `1h 30m`, `-1h`, `1H`, `1x`, `h`, `30s1h`, leading/trailing space) correctly raise `ValueError`.

DONE
