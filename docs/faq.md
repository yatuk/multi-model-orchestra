# FAQ

[Back to the README](../README.md)

- [Why not just tell the model to use subagents?](#why-not-just-tell-the-model-to-use-subagents)
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

Two honest caveats. A one-line "use Sonnet subagents" prompt was not tested and may capture most of that saving.
And `total_cost_usd` is a list-price proxy, not your plan usage. What the skill adds beyond the model choice is the
rest of the policy: routing to GPT, Kimi and DeepSeek lanes, status gates, worktree-only writes and the rule that the
conductor runs the check itself. The A/B test did not measure those.

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
