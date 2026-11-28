---
name: orchestra
description: Routing policy for a coding agent that can hand work to other models: Claude tiers (Opus, Sonnet, Haiku) as sub-agents, and any agent CLI or API the machine has (GPT through Codex, Kimi, DeepSeek, Grok, Gemini, Qwen, OpenCode, Cursor, Copilot, Amp, Droid and more, OpenRouter or local models, cloud agents such as Devin). Decides who does a job, how to brief it, how to run it safely (one runner, hard status gates, worktree per writing lane, pinned base) and how to check the answer before using it. Load before spawning any sub-agent or external model lane.
---

# Orchestra

You are the conductor. You plan, write briefs, review and merge. Other models play the parts.
The conductor's time is the most expensive in the room, so it should not play the long, plain parts itself,
and it should never pass on an answer it has not checked.

## 1. Should this be delegated at all?

Do it yourself when any of these hold:
- It takes fewer steps than writing the brief would.
- It needs the conversation's context that you cannot write down in a page.
- It touches secrets, credentials, production systems, or anything irreversible.
- The user is waiting on a quick answer.

Delegate when the job can be described in one self-contained brief and checked from the outside
(tests, a diff, an exact answer, a schema). Scale the effort to the job: one lane for one job. Several
lanes writing in the same area of the code cost more in conflicts than they save.

## 2. Who plays what

**First step of any session that will delegate: the roster.** `scripts/mmo-roster show` (exit 3 means
missing or older than 12 hours: run `scripts/mmo-roster probe`, one tiny read-only call per lane). It
lists which lanes really answer here now, for which tier, and why the others do not (limit, signed
out, model id). Route by the kind of work to a tier, then take the first READY lane of that tier
(`scripts/mmo-roster ready --tier cheap`), the cheapest tier that will pass the check. Below the
strong tier, external lanes come first and Claude sub-agents are the fallback, not the default.
The strong tier is the other way round: the hardest work goes to Claude Opus when it is ready.
The user can reorder any tier in `~/.config/mmo/prefer` (lines `tier lane [model]`).

**Tell the user the lineup** before the first brief: paste `scripts/mmo-roster lineup` (one line per
tier, then what is installed but unusable and why). It is an announcement, not a question: do not
wait for approval unless the user asked to approve lanes. When it changes mid-session (a lane hits a
limit and is replaced), say so in one line.

| Job | Tier | Brief style |
|---|---|---|
| Hard design, tricky bug, unfamiliar code | Strong: Claude Opus; then a top GPT, Gemini or Grok lane at high effort | Goal + constraints, let it plan |
| Routine feature, clear bug, refactor with tests | Middle: gpt-6.1-sol, a comparable agent CLI, Claude Sonnet | Steps, files, done-check |
| Easy, well-specified, testable work | Cheap: DeepSeek, Kimi, Qwen, GLM, a small GPT | Numbered steps, exact files, exact check |
| Bulk mechanical work (labeling, renames, cleanup) | Bulk: gpt-6-luna, deepseek-flash, a local model, Claude Haiku | Rules + format + examples |
| Second opinion, "what are we missing" | A strong model from **another family** than yours, read-only | The question + the evidence, ask for disagreement |
| A decision with no single right answer | Council (3 families, blind) | Same question to all |
| Long self-contained work while local lanes are busy | Cloud agent (`cloud-lane` skill), only on pushed code | A brief that needs nothing from this machine |

- Every sub-agent call names its model. A call without one inherits yours, and nine parallel lanes
  become nine copies of the most expensive model.
- Claude tiers run as your own sub-agents. Everything else goes through `scripts/mmo-run`.
  [`lanes.md`](lanes.md) lists every lane with its family, tier and how read-only is enforced; the
  `*-lane` skills hold the details for the ones used most.
