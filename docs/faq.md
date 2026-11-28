# FAQ

[Back to the README](../README.md)

- [Why not just tell the model to use subagents?](#why-not-just-tell-the-model-to-use-subagents)
- [Should the strongest model conduct, or build?](#should-the-strongest-model-conduct-or-build)
- [Doesn't the conductor burn the usage anyway?](#doesnt-the-conductor-burn-the-usage-anyway)
- [How do I know a lane did not bend the tests to pass?](#how-do-i-know-a-lane-did-not-bend-the-tests-to-pass)
- [Every task was green and the full run was red. Why?](#every-task-was-green-and-the-full-run-was-red-why)
- [What stops a lane that is stuck in a loop?](#what-stops-a-lane-that-is-stuck-in-a-loop)
- [Which lanes are supported, and which were really run?](#which-lanes-are-supported-and-which-were-really-run)
- [Does it run locally?](#does-it-run-locally)
- [What leaves my machine?](#what-leaves-my-machine)
- [What happens when a lane hits a limit?](#what-happens-when-a-lane-hits-a-limit)
- [A GPT model id is rejected. What now?](#a-gpt-model-id-is-rejected-what-now)
- [Does it work on Windows?](#does-it-work-on-windows)
- [Is otomode safe to leave running?](#is-otomode-safe-to-leave-running)
- [How does this compare to other projects?](#how-does-this-compare-to-other-projects)

## Why not just tell the model to use subagents?

We tested exactly that ([A/B test](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21)).
On `claude-fable-5-2`, 2 runs per arm, the plain "Use subagents for implementation." prompt and the orchestra skill
both passed all 36 hidden tests in every run, with the visible tests intact. The task set was too easy to tell them
apart on quality.

The difference was cost: the skill arm averaged $1.88 per run against $3.21 (about 40% less, and the ranges do not
overlap). The saving came from the sub-agents running on Sonnet instead of inheriting Fable. There was no speed gain
(3.2 vs 3.5 minutes).

We then tested the one-line "use Sonnet subagents" prompt without the skill (2026-11-28, 2 runs, sub-agents named on every call). Both runs passed 36/36 and
cost $1.22 and $1.75 (mean $1.49), with sub-agents on Sonnet. So for the model choice alone, one sentence is enough;
the skill did not save more. A and B ran a week earlier, so this is not a controlled comparison.

Two honest caveats. Two runs per arm is small.
And `total_cost_usd` is a list-price proxy, not your plan usage. What the skill adds beyond the model choice is the
rest of the policy: routing to GPT, Kimi and DeepSeek lanes, status gates, worktree-only writes and the rule that the
conductor runs the check itself. The A/B test did not measure those.

## Should the strongest model conduct, or build?

Both setups are published, and they are for different jobs.

- **Strong conductor, cheaper workers.** This repo. Anthropic's
  [multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) ran a strong
  lead with cheaper sub-agents. It suits work that splits into independent, checkable jobs, because the lead
  spends its tokens on the split, the briefs and the review, and the bulk of the tokens are spent one tier down.
- **Cheaper executor, strong advisor.** Anthropic's [advisor strategy](https://claude.com/blog/the-advisor-strategy)
  turns it around: a cheaper model does the whole task and asks a stronger one for advice at the hard points
  (`/advisor` in Claude Code). It suits one long task done step by step. There is no splitting and no worker pool.

This repo now has both: `orchestra` for the first, and the [`advisor`](../skills/advisor/SKILL.md) skill for the
second, with the advisor on any vendor's strong lane.

What nobody recommends is a weak planner handing work to a strong builder: the plan sets the ceiling.
Cognition [reports](https://cognition.com/blog/multi-agents-working) the same from their side.

Nothing in the scripts depends on which model conducts. The skills are plain text and the runner is bash, so a
GPT or Gemini session can conduct as well; that is not measured here. If your work is one long thread, use the
advisor setup instead of this repo's policy.

## Doesn't the conductor burn the usage anyway?

It reads every result, so its context does grow. Three things keep that small:

- A lane reports in at most ten lines and writes anything longer to a file. The conductor reads the check report
  and the diff, not a transcript.
- State lives in files (the plan table, lane outputs, check reports), so a compacted or new session rebuilds from
  them instead of carrying the whole run in context.
- Most of what a long session re-reads is served from the prompt cache.

Measured, not promised: in the [A/B test](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) the
skill arm cost about 40% less, all of it from sub-agents not inheriting the main model. One five-hour unattended
run of 13 tasks moved the author's weekly limit from 25% to 31%. That is one run on one plan.
[Cost](cost.md) lists each lever with the command that enforces or measures it.

## How do I know a lane did not bend the tests to pass?

You do not take its word. Reports of agents editing tests or special-casing inputs to get a green check are
common, and telling a model "do not cheat" changes little
([METR](https://metr.org/blog/2025-06-05-recent-reward-hacking/),
[ImpossibleBench](https://arxiv.org/abs/2510.20270)). ImpossibleBench reports that what a lane is
allowed to do with the tests changes how often it cheats, so the policy is structural:

- **Existing tests are read-only** in every brief, and `mmo-check` lists each existing test a lane changed or
  deleted. `--protect "tests/*"` turns a touched test into a failed check.
- **A way out.** Every brief says `BLOCKED: <reason>` is an acceptable answer. A lane with no honest exit takes
  a dishonest one.
- **Red before green.** `mmo-check --red` runs the check on the base code plus the lane's new tests. It must fail
  there. A check that passes without the change proves nothing about the change.
- **The conductor runs the check itself** and reads the whole diff. For work that matters, a fresh reviewer that
  never saw the lane's reasoning goes over it (`templates/review.md`).

None of this proves a change correct. Weak tests still pass wrong code.

## Every task was green and the full run was red. Why?

That is the normal shape of parallel work: each change is correct against its own check, and two of them break
each other, or a repo-wide rule (an architecture test, a golden file, a linter) is not in any task's check.
The policy: merge one lane at a time, run the quick check after each merge, and run the full check after every
few merges instead of once at the end, so the culprit is one of a handful of commits.

A second cause is a lane that started from the wrong commit. Create each worktree from the branch you are
working on and pass `mmo-run --base <branch>`; the runner refuses a worktree that does not contain it. Claude
Code sub-agent worktrees start from the default branch unless the setting `worktree.baseRef` is `head`.

## What stops a lane that is stuck in a loop?

The limits belong to the caller. Every `mmo-run` call has a hard timeout (`-t`). `--idle SECONDS` kills a lane
that has printed nothing for that long (`status=stalled`), and `--max-turns` is passed to the CLIs that can cap
turns. A lane that fails its check twice goes one tier up; in otomode a task is marked blocked after three tries
and the run moves on. What the runner does not do is read a lane's tool calls to spot the same failing command
repeated; a loop that keeps printing is caught by the timeout, not sooner.

## Which lanes are supported, and which were really run?

`mmo-run --list` shows every adapter with a CHECKED column. A date means the lane was run on that day. A value
like `docs-1.2.3` means the adapter was written from that version's documentation and never run by the
maintainer. Those are real adapters with offline tests of the flags and the output parsing, but treat them as
untested until a one-line brief answers on your machine, and please report what you see.
See [lanes](lanes/README.md).

## Does it run locally?

The skills and scripts do. They are plain bash and Python, run on your machine, and call the CLIs you already have
(`codex`, `kimi`, and the host agent's own sub-agents). There is no server. The models themselves run at their vendors,
so every lane call goes over the network to that vendor, under your own account and plan.

## What leaves my machine?

Whatever is in a brief, plus whatever the lane's CLI reads from the worktree you point it at. Briefs go to other
vendors (OpenAI, Moonshot for Kimi, DeepSeek), so never put secrets, tokens or personal data in a brief. The skills
say this too. `mmo-preflight` is offline: it never signs in and never calls a model.

## What happens when a lane hits a limit?

`mmo-run` exits 6 with `status=limit` (quota, balance, rate limit or plan). The routing table in
[`skills/orchestra/SKILL.md`](../skills/orchestra/SKILL.md) has a fallback column, and the policy is to switch to it,
not to retry the same lane in a loop. In otomode, a `limit` from DeepSeek moves the task and the rest of the run to
Claude lanes, and the usage gate pauses the whole run at 85% of the Claude plan until the reset.

## A GPT model id is rejected. What now?

On some ChatGPT plans the Codex CLI now serves different model ids and rejects others. On 2026-11-21 one plan rejected
`gpt-6.1-sol` and `gpt-6-astra` with `model_not_found` and served `gpt-5.6-terra`, `gpt-6-luna` and `gpt-5.6-luna`.
The skill files name the defaults; smoke-test the ids your plan accepts with a one-line brief through `mmo-run`
(after `mmo-preflight` shows the CLI is installed), and pass the working id with `-m`. See
[Model ids](how-it-works.md#model-ids).

## Does it work on Windows?

Yes, through Git Bash. You need bash, git, `timeout` and Python 3. The 2026-11-11 benchmark caught a Windows-specific
bug (the answer extractor crashed on a non-ASCII character on a Windows console code page); it is fixed.

## Is otomode safe to leave running?

It is built not to wait and not to do anything irreversible: one question round, then a hook denies every prompt
and logs it, and it refuses delete, deploy, push and send commands. But the hook matches patterns. It is a guard rail,
not a sandbox. Run it on a repo where the worst case is a branch you throw away. See [otomode.md](otomode.md).

## How does this compare to other projects?

Other projects solve parts of this well. This repo borrows no code from them; the table is from their public READMEs as of November 2026.

| Project | Best at | What this repo adds |
|---|---|---|
| jarrodwatts/claude-delegator (archived) | Expert personas over Codex/GPT, advisory vs. implementation modes | Kimi and DeepSeek lanes, Claude tier routing, one status contract for all CLIs |
| hkasahar/claude-code-skills | File-based delegation with a checkable header, offline preflight | Same ideas across four CLIs, plus worktree-only writes and a benchmark |
| k1064190/claude-code-gemini-cli-skills | Strict timeouts, exit-code gates, pinned models for Gemini | The same discipline for GPT, Kimi and DeepSeek |
| rachittshah/llmcouncil | Many council modes (vote, debate, critique), anonymized peer review | A small blind council that runs on CLIs you already pay for, with failed lanes excluded |
| PAL MCP (consensus) | Stance-steered consensus through one MCP server | No server: plain scripts and skills, enforced read-only for every lane |

None of the above covered Kimi or DeepSeek through their coding CLIs when this was written.
