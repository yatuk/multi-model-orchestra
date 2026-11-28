# Lanes

[Back to the README](../../README.md)

A lane is one model reached one way. `mmo-run <lane>` runs it; `mmo-run --list` shows every lane, whether
its CLI is on this machine, and how far it has been checked.

| Page | Lanes |
|---|---|
| [group1.md](group1.md) | OpenCode, Gemini CLI, Antigravity (`agy`), Qwen Code, Crush, Goose, Aider |
| [group2.md](group2.md) | Cursor, GitHub Copilot, Amp, Droid, Auggie, Kiro, Cline, Kilo, Mistral Vibe, Pi |
| [group3.md](group3.md) | Devin CLI, CodeBuddy, Letta Code, Qoder, gptme, llm |
| [api.md](api.md) | The `api` lane (any OpenAI-compatible endpoint, no agent CLI) and Claude Code on DeepSeek, Kimi and MiniMax endpoints |
| [cloud.md](cloud.md) | Experimental: Devin, Cursor cloud agents and Copilot agent tasks through `mmo-cloud` |
| The lane skills | [chatgpt-lane](../../skills/chatgpt-lane/SKILL.md) (Codex), [kimi-lane](../../skills/kimi-lane/SKILL.md), [deepseek-lane](../../skills/deepseek-lane/SKILL.md), plus `grok` and `claude` in [lanes.md](../../skills/orchestra/lanes.md) |

## Which models a lane uses

A lane with a default model (`codex`, `grok`, `deepseek`, `kimi`, `claude`) uses it unless you pass `-m`.
Lanes without one (`opencode`, `api`, `copilot`, `cursor`, `agy` and most others) use what the CLI is
set to, and `mmo-roster probe` reports them as `needs-model` until it is told which ids to try. Put
them in a models file, one `lane model` per line (`#` comments, blank lines ignored; several lines for
one lane are all probed and each gets a roster row). `mmo-roster probe` reads, in this order:
`--models FILE`, else the file named by `MMO_MODELS`, else `~/.config/mmo/models` if it exists.
[`skills/orchestra/models.example`](../../skills/orchestra/models.example) has a commented example per
lane. The tier of each model comes from one table, `skills/orchestra/scripts/mmo_tiers.py`.

## What "checked" means

| CHECKED in `--list` | Meaning |
|---|---|
| a date | The maintainer ran the lane on that day: a read-only answer, a write in a worktree, and at least one real failure classified. |
| `help-<version>` | The CLI at that version was installed and its real `--help` was compared with every flag the adapter passes; a signed-out run showed the real error and it classifies correctly. Nobody has seen an answer yet. |
| `docs-<version>` | Written from that version's documentation. The flags, the output parsing and one error are covered by offline tests with a fake CLI. Nobody has seen it answer. |

As of 2026-11-28: `claude`, `codex`, `kimi`, `deepseek`, `opencode`, `grok` and `api` have been run. Everything else is
`docs-...`. If you use one of those CLIs, a one-line brief and the header line it produces is the most
useful thing you can send: see [CONTRIBUTING](../../CONTRIBUTING.md).

## Which lane comes first in a tier

`mmo-roster ready --tier X` and `lineup` list a tier's ready lanes in this order: external lanes, then
Claude sub-agents, each group by measured first-try pass rate once there is enough data. The strong tier
is the exception: Claude Opus first, external strong lanes as its fallback. To choose yourself, write
`~/.config/mmo/prefer` (or the file `MMO_PREFER` names), one line per choice in the order you want:

```
# tier   lane      [model]
strong   subagent  opus
middle   grok
bulk     opencode  opencode/beam-free
```

Lanes you list come first; the rest keep the default order. Only READY lanes are ever used.

## Adding a lane

One file, `skills/orchestra/scripts/providers/<name>.sh`:

```bash
LANE_BIN=mycli                 # must be on PATH
LANE_DEFAULT_MODEL=""          # used when -m is not given
LANE_FAMILY=any                # openai, anthropic, google, xai, deepseek, moonshot, alibaba, mistral, any
LANE_RO=throwaway              # sandbox | throwaway | notools
LANE_EXTRACT=text              # text | field:KEY | jsonl:KEY | a parser in mmo_extract.py | answer-file
LANE_VERIFIED=docs-1.2.3       # a date once you have run it
LANE_NOTE="install and sign-in hint"
LANE_PROMPT=stdin              # or arg
lane_cmd() {
  CMD=(mycli run --json)
  [ -n "$MODEL" ] && CMD+=(--model "$MODEL")
  [ "$MODE" = rw ] && CMD+=(--auto-approve)
}
```

`lane_cmd` may use `$MODE $MODEL $EFFORT $RUNDIR $PROMPT $PROMPT_FILE $ANS $MAX_TURNS $TIMEOUT`. Optional
functions: `lane_env` (export variables in the child just before the CLI starts), `lane_model` (normalize
`$MODEL`), `lane_ready` (an offline readiness test for `--list`). If the CLI cannot be held read-only by a
documented flag, say `throwaway` and the runner does the rest. Then add its real error lines to
`mmo_classify.py` if they do not classify already, and a test with a fake CLI.
