# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- **Classifier.** "Model is unavailable" is `model`; Anthropic's "credit balance is too low" and Gemini's
  `RESOURCE_EXHAUSTED` are `limit`; `invalid_api_key`, `invalid x-api-key` and "api key is invalid, expired or
  missing" are `auth` (#13, thanks to @techkayacodes).

### Changed

- The loose phrase "api key is invalid, expired or missing" is checked after the model and limit patterns, so a
  message that is really about a model or a quota and merely mentions the key keeps its class.

## [1.1.0] - 2026-11-28

Much of this came from the comments on the Reddit posts about the first release: pin the base of every
worktree, gate each batch and not only the end, give lanes ceilings the parent owns, send a failed check's
output back word for word, classify what the away-mode hook denied, and catch tests bent to pass.

### Added

- **otomode, six fixes from a real run.** The hook suggests one allow rule per segment of a compound command; `on` writes `.otomode/` and `QUESTIONS.md` into `.git/info/exclude` itself, refuses without a `Lanes:` line or a session id (`--force`, `--all-sessions`), and `merged`, `cron` and `gate`'s `why` record what the conductor used to skip; lanes read `<lane> <model>` everywhere. See `docs/otomode.md`.
- **What a run cost, a cost ceiling and quota memory.** `mmo-run` adds `in=`, `out=`, `cached=`, `cost=` (and
  `served=` when the served model differs from the requested one) to the out file header and
  `tokens_in`, `tokens_out`, `tokens_cached`, `cost_usd`, `served_model` to the `MMO_LOG` line, only where the
  tool itself reported them (`claude` lanes and the `api` lane; nothing is estimated, and lanes with no usage
  in their known output write none). `mmo-score --cost [--prices FILE]` sums them per lane and gives cost per
  passed task, retries included; runs with no reported cost are counted, not treated as free, and a price
  file you own (`skills/orchestra/prices.example`) turns tokens into a separate, `~`-marked estimate.
  `mmo-run --max-cost USD` reaches the `claude` lanes (`--max-budget-usd`) and `vibe` (`--max-price`); other
  lanes ignore it with one stderr note, and a claude lane that stops at the ceiling is `limit` with
  `ceiling=cost`. A `limit` whose message says when it comes back gets `retry_after=` in the header and log
  (`mmo_limit.py`), and `mmo-roster` makes no call to that lane until then (`limit until <date time>`).
  Tested in `test-mmo-usage.sh` and `test_mmo_limit.py`.
- **`mmo-advise` hardened.** The header says whether the advisor lane had no tools or only a read-only empty folder (`--strict-no-tools` refuses the latter, the roster prefers a notools lane), answers are capped by characters too (`--max-chars`, full answer kept as `.full.md`), a character budget (`--budget-chars`) and `mmo-advise status` join the count budget, and the budget file is locked and written atomically. Exit 10 is now over budget and 11 an answer without a verdict; 6 stays the lane's own limit.
- **One key file for every lane.** `mmo-run` loads `~/.config/mmo/keys.env` (or the file `MMO_KEYS_FILE`
  names) in the lane's child shell, so the `claude-deepseek`, `claude-kimi` and `claude-minimax` lanes
  find their keys there, not only the `api` lane. `--list` reads it in a throwaway subshell, so those
  lanes show `ok` when the key is only in the file.
- **`mmo-run --loop N`** kills a lane that streams JSON lines and repeats the same tool call or error N
  times in a row (status `looping`, exit 4). Ids, timestamps and durations are ignored; plain-text lanes
  are not covered. The comparison lives in `mmo_loop.py`.
- **`bench/run.sh`** reads api lane specs with colons in the model (`api:ollama:qwen3:8b`), honors
  `BENCH_OUT` and `BENCH_APPEND`, skips the bugfix task for lanes with no tools, and has `--dry-run`.
- **`mmo-roster`: route by what really answers here.** `probe` sends one tiny read-only brief per installed
  lane and model (four at a time, no retries) and records READY lanes per tier, and for the others the reason
  and the fix; `show`, `ready --tier` and `lineup` read it back. The orchestra and otomode skills start from
  it and tell the user the lineup, and otomode no longer drifts to Claude lanes only after a limit.
