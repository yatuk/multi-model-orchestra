# Contributing

Small, focused changes are easiest to review. For questions and ideas, use
[Discussions](https://github.com/yatuk/multi-model-orchestra/discussions); for bugs, lane requests and
benchmark results, use the issue forms.

## Setup

Needs bash, git, `timeout` and Python 3. On Windows, use Git Bash. Each lane needs its own CLI, signed in
(`codex` for GPT, `kimi` for Kimi and DeepSeek), but you can work on most of the repo without any of them.

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link
skills/orchestra/scripts/mmo-preflight     # offline, never calls a model
```

## Add a lane

1. Add the provider to `skills/orchestra/scripts/mmo-run`: the non-interactive command, how the model and
   effort flags are passed, and how a read-only run is enforced. If the CLI has no read-only mode, use the
   throwaway worktree approach the Kimi lane uses.
2. Teach `mmo_classify.py` the CLI's quota, auth and unknown-model messages so they map to `limit`, `auth`
   and `model`. Add cases to `test-mmo-classify.sh`.
3. Add the lane to `mmo-preflight`, and a skill in `skills/<name>-lane/SKILL.md` that stays short.
4. Run the benchmark on the new lane and attach the `results.tsv` to the PR.

## Tests

```bash
bash skills/orchestra/scripts/test-mmo-classify.sh
python -m pytest skills/otomode/scripts -q
bash -n skills/orchestra/scripts/mmo-run bench/run.sh install.sh
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
