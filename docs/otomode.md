# otomode: work while you are away

[Back to the README](../README.md) · Skill: [`skills/otomode/SKILL.md`](../skills/otomode/SKILL.md) · Turkish write-up: [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md)

```
otomode 6h        ask everything once, write OTOMODE.md, turn the hook on, work
otomode off       hook off first, short report, then the questions it saved
otomode status    state, usage and the next cron
otomode resume    continue after a usage pause (started by cron)
otomode watchdog  hourly check that the loop has not stalled (started by cron)
```

The danger in leaving an agent alone is that it waits for hours on a permission prompt, or stops because a
question got no answer. otomode turns that around: everything is asked once at the start, then nothing waits.

## In short

- **One round of questions, then none.** Tasks, the check for each (a command whose exit code decides), the allow rules the run needs, what is off limits. After that a hook denies every permission prompt and every question for that session and appends it to `QUESTIONS.md`; the agent takes the safe default or marks the task blocked and moves on.
- **Never delete, deploy or send.** The hook also refuses `rm`, `git push`, branch and worktree removal, `reset --hard`, deploy CLIs, ssh/scp, write requests, `gh pr`/`issue` writes, publish and mail, plus MCP tools named send, post, delete, submit or upload. It is a guard rail, not a sandbox.
- **Lanes do the work, the conductor checks it.** Each task goes to a sub-agent or an `mmo-run` lane in its own worktree; the main agent runs the task's check itself through `mmo-check` and commits the task alone on an `otomode/<time>` branch. Three failed tries or a blocker: note why, move on.
- **Usage aware.** `otomode.py gate` says go or stop before every task; at 85% it stops starting work and schedules a one-shot cron for just after the reset. An hourly watchdog cron restarts a stalled loop. Crons live in the session, so keep it open.

## Setup, once

```bash
python ~/.claude/skills/otomode/scripts/otomode.py install     # python3 where python is not on PATH
```

This registers the hook in `~/.claude/settings.json` (PermissionRequest `*`, PreToolUse on Bash, PowerShell,
ask tools and `mcp__.*`). `otomode.py uninstall` removes it. The hook does nothing while otomode is off.

For the usage gate in the CLI, use `skills/otomode/scripts/statusline.py` as your status line (or call it from
yours); it saves the plan usage Claude Code passes to it. In the Claude desktop app the gate reads usage from the
app instead.

The helper script holds all state, the hook and the usage readout:

```bash
OTO="python ~/.claude/skills/otomode/scripts/otomode.py"
$OTO on --project "<repo root>" --hours <N>   # hook ON for this session (needs a Lanes: line and a session id)
$OTO off                                      # hook OFF
$OTO status                                   # state + usage
$OTO gate [--percent P --reset ISO]           # go / stop / unknown before each task
$OTO usage                                    # usage from the statusline file (CLI)
$OTO lane T<n> <lane>                         # record a Claude lane launch for the scoreboard
$OTO merged T<n> --quick-exit <code>          # after each cherry-pick: the quick check's exit code
$OTO cron [--watchdog ID] [--resume ID]       # record cron job ids in the state
$OTO score                                    # per-lane first-try passes from .otomode/lanes.jsonl
```

## 1. The start round

`otomode 6h` first runs `mmo-roster probe` (one tiny read-only call per installed lane) and shows the
**lineup**: which lane and model will play each tier, and what is installed but unusable now and why (out of
credit, not signed in, needs a model id). Then it asks one round, as a plain numbered message, and waits:

1. The tasks, in priority order, each with the files it may touch.
2. For each task, how to check it is done: a command (test, build, lint, script) whose exit code decides.
3. The permissions the run will need. The agent reads the settings files, derives the commands from the tasks
   and checks, and lists the allow rules still missing (for example `Bash(go test:*)`, file edits in the repo
   and its worktrees, the helper script itself). Everything not allowed now will be denied later.
