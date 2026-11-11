Fix `parse_duration` in `durations.py` so it follows every rule in its docstring.

Steps:
1. Read `durations.py` and `test_durations.py` in the current directory.
2. Change only `durations.py`. Keep the function name and signature.
3. Every rule 1-5 in the docstring must hold, including rules the visible tests do not cover.
4. Run `python -m unittest test_durations` and make sure it passes.

Out of scope: do not edit or add test files, do not add dependencies, do not commit.
Finish with one line: DONE or FAILED and the reason.