- **Escalate on failure, not on a hunch.** Start at the cheapest tier that fits. When a lane fails its
  check twice, move the task one tier up (the tier's first ready lane) with the check output in the
  new brief. A `limit`, `auth` or `model` status is not a failed check: drop that lane, take the next
  ready lane of the same tier, and re-probe it later (`mmo-roster probe --lanes <lane>`).
- Model ids the CLI has no default for go in a models file (`lane model` per line,
  `mmo-roster probe --models FILE`; without it probe reads `$MMO_MODELS` or `~/.config/mmo/models`,
  see `models.example`); a lane is only READY with an id that answered.
- A lane marked `docs-...` or `help-...` in `--list` has never answered here. The roster probe is its
  smoke test; do not route real work to a lane the roster has not seen answer.
- Keep score: with `MMO_LOG=<file>` set, the runner and the checker log one line per run;
  `scripts/mmo-score <file>` shows first-try pass rates, and the roster adds them once a lane has five
  checked tasks. `mmo-score --task ID` gives the escalation advice for one task, `--share` shows
  whether the work drifted to Claude only, `--routes` ranks lanes per tier from your own runs. Record
  your own sub-agent runs with `mmo-score log-agent` so they count. `bench/run.sh` measures a lane
  before you trust it at all.
- Cost: the header and log carry the tokens and dollars a tool itself reported; `mmo-score --cost` gives
  cost per passed task, and `mmo-run --max-cost USD` caps a run where the CLI has a budget flag (docs/cost.md).

The other way round, for one long task done step by step: a cheaper model does the whole job and asks
a stronger one for advice at the hard points (Claude Code: `/advisor`; across vendors: the `advisor` skill).
Use that when there is nothing to run in parallel. This policy is for work that splits into checkable jobs.

## 3. Brief rules

A lane sees only the brief. Write it so a stranger could do the job.
- First line: the outcome, in one sentence.
- The files it may touch, and the ones it must not. Tests that already exist are read-only unless the
  job is to change them.
- The exact check it must run and pass (a command, not "make sure it works").
- Out of scope: commits, pushes, new dependencies, anything you would not accept in review.
- The way out: the last line is `DONE`, `FAILED: <reason>` or `BLOCKED: <reason>`. Say that BLOCKED
  is an acceptable answer and that editing a test or special-casing an input to get a green check is
  not. A lane with no honest way out finds a dishonest one.
- The report: at most ten lines (what changed, which files, the check's result). Anything longer goes
  into a notes file you name. You read the diff and the check, not a story.
- Never put secrets, tokens or personal data into a brief. Briefs go to other vendors.

Templates: `templates/execute.md`, `templates/retry.md`, `templates/opinion.md`, `templates/bulk.md`.

## 4. Running a lane

Always go through `scripts/mmo-run`. It is the one place where the safety rules live:

```bash
scripts/mmo-run --list                      # every lane, and whether it is ready here (offline)
git worktree add ../wt-auth -b lane/auth    # from the branch you are working on
scripts/mmo-run codex -m gpt-6.1-sol -e high --mode rw -C ../wt-auth --base my-branch \
  --brief brief.md --out out/auth.md -t 1800 --idle 600
scripts/mmo-run deepseek --mode ro --brief q.md --out out/ds.md
```

- `--mode ro` for anything that only reads. `--mode rw` refuses to run outside a linked git worktree,
  so a writing lane never edits your main checkout. One worktree per writing lane.
- **Pin the base.** Create the worktree from the branch you are on, and pass `--base <that branch or
  commit>`: the runner refuses (exit 9) when the worktree does not contain it. A lane on a stale base
  reports problems that are already fixed. Sub-agent worktrees can start from the default branch
  instead of your branch: have the brief's first step confirm the base, or merge your branch in.
- **Ceilings are yours, not the lane's.** Every run has `-t` (hard timeout). Add `--idle` for lanes
  that stream progress, and `--max-turns` where the CLI supports it. A lane cannot raise its own limits.
- The output file's first line is a status header:
  `<!-- mmo provider=… model=… mode=… status=… exit=… seconds=… base=… changed=… -->`
- Exit codes: 0 ok, 2 usage, 3 failed, 4 timeout or stalled, 5 empty, 6 limit/balance, 7 auth,
  8 model (id rejected), 9 wrong base.
- Run independent lanes in parallel. Wait for all of them before you judge any.

## 5. Gates before you use an answer

1. Status header says `ok`. Anything else is not an answer. Do not read meaning into a failed lane.
   `committed=yes` on a lane told not to commit, or `changed=0` on a writing job, is a reason to look.
2. Run the check yourself, in the lane's worktree. A lane saying DONE proves nothing, and its FAILED is a claim just the same (a lane that cannot run commands cannot run the check): run `mmo-check` on the worktree before discarding the work.
   ```bash
   scripts/mmo-check -C ../wt-auth --cmd "go test ./internal/auth/..." \
     --allow "internal/auth/*" --red --out out/auth.check.md
   ```
   It runs the command, lists the files touched outside `--allow`, existing tests that were changed or
   deleted, and changed dependency manifests. With `--red` it also runs the check on the base code
   plus the new tests, where it must fail: a check that passes without the change proves nothing
   about the change. (Read the red log: a missing dependency also fails.)
3. Read the whole diff. Reject edits outside the allowed files, weakened or deleted tests, inputs
   special-cased to satisfy a test, new dependencies, silenced warnings.
4. For work that matters, a fresh reviewer that did not see the lane's reasoning: first "does the diff
   do what the brief asked, nothing more", then "is it correct". Tell it to report correctness
   problems with evidence and to skip style; a reviewer asked to find something always does.
5. For opinions: weigh arguments, not votes. Two models agreeing is a hint, not proof.
6. Merge one lane at a time and run the quick check after each. Run the full suite after every few
   merges, not only at the end: two correct changes can break each other, and a small batch keeps
   the culprit findable.

## 6. When a lane fails

- `limit` (quota, balance, 429): switch to another lane of the same tier. Do not retry in a loop.
- `model` (unknown or unsupported model id): switch to an id the CLI accepts, or another lane. Waiting
  will not help.
- `auth`: tell the user which CLI needs a fresh login. Do not try to log in for them.
- `timeout`, `stalled` or `empty`: shrink the brief or split the job, then retry once.
- `base`: the worktree is stale. Recreate it from your branch. This is not the lane's failure.
- The check failed: retry with `templates/retry.md`, which carries the check's output word for word,
  not your summary of it. Second failure on the same check: one tier up.
- `BLOCKED`: not a failure. Read the reason; it is usually a question for you or the user.
- Never hide a failure in the final report. Say which lane failed, why, and what replaced it.

## 7. Keep your own context small

Long runs fill the conductor's context with lane reports. Keep state in files, not in your memory of
the conversation: a plan file with one row per task (status, lane, tries, commit), lane outputs and
check reports on disk, and reports capped at ten lines. After a compaction or in a new session,
rebuild from the plan file.

## 8. Lessons that were checked

Not a memory system: a short log that can only be written with proof. When a retry or an escalation
taught you something about a lane that the next brief should say (a flag it needs, a step it skips,
a kind of job it cannot carry), record it, with the passing check report as evidence:

```bash
scripts/mmo-lessons add --lane opencode --text "Name the test file in the brief or it writes none."   --check out/auth.check.md
scripts/mmo-lessons show --lane opencode      # at most 5 lines, paste them into the next brief
```

`add` refuses without a report whose status is `pass`, and refuses anything that looks like a secret
or a private path. A lesson goes stale by itself when the lane's adapter file changes. Five lines per
brief is the ceiling: a long list of old advice costs tokens and helps nobody.

## 9. Council

For decisions where reasonable models disagree, use the `council` skill: the same question to three lanes
from different families, read-only, answers shuffled and anonymized before you judge them.