4. Anything off limits (files, directories, services, vendors). Every ready lane may be used unless you veto it.
5. A time budget per task (default 45 minutes).
6. Whether to set `worktree.baseRef` to `"head"`: without it, Claude sub-agent worktrees start from the default
   branch, not from the otomode branch.
7. If the work tree is dirty: leave it, or include it in the first commit.

Then it adds the approved allow rules to `.claude/settings.local.json`, runs one lane tool in the exact command form
the run will use (so a rule that does not match shows while you are there), creates the branch
`otomode/<YYYY-MM-DD-HHMM>`, writes `OTOMODE.md` at the repo root and commits it as `otomode: plan`,
turns the hook on, and schedules the hourly watchdog cron.

`OTOMODE.md` holds the run: start and end time, branch, usage stop, cron ids, the `Lanes:` line (ready lanes per
tier, and the ones out with the time and reason), the user's rules, a task table
(task, check, lane, status, tries, commit, notes) and a log. It is how a resumed or compacted session knows where it is.

## 2. What the hook does while it is on

For that session only, it:

- denies every permission prompt, `AskUserQuestion`, `EnterPlanMode` and `ExitPlanMode`, and appends each one to `<repo>/QUESTIONS.md`;
- denies delete, deploy, push and send commands outright (rm, git push, branch or worktree removal, reset --hard,
  kubectl/terraform/az/aws and other deploy CLIs, ssh/scp, POST requests, gh pr/issue writes, publish, mail) and MCP
  tools named send, post, delete, submit, upload and the like, also logged.

Every denial is logged with a class: `off_limits` (a delete, push, deploy or send rule fired: working as designed),
`question` (a question or plan-mode tool) or `allowlist_gap` (a plain permission prompt for something the start round
did not allow). `otomode.py status` and `off` print the counts and, for the gaps, the distinct commands or tools as
suggested allow rules (first word or two of each command segment, deduplicated, at most 20). Claude Code needs every
segment of a compound command (`a; b`, `a && b`, a pipe, a loop body) allowed, so the hook lists one rule per segment;
it does not read Claude Code's allow rules, so it cannot tell which segments were already covered and lists all of
them. Classify before loosening anything: only the gaps are candidates for new allow rules.

A denial is not a failure to retry: the agent reads the reason, takes the safe default or marks the task blocked,
and moves on. The hook matches command patterns; it is a guard rail, not a sandbox. Do not count on it to catch
every harmful command.

## 3. The work loop

Before each task: the usage gate and the deadline check. Then, for each `todo` task in order:

1. Give the task a tier (strong, middle, cheap, bulk) and take the first lane of that tier on the `Lanes:` line:
   external lanes first, a Claude sub-agent only when no external lane of that tier is left. The parent owns
   the ceilings: `mmo-run` lanes get `-t <budget>`, `--idle 600`, `--max-turns` and `--base otomode/<stamp>` (exit 9
   means a stale worktree: recreate it, not a try); Claude sub-agents get the task's time budget, which the watchdog
   enforces. A lane that hits a ceiling is stopped and counts as a try. A `limit`, `auth` or `model` exit takes only
   that lane out (noted on `Lanes:` with the time); the task moves to the next lane of the same tier, not a try.
   Every lane change is a log line, so the end report says which model did which task.
2. Write the brief: goal, exact files, steps, the check command, the repo's rules, and "do not commit, do not push,
   do not ask questions". Changing tests or special-casing to make the check pass is not acceptable; `BLOCKED: <reason>`
   is an acceptable last line. The lane ends with at most 10 lines (what changed, files, check result, DONE, FAILED or
   BLOCKED) and puts anything longer in `.otomode/T<n>.notes.md`. Claude lanes first merge the otomode branch into
   their worktree. Independent tasks may run in parallel, at most 3 lanes at a time.
