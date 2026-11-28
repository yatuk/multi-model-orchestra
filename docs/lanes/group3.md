# Lanes, group 3

Six more lanes. Every adapter here was written from the vendor docs of the version named in its section and has never been run against the real CLI. The offline test (`skills/orchestra/scripts/test-mmo-lanes-3.sh`) only proves that the flags and output shapes in the docs are handled. Run one real job per lane before relying on it, and read the `ro_violation` field in the header of a read-only result.

"throwaway" means the CLI cannot be held read-only by documented flags, so `mmo-run` runs read-only jobs in a discarded worktree and reports any file the lane wrote. "sandbox" means the CLI's own flags hold it read-only. "notools" means the lane cannot touch files at all.

Effort (`-e`) is not passed to any of these CLIs.

## devin

- Written from the docs of version 3000.15.14 (2026-11-25), not run.
- Install: `curl -fsSL https://cli.devin.ai/install.sh | bash` (Windows: the PowerShell installer from the Devin CLI docs). This is the local agent. Windsurf's old CLI became this one, so there is no separate `windsurf` lane. The cloud Devin is a different thing (see [cloud.md](cloud.md)).
- Sign in: `devin auth login`. The docs read did not name an API key variable for `-p` (`WINDSURF_API_KEY` is documented only for `devin acp`).
- Model: `--model <id>` (or `DEVIN_MODEL`); `devin models` lists them.
- Read-only: throwaway. There is no read-only flag; plan mode is a slash command. In print mode a tool call that needs approval is denied and the run goes on to an answer. rw passes `--permission-mode dangerous`.
- Gotchas: print mode fails in a folder it does not trust, so the adapter passes `--respect-workspace-trust false`. The permission mode names differ between the English and some translated docs (`dangerous` is documented in English); check `devin --help`. The prompt is an argument after `--`. The answer is plain text; no JSON shape is documented.

## codebuddy

- Written from the docs of version 2.187.0 (2026-11-25), not run.
- Install: `npm install -g @tencent-ai/codebuddy-code` (a PowerShell installer exists for Windows, in beta).
- Sign in: run `codebuddy` once and pick a site (China, international, enterprise). `CODEBUDDY_API_KEY` is documented as always used in print mode.
- Model: `--model <alias or full name>`.
- Read-only: throwaway. The docs say print mode blocks writes, commands and network calls unless `-y` is given, but no read-only flag is documented, so ro simply leaves `-y` off. rw passes `-y`.
- Gotchas: `-y` is "not a true full pass": a few high-risk commands can still ask. `CODEBUDDY_IS_SANDBOX=1` silences them, but the docs limit it to isolated sandboxes, so the adapter does not set it. The brief goes on stdin. The answer is `result` of `--output-format json`. `--max-turns` is passed when the runner sets a ceiling.

## letta

- Written from the docs of version 0.34.72 (2026-11-27), not run.
- Install: `npm install -g @letta-ai/letta-code`.
- Sign in: run `letta` once. The docs read did not name an API key variable.
- Model: `--model <alias>` such as `sonnet`, or `auto`.
- Read-only: sandbox. `--tools "Read,Glob,Grep"` is the documented way to limit a run to read-only operations. rw passes `--yolo`.
- Gotchas: Letta keeps a stateful agent with memory per folder. The adapter passes `--ephemeral` so a lane creates and resumes nothing. The brief goes on stdin. The answer is `result` of `--output-format json`.

## qoder

- Written from the docs of version 1.1.101 (2026-11-28), not run.
- Install: `npm install -g @qoder-ai/qodercli`. The docs call the command `qoder`.
- Sign in: run `qoder` once, or set `QODER_PERSONAL_ACCESS_TOKEN` for scripts.
- Model: `--model` with `auto`, `lite`, `performance` or a BYOK key.
- Read-only: throwaway. `--permission-mode plan` exists but the docs do not say what it restricts. rw passes `--yolo` (`bypass_permissions`); `accept_edits` would still reject shell commands.
- Gotchas: the answer is the plain text output, because the JSON field holding the answer is not documented. The brief goes on stdin. The turn-limit flag is documented without its name in the page read, so no ceiling is passed.