- **Six more lanes from the docs (group 3):** Devin CLI (`devin`), Tencent CodeBuddy (`codebuddy`), Letta Code
  (`letta`, read-only held by `--tools`), Qoder CLI (`qoder`), gptme (`gptme`, with a small `gptme` parser in
  `mmo_extract.py`) and `llm` (no tools). None has been run; `test-mmo-lanes-3.sh` covers them with fake CLIs.
  `docs/lanes/group3.md` also lists the CLIs that were looked at and left out, and why.
- **Cost levers you can enforce or measure.** `mmo_model_guard.py` is a hook that denies a sub-agent call
  without a model; `mmo-score` gains `--task`, `--share`, `--routes`, `--councils`, `--reports`,
  `log-agent` and `council-note`. See [docs/cost.md](docs/cost.md).

- **A/B arm C: one-line "use Sonnet subagents".** `bench/ab/run_ab.sh` takes `ARMS` and `RUNS` (for example `ARMS="C" RUNS=2`) and
  `PRINT_PROMPTS=1`. Two runs on 2026-11-28: 36/36 hidden tests, $1.49 mean against $3.21 (A) and $1.88 (B), sub-agents on
  Sonnet. One sentence captured the whole saving; see `bench/ab/results/2026-11-28/RESULTS.md`.
- **One adapter file per lane.** `mmo-run` loads `providers/<name>.sh`, so a new CLI is one small file
  instead of an edit to the runner. `mmo-run --list` shows every lane, whether its CLI is installed, its
  family, how read-only is held, and whether it was ever really run.
- **21 new lanes.**
  - Run by the maintainer: `opencode` (OpenCode 2.4.1) and `grok` (Grok CLI 1.0.92), each with a read-only
    answer, a write in a worktree and an unknown model; and `api` (any OpenAI-compatible endpoint with no
    agent CLI, run against a local Ollama, OpenRouter and one custom endpoint).
  - Written from each CLI's documentation, with offline tests of the flags and the output parsing, and not
    yet run: `gemini`, `agy`, `qwen`, `crush`, `goose`, `aider`, `cursor`, `copilot`, `amp`, `droid`,
    `auggie`, `kiro`, `cline`, `kilo`, `vibe`, `pi`, and Claude Code on the Anthropic-compatible endpoints of
    DeepSeek, Kimi and MiniMax (`claude-deepseek`, `claude-kimi`, `claude-minimax`).
- **`mmo-check`.** The conductor's own run of a task's check in the lane's worktree. It lists files touched
  outside `--allow`, existing tests that were changed or deleted, and changed dependency manifests;
  `--protect` fails the check when a protected file is touched; `--red` requires the check to fail on the
  base code with only the new tests, so a check that passes without the change is caught.
- **Runner ceilings and base pin.** `--base REF` refuses a worktree that does not contain the conductor's
  branch (exit 9, status `base`). `--idle SECONDS` kills a lane that prints nothing (status `stalled`).
  `--max-turns` is passed to the CLIs that can cap turns. The header of a writing lane carries `base=`,
  `changed=` and `committed=yes`.
- **Scoreboard.** With `MMO_LOG` set, `mmo-run`, `mmo-check` and `mmo-council` append one JSON line per run;
  `mmo-score` prints runs, failures and first-try pass rate per lane.
- **`mmo-lessons`.** A capped log of lessons about a lane that can only be written with a passing `mmo-check`
  report as proof. `show` gives at most five lines for the next brief; a lesson goes stale when the lane's
  adapter changes; text that looks like a secret or a private path is refused. It is deliberately not a
  memory system.
- **Key file for the `api` lane.** `~/.config/mmo/keys.env` (or `MMO_KEYS_FILE`) is read in the child process
  only, so keys stay out of the shell profile, the brief and the output.
- **Benchmark, 2026-11-28.** 17 lanes: 11 free OpenCode models, 4 Grok models, 2 DeepSeek models.
- **Order within a tier.** External lanes first and Claude sub-agents as the fallback, except the strong
  tier, where Claude Opus comes first. `~/.config/mmo/prefer` (or `MMO_PREFER`) lets the user reorder any tier.
