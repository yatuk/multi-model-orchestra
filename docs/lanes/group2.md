# Lanes, group 2

Ten more coding-agent CLIs as `mmo-run` lanes. Every adapter here was written from the vendor docs of the version named in its section and has never been run against the real CLI. The offline test (`skills/orchestra/scripts/test-mmo-lanes-2.sh`) only proves that the flags and the output shapes in the docs are handled. Run one real job per lane before relying on it, and read the `ro_violation` field in the header of a read-only result.

"throwaway" means the CLI cannot be held read-only by documented flags, so `mmo-run` runs read-only jobs in a discarded worktree and reports any file the lane wrote. "sandbox" means the CLI's own flags hold it read-only.

Not included: OpenHands (its CLI is no longer maintained, and headless mode always auto-approves).

Effort (`-e`) is not passed to any of these CLIs: the runner always sends a value, and most of these CLIs only accept it for some models.

## cursor (binary `cursor-agent`)

- Run on 2026-11-28 with version 2026.11.22: read-only answer, read-only refusal of a write, rw write in a worktree, unknown model.
- Install: `curl https://cursor.com/install -fsS | bash` (Windows: `irm 'https://cursor.com/install?win32=true' | iex`). The CLI's binary is now `agent`, a name other tools install too (the Grok CLI ships one), so the lane calls `cursor-agent`, which the installer still creates.
- Windows: the installer creates `cursor-agent.cmd` and `agent.cmd` in `%LOCALAPPDATA%/cursor-agent`. Git Bash cannot start a `.cmd` by bare name, and a `.cmd` wrapper (through `cmd.exe`) cuts a multi-line prompt at the first newline, so the options after it are lost and the run stops at the workspace-trust prompt. Use a small `cursor-agent` shell script on PATH that runs the bundled `node.exe` on `versions/<version>/index.js` with `CURSOR_INVOKED_AS=cursor-agent.cmd`. The adapter itself needs no change.
- Sign in: `cursor-agent login`, or `CURSOR_API_KEY`. Signed out, a run prints "Authentication required" and ends as `status=auth` (exit 7).
- Model: `--model <id>`; `cursor-agent --list-models` prints the ids (about 300, one per effort and speed variant, for example `composer-2.5`, `gpt-5.6-sol-high`, `claude-haiku-5-5-medium`). With no flag the CLI uses `auto`. An unknown id prints "Cannot use this model: ... Available models: ..." and ends as `status=model` (exit 8).
- Read-only: throwaway. `--mode ask` is passed and the model refused to create a file in a read-only run; the runner's throwaway worktree is still the guard. rw passes `--force`.
- Gotchas: without `--force` some steps are skipped silently and the run still exits 0. A team admin can disable headless mode, which makes `cursor-agent -p` fail before sending the prompt. Failures print no JSON, only stderr and a non-zero exit. `--trust` is passed so the workspace-trust prompt does not block. The json result has no cost field, only token counts.

## copilot

- Checked with a real run of version 1.0.117 (answered PONG; the CLI was already signed in on the machine, no login was done here). Read-only enforcement passed: without an allow flag, headless runs deny both file writes and shell commands (`Permission denied because no interactive user response was available`), and the main checkout stayed clean. rw in a linked worktree created `pong.txt` (changed=1). An unknown model gives `Execution failed: Model "x" is not available.`, now classified `model` (8). The docs-written adapter had no wrong flags; the help also lists `--available-tools`, `--excluded-tools`, `--deny-tool`, `--output-format json`, `--plan` and `--max-ai-credits`. Windows: npm puts a `.cmd` and an extensionless sh shim in its `.bin` folder; Git Bash starts the bare name when that folder is on PATH in POSIX form (`/c/...`), so no wrapper is needed.
- Install: `npm install -g @github/copilot` (or winget, brew).
- Sign in: `/login` once, or a fine-grained token in `COPILOT_GITHUB_TOKEN` (then `GH_TOKEN`, `GITHUB_TOKEN`) with the "Copilot Requests" permission.
- Model: `--model=<id>`, for example `gpt-6.1-sol` or `claude-sonnet-5.5`. What is available depends on the plan and org policy.
- Read-only: sandbox. There is no read-only flag, but unattended runs deny every tool call that no allow rule approves (tested: write and shell both denied). rw passes `--allow-all-tools`.
- Gotchas: `-p` ignores piped stdin, so the brief is a command-line argument (about 32k characters on Windows). `-s` keeps usage stats out of the answer. Usage is billed as premium requests. The JSON output shape of the final message is not documented, so the plain output is used.

## amp

- Not run against the real tool: `npm install @ampcode/cli` succeeds, but the native binary is fetched by a postinstall script and the stub alone prints `Amp native binary not installed`, so it was left docs-written.
- Written from the docs of version 0.0.1795852840 (a build number), not run.
- Install: `curl -fsSL https://ampcode.com/install.sh | bash`, or `npm install -g @ampcode/cli`. The docs name WSL for Windows.
- Sign in: `amp login` (the session is short lived), or `AMP_API_KEY` with an access token that starts `sgamp_`.
- Model: `--model provider/name`, for example `openai/gpt-6-astra`. No model-list command is documented.
- Read-only: throwaway. "Amp does not ask for approval before running tools", so ro and rw use the same flags.
- Gotchas: threads live on ampcode.com, so briefs leave the machine. `-ox` returns at once with a thread URL and must not be used. The brief goes on stdin. The answer is the `result` of the last `{"type":"result"}` line; the parser `result-stream` reads it and treats `is_error` as a failure. Exit 1 means the run failed.