## gptme

- Written from the docs of version 0.37.0 (2026-11-15), not run.
- Install: `pipx install gptme` (Python 3.11.5 or newer).
- Sign in: set `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` or `OPENROUTER_API_KEY` (others such as `GROQ_API_KEY` also work).
- Model: `-m provider/model`, for example `groq/llama-3.3-70b-versatile`. Giving only a provider picks its recommended model.
- Read-only: throwaway. `-n` implies `--no-confirm`, so every tool call is approved and nothing can hold it back. A tool allowlist exists (`-t`, `TOOL_ALLOWLIST`) but the tool names are not listed in the docs read, and `shell` can write.
- Gotchas: `--output-format json` prints one JSON object per message, so the lane reads the last message with role `assistant` (the `gptme` parser in `mmo_extract.py`). The documented message fields are `role` and `content`. A missing model prints "Provider X requires specifying a model", which now classifies as a model error. Exit 1 means the task failed. The prompt is an argument.

## llm

- Written from the docs of version 0.38 (2026-11-17), not run.
- Install: `pipx install llm`. The name `llm` is generic: this lane means the tool from llm.datasette.io.
- Sign in: `llm keys set openai` or `OPENAI_API_KEY`. Other providers are `llm` plugins (for example `llm-anthropic`), each with its own key.
- Model: `-m <model>`; `llm models` lists them. With no `-m` it uses the default model, which is an OpenAI one.
- Read-only: notools. It uses tools only when given `-T` or `--functions`, which the adapter never passes, so it answers and cannot edit files; `mmo-run --mode rw` refuses it.
- Gotchas: the brief goes on stdin and must carry everything the model needs. The docs read give no exact missing-key or unknown-model text, so those failures show up as `failed` unless the message matches an existing pattern.

## Variant: Codex on a local model

The existing `codex` lane can run on a local Ollama or LM Studio model with `codex exec --oss --local-provider ollama -m <model>` (the flags are in the Codex CLI reference). This is the same binary, so it is not a new lane. The adapter does not pass `--oss`; to use it today, set `oss_provider` in the Codex config, or write a copy of `providers/codex.sh` with the extra flags. The docs read do not say how `-m` behaves together with `--oss`.

## Looked at and left out

- Continue CLI (`cn`): the last npm release is 1.5.47 (2026-06-18) and the project describes a final 2.0.0; treated as no longer maintained. Its flags (`-p`, `--model`, `--auto`, `--readonly`) are documented, so an adapter is easy if it comes back.
- Trae Agent (ByteDance): `trae-cli run` exists, but no approval model, no output shape for the final answer (it writes a trajectory file) and no release date were found.
- Warp: the docs disagree on the command (`oz agent run` is "legacy", `warp agent run` is the new one), no permission flag is documented for it, and there is no standalone Windows package.
- Codebuff: no print or JSON mode in the CLI; headless use needs the paid SDK.
- Plandex: needs a plan and a server, and no read-only or approval flag for a one-shot run is documented.
- JetBrains Junie CLI (3110.7.0): `--task`, `--model`, `--output-format json` and `--project` are documented, but nothing says whether a headless run approves edits and commands (`--brave` is "interactive mode only").
- Atlassian Rovo Dev (`acli rovodev run --yolo`): no model flag and no output shape are documented.
- iFlow CLI: shut down on 2026-04-17.
- Roo Code CLI: the repository was archived on 2026-05-15; no Windows build.
- Windsurf: the CLI is now the Devin CLI (see `devin`).
- Open Interpreter: rewritten in Rust in 2026; the old `-y` flag is not confirmed for the new one.
- Zed: no scriptable agent run (a `--agent` flag for the `zed` CLI is only an open proposal).
- Deep Agents Code (`dcode`, LangChain): `-n`, `-M provider:model` and `-q` are documented, but its auto-approve flags need an interactive session and edits in non-interactive mode are not described.
