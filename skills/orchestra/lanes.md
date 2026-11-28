# Lanes

Every lane is one file in `scripts/providers/`. `scripts/mmo-run --list` shows which are ready on this
machine and when each was last really run (CHECKED: a date, or `docs-<version>` for adapters written
from documentation and not run by the maintainer). `scripts/mmo-roster probe` sends each lane a one-line
read-only brief and records which really answer, for which tier. Read-only: `sandbox` = held by the CLI's own flags; `throwaway` = the CLI cannot be
held, so read-only jobs run in a discarded worktree; `notools` = the lane cannot touch files at all.

| Lane | What it reaches | Read-only | Good for |
|---|---|---|---|
| `claude` | Claude through Claude Code print mode (outside Claude Code; inside it use sub-agents) | sandbox | any tier, by model |
| `codex` | GPT through the Codex CLI | sandbox | execution (sol), second opinion (astra), bulk (luna) |
| `kimi` | Kimi through Kimi Code | throwaway | cheap execution |
| `deepseek` | DeepSeek through Kimi Code | throwaway | cheap execution, bulk (flash), another family's opinion |
| `opencode` | Any provider OpenCode is signed in to: DeepSeek, OpenRouter, local Ollama, its own free models | throwaway | cheap and bulk work on many models with one CLI |
| `grok` | xAI Grok through the Grok CLI | sandbox | another family's opinion, execution |
| `gemini` | Gemini through Gemini CLI (Code Assist or API key) | sandbox | large-context reading, opinion |
| `agy` | Gemini through Google Antigravity's CLI (personal Google plans) | throwaway | same, on a personal plan |
| `qwen` | Qwen through Qwen Code | sandbox | cheap execution |
| `cursor` | The models of a Cursor plan through `cursor-agent` | throwaway | execution on a plan you already pay for |
| `copilot` | The models of a GitHub Copilot plan | throwaway | same |
| `amp` | Sourcegraph Amp | throwaway | execution; it never asks before acting |
| `droid` | Factory Droid | sandbox | execution with graded autonomy |
| `auggie` | Augment's CLI | sandbox | execution in large codebases |
| `kiro` | AWS Kiro CLI | sandbox | execution on an AWS plan |
| `cline`, `kilo` | Cline and Kilo Code CLIs (bring your own provider) | throwaway | execution |
| `vibe` | Mistral models through Mistral Vibe | throwaway | another family; caps on turns, price and time |
| `crush`, `goose`, `aider`, `pi` | Open-source agents (bring your own provider or local model) | throwaway (pi: sandbox) | cheap or local execution |
| `devin`, `codebuddy`, `letta`, `qoder`, `gptme` | Cognition's Devin CLI, Tencent CodeBuddy, Letta Code, Qoder CLI, gptme | throwaway (letta: sandbox) | execution on a plan or provider you already have; docs-only, never run |
| `llm` | Simon Willison's `llm`: one model, no tools | notools | an extra opinion from any model an `llm` plugin reaches |
| `api` | Any OpenAI-compatible endpoint, as `-m endpoint:model`: OpenRouter, DeepSeek, Moonshot, Z.ai, MiniMax, xAI, Mistral, Groq, Cerebras, Together, Fireworks, Gemini, local Ollama or LM Studio, or your own | notools | opinions, council seats, bulk labeling; the brief must carry everything |
| `claude-deepseek`, `claude-kimi`, `claude-minimax` | Claude Code as the harness on that vendor's Anthropic-compatible endpoint | sandbox | a cheap model with Claude Code's tool limits (not supported by Anthropic) |

Cloud agents (Devin, Cursor cloud agents, Copilot agent tasks) are not lanes of `mmo-run`: they work on
pushed code and return a pull request. See the `cloud-lane` skill.

Notes that save a failed run:
- A lane with no default model (blank in `--list`) uses whatever its CLI is configured for; pass `-m`.
- Two lanes on one CLI started in the same second can collide on its session storage; stagger them.
- `-e` (effort) reaches `codex`, `grok` and the `claude` lanes only.
- Per-lane install lines, sign-in variables and known traps: `docs/lanes/` in the repository.
