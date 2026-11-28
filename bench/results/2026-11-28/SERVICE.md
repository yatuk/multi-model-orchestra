# service task, 2026-11-28

`BENCH_TASKS=service`, one task, 8 lane runs (2 per lane), run one at a time on one Windows machine, graded
offline by `bench/grade.py service`. Score = share of 59 hidden tests. Group columns: NewBehaviour /10,
BugFix /8, KeepWorking /28, LateCancel /6, OldData /7. Seconds = wall time reported by `mmo-run`.
"Last line" is what the lane ended its report with (the brief asks for DONE or FAILED).

| Lane | Run | Score | New | Bug | Keep | Late | Old | Seconds | Status | Last line |
|---|---|---|---|---|---|---|---|---|---|---|
| deepseek:deepseek/deepseek-flash | 1 | 1.00 | 10 | 8 | 28 | 6 | 7 | 258 | ok | DONE |
| deepseek:deepseek/deepseek-flash | 2 | 1.00 | 10 | 8 | 28 | 6 | 7 | 189 | ok | DONE |
| claude:sonnet | 1 | 1.00 | 10 | 8 | 28 | 6 | 7 | 141 | ok | no DONE line |
| claude:sonnet | 2 | 1.00 | 10 | 8 | 28 | 6 | 7 | 81 | ok | no DONE line |
| claude:opus | 1 | 1.00 | 10 | 8 | 28 | 6 | 7 | 272 | ok | DONE |
| claude:opus | 2 | 1.00 | 10 | 8 | 28 | 6 | 7 | 191 | ok | DONE |
| grok:grok-4.7 | 1 | 0.97 | 10 | 6 | 28 | 6 | 7 | 927 | ok | DONE |
| grok:grok-4.7 | 2 | 0.97 | 10 | 6 | 28 | 6 | 7 | 1061 | ok | DONE |

Offline headroom for comparison (`bench/test-grade.sh`): reference 1.00, starting code 0.59, the six
plausible wrong patches 0.86 to 0.95.

Both Grok runs missed the same thing: they fixed the importer and rewrote old imported rows, but not the
series writer, which stores timestamps with seconds (a booking right after a series meeting is refused,
and the room shows busy at the minute the meeting ends). Both reported DONE.