## droid

- Checked against the real help of version 1.23.0 (npm `droid`, which pulls the vendor's platform package). Flags exist as used: `exec -f FILE`, `-o json`, `--cwd`, `-m`, `--auto low|medium|high`; default model shown as `claude-opus-5-5`. Not signed in: `Authentication failed. Please log in using /login or set a valid FACTORY_API_KEY environment variable.`, classified `auth` (7). Read-only stays `throwaway` until a signed-in run proves the default read-only mode. The help also lists `--only-tools`, `--remove-tools`, `--list-tools` and `--skip-permissions-unsafe`. Windows: npm puts a `.cmd` and an extensionless sh shim in its `.bin` folder; Git Bash starts the bare name when that folder is on PATH in POSIX form (`/c/...`), so no wrapper is needed.
- Install: `curl -fsSL https://app.factory.ai/cli | sh` (Windows installer at `https://app.factory.ai/cli/windows`), or `npm i -g droid`.
- Sign in: `FACTORY_API_KEY` (starts `fk-`).
- Model: `-m <id>`; `droid exec --help` lists them. Custom models are `custom:<Name>-<index>`, and an unknown `custom:` id may fall back to the default with only a warning.
- Read-only: throwaway, with the guard still in place: `droid exec` is read-only by default. rw passes `--auto medium` (builds, tests, git commit and push); `low` would only allow file edits.
- Gotchas: it does not ask for folder trust and runs the repo's project hooks, so treat untrusted repos with care. An action above the autonomy level stops the run with an error and a non-zero exit; edits made before that stay. The brief is read from a file (`-f`).

## auggie

- Checked against the real help of version 1.2.3. It is built on the same engine as Pi: `-p/--print` is a boolean flag and the message is positional (`[@files...] [messages...]`), so `--print @file` works. The help lists `--mode text|stream|json|rpc` (so the claim below that a JSON output does not exist is out of date; the event shape is still unseen), `--tools`, `--no-tools`, `--permission tool:policy`, `-w`, `--model`, `--no-session`. Not signed in: `No API key found for unknown. Use /login or set an API key environment variable.`, classified `auth` (7). Read-only stays `throwaway` until a signed-in run proves the tool allowlist. Windows: npm puts a `.cmd` and an extensionless sh shim in its `.bin` folder; Git Bash starts the bare name when that folder is on PATH in POSIX form (`/c/...`), so no wrapper is needed.
- Install: `npm install -g @augmentcode/auggie` (Node 20.6 or newer).
- Sign in: `auggie auth login`, or `AUGMENT_SESSION_AUTH` with the output of `auggie token print`. The session JSON is a bearer credential.
- Model: `--model <name>`, optionally with `:<effort>`; `auggie model list` shows them.
- Read-only: throwaway, with the guard still in place, a tool allowlist: `--tools read,grep,find,ls`. rw passes `--permission` allow rules for `bash`, `edit` and `write`. Those three names come from the documented tool list; the docs do not show them in a `--permission` example.
- Gotchas: the v2 rewrite dropped `--max-turns`, `--quiet`, `--instruction-file` and `--output-format json`. The help now shows `--mode json`, but its event shape was not seen, so the plain output is used. The brief is read from a file with `@file`. The CLI auto-updates unless `AUGMENT_DISABLE_AUTO_UPDATE` is set.

## kiro (binary `kiro-cli`)

- Not run against the real tool: it can only be installed with the vendor's installer script, so it stays docs-written.
- Written from the docs of version 3.6.2, not run.
- Install: `curl -fsSL https://cli.kiro.dev/install | bash`.
- Sign in: `kiro-cli login` (`--use-device-flow` over SSH), or `KIRO_API_KEY` for paid plans.
- Model: `--model <id>`; `kiro-cli chat --list-models` prints the ids.
- Read-only: sandbox. Headless has no approver, so only the tools named in `--trust-tools=read_file,grep_search` run; everything else is denied with `[denied] tool permission approval is not supported in non-interactive mode`. rw passes `--trust-all-tools`.
- Gotchas: a stored login silently wins over `KIRO_API_KEY` (run `kiro-cli logout` to use the key). An unknown model only warns on stderr and the run continues on another model, so check the model in the answer. `--v3` is pinned because the default harness differs between releases. The success record of `--output-format stream-json` is not documented, so the plain output is used. Documented exit codes: 0 success, 1 failure, 3 required MCP server failed, 4 requested mode or agent not offered. The brief goes on stdin.

## cline

- Checked against the real help of version 3.0.76. What the docs-written adapter had wrong: with `--json`, stdin alone is refused (`JSON output mode requires a prompt argument or piped stdin`, exit 1), so the adapter now sends the brief on stdin plus the short argument `Follow the instructions given on stdin.`. Other flags exist as used (`-c`, `-m`, `--plan`, `--yolo`, `--auto-approve <boolean>`). Not signed in: `Unauthorized: ... re-authenticate your Cline account.`, classified `auth` (7); every run also prints `hook dispatch failed` noise lines that can be ignored. Windows: npm puts a `.cmd` and an extensionless sh shim in its `.bin` folder; Git Bash starts the bare name when that folder is on PATH in POSIX form (`/c/...`), so no wrapper is needed.
- Install: `npm install -g cline`.
- Sign in: `cline auth`, or a provider key such as `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`.
- Model: `-m <id>`, where the id format depends on the provider (`-P`, default `cline`), for example `anthropic/claude-sonnet-5.5`.
- Read-only: throwaway. The adapter passes `--plan --auto-approve false`; the docs do not say plan mode blocks edits. rw passes `--yolo`.
- Gotchas: one-shot runs are yolo by default, which is why ro turns approval back on. Never use `--zen`: it detaches to a hub daemon and prints nothing, so a runner would see an empty run. `--key` is saved to the config. The brief goes on stdin and the answer is the `text` of the `run_result` line of `--json`.

## kilo

- Checked against the real help of version 7.8.40 (an OpenCode fork). `kilo run [message..]`, `--dir`, `--format default|json`, `-m provider/model` and `--auto` exist as used; nothing needed changing. Not signed in: `You need to sign in to use this model. Run \`kilo auth login\``, exit 1, classified `auth` (7); the run took 14 s. The help also lists `--variant`, `-f/--file`, `--agent` and `--pure`. Windows: npm puts a `.cmd` and an extensionless sh shim in its `.bin` folder; Git Bash starts the bare name when that folder is on PATH in POSIX form (`/c/...`), so no wrapper is needed.
- Install: `npm install -g @kilocode/cli`.
- Sign in: `kilo auth login`.
- Model: `-m provider/model`; `kilo models` lists them.
- Read-only: throwaway. Without `--auto` permission requests are rejected and the run exits 1, but the docs do not say which actions ask in the first place. rw passes `--auto`.
- Gotchas: its own exit 124 means the task hit a time limit, and `mmo-run` reports that as a timeout. `run ended without an assistant message` is exit 1. Each run starts a local server, and telemetry is on unless `KILO_TELEMETRY_LEVEL=off`. The JSON event shape is not documented, so the plain output is used.

## vibe

- Not run against the real tool: `pip install mistral-vibe` needs more than the Windows 260-character path limit allows in a deep scratch folder, so it stays docs-written.
- Written from the docs of version 3.1.5, not run.
- Install: `uv tool install mistral-vibe` (Python 3.12 or newer), or the install script on mistral.ai.
- Sign in: `MISTRAL_API_KEY` (this also skips the first-run wizard).
- Model: `--model <alias>`, an alias from `config.toml`; there is no list flag. An unknown alias is a usage error (exit 1).
- Read-only: throwaway. `--approval-policy accept-edits` is passed explicitly, which still lets the lane edit files; `ask` would deny every tool call, including reads. rw passes `--auto-approve`.
- Ceilings: `--max-turns` follows `--max-turns` of `mmo-run`; `--time-limit` is set to the `-t` value minus 20 seconds, so the lane stops by itself before the hard kill (only when `-t` is above 40).
- Gotchas: exit 3 means it stopped without finishing (turn, token, price or time limit, refusal) and is reported as `failed`; exit 2 is an infrastructure failure. The brief goes on stdin, so `-p` is the last argument.

## pi

- Checked against the real help of version 1.7.0. Flags exist as used (`--print`, `--model`, `--tools`, `--no-mcp`, `--` before the message); the adapter now also passes `--no-session`. Not signed in: `No API key found for the selected model. Use /login ...`, classified `auth` (7). Read-only stays `throwaway` until a signed-in run proves the allowlist. The help also lists `--mode json`, `--no-context-files` and `--agent-dir`. Windows: npm puts a `.cmd` and an extensionless sh shim in its `.bin` folder; Git Bash starts the bare name when that folder is on PATH in POSIX form (`/c/...`), so no wrapper is needed. The repo moved from `badlogic/pi-mono` to `earendil-works/pi`, and the package is `@earendil-works/pi-coding-agent`.
- Install: `npm install -g --ignore-scripts @earendil-works/pi-coding-agent` (Node 22.19 or newer), or the script at pi.dev. On Windows it uses Git Bash for its `bash` tool.
- Sign in: `pi auth login <provider>`, or a provider key env such as `ANTHROPIC_API_KEY`.
- Model: `--model <id or pattern>`, with an optional `:<thinking>` suffix; `pi --list-models` prints them.
- Read-only: throwaway. Pi has no permission system, so the guard is the allowlist `--tools read,grep,find,ls` plus `--no-mcp` (the allowlist does not remove MCP tools). rw leaves the default tools, which can edit.
- Gotchas: project `.pi/settings.json` and extensions load from the working directory, which matters in repos you do not trust. No ceilings are documented. The brief is a command-line argument after `--`.
