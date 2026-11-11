<!-- mmo provider=deepseek model=deepseek/deepseek-v4-pro mode=rw status=ok exit=0 seconds=49 -->
All checks pass. The `'1h0s'` line was a mislabeled test on my end — `1h0s` is actually valid (`1h` + `0s`), so no bug there.

Verified behavior:
- Rule 1 (each unit once): `1h1h` → `ValueError`
- Rule 2 (order h→m→s): `1m1h`, `1s1m` → `ValueError`
- Rule 3 (number needs a unit): `90`, `1h30` → `ValueError`
- Rule 4 (empty): `""` → `ValueError`
- Rule 5 (spaces/letters/signs): ` 1h`, `1h 30m`, `1x`, `-1h`, `+1h`, `1h-30m` → `ValueError`
- Bare units: `h`, `m` → `ValueError`
- Valid: `45s`, `2h5s`, `0h0m0s`, `1h30m15s` all correct
- `python -m unittest test_durations` → 4 tests OK

DONE