- **One tier table and a default models file.** `mmo_tiers.py` is shared by mmo-roster and mmo-score; `mmo-roster probe` reads `$MMO_MODELS` or `~/.config/mmo/models` (example in `skills/orchestra/models.example`); `probe --write` tests from the outside that a lane can write files and run commands (`ready --for write`); mmo-run warns when a key file does not load.
- **Harder benchmark tasks.** `multifile` (a bug whose cause is in another file, plus a quieter documented
  defect), `refactor` (an options object and streaming across callers) and `spec` (20 artifacts under a
  retention policy with precedence and nested exceptions). The grader runs its own copies of the tests in a
  fresh directory, caps a lane that edits or deletes a visible test at 0, and reports missing public names;
  `bench/test-grade.sh` proves the reference solutions score 1.00 and the starting code scores low.
  `BENCH_TASKS` selects tasks. A two-lane calibration (DeepSeek flash, Claude Sonnet) scored 1.00 on all three
  even after one round of making them harder; see `docs/benchmark.md`.
- **Large benchmark task `service` (opt-in, `BENCH_TASKS=service`).** A 2,300-line booking application with a
  ticket-style brief, 59 hidden tests in five scored groups and six plausible wrong solutions that score 0.86
  to 0.95 offline. Measured on 2026-11-28: DeepSeek flash, Claude Sonnet and Claude Opus all scored 1.00 in
  two runs each, and Grok 4.7 scored 0.97 twice; see `bench/results/2026-11-28/SERVICE.md`.
- **Write tasks are graded even when the lane reports failure.** A lane whose status is not `ok`, or whose
  last line says FAILED or BLOCKED, is graded on its worktree with that fact in the detail; only an unchanged
  worktree scores 0.
- **Claude lane in rw mode can run commands** (`--allowedTools Bash`), so it can run the tests it is told to run.
- **`mmo-cloud` and the `cloud-lane` skill (experimental).** Start, poll, fetch and cancel a session on Devin,
  Cursor cloud agents or Copilot agent tasks behind one status contract, with a required cost cap where the
  vendor has one. Written from vendor documentation and tested against fakes only.
- **`advisor` skill and `mmo-advise`.** The inverse of the conductor setup: the session's cheaper model does one
  long task and asks a stronger lane of any vendor for advice at three moments (plan, stuck, done). One read-only
  brief per call, a fixed verdict line (`PROCEED`, `CHANGE:`, `STOP:`) with at most 12 lines of reasons, a
  per-session budget, capped evidence and diff, key-like text refused. Tested offline in `test-mmo-advise.sh`.
- **Templates.** `retry.md` (carries the failed check's output word for word) and `review.md` (a fresh
  reviewer: does the diff do what was asked, then is it correct; no style notes).
- **Docs.** `docs/lanes/` with one section per lane, and FAQ answers to the questions the Reddit threads
  raised (who should conduct, conductor usage, bent tests, green tasks with a red full run, stuck lanes).

### Changed

- `mmo-run --list` builds the table once (no "write error" lines when piped into `head`) and uses wider
  columns so long lane names line up.
- **`orchestra` skill.** Routes by tier to the lanes that are ready instead of naming one model per job;
  escalates one tier after two failed checks; existing tests are read-only in every brief; every brief offers
  `BLOCKED: <reason>` as an honest way out; lane reports are capped at ten lines; the full suite runs after
  every few merges.
- **`council` skill.** The rubric is written before the answers are read, the judging is per claim, the
  answers are read a second time in reverse order (`order-reversed.txt`), and the skill says when a council
  does not help. One round only.
- **`otomode`.** Denials are classed (`off_limits`, `question`, `allowlist_gap`) with suggested allow rules
  for next time; lanes are verified with `mmo-check` and launched with `--base`, `-t`, `--idle` and
  `--max-turns`; a per-task time budget; the full check after every four merged tasks; a `BLOCKED` lane is
  not a failed try; a per-lane score in the end report.
- **`mmo-preflight`** lists every adapter instead of three hard-coded CLIs.
- **`mmo-council`** staggers lane starts by a second: two lanes on one CLI started together could fail on its
  session storage.
