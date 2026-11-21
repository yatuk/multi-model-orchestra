# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/).

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
