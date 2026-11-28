# Lanes, group 1

Seven coding-agent CLIs. Every adapter below was written from the CLI's documentation or source at the version named, never run. Each says "written from the docs of version X, not run". Test them once signed in before relying on them. Run `mmo-run --list` to see which are installed.

Common to all: mmo-run does not pass an effort flag to these CLIs (several reject unsupported values). Failures are classified from error text only; the exit codes some of these CLIs document (41 auth, 53 turn limit and so on) are not read by mmo-run.

## opencode
- Install: v2 `npm i -g @opencode/cli@latest` (or `curl -fsSL https://opencode.ai/v2/install | bash`). v1 is `npm i -g opencode-ai`.
- Sign in: `opencode auth login`; or the provider's own key variable (for example `OPENROUTER_API_KEY`).
- Model id: `provider/model`, v2 also `provider/model#variant`. Empty uses the configured default.
- Read-only: not enforced by a flag. The lane runs in a throwaway worktree without `--auto`. rw adds `--auto`.
- Gotchas: v1 and v2 are both live and differ (v1 has `--dir` and the `--yolo` alias; the flags used here exist in both). v2 runs a background service; env keys may not reach an already running one, and the docs suggest `--standalone` in CI (not used, because not confirmed for `run`). The brief goes in on stdin next to a short message argument.
- Written from the docs of version 2.4.2, not run.

## gemini
- Install: `npm install -g @google/gemini-cli`.
- Sign in: sign in once interactively, or set `GEMINI_API_KEY` (or the Vertex variables). Since 2026-06 personal Google AI plans no longer work here; use agy.
- Model id: `auto`, `pro`, `flash`, or a concrete id such as `gemini-2.5-pro`. Empty uses the CLI default.
- Read-only: `--approval-mode plan`. rw uses `--approval-mode yolo` (`--yolo` is deprecated).
- Gotchas: `--skip-trust` is passed so an untrusted folder does not abort. Exit 41 means auth and 53 turn limit; mmo-run matches the error text instead ("Please set an Auth method", "exhausted your capacity"). No max-turns flag.
- Checked against the real help of version 0.71.1 (installed with npm into an isolated folder): every flag the adapter passes exists with the form used (`-o json`, `--skip-trust`, `-m`, `--approval-mode plan|yolo`, `-p` appended to stdin); nothing needed changing. Not signed in: exit 41 with a JSON error (`Please set an Auth method ... GEMINI_API_KEY ...`), classified `auth` (7). Read-only is now `throwaway` too, because plan mode is documented but no signed-in run has proven it. The help also lists `--list-models` and `--worktree`. Windows: npm puts a `.cmd` and an extensionless sh shim in its `.bin` folder; Git Bash starts the bare name when that folder is on PATH in POSIX form (`/c/...`), so no wrapper is needed.

## agy (Google Antigravity CLI)
- Install: download from antigravity.google/download. On Windows it lands in `%LOCALAPPDATA%gyingy.exe` and that folder is added to the user PATH (open a new shell to see it).
- Sign in: sign in once with the CLI; plan access is tied to the Google account.
- Model id: a slug from `agy models`, effort included in the slug (`gemini-4-neon-high`, `claude-sonnet-5-5-medium`, `gpt-oss-120b-medium`, `gemini-pro-orchestrator`). Empty uses the default. An unknown slug exits 1 with "model x is not recognized as a known model", which classifies as model (8).
- Output: `--output-format json` prints one object; the answer is `response`, failures have `status":"ERROR"` and an `error` text. Read with `field:response`.
- Read-only: no sandbox. `--mode plan` refuses writes in the workspace (it writes its plan file to its own state folder, outside the repo) but is enforced by the model; the default mode created a file headlessly. So ro uses `--mode plan` and still runs in a throwaway worktree. rw adds `--dangerously-skip-permissions`.
- Gotchas: no working-directory flag (mmo-run changes into the folder). The prompt goes on the command line. A model that reaches for a shell command in ro mode gets it auto-denied and may return nothing ("jetski: no output produced ... command permission"), which mmo-run reports as empty (5); seen once on gemini-3.8-flash-high in the bulk task. Bench 2026-11-28 (hidden tests 6/6, reasoning 3/3, bulk 60/60): all nine of gemini-4-neon/carbon/argon/hydrogen, gemini-pro-orchestrator, claude-opus-5-5, claude-sonnet-5-5, gpt-oss-120b scored full marks, gemini-3.8-flash-high everything except that bulk run.
- Verified 2026-11-28 on version 1.5.19: read-only answer, a refused write, a write in a worktree, an unknown model. The docs-written version read plain text, used the default mode for ro, and had no error text; the real CLI has JSON output and `--mode plan`.