- **Classifier.** A CLI that starts a sign-in flow is `auth` whatever it prints afterwards; "model
  unavailable" is `model`.

### Fixed

- The Cursor lane calls `cursor-agent`: the CLI's new binary name, `agent`, is also installed by the Grok CLI.

## [1.0.0] - 2026-11-21

First release.

### Added

- **Skills.** `orchestra` (routing policy, brief rules, gates, fallbacks, templates), `council` (the same question to three model families, read-only, answers shuffled to letters before judging), `chatgpt-lane` (GPT through the Codex CLI), `kimi-lane` (Kimi through the Kimi Code CLI), `deepseek-lane` (DeepSeek v4-pro and flash through the Kimi Code CLI) and `otomode` (unattended runs). Claude Opus, Sonnet and Haiku run as the host agent's own sub-agents and need no script.
- **`mmo-run`, one runner for every provider.** Writes an output file whose first line is a status header. Exit codes: 0 ok, 3 failed, 4 timeout, 5 empty, 6 limit, 7 auth, 8 model (the model id was rejected). Every CLI runs with no stdin under a timeout.
- **Runner safety.** `--mode rw` refuses to run unless `-C` is a linked git worktree. Read-only Codex lanes use the Codex read-only sandbox. Read-only Kimi and DeepSeek lanes run in a throwaway detached worktree, and anything they write is discarded and flagged `ro_violation=yes`.
- **Status classification.** `mmo_classify.py` matches limit and model-id errors only in the CLI's own error lines, so a brief echoed on stderr no longer turns a `model_not_found` error into `limit` or `failed`. It comes with `test-mmo-classify.sh`.
- **`mmo-council`.** Runs three lanes in parallel and read-only. A failed lane is recorded as not an answer and not a vote.
- **`mmo-preflight`.** Offline check of which lanes exist on this machine. It never calls a model.
- **`otomode`.**
  - One round of questions up front, then a hook denies every permission prompt and question for the session and logs it to `QUESTIONS.md`.
  - The hook judges only the commands that actually run (`cmdscan.py` parses the command line), and refuses `rm`, `git push`, branch and worktree removal, `reset --hard`, deploy CLIs, ssh/scp, write requests, `gh pr` and `issue` writes, publish and mail, plus MCP tools named send, post, delete, submit or upload.
  - `otomode.py log` writes timestamped lines into the `OTOMODE.md` log.
  - `otomode off` prints a cleanup list with the exact commands for housekeeping the hook blocked.
  - Run rules: record the base branch and check each lane branch against it before merging, run the repo's quick check after every merge, and smoke-test every lane and model id while the user is still present.
  - A usage gate stops new work at 85% of plan usage and schedules a resume after the reset. An hourly watchdog restarts a stalled loop. `statusline.py` saves plan usage for the gate. Tests are in `test_otomode.py`.
- **Benchmark.** `bench/run.sh` runs a bugfix, a reasoning and a bulk-labeling task on every lane in parallel, graded by `bench/grade.py` with no model in the loop. Results for 2026-11-11 and a fresh run for 2026-11-21 (with a `COMPARISON.md`) are in `bench/results`.
- **A/B test.** `bench/ab` compares the orchestra skill with a plain "use subagents" prompt on four small tasks, with hidden tests and per-run records. Results are in `bench/ab/results/2026-11-21/RESULTS.md`.
- **Documentation.** README with install, runner and safety notes, an illustration, a Turkish write-up on orchestration and otomode, and README translations in 19 languages, including Crimean Tatar in Latin script. There is no Russian version.
- **Repository.** `install.sh` (copy or `--link`, `--dir PATH`), MIT license, GitHub issue and pull request templates, and a light CI workflow.

### Known limits

- On Windows, use Git Bash.
- Kimi Code has no read-only sandbox, so read-only Kimi and DeepSeek lanes run in throwaway worktrees.
- The otomode hook is a guard rail, not a sandbox.
- Model ids differ per plan. On 2026-11-21 the ChatGPT plan used for the benchmark no longer served `gpt-6.1-sol` or `gpt-6-astra`; smoke-test the ids your plan uses.
