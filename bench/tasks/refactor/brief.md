Refactor the `evlog` package in the current directory: replace the positional parse flags with
an options object, and make parsing streaming where the rules below say so. Behaviour must stay
the same.

Today every function takes the flags `min_level, strict, utc_offset` as extra arguments, and
callers pass them positionally (`parse_events(lines, "INFO", True, 60)`). `parse_events`
builds a list of every event, so a large log is held in memory several times over.

`test_evlog.py` is already written against the new interface and fails until you are done.
It covers only the happy path. Held-out tests check every rule below, the callers, and that
what works today keeps working.

Acceptance rules:
1. Add `ParseOptions`, a frozen dataclass defined in `evlog/reader.py` and exported from
   `evlog`, with exactly these fields in this order: `min_level: str = "DEBUG"`,
   `strict: bool = False`, `utc_offset: int = 0`. They mean what the old arguments meant.
   An unknown `min_level` raises ValueError when the ParseOptions is created.
2. New signatures, with no other parameters:
   `parse_events(lines, options=None)`, `summarize(lines, options=None)`,
   `top_messages(lines, n=3, options=None)`, `in_window(lines, start, end, options=None)`,
   `tail(lines, n=10, options=None)`, `merge(sources, options=None)`.
   `options=None` means `ParseOptions()`.
3. When `options` is neither None nor a ParseOptions, each of these six functions raises
   TypeError at the moment it is called, before it reads any line, including the ones that
   return iterators. So old-style calls like `parse_events(lines, "INFO")` fail at once.
4. `parse_events` and `in_window` return iterators and are lazy: they take a line from `lines`
   only when the caller asks for the next event, and read no further than that event needs.
   Creating the iterator reads nothing. `lines` may be any iterable of strings: a list, a
   one-shot generator, an open file.
5. In strict mode the ParseError is raised when iteration reaches the malformed line, after
   the events before it have been delivered. Messages and line numbers do not change.
6. `summarize` and `top_messages` accept a one-shot iterable and read it exactly once.
   `summarize` keeps memory independent of the number of events (no list of events or lines);
   `top_messages` keeps one count per distinct message. `tail` holds at most n events and
   still returns a list.
7. `merge` keeps returning a list, with exactly the results it gives today for every input,
   including sources that are not in time order themselves. It is exempt from rule 4.
8. `evlog.cli.main(argv=None, out=None)`: same command line, same output, same return codes.
   It must not read the whole file into memory; it may open the file twice.
9. Everything else stays as it is: `Event`, `ParseError`, `LEVELS`, the line format, return
   values, error messages, and the meaning of every rule in the docstrings.

Constraints: change only files inside `evlog/`. Do not edit, delete or add test files.
Standard library only. Run `python -m unittest test_evlog` and make sure it passes.
Do not commit. Finish with one line: DONE or FAILED and the reason.
