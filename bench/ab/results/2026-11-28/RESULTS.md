# A/B third arm: does a one-line "use Sonnet subagents" capture the saving?

The 2026-11-21 write-up ([RESULTS.md](../2026-11-21/RESULTS.md)) named one untested case: a one-line prompt
telling the main model to use Sonnet sub-agents, with no skill. This run tests it.

## Setup

Same task repo, hidden tests, grader, permission flags, main model (`claude-fable-5-2`) and budget cap as
2026-11-21. Arms A and B were not run again; their numbers below are quoted from that day.

- **C (one line)**: the arm A prompt with its last sentence replaced by
  "Use Sonnet subagents for implementation, and name the model explicitly on every sub-agent call."
  No skill is loaded.
- 2 runs (C1, C2), run today with `ARMS="C" RUNS=2 bench/ab/run_ab.sh`.

## Results

| Run | Cost (USD) | Wall (min) | Hidden tests | Visible tests intact | Sub-agents | Cost by model |
|---|---|---|---|---|---|---|
| C1 | 1.75 | 2.5 | 36/36 | yes | 4 | fable-5-2 $1.22, sonnet-5-5 $0.53 |
| C2 | 1.22 | 2.5 | 36/36 | yes | 2 | fable-5-2 $0.97, sonnet-5-5 $0.25 |

| Arm | Runs from | Mean cost | Range | Mean wall | Hidden tests | Sub-agent model in the usage |
|---|---|---|---|---|---|---|
| A, "use subagents" | 2026-11-21 | $3.21 | $2.93-$3.48 | 3.5 min | 72/72 | Fable only |
| B, orchestra skill | 2026-11-21 | $1.88 | $1.65-$2.10 | 3.2 min | 72/72 | Fable and Sonnet |
| C, "use Sonnet subagents" | 2026-11-28 | $1.49 | $1.22-$1.75 | 2.5 min | 72/72 | Fable and Sonnet |

The run records (`C1.json`, `C2.json`) show only `claude-fable-5-2` and `claude-sonnet-5-5` in the per-model usage,
so the sub-agents did run on Sonnet. The model naming in the one-line prompt was followed.

## What this shows

- **The one line captured the whole saving here.** Both C runs passed 36/36 and cost less than every A run:
  C averaged $1.49 against $3.21 for A (about 54% less), and it was not more expensive than B ($1.88).
- **The saving still comes from the sub-agent model.** In C, Sonnet did $0.25-$0.53 of the work and Fable
  the rest, the same pattern as B. The skill is not needed to get Sonnet workers; one sentence did it.
- **The C-versus-B gap is not a result.** C was lower than B, but the ranges overlap ($1.22-$1.75 against
  $1.65-$2.10) and C used fewer sub-agents (4 and 2) and fewer turns (6 and 7), which is run-to-run variation as much as anything.

## What this does not show

- A and B ran on a different day, with the same script and prompts but not in the same session, so this is not a
  controlled three-way comparison. Two runs per arm is small.
- Quality did not separate the arms (all 36/36 everywhere), so this says nothing on whether the skill's checks matter for correctness.
- `total_cost_usd` is list price, a proxy for plan usage.
- Claude tiers only; the skill's routing to GPT, Kimi and DeepSeek lanes is still not measured.

## Re-run

```bash
ARMS="C" RUNS=2 bench/ab/run_ab.sh     # C1 C2, needs a signed-in `claude`
PRINT_PROMPTS=1 bench/ab/run_ab.sh     # print the A, B and C prompts and exit
```
