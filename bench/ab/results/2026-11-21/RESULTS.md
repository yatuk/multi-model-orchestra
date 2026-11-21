# A/B: orchestra skill vs. "Use subagents for implementation."

Question from a reader: does the orchestration skill beat just telling Fable to use subagents?

## Setup

- **Task repo** (`bench/ab/taskrepo`): Python, standard library only, four independent tasks in `TASKS.md`:
  a bugfix (`intervals.py`), a feature (TTL for an LRU cache), a refactor that must add its own tests
  (`report.py`), and a parser plus evaluator for a small filter language (`query.py`).
  12 visible tests; 36 hidden tests in `bench/ab/hidden`, graded by `bench/ab/grade_ab.py` with no model in the loop.
- **Runner** (`bench/ab/run_ab.sh`): each run gets a fresh temp git repo and one headless Claude Code call,
  main model `claude-fable-5-2`, Claude Code 2.1.329, runs sequential.
  - **A (baseline)**: prompt = do the four tasks in TASKS.md, run the visible tests, do not edit tests,
    do not commit, "Use subagents for implementation."
  - **B (skill)**: the same prompt plus "Follow the orchestra skill.", with `skills/orchestra` from this repo
    and the author's local `fable-orchestration` routing note copied into the temp repo's `.claude/skills`
    (that note is not published here; leave `FABLE_SKILL_DIR` unset to run B with `orchestra` alone).
  - Both arms: `--setting-sources project --strict-mcp-config` (no user settings, user skills, hooks or MCP
    servers, so A sees no routing skill), `--permission-mode acceptEdits --permission-prompts none`,
    Bash/PowerShell allowed only for `python`, `git`, `cd`, `ls`, `cp`; no web tools; `--max-budget-usd 25`.
    No arm could reach the GPT, Kimi or DeepSeek lanes (the runner script is not allowed), so B could
    only route among Claude tiers.
- Graded on what landed in the main checkout. Sub-agent worktrees did not count.
- 2 runs per arm, order A1, B1, A2, B2.

## Results

| Run | Cost (USD) | Tokens in+out (cache read / write) | Wall (min) | Turns | Hidden tests | Per task (bug / feat / refac / parse) | Visible tests intact | Cost by model |
|---|---|---|---|---|---|---|---|---|
| A1 | 2.93 | 30,871 (1,100,107 / 128,235) | 2.9 | 3 | 36/36 | 8/8 / 8/8 / 6/6 / 14/14 | yes | fable-5-2 $2.93 |
| A2 | 3.48 | 41,948 (944,773 / 139,156) | 4.1 | 21 | 36/36 | 8/8 / 8/8 / 6/6 / 14/14 | yes | fable-5-2 $3.48 |
| B1 | 1.65 | 25,325 (1,066,338 / 112,962) | 3.1 | 10 | 36/36 | 8/8 / 8/8 / 6/6 / 14/14 | yes | fable-5-2 $1.29, sonnet-5-5 $0.36 |
| B2 | 2.10 | 32,777 (1,378,723 / 133,091) | 3.2 | 38 | 36/36 | 8/8 / 8/8 / 6/6 / 14/14 | yes | fable-5-2 $1.69, sonnet-5-5 $0.41 |

| Arm | Mean cost | Mean wall | Hidden tests | Sub-agents spawned |
|---|---|---|---|---|
| A, "use subagents" | $3.21 | 3.5 min | 72/72 | 4, 5 (all on Fable) |
| B, orchestra skill | $1.88 | 3.2 min | 72/72 | 4, 5 (Sonnet; no other sub-agent model in the usage) |

Per-run records (`A1.json` ...) hold per-model usage, sub-agent stats, permission denials and the final
message; `A1.diff` ... are the changes each run left in the repo. Local paths are replaced with `<dir>`.

## What this shows

- **Same quality, about 40% lower cost for B.** Every run passed all 36 hidden tests and left the
  visible tests alone. B cost $1.65 and $2.10, A cost $2.93 and $3.48; the ranges do not overlap.
- **The saving comes from one thing: the sub-agent model.** In A every sub-agent inherited Fable, so
  100% of the spend was Fable. In B the routing policy sent the sub-agents to Sonnet (the usage
  records show only Fable and Sonnet); Sonnet did the implementation for about $0.40 and the Fable share fell to $1.29-$1.69.
  The skill's other rules (re-run the check yourself, read the diff) showed up in the final reports,
  but they did not change the score here because A also passed everything.
- **No speed gain.** Wall time was about the same (B 3.1-3.2 min, A 2.9-4.1 min).

## What this does not show

- **n = 2 per arm.** Enough to see a cost gap this size, not enough for a confidence interval.
- **The tasks did not separate the arms on quality.** Both arms scored 100%. During a dry run of the
  pipeline, a Haiku-only run also passed 36/36, so this task set is too easy to show whether the
  skill helps or hurts correctness. A harder task set is needed for that question.
- **A cheaper baseline was not tested.** "Use Sonnet subagents for implementation" would probably
  capture most of B's saving with one sentence and no skill. This experiment does not tell the skill
  apart from that.
- **Cost is the CLI's list-price figure (`total_cost_usd`).** On a subscription plan nothing is billed
  per run; read it as a proxy for how much plan usage each arm burns, weighted by model price.
- **Claude tiers only.** The skill's main feature, routing to GPT, Kimi and DeepSeek lanes with status
  gates, was out of reach in both arms by design, so it is not measured here.
- **One machine, one day, one Claude Code version.** Sub-agents ran in their own worktrees and some of
  their shell calls were denied by the permission setup in both arms; the main loops ran the checks
  themselves. A different permission setup may change turns and cost.

## Re-run

```bash
bench/ab/run_ab.sh                 # A1 B1 A2 B2, needs a signed-in `claude`
FABLE_SKILL_DIR=~/.claude/skills/fable-orchestration bench/ab/run_ab.sh B3
MODEL=haiku CAP_USD=2 bench/ab/run_ab.sh A0       # cheap pipeline check
```
