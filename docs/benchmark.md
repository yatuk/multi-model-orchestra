# Benchmark

[Back to the README](../README.md)

Two kinds of measurement live in `bench/`:

- **Lane benchmark** (`bench/run.sh`): does each external lane work end to end, and is it good enough for a job.
- **A/B test** (`bench/ab/`): does the orchestra skill beat just telling the main model "use subagents".

Both are small. Read them as smoke tests, not leaderboards.

## Lane benchmark

`bench/run.sh` runs three tasks on every lane in parallel and grades them with no model in the loop:

| Task | Mode | Graded by |
|---|---|---|
| **bugfix**: fix a duration parser so it follows five written rules | rw, own worktree | visible tests must pass and stay unedited; score = share of 6 hidden tests passed |
| **reasoning**: two Python trace questions and one counting question, no running code | ro | exact match against answers computed by running the code |
| **bulk**: label 60 log lines CRITICAL / ERROR / WARN / INFO by first-match rules with traps (`panicked`, `errorless`, 404) | ro | accuracy against gold labels generated from the same rules |

### Latest: 2026-11-21

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
- A one-line "use Sonnet subagents" prompt was not tested and may capture most of the saving.
- `total_cost_usd` is the CLI's list-price figure, a proxy for usage, not what a subscription plan bills.
- The skill's routing to GPT, Kimi and DeepSeek lanes was out of reach in both arms, so it is not measured here.

Re-run:

```bash
bench/ab/run_ab.sh                 # A1 B1 A2 B2, needs a signed-in `claude`
```
