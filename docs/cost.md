# Cost

Eight levers, what each one does, and the command that enforces or measures it. Where a number exists it
was measured; where none is given, none was.

All the measuring commands read the log that `mmo-run`, `mmo-check` and `mmo-council` write when
`MMO_LOG=<file>` is set. Claude sub-agents do not go through `mmo-run`, so record them yourself with
`mmo-score log-agent`.

## The measured number

In the [A/B test](../bench/ab/results/2026-11-21/RESULTS.md) (four small tasks, same hidden tests):

| Arm | Mean cost per run |
|---|---|
| A, "use subagents" (sub-agents inherit the main model) | $3.21 |
| B, orchestra skill | $1.88 |
| C, one sentence: "use Sonnet sub-agents, name the model on every call" (run on 2026-11-28) | $1.49 |

All arms scored the same on the hidden tests. Two runs per arm on an easy task set is thin: read the
numbers as a direction, not a forecast. Nothing below promises a saving beyond that.

## The levers

1. **Every sub-agent call names its model.** A call without a model inherits the expensive main model;
   this is where the A to C difference came from. `python skills/orchestra/scripts/mmo_model_guard.py install`
   registers a Claude Code hook that denies a sub-agent call with no `model` (forks are allowed). Set
   `MMO_MODEL_GUARD=warn` to warn instead of deny, `off` to disable. `uninstall` removes it.
2. **Easy, well-specified work goes to non-Claude lanes.** This is routing, not a script. What can be
   measured is where the work went: `mmo-score LOG --share` prints the share of runs and wall seconds by
   family. Log your own sub-agents with `mmo-score log-agent --model sonnet --task ID --seconds N`.
3. **An unattended run must not drift to Claude only.** `--share` also prints one sentence when more than
   80% of at least 10 runs went to Claude while external lanes answered ok in the same log.
4. **Keep the conductor's context small.** Lanes report in ten lines. `mmo-score --reports DIR` lists the
   lane outputs whose answer is longer than 40 lines (`--lines N` to change), with the lane that wrote them.
   It reads files only.
5. **Escalate on failure.** `mmo-score LOG --task ID` shows the task's runs and checks and one line of advice:
   under 2 failed checks, retry on the same tier with the check output; 2 or more, one tier up; limit, auth
   or model errors, another lane of the same tier; a wrong base, recreate the worktree. Tiers come from one
   map in `mmo_tiers.py` (`MODEL_TIER`); a lane not in it gets no tier advice.
6. **Use the council sparingly.** After each council, `mmo-score council-note --task ID --agreed` or
   `--split`. `mmo-score LOG --councils` counts them, and says so when at least 5 are noted and at least 80%
   agreed: the panel is mostly confirming.
7. **Advisor.** Not covered here.
8. **Route by your own numbers.** `mmo-score LOG --routes` ranks lanes by first-try pass rate within each
   tier, only for lanes with at least 5 checked tasks. Below that it prints "not enough data (n=3)" and
   ranks nothing.

## What a run cost

`mmo-run` records what the tool itself reports about a run, and nothing it works out on its own. A field the
tool's output does not contain is left out, never filled in with a guess.

| Lane | Recorded |
|---|---|
| `claude`, `claude-deepseek`, `claude-kimi`, `claude-minimax` | input, output and cached tokens, `total_cost_usd`, the model that served the run |
| `api` | `prompt_tokens`, `completion_tokens` and `cost` when the endpoint returns one (OpenRouter can), and the response's `model` |
| every other lane | nothing: no usage in the known output |

The lanes with nothing are the ones whose JSON this repo has not seen carry token or cost fields, or whose
output is plain text (`codex`, `opencode`, `agy`, `grok`, `gemini`, `qwen`, `vibe`, `cursor`, `droid`, `amp`
and the rest). If a CLI starts to print them, add its shape to `mmo_usage.py`; a wrong number is worse than none.

Where it goes: the out file header gets `in=`, `out=`, `cached=`, `cost=` and, when the served model differs
from the requested one, `served=`, after the existing fields. The `MMO_LOG` line gets `tokens_in`,
`tokens_out`, `tokens_cached`, `cost_usd` and `served_model`. Absent fields are absent.

**Subscription plans report no dollars.** Codex on a ChatGPT plan, Kimi, Antigravity and similar plan-based CLIs
print no cost, so those runs show tokens if the tool gives them, or nothing. The `claude` lanes do print a
`total_cost_usd`, but it is a list-price figure, not what your plan bills. Treat all of it as a proxy for
usage, as the [benchmark](benchmark.md) does.

### `mmo-score LOG --cost [--prices FILE]`

Per lane: runs, runs with a reported cost (`COSTED`), the sum of reported cost, tokens in and out, the tasks
that passed, and the cost per passed task. That last number is the reported cost of all the lane's labelled
runs, retries and failed tasks included, divided over the tasks whose check passed. It is what makes a cheap
lane that needs three tries comparable to a dearer one that passes first time. A task that fails on one lane
and passes on the next leaves its cost with the first lane and its pass with the second.

Runs with no reported cost are counted separately ("12 runs, 9 with reported cost") and are never treated as
free; when a lane has both, `$/PASSED` covers only the costed runs and the output says so.

### The price file

Optional, and yours. The repo ships no prices because they change and plans differ; see
`skills/orchestra/prices.example` for the format (two fake lines). Put real lines in
`~/.config/mmo/prices`, or name the file with `MMO_PRICES` or `--prices`:

```
provider/model-pattern   input-per-million   output-per-million   [cached-input-per-million]
```

A pattern is a shell-style glob matched against `provider/model`, the first match wins, `#` starts a comment.
When a run has tokens but no reported cost and a line matches, the cost is computed and shown in its own `~`
column. Estimated and reported sums are never added into one unmarked number: `~$/PASSED` says it includes
estimates. Cached tokens are priced only when the line has a cached price.

### A cost ceiling: `mmo-run --max-cost USD`

Passed to the lanes whose CLI has a real budget flag: the `claude` lanes (`--max-budget-usd`) and `vibe`
(`--max-price`). Every other lane ignores it, with one stderr note per run, so a ceiling is never silently
assumed. When a claude lane stops at the ceiling (its result says `error_max_budget_usd`), the run is status
`limit` with `ceiling=cost` in the header, not a plain failure. Vibe's text output does not say why it
stopped, so a stop there stays whatever the tool reports. The cost of the stopped run is still recorded.

### Quota memory

A `limit` whose message says when it comes back gets `retry_after=<UTC time>` in the header and the log, and
`mmo-roster` remembers it: until then a probe makes no call to that lane, and `show` and `lineup` say
`limit until <date time>`. Understood: `try again at Dec 21st, 2026 9:18 AM`, `resets 4pm (Europe/Istanbul)`
(only with a zone named) and `Retry-After: <seconds>` from the api lane. A time that cannot be read with
confidence is not guessed, and then nothing is remembered.
