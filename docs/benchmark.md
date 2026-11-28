# Benchmark

[Back to the README](../README.md)

Two kinds of measurement live in `bench/`:

- **Lane benchmark** (`bench/run.sh`): does each external lane work end to end, and is it good enough for a job.
- **A/B test** (`bench/ab/`): does the orchestra skill beat just telling the main model "use subagents".

Both are small. Read them as smoke tests, not leaderboards.

## Lane benchmark

`bench/run.sh` runs six tasks on every lane in parallel and grades them with no model in the loop
(`BENCH_TASKS="bugfix multifile" bench/run.sh ...` runs a subset):

| Task | Mode | Graded by |
|---|---|---|
| **bugfix**: fix a duration parser so it follows five written rules | rw, own worktree | visible tests must pass and stay unedited; score = share of 6 hidden tests passed |
| **reasoning**: two Python trace questions and one counting question, no running code | ro | exact match against answers computed by running the code |
| **bulk**: label 60 log lines CRITICAL / ERROR / WARN / INFO by first-match rules with traps (`panicked`, `errorless`, 404) | ro | accuracy against gold labels generated from the same rules |
| **multifile**: a 6-file shipping-quote package; the failing test points at `quote()`, the cause is elsewhere, and two more documented defects have no visible test | rw, own worktree | share of 15 hidden tests in four groups |
| **refactor**: replace positional parse flags with an options object and make parsing streaming, across six functions and a CLI | rw, own worktree | share of 20 hidden tests in four groups |
| **spec**: apply a written retention policy (precedence, boundaries, an exception to an exception, a rule that depends on another artifact's result) to 20 artifacts | ro | exact `ID DECISION RULE` per artifact, gold from a reference implementation |
| **service** (opt-in, not in the default list): a ticket against a 2,300-line booking application; a feature across five layers, a buried bug, a migration | rw, own worktree | share of 59 hidden tests in five groups |

### The harder tasks (multifile, refactor, spec)

On 2026-11-28 nearly every lane, free models included, got full marks on the first three tasks, so they
show whether a lane works, not how good it is. The three newer tasks are meant to leave headroom.

- **multifile** separates lanes that find a cause from lanes that patch a symptom. The report says "the
  second quote is higher"; the cause is a function in another module that changes a cached table it was
  told not to change. Two quieter defects have no visible test: the docstring says surcharges round half
  up, the code uses Python's `round()`, which rounds halves to even; and zone codes are documented as
  case-insensitive, which holds for the table lookup but not for the over-weight fee or the quote text.
  A symptom patch (clearing the cache before every quote) passes every visible test and scores 0.53;
  answering the visible inputs from a table scores 0.40.
- **refactor** separates lanes that read acceptance rules precisely from lanes that make the visible tests
  green. The visible tests use the new interface on the happy path only. The hidden tests check that old
  positional calls fail with TypeError at call time (a plain generator function delays that), that the
  iterators are lazy, that `summarize` keeps flat memory (checked with `tracemalloc`), that strict-mode
  errors arrive after the events before them, that `tail` holds only n events, and that the callers and
  the CLI behave as before. `merge` is the trap in the other direction: it must keep sorting, because a
  streaming `heapq.merge` changes its results for sources that are not in time order (0.90). A shim that
  puts the new interface on top of a list scores 0.75.
- **spec** separates careful rule application from pattern matching, without arithmetic: a pinned artifact
  that loses its protection and is then saved by its tag, `releases/old` that is not a release branch,
  2048 MB that is not "larger than 2048 MB", downloads that save an artifact except on a feature branch.
  Rule 8 makes logs and reports follow their binary's result, with its own exceptions, so some answers
  depend on another row, sometimes a later one. Each answer must name the rule that decided it, so a right
  decision for the wrong reason is wrong.

How grading resists bent tests:

- The lane works in a scratch repo that holds only the task's `start/` files. Hidden tests live in
  `bench/tasks/<task>/hidden/` and reference solutions in `bench/reference/`; `run.sh` copies neither.
- `grade.py` copies only the lane's package into a fresh directory, adds its own pristine copies of the
  visible and hidden tests, and runs them there with `python -I` and a small stdlib runner
  (`bench/hidden_runner.py`). Test files the lane wrote or changed in its worktree are never run.
- A lane's own verdict does not zero its work: when the status header is not `ok`, or the last line says
  FAILED or BLOCKED, the worktree is graded anyway and the detail starts with `lane status=<status>; ` or
  `lane said FAILED; `; only an unchanged worktree scores 0 (`lane failed: <status>, no changes`).
- A visible test that was edited or deleted caps the task at 0, and the detail column says which file and
  what the score on pristine tests would have been. Line endings changed by a checkout do not count.
- The total comes from the test source, not from what ran, so a package that breaks the import or hides
  a test cannot shrink the denominator. Public names the hidden tests use are checked and reported.
- `bench/test-grade.sh` (offline, in CI) proves it: each reference solution scores 1.00, the starting
  code scores 0.33 (multifile) and 0.35 (refactor) because some hidden tests already pass and must keep
  passing, an edited or deleted visible test gets 0.00 with the reason, and special-casing scores low.

Honest limits:

- Still small: a few hundred lines per task, one sitting, Python only. A lane that is good here may still
  fail on a large codebase.
- One run per lane is noise. A one-test difference on these tasks is within run-to-run variation; rerun
  before reading anything into it.
- A write task measures the lane, not the model: the agent harness (whether it can run the tests, how many
  turns it gets, how it edits files) matters as much as the model. The `claude` lane in rw mode, for
  example, could edit but not run Python unattended until its write mode got `--allowedTools Bash`; it
  then honestly reported FAILED, and `run.sh` used to score a failed lane 0 whatever its diff contained.
  It now grades the diff and keeps the lane's status in the detail.
- The grader is not a sandbox. It defeats edited tests and planted test files, not code written to detect
  the grader at run time; read the diff (`<lane>.<task>.diff`) when a score looks too good.
- The tasks and their answers are public in this repo, so a model trained on it after publication could
  have seen them.

#### Calibration, 2026-11-28: the harder tasks do not separate these two lanes

Before publishing, the new tasks ran on two lanes, one run each: DeepSeek flash (a cheap lane) and Claude
Sonnet (a middle lane). First version:

| Task | deepseek-flash score | s | claude sonnet score | s |
|---|---|---|---|---|
| multifile (12 tests) | 1.00 | 57 | 0.00 lane failed (diff graded by hand: 1.00) | 33 |
| refactor (16 tests) | 1.00 | 84 | 0.00 lane failed (diff graded by hand: 1.00) | 67 |
| spec (rules 1-7) | 1.00 | 11 | 1.00 | 14 |

Both lanes solved everything, so each task was made harder once (the versions now in the repo): multifile
lost its worked rounding examples and gained the zone defect, refactor gained `tail` and `merge`, spec
gained rule 8. Second run:

| Task | deepseek-flash score | s | claude sonnet score | s |
|---|---|---|---|---|
| multifile (15 tests) | 1.00 | 66 | 0.00 lane failed (diff graded by hand: 1.00) | 36 |
| refactor (20 tests) | 1.00 | 145 | 0.00 lane failed (diff graded by hand: 1.00) | 59 |
| spec (rules 1-8) | 1.00 | 26 | 1.00 | 17 |

"Lane failed" is the harness: Sonnet fixed both packages correctly, could not run Python, and said so.

What this means: small, fully specified, single-sitting tasks do not separate a cheap current model from a
middle one; both read every docstring and every acceptance rule. The tasks are kept because they still
give partial credit to symptom patches and zero to test editing (the starting code and the constructed
cheats in `bench/test-grade.sh` score 0.33 to 0.90), and a weaker free model may miss the quiet defects;
that has not been measured yet. To
separate strong tiers you would need larger code with less written down, repeated runs, or cost and time
as the measure rather than pass rate.

### The large task: service (opt-in)

`service` is the next step after that calibration: a realistic internal tool instead of a small package.
`roombook` is a meeting-room booking application of about 2,300 lines of stdlib Python in 47 files (36 with
code): time parsing, a domain model, sqlite storage with schema upgrades and JSON backups, a rules engine,
free-slot search and weekly series, reports (listing, usage, finance CSV, iCalendar, digest), an audit log,
an outbox, and a CLI. Settings live in three places (defaults, an ini file, environment variables), and
some conventions are visible only in neighbouring code (every change goes through `clock.now()` and writes
an audit row). The brief is a ticket in user terms, naming no files or functions:

- **Feature:** cancelling keeps the booking (who, when, reason), shows it in `show` and in the day listing,
  frees the room everywhere else, adds a `cancelled` column to the usage report, keeps cancellations in
  backups, and must keep existing databases and backup files working.
- **Easy to miss:** a late cancellation (inside the notice period the cancel command already warns
  about) still counts in the usage report's bookings and hours. That needs the cancel time recorded and the
  configured period, not a hard-coded 24.
- **Conflict:** "the day listing shows cancelled bookings" collides with a visible test of the tsv listing
  other teams' scripts read; the tsv must not change.
- **Bug:** double bookings over imported meetings. The cause is far from the symptom: the importer stores
  `2030-01-08T09:00`, the store compares timestamps as text, and `T` sorts after a space. Series rows store
  seconds, a quieter form of the same defect.

Five hidden groups, 59 tests, each scored in the detail column: **NewBehaviour** (10, end to end),
**BugFix** (8: the symptom, re-import duplicates, status and ordering, rows imported before the fix, and the
series form), **KeepWorking** (28 pass-to-pass tests over behaviour the ticket does not change, including
every reader that must not see cancelled bookings), **LateCancel** (6) and **OldData** (7: v1 and v2
databases built by hand, format 1 and 2 backups). The visible tests (10) cover only part of NewBehaviour
and the happy path. The suite runs in about 4 seconds.

Offline headroom, proven by `bench/test-grade.sh`: the reference scores 1.00, the starting code 0.59 (all
of KeepWorking passes already). Six plausible wrong solutions kept as patches in
`bench/reference/service-wrong/` score 0.95 (fixes only the importer), 0.93 (no late-cancel rule), 0.93
(cancel time from `datetime.now()` instead of `clock.now()`), 0.92 (no migration for old databases), 0.86
(store readers return cancelled rows, only the visible paths filter) and 0.86 (feature only, bug not
found). The spread is narrow because the score is a share of tests and KeepWorking is the largest group;
the group scores show the difference.

Run it on its own; it is not in the default task list because each lane may take up to 30 minutes:

```bash
BENCH_TASKS=service bench/run.sh deepseek:deepseek/deepseek-flash claude:sonnet
```

The per-lane timeout is 1800 s (twice the other write tasks: the lane reads about 40 files and runs the
tests more than once; the slowest lane below needed 1061 s). `run.sh` passes no idle limit.

#### Measured, 2026-11-28: it does not separate these tiers

Two runs each, one at a time, on one machine. Details in
[`SERVICE.md`](../bench/results/2026-11-28/SERVICE.md).

| Lane | Run 1 | Run 2 | Seconds (1 / 2) | Groups missed |
|---|---|---|---|---|
| DeepSeek flash | 1.00 | 1.00 | 258 / 189 | none |
| Claude Sonnet | 1.00 | 1.00 | 141 / 81 | none |
| Claude Opus | 1.00 | 1.00 | 272 / 191 | none |
| Grok grok-4.7 | 0.97 | 0.97 | 927 / 1061 | BugFix 6/8 both times (series form of the bug) |

What it shows:

- **A cheap, a middle and a strong lane tie at 1.00, twice each.** A 2,300-line codebase with a buried
  cause, an easy-to-miss rule, a conflicting visible test and a migration did not separate DeepSeek flash,
  Sonnet and Opus. That supports routing well-specified work to cheap lanes more than it undermines the
  benchmark: when a ticket states what it wants, the cheap lane delivers it.
- **The one gap is repeatable.** Grok missed the same quiet variant in both runs and took 4 to 10 times
  longer. Run-to-run spread within a lane was zero on score and up to 1.7x on time.
- **Time separates more than score:** Sonnet 81 to 141 s, DeepSeek flash 189 to 258 s, Opus 191 to 272 s,
  Grok 927 to 1061 s.
- **Report honesty:** Grok said DONE with a hidden group failing (it had no way to see it; a conductor's own
  check would not have caught it either, since the visible tests pass). Sonnet ended neither run with the
  requested DONE line; its reports were accurate. Opus and Sonnet both named the tsv conflict and the
  judgement calls they made without being asked.

Caveats: 8 runs, one machine, one day; the harness and the model are measured together (the `claude` lane
got `--allowedTools Bash` in rw mode just before these runs, so it could run the tests); the brief says
"make sure the meetings imported before your fix are protected too", which hands lanes one of the three
quiet variants; the task is public, so later models may have seen it. To separate these tiers you would
probably need a brief that states less, work that spans several sittings, or cost per solved task as the
measure.

Lane specs are `provider:model[:effort]`; api lanes work too (`api:ollama:qwen3:8b`, the model keeps its
colons, the last field is an effort only when it is `low`, `medium`, `high`, `xhigh`, `max`, `minimal` or
`none`; an effort needs a model before it, so `codex:high` reads as model `high`). `BENCH_OUT=DIR` writes the results somewhere else than `bench/results/<date>`, `BENCH_APPEND=1`
adds rows to an existing `results.tsv`, and a lane with no tools (api) gets a `skipped` row for the bugfix
task. `bench/run.sh --dry-run LANE...` prints how each spec is read without calling a model.

### Latest: 2026-11-28 (OpenCode, Grok, DeepSeek, Antigravity, Cursor, API)

What was run: 11 free models through the new `opencode` lane, 4 Grok models through the new `grok` lane, the 2
DeepSeek models (v4-pro, flash), 9 models through Antigravity (`agy`), 2 through Cursor (`composer-2.5` and the
default `auto` model), and 13 through the `api` lane (3 abliteration.ai models, 10 free OpenRouter models). 41 lanes,
one run per cell. The full table and notes are in
[`COMPARISON.md`](../bench/results/2026-11-28/COMPARISON.md); raw answers are in
[`bench/results/2026-11-28`](../bench/results/2026-11-28).

- The task set is easy, so most lanes score full marks on every task they ran and differ on speed: among
  full-score three-task lanes the total time runs from 31 s (DeepSeek flash) to 430 s (agy/gemini-4-carbon-high).
- The 13 API lanes have no tools and ran two of three tasks (reasoning and bulk), so their totals are not
  comparable with three-task lanes; the table has a `tasks` column for this.
- Lost points: opencode/nemotron-3.5-lightning-free passed 5 of 6 hidden bugfix tests; the OpenRouter
  nemotron-3-nano-omni got 2 of 3 reasoning answers; agy/gemini-3.8-flash-high gave an empty bulk answer (score 0).
- Provider-side failures: opencode/tidepool-alpha-free (`Model is unavailable`, also on a rerun), the two
  OpenRouter gemma models (rate limit), and an empty bulk answer from liquid/lfm-3-1.7b.
- Cursor's plan refused muse-wonder, muse-spark, kimi-k3, kimi-k2.7-code and glm-5.2 ("not included in your
  weekly usage"), and the CLI does not list glm-5.3 or glm-5.3-flash; none of these has a score row. The
  cursor/auto timings are approximate (two runs overlapped).
- Free models are rate limited and come and go; one run per lane, so small gaps are not meaningful.

### 2026-11-21

One run per cell. Claude tiers were not re-run. Raw answers and diffs are in
[`bench/results/2026-11-21`](../bench/results/2026-11-21); the change against the previous run, with notes,
is in [`COMPARISON.md`](../bench/results/2026-11-21/COMPARISON.md).

| Lane | bugfix (hidden) | reasoning | bulk | wall time (s) b / r / k |
|---|---|---|---|---|
| GPT gpt-6.1-sol | ~6/6 | ~3/3 | ~60/60 | ~110 / ~17 / ~21 |
| GPT gpt-6-astra | ~6/6 | ~3/3 | ~60/60 | ~63 / ~20 / ~24 |
| GPT gpt-5.6-terra (effort medium) | 6/6 | 3/3 | 60/60 | 63 / 17 / 21 |
| GPT gpt-6-luna (effort low) | 6/6 | 0/3 | 58/60 | 55 / 9 / 12 |
| GPT gpt-5.6-luna (effort low) | 6/6 | 3/3 | 59/60 | 57 / 13 / 17 |
| Kimi k3.1-pro | 6/6 | 3/3 | 60/60 | 51 / 23 / 30 |
| DeepSeek v4-pro | 6/6 | 3/3 | 60/60 | 95 / 18 / 30 |
| DeepSeek flash | 6/6 | 3/3 | 60/60 | 17 / 14 / 16 |

~ = estimated, not run on 2026-11-21 (model not served on this plan): scores from the 2026-11-11 run, times scaled by about 1.4x, the slowdown the other lanes showed today.

Wall time columns: b = bugfix, r = reasoning, k = bulk.

What changed since 2026-11-11:

- **The GPT ids changed.** The ChatGPT account behind the Codex CLI now rejects `gpt-6.1-sol` and `gpt-6-astra`
  (and `gpt-5.6-sol`) with HTTP 400 `model_not_found`. The skill files still name sol and astra as defaults; on a
  plan like this one the lane fails fast with a status, and you need a working id. See [Model ids](how-it-works.md#model-ids).
- **One error, two statuses.** The same `model_not_found` came back as `failed` on two briefs and as `limit` on the
  bulk brief, because `mmo-run` matched limit words in the brief that Codex echoes on stderr. Details and the fix
  direction are in [`COMPARISON.md`](../bench/results/2026-11-21/COMPARISON.md).
- **gpt-6-luna is noisy.** Its bugfix passed this time, its reasoning dropped to 0/3. Read luna as "needs a check every time".
- **Everything else held.** Kimi k3.1-pro and both DeepSeek lanes scored the same as before, with higher wall times.

### History: 2026-11-11

One run per cell; full answers and diffs in [`bench/results/2026-11-11`](../bench/results/2026-11-11).

| Lane | bugfix (hidden) | reasoning | bulk | wall time (s) b / r / k |
|---|---|---|---|---|
| GPT gpt-6.1-sol | 6/6 | 3/3 | 60/60 | 79 / 12 / 15 |
| GPT gpt-6-astra | 6/6 | 3/3 | 60/60 | 45 / 14 / 17 |
| GPT gpt-6-luna (effort low) | visible tests fail (2/4) | 2/3 | 56/60 | 38 / 11 / 13 |
| Kimi k3.1-pro | 6/6 | 3/3 | 60/60 | 36 / 11 / 16 |
| Kimi k3.1-pro-highspeed | not on this plan (`limit`) | not on this plan | not on this plan | n/a |
| DeepSeek v4-pro | 6/6 | 3/3 | 60/60 | 49 / 10 / 17 |
| DeepSeek flash | 6/6 | 3/3 | 60/60 | 14 / 4 / 9 |
| Claude Opus (sub-agent) | 6/6 | 3/3 | 60/60 | n/a |
| Claude Sonnet (sub-agent) | 6/6 | 3/3 | 60/60 | n/a |
| Claude Haiku (sub-agent) | 6/6 | 3/3 | 60/60 | n/a |

### How to read it

- **This is a smoke test, not a leaderboard.** One run per cell, small tasks. Most strong lanes max it out. It tells you which lanes work end to end on your machine and which are not good enough for a job, not which model is "best".
- **The cheap tier is where it bites.** gpt-6-luna at low effort broke the visible tests on 2026-11-11 and got the reasoning wrong on 2026-11-21, so work on luna needs a check every time. DeepSeek flash was fastest and clean in both runs.
- **The benchmark found runner bugs before you would have.** On 2026-11-11: Kimi Code rejects `-p` with `--auto` (write lanes failed in 1 s), and the answer extractor crashed on a non-ASCII arrow on a Windows console code page, which turned a correct DeepSeek fix into `empty`. Both are fixed and the lanes re-run; the table shows the re-runs. On 2026-11-21: the `limit` mislabel above. That is the point of hard status gates: the failure showed up as a status, not as a silent wrong answer.
- Claude tiers ran as Claude Code sub-agents, so there are no comparable wall times.

### Run it on your own stack

```bash
bench/run.sh                                    # default lanes
bench/run.sh codex:gpt-5.6-terra:medium kimi:kimi-code/k3.1-pro
BENCH_TASKS="multifile refactor spec" bench/run.sh kimi:kimi-code/k3.1-pro   # only the harder tasks
bash bench/test-grade.sh                        # offline check of the grader, no model
```

A lane is `provider:model:effort` (effort is optional, default medium). With no arguments it runs
gpt-6.1-sol, gpt-6-astra, gpt-6-luna (low), Kimi k3.1-pro, DeepSeek v4-pro and DeepSeek flash; pass the ids your
plan serves if those are rejected. Results go to `bench/results/<date>/`: one answer file per lane and task, plus
`results.tsv`. The Claude tiers are not run by the script.

## A/B test: orchestra skill vs. "use subagents" (2026-11-21)

Full write-up: [`bench/ab/results/2026-11-21/RESULTS.md`](../bench/ab/results/2026-11-21/RESULTS.md).

Four independent Python tasks (bugfix, feature, refactor with its own tests, small parser), 12 visible and 36 hidden
tests, graded with no model in the loop. Main model `claude-fable-5-2`, 2 runs per arm, one headless Claude Code call
per run. Arm A got the prompt plus "Use subagents for implementation."; arm B got the same prompt plus "Follow the
orchestra skill." Neither arm could reach the GPT, Kimi or DeepSeek lanes, so B could only route among Claude tiers.

| Arm | Runs | Hidden tests | Cost per run (USD) | Mean cost | Mean wall time |
|---|---|---|---|---|---|
| A, "use subagents" | 2 | 36/36, 36/36 | 2.93, 3.48 | $3.21 | 3.5 min |
| B, orchestra skill | 2 | 36/36, 36/36 | 1.65, 2.10 | $1.88 | 3.2 min |

What it shows:

- **Same quality.** All four runs passed 36/36 hidden tests and left the visible tests intact. The task set is too easy
  to separate the arms on quality.
- **About 40% lower cost for B**, and the ranges do not overlap. The saving comes from one thing: in A every sub-agent
  inherited Fable; in B the sub-agents ran on Sonnet.
- **No speed gain:** 3.2 vs 3.5 minutes.

What it does not show:

- n = 2 per arm.
- A one-line "use Sonnet subagents" arm (C) was run on 2026-11-28, 2 runs, 36/36 both, $1.22 and $1.75 (mean $1.49), sub-agents on Sonnet. It captured the whole saving here, so the skill is not needed for the model choice alone. A and B were run on 2026-11-21, so this is not a controlled comparison. See [RESULTS.md](../bench/ab/results/2026-11-28/RESULTS.md).
- `total_cost_usd` is the CLI's list-price figure, a proxy for usage, not what a subscription plan bills.
- The skill's routing to GPT, Kimi and DeepSeek lanes was out of reach in both arms, so it is not measured here.

Re-run:

```bash
bench/ab/run_ab.sh                 # A1 B1 A2 B2, needs a signed-in `claude`
ARMS="C" RUNS=2 bench/ab/run_ab.sh # the one-line Sonnet arm
```
