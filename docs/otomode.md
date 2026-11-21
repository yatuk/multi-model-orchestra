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
- **Lanes do the work, the conductor checks it.** Each task goes to a sub-agent or an `mmo-run` lane in its own worktree; the main agent runs the task's check itself and commits the task alone on an `otomode/<time>` branch. Three failed tries or a blocker: note why, move on.
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
$OTO on --project "<repo root>" --hours <N>   # hook ON for this session
$OTO off                                      # hook OFF
$OTO status                                   # state + usage
$OTO gate [--percent P --reset ISO]           # go / stop / unknown before each task
$OTO usage                                    # usage from the statusline file (CLI)
```

## 1. The start round

`otomode 6h` asks one round, as a plain numbered message, and waits for the answer:

1. The tasks, in priority order.
2. For each task, how to check it is done: a command (test, build, lint, script) whose exit code decides.
3. The permissions the run will need. The agent reads the settings files, derives the commands from the tasks
   and checks, and lists the allow rules still missing (for example `Bash(go test:*)`, file edits in the repo
   and its worktrees, the helper script itself). Everything not allowed now will be denied later.
4. Anything off limits (files, directories, services), and whether DeepSeek may be used.
5. If the work tree is dirty: leave it, or include it in the first commit.

Then it adds the approved allow rules to `.claude/settings.local.json`, creates the branch
`otomode/<YYYY-MM-DD-HHMM>`, writes `OTOMODE.md` at the repo root and commits it as `otomode: plan`,
turns the hook on, and schedules the hourly watchdog cron.

`OTOMODE.md` holds the run: start and end time, branch, usage stop, cron ids, the user's rules, a task table
(task, check, lane, status, tries, commit, notes) and a log. It is how a resumed or compacted session knows where it is.

## 2. What the hook does while it is on

For that session only, it:

- denies every permission prompt, `AskUserQuestion`, `EnterPlanMode` and `ExitPlanMode`, and appends each one to `<repo>/QUESTIONS.md`;
- denies delete, deploy, push and send commands outright (rm, git push, branch or worktree removal, reset --hard,
  kubectl/terraform/az/aws and other deploy CLIs, ssh/scp, POST requests, gh pr/issue writes, publish, mail) and MCP
  tools named send, post, delete, submit, upload and the like, also logged.

A denial is not a failure to retry: the agent reads the reason, takes the safe default or marks the task blocked,
and moves on. The hook matches command patterns; it is a guard rail, not a sandbox. Do not count on it to catch
every harmful command.

## 3. The work loop

Before each task: the usage gate and the deadline check. Then, for each `todo` task in order:

1. Pick the cheapest lane that can carry it: DeepSeek through `mmo-run` for easy, well-specified work when the user
   allowed it; `sonnet` for scoped, clear work; `opus` for multi-file or debugging work. A `limit` exit from DeepSeek
   moves the task, and the rest of the run, to Claude lanes.
2. Write the brief: goal, exact files, steps, the check command, the repo's rules, and "do not commit, do not push,
   do not ask questions; if blocked, stop and say why". Every lane works in its own worktree. Independent tasks may
   run in parallel, at most 3 lanes at a time.
3. When the lane returns, the conductor checks it itself: reads the diff and runs the task's check in the worktree.
   The sub-agent's word is not the check.
4. Pass: bring the change onto the otomode branch and commit it alone as `otomode T<n>: <task>`.
5. Fail: retry with the failure in the brief, escalating DeepSeek to sonnet or sonnet to opus. After 3 failed tries,
   or when the task is blocked, mark it `blocked` or `failed`, write why in the notes and in `QUESTIONS.md`, and move on.
6. When no task is left or the deadline passed: write the summary into `OTOMODE.md`, commit it, and stay idle with
   the hook on until you say `otomode off`.

## 4. Usage gate, resume and watchdog

- **Gate.** Before every new task, `otomode.py gate` looks at the higher of the 5-hour and weekly windows.
  `go` starts the task, `unknown` allows one task and then gates again, `stop` (85% or more) starts nothing new:
  running lanes finish, ready work is committed, and a one-shot `otomode resume` cron is scheduled for just after
  the reset.
- **Resume.** Re-reads `OTOMODE.md`, gates again and continues from the first unsettled task. A task left `running`
  is checked first: if its worktree has a change it is verified, otherwise restarted (and counted as a try).
- **Watchdog.** Every hour: is otomode still on, is a resume cron needed, did the loop stall, has a lane been running
  for more than 90 minutes, is the run past its end time. It appends one line to the log.

Crons live in the session. Keep the session open.

## 5. `otomode off`

In this order:

1. The hook goes off first, so nothing in the report step is denied.
2. The watchdog and any resume cron are deleted.
3. A short report, under 15 lines: tasks done with commit hashes, blocked or failed with the reason, the branch name,
   worktrees left in place, how many prompts were denied, usage at the end. Nothing is pushed or merged.
4. The saved questions from `QUESTIONS.md`, grouped, with the offer to redo the blocked tasks with your answers.

## Hard rules for the whole run

- Never wait on the user, never ask a question after the start round.
- Never delete, deploy, push or send, even if a task seems to need it; write what would be needed into the notes.
- Never remove the worktrees or branches it created; list them in the report.
- Commit only on the otomode branch, one commit per task, task id in the subject.
- Every sub-agent call names its model explicitly; no sub-agent asks questions or commits.

## One real run

One run, not a benchmark: 5 hours, 13 tasks, one commit each. Weekly plan usage went from 25% to 31%,
and 6 prompts were denied and logged to `QUESTIONS.md` for the end of the run.