3. When the lane returns, the conductor checks it itself with
   `mmo-check -C <worktree> --cmd "<task check>" --allow <task files> --out .otomode/T<n>.check.md` (plus `--red` for
   tasks that add tests). fail = a failed try; policy (files outside the task) = reject, or keep with the reason in
   the notes; not-red = the new test does not test the change, a failed try. Changed or deleted existing tests are
   read before merge. A `BLOCKED` lane is not a failed try: the task goes to `blocked` with the reason.
4. Pass: commit the change alone as `otomode T<n>: <task>`, bring it onto the otomode branch, run the quick check and
   record its exit code with `otomode.py merged T<n> --quick-exit <code>` (`status` and the end report then show
   "quick check after merge: 3 of 3 tasks").
5. Fail: retry with the tail of the check report pasted verbatim (not a summary); the second failure moves the task
   one tier up, to that tier's first lane. After 3 failed tries, or when the task is blocked, mark it `blocked` or `failed`, write why in the
   notes and in `QUESTIONS.md`, and move on.
6. Integration gate: after every 4 merged tasks, and at the end, the full check runs on the otomode branch. A red full
   check is fixed or the offending commit reverted before any new merge.
7. When no task is left or the deadline passed: write the summary (with `otomode.py score`) into `OTOMODE.md`, commit
   it, and stay idle with the hook on until you say `otomode off`.

`mmo-run` and `mmo-check` run with `MMO_LOG=<repo>/.otomode/lanes.jsonl MMO_TASK=T<n>`, so every lane run and check
lands in one JSONL file; `otomode.py score` turns it into first-try pass counts per lane.

After a resume or a compaction the session re-reads the `Lanes:` line instead of its memory, and the watchdog
re-probes when the roster is older than 12 hours or a lane is out, so a lane whose limit has reset comes back.
Without this, earlier runs drifted to Claude lanes only: see [failures](failures.md).

## 4. Usage gate, resume and watchdog

- **Gate.** Before every new task, `otomode.py gate` looks at the higher of the 5-hour and weekly windows.
  `go` starts the task, `unknown` allows one task and then gates again (the JSON says `why`: no usage file at a path,
  or one older than 15 minutes; print mode has neither the statusline file nor the desktop usage tool, so there the
  gate stays `unknown` and the run goes one task at a time), `stop` (85% or more) starts nothing new:
  running lanes finish, ready work is committed, and a one-shot `otomode resume` cron is scheduled for just after
  the reset.
- **Resume.** Rebuilds from `OTOMODE.md` and `.otomode/` (not from the conversation), gates again and continues from the first unsettled task. A task left `running`
  is checked first: if its worktree has a change it is verified, otherwise restarted (and counted as a try).
- **Watchdog.** Every hour: is otomode still on, is a resume cron needed, did the loop stall, has a lane run past
  its task's time budget, is the run past its end time. It appends one line to the log.

Crons live in the session. Keep the session open.

## 5. `otomode off`

In this order:

1. The hook goes off first, so nothing in the report step is denied.
2. The watchdog and any resume cron are deleted.
3. A short report, under 15 lines: tasks done with commit hashes, blocked or failed with the reason, the branch name,
   worktrees left in place, denials per class with suggested allow rules, per-lane first-try passes,
   usage at the end. Nothing is pushed or merged.
4. The saved questions from `QUESTIONS.md`, grouped, with the offer to redo the blocked tasks with your answers.

## Hard rules for the whole run

- Never wait on the user, never ask a question after the start round.
- Never delete, deploy, push or send, even if a task seems to need it; write what would be needed into the notes.
- Never remove the worktrees or branches it created; list them in the report.
- Commit only on the otomode branch, one commit per task, task id in the subject.
- Every sub-agent call names its model explicitly; no sub-agent asks questions or commits.

## Native Claude Code settings that overlap

The Claude Code docs name settings that cover part of what the hook and the gate do. They are alternatives to know
about, not replacements: none of them logs to `QUESTIONS.md` or refuses an allowed command that deletes or pushes.
Check your Claude Code version before relying on them; they are not tested with otomode.

