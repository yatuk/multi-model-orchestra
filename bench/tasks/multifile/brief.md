The `parcel` package in the current directory computes shipping quotes. A bug report:

> Quotes drift. When a page quotes the same parcel twice with a fuel surcharge, the second
> price is higher than the first. Restarting the service makes the first quote right again.
> `python -m unittest test_parcel` fails, although most of its tests pass when run one by one.

Fix the package.

Rules:
1. Read the whole package (`parcel/*.py`) and `test_parcel.py` first. The docstrings are the
   specification. After your change every rule in every docstring must hold, including rules the
   visible tests do not check.
2. Find the cause; do not only make the visible test pass. Held-out tests check the documented
   behaviour of each public function, and that everything that works now keeps working.
3. Keep every public name and signature listed in `parcel/__init__.py`.
4. Change only files inside `parcel/`. Do not edit, delete or add test files. Standard library only.
5. Run `python -m unittest test_parcel` and make sure it passes.

Do not commit. Finish with one line: DONE or FAILED and the reason.
