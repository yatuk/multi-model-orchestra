<!-- mmo provider=opencode model=opencode/flint-40b-free mode=rw status=ok exit=0 seconds=46 base=0c54c1f8b changed=1 -->
`DONE` — `parse_duration` now enforces all docstring rules (at-most-once units, strict h→m→s ordering, numbers always followed by a unit, empty string rejected, any other character rejected), keeps the name/signature, and `python -m unittest test_durations` passes all 4 tests.