- `permissions.denyInsteadOfPrompting` (or `--permission-prompts none` in headless runs) denies instead of prompting;
  denials arrive in `permission_denials` in the JSON result. Source: the headless docs, code.claude.com/docs/en/headless.
- `autoContinueAtUsageLimit` waits for the usage reset and continues, like the gate's resume cron. Source: the costs
  docs, code.claude.com/docs/en/costs.
- `worktree.baseRef: "head"` makes sub-agent worktrees start from your current HEAD. Source: the worktrees docs,
  code.claude.com/docs/en/worktrees. otomode offers this one in the start round.

## What changed in 1.1

- Denials carry a class (`off_limits`, `question`, `allowlist_gap`); `status` and `off` count them and list the gaps
  as suggested allow rules. `QUESTIONS.md` entries show the class.
- Base pinning is mechanical: `mmo-run --base otomode/<stamp>` for external lanes, `worktree.baseRef` offered for
  Claude lanes.
- Task checks run through `mmo-check` (allowed files, `--red` for new tests); retries get the check output verbatim.
- Lanes may stop with `BLOCKED: <reason>`, which is not a failed try; gaming the check is named as unacceptable.
- The full check runs after every 4 merged tasks, not once in the middle of long runs.
- Per-task time budgets (default 45 minutes) and parent-owned ceilings (`-t`, `--idle`, `--max-turns`).
- Lanes end with at most 10 lines; longer notes go to `.otomode/T<n>.notes.md`.
- Scoreboard: `MMO_LOG` and `MMO_TASK` on every lane call, `otomode.py score` for first-try passes per lane.

## One real run

One run, not a benchmark: 5 hours, 13 tasks, one commit each. Weekly plan usage went from 25% to 31%,
and 6 prompts were denied and logged to `QUESTIONS.md` for the end of the run.

## Found in a real run

A first end-to-end run (3 tasks on an external lane, each verified with `mmo-check`, one with red before green, one
commit per task, 2 denials, both allowlist gaps) completed, and showed six rough edges. Each is fixed:

1. **The skill's own command form was denied.** `mmo-check ...; echo exit=$?` needs an allow rule for each segment, and
   `echo` had none. `mmo-check` and `mmo-run` write a status header as the first line of their out file, so the skill now
   runs them as one simple command and reads that header; the `; echo "exit=$?"` tail is kept only for a raw check and
   the start round asks for `Bash(echo:*)`. Loops and chains are to be avoided: every segment needs its own rule.
2. **The suggested rule named the wrong command.** For a compound command the hook suggested the first word. It now
   splits the command with `cmdscan` and suggests one rule per segment (env prefixes and loop keywords skipped), and the
   `QUESTIONS.md` entry says a compound command needs every segment allowed.
3. **`.git/info/exclude` could not be edited.** Claude Code refuses a model edit of it. `otomode.py on` now appends
   `.otomode/` and `QUESTIONS.md` itself (resolved with `git rev-parse --git-path`, so a worktree works) and reports the
   result in its JSON; it never fails the `on`.
4. **Steps were skipped.** `on` now refuses (`--force` overrides) when OTOMODE.md has no `Lanes:` line naming a lane,
   and reminds that the lineup must have been shown; `merged T<n> --quick-exit <code>` records the quick check after
   each merge. When background running is not available, lanes run one at a time in the foreground.
5. **Record-keeping.** `otomode.py cron --watchdog ID` / `--resume ID` store the cron ids in the state (`status` shows
   them); `gate` says why it is `unknown`; lanes are written `<lane> <model>` (a space, copied from `mmo-roster lineup` or
   `ready`), not `lane/lane-model-id`.
6. **Session scoping.** Without a session id the hook would deny in every session on the machine. `on` now refuses
   unless `--all-sessions` is given, and `status` shows the first 8 characters of the bound session.