## qwen
- Install: `npm install -g @qwen-code/qwen-code@latest` (Node 22 or later).
- Sign in: `/auth` once interactively, or `OPENAI_API_KEY` plus `OPENAI_BASE_URL` for an OpenAI-compatible endpoint.
- Model id: the provider's own id, no prefix (default `qwen3-coder-plus`).
- Read-only: `--approval-mode plan`. rw uses `--approval-mode yolo` and sets `QWEN_CODE_SUPPRESS_YOLO_WARNING=1`.
- Gotchas: output is a JSON array; the answer is the last `result` item, and `is_error` makes the lane fail. `--max-session-turns` is passed for `--max-turns`. Error strings for auth and limits are not quoted in the docs, so only generic matches (such as "429" and "rate limit") classify.
- Checked against the real help of version 0.29.0. Flags exist as passed (`-m`, `--output-format json`, `--approval-mode plan|yolo`, `--max-session-turns`); `-p` is marked deprecated in favor of a positional prompt but still works with stdin. What the docs-written adapter got wrong: the error is not in `result` but in `error.message` of the result item (`No auth type is selected. Please configure an auth type ...`, exit 1), so the extractor now reads it and the classifier knows the string. Not signed in: `auth` (7). The help also lists `--max-wall-time` and `--max-tool-calls` (exit 55) and an `auto` approval mode. Read-only is `throwaway` until a signed-in run proves plan mode. Windows: npm puts a `.cmd` and an extensionless sh shim in its `.bin` folder; Git Bash starts the bare name when that folder is on PATH in POSIX form (`/c/...`), so no wrapper is needed.

## crush
- Install: `npm install -g @charmland/crush` (or brew, winget, scoop).
- Sign in: a provider API key variable (`ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`, ...) or the provider set up inside crush.
- Model id: `model` or `provider/model`. Empty uses the configured model.
- Read-only: none. `crush run` approves every permission request and has no flag to change that, so ro runs in a throwaway worktree, and rw is the same command.
- Gotchas: no JSON output; stdout of `run -q` is the answer. Telemetry is turned off with `CRUSH_DISABLE_METRICS=1`. Its config files are trusted code: do not run it in a folder you do not trust. No turn or budget cap.
- Checked against the real help of version 0.104.0. `crush run [prompt...]` reads the prompt from stdin, and `-q`, `-m model|provider/model` exist as used. The help also lists `-y/--yolo` ("skip permission prompts"), `-c/--cwd`, `--reasoning-effort` and `-C/--continue`; the docs-written note that `run` approves everything is not confirmed by the help, so ro stays `throwaway`. Not signed in: `No providers configured - please run 'crush' to set up a provider interactively.`, exit 1, classified `auth` (7). The npm package is a thin wrapper that downloads `crush.exe` from the vendor's GitHub release on first start (npm 12 does not run install scripts by default). Windows: npm puts a `.cmd` and an extensionless sh shim in its `.bin` folder; Git Bash starts the bare name when that folder is on PATH in POSIX form (`/c/...`), so no wrapper is needed.

## goose

- Not run against the real tool: it can only be installed with the vendor's installer, so it stays docs-written.- Install: `curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash` (add `CONFIGURE=false` to skip the wizard); works in Git Bash.
- Sign in: `goose configure` once, or provider env keys. On a headless Linux box with no keyring set `GOOSE_DISABLE_KEYRING=1` yourself.
- Model id: `provider/model`, split at the first slash (`openrouter/vendor/model` is provider `openrouter`). A bare id uses the provider from `GOOSE_PROVIDER` or the config.
- Read-only: none. The default `GOOSE_MODE=auto` approves every tool, so ro runs in a throwaway worktree. rw sets `GOOSE_MODE=auto` explicitly.
- Gotchas: `-q --no-session` prints only the reply to stdout. No cwd flag (mmo-run changes directory). Failure exit codes and error strings are not documented; only generic matches classify. `--max-turns` is passed through.
- Written from the docs of version 1.61.1, not run.

## aider

- Not run against the real tool: `pip install aider-chat` fails on Python 3.14 (aider needs 3.12 or older), so it stays docs-written.- Install: `python -m pip install aider-install && aider-install`, or `uv tool install aider-chat`.
- Sign in: API key variables only (`DEEPSEEK_API_KEY`, `OPENROUTER_API_KEY`, `OPENAI_API_KEY` with `OPENAI_API_BASE`, ...).
- Model id: litellm style (`deepseek/deepseek-chat`, `openrouter/vendor/model`, `ollama_chat/model`). Empty uses aider's default.
- Read-only: `--chat-mode ask` (never edits) plus a throwaway worktree. ro does not pass `--yes-always`; if aider asks something unexpected it reads end of input, which is untested. rw adds `--yes-always` and `--no-auto-commits` so the conductor reviews the diff.
- Gotchas: no machine-readable output. The adapter appends a line to the brief asking for `MMO-ANSWER-BEGIN` and `MMO-ANSWER-END` lines and the `aider` parser keeps the last pair; without markers the whole output is the answer. aider can exit 0 after printing a litellm error: the parser turns that into a failed lane. The project had no commits for about six months in 2026.
- Written from the docs of version 0.86.2, not run.
