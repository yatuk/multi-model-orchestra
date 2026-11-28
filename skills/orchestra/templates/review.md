You are reviewing a change you did not write. You have not seen how it was made, on purpose.

The task that was given: <the outcome and constraints from the brief>
The diff: <path to the diff file, or `git diff <base>` in this checkout>
The check that passed: `<command>`

Answer two questions, in this order:
1. Does the diff do what the task asked, all of it, and nothing more? List anything missing and
   anything extra (files touched outside the task, behaviour changed that was not asked for).
2. Is it correct? Look for: wrong results on inputs the tests do not cover, tests that were weakened
   or that would pass without the change, inputs special-cased to satisfy a test, errors swallowed.

Rules: report only problems that change behaviour, each with evidence (file and line, an input that
breaks it, or a command and its output). No style notes, no naming, no "consider". If you find
nothing, say "no correctness problems found" and stop; do not invent one.

Read-only: do not change any file.
