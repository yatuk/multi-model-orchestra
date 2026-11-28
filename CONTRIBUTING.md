# Contributing

Small, focused changes are easiest to review. For questions and ideas, use
[Discussions](https://github.com/yatuk/multi-model-orchestra/discussions); for bugs, lane requests and
benchmark results, use the issue forms.

## Setup

Needs bash, git, `timeout` and Python 3. On Windows, use Git Bash. Each lane needs its own CLI, signed in
(`mmo-run --list` shows them), but you can work on most of the repo without any of them.

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link
skills/orchestra/scripts/mmo-preflight     # offline, never calls a model
```

## Add a lane

1. Add one file, `skills/orchestra/scripts/providers/<name>.sh`: the non-interactive command, the model
   flag, and how a read-only run is held. The fields are in [docs/lanes](docs/lanes/README.md#adding-a-lane).
   If the CLI has no read-only mode, set `LANE_RO=throwaway` and the runner uses a discarded worktree.
2. If the CLI's quota, auth or unknown-model messages do not already map to `limit`, `auth` and `model`,
   add them to `mmo_classify.py`. Add a test with a fake CLI (see `test-mmo-lanes-1.sh`).
3. Add a row to `skills/orchestra/lanes.md` and a section under `docs/lanes/`.
4. Run the benchmark on the new lane and attach the `results.tsv` to the PR.

## Confirm a lane that was written from docs

Most lanes are marked `docs-<version>` in `mmo-run --list`: nobody has seen them answer. If you have the
CLI, run a one-line read-only brief and a small write in a worktree, and open an issue or PR with the
header lines (the first line of each output file) and, if it failed, the last stderr lines with anything
private removed. Changing `LANE_VERIFIED` to the date is a welcome one-line PR.

## Tests

```bash
for t in classify run check lessons lanes-1 lanes-2 api cloud roster lanes-3 score advise usage tiers; do bash skills/orchestra/scripts/test-mmo-$t.sh; done
bash bench/test-run-parse.sh
bash bench/test-grade.sh
python -m pytest skills/otomode/scripts skills/orchestra/scripts/test_mmo_model_guard.py skills/orchestra/scripts/test_mmo_limit.py -q
python -m py_compile skills/orchestra/scripts/mmo_loop.py
for f in skills/orchestra/scripts/mmo-* skills/orchestra/scripts/test-mmo-*.sh skills/orchestra/scripts/providers/*.sh bench/run.sh bench/test-run-parse.sh bench/test-grade.sh install.sh; do bash -n "$f"; done
```

None of these call a model. CI runs the same commands.

## Benchmark

```bash
bench/run.sh                                   # default lanes
bench/run.sh codex:gpt-6.1-sol:high kimi:kimi-code/k3.1-pro
```

It calls real models with your accounts. Results land in `bench/results/<date>/`. Commit a results folder only
after you have read it for anything private.

## Briefs and privacy

Briefs, outputs and logs go to other vendors and into this public repo. Never include secrets, tokens,
personal data, private code, real hostnames or paths from your machine. Use placeholders.

## Style

- Docs: plain language, no em dashes, no emojis. Keep `SKILL.md` files concise.
- Commits: short imperative subject, optionally prefixed with a type and scope, for example
  `fix(runner): map model_not_found to status model`. Keep pure moves apart from behavior changes.
