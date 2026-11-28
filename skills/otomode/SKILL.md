---
name: otomode
description: "Unattended work mode for when the user is away. `otomode 6h` asks everything up front in one round (tasks, how to check each, permissions), writes OTOMODE.md, turns on a hook that denies every permission prompt and question and logs it to QUESTIONS.md, then works task by task through every lane that answered the start-round probe (external CLIs through mmo-run, Claude sub-agents), verifies each with its own check and commits each separately, pauses at 85% usage and resumes by cron after the reset, with an hourly watchdog. `otomode off` turns the hook off, reports and asks the saved questions. Also handles `otomode resume`, `otomode watchdog`, `otomode status`."
---

# otomode

The user is away. Work through an agreed task list without ever waiting on
them; leave everything reviewable: one commit per task, a plan file, a
question log. Helper script (state, hook, log, usage readout):

```bash
OTO="python $HOME/.claude/skills/otomode/scripts/otomode.py"   # python3 where python is not on PATH
$OTO on --project "<repo root>" --hours <N>   # hook ON for this session (refuses: see step 6)
$OTO off                                      # hook OFF; prints cleanup_left_for_you
$OTO status                                   # state, session, crons, quick checks, denials, usage
$OTO log "<text>"                             # "- HH:MM <text>" into the OTOMODE.md log
$OTO gate [--percent P --reset ISO]           # go / stop / unknown (with why) before each task
$OTO lane T<n> <lane>                         # record a Claude lane launch (scoreboard)
$OTO merged T<n> --quick-exit <code>          # after each cherry-pick: the quick check's exit code
$OTO cron [--watchdog ID] [--resume ID]       # record cron job ids in the state
$OTO score                                    # per-lane first-try passes from lanes.jsonl
```

`$OTO` is shorthand: write the full command each time (variables do not
survive between tool calls), exactly as in its allow rule. Setup, once:
`$OTO install` registers the hook in `~/.claude/settings.json` (`uninstall`
removes it); it does nothing while otomode is off. For usage in the CLI use
`scripts/statusline.py` as the status line; the desktop app has `get_usage`
(section 3). While on, for this session only, the hook:

- denies every permission prompt, `AskUserQuestion`, `EnterPlanMode` and
  `ExitPlanMode`, and appends each one to `<repo>/QUESTIONS.md`;
- denies delete, deploy, push and send commands (rm, git push, branch or
  worktree removal, reset --hard, kubectl/terraform/az/aws, ssh/scp, POST
  requests, gh pr/issue writes, publish, mail, `| sh`) and MCP tools named
  send, post, delete, submit, upload and the like, logged for the end report.
  Bash is judged by the commands that would run (echo and commit messages may
  name them); unparseable lines and PowerShell by whole-text regex.

Denial classes: `off_limits` (as designed), `question`, `allowlist_gap` (a
prompt the start round did not allow; a compound command gets one suggested
rule per segment). `status` and `off` print counts and rules. A denial is not
a failure to retry: take the safe default or mark the task blocked.

## Hard rules (whole run)

- Never wait on the user; no AskUserQuestion after the start round.
- Never delete, deploy, push or send messages, even if a task seems to need it;
  write what would be needed into the task's notes. Never remove worktrees or
  branches you created; list them in the report.
- Commit only on the otomode branch, one commit per task, task id in the
  subject, following the repo's CLAUDE.md and trailer rules.
- Every launch names its model (a sub-agent's `model`, an mmo-run lane's
  `-m`); no lane asks questions or commits. Every lane works on the otomode
  branch's code, never the default branch's (loop steps 1, 2 and 4).
- Task checks go through `mmo-check` (loop step 3). mmo-check and mmo-run
  write a status header as the first line of their out file: run each as ONE
  simple command, then read that header in a separate call; no `; echo`. For a
  raw quick or full check never let a pipe hide the exit code: run
  `<check> > <repo>/.otomode/<name>.log 2>&1; echo "exit=$?"` (needs
  `Bash(echo:*)`), read the log's tail in a separate call. If you must pipe,
  start with `set -o pipefail`.
- Every segment of a compound command (`a; b`, `a && b`, pipes, `for`/`while`
  loops) needs its own allow rule, or the whole command is denied. Avoid
  chains and loops: one simple command per call, one call per worktree.
- Your state is OTOMODE.md and `<repo>/.otomode/`, not the conversation: after
  a resume or a compaction rebuild from them; the `Lanes:` line is the routing
  table (re-probe when the roster is stale).
- Never write a time from memory: `$OTO log` for log lines, else `date +%H:%M`.

## 1. Start: `otomode <duration>` (e.g. `otomode 6h`)

`TOOL <name>` stands for the one command form every lane tool runs in:
`MMO_LOG=<repo>/.otomode/lanes.jsonl MMO_TASK=<id> bash <home>/.claude/skills/orchestra/scripts/<name>`
(absolute home, no `~`), written in full and always in exactly this form, so
one allow rule covers mmo-run, mmo-check and mmo-roster.

1. Probe the lanes first, while the user is there: `TOOL mmo-roster probe
   --out <repo>/.otomode/roster.json` (`MMO_TASK=roster`; one tiny call per
   lane; `--models <file>` for lanes without a default id), then
   `... mmo-roster lineup --file <repo>/.otomode/roster.json`.
2. Ask **one** round, as a plain numbered message (not AskUserQuestion, so
   free text fits), and wait. It is not optional: paste the **lineup** from
   step 1 on top, unedited (which model plays which tier, what is unusable and
   why; the user may veto a lane or fix a sign-in now). `on` (step 6) refuses
   without a `Lanes:` line. If the message already lists tasks and checks, use
   them and ask only what is missing:
   1. The tasks, in priority order, each with the files it may touch.
   2. For each task, how to check it is done: a command (test, build, lint,
      script) whose exit code decides. Offer a concrete check per task. Also
      the repo's **quick check** (its fast gate, run after every merge) and
      **full check** (what CI runs), e.g. from CLAUDE.md or the CI config.
   3. The permissions the run will need. Read `.claude/settings*.json` and
      `~/.claude/settings.json`, derive the commands from the tasks and checks
      (test runners, build, git checkout/add/commit/merge/cherry-pick/
      worktree add, `date`), and list the allow rules still missing, e.g.
      `Bash(go test:*)`. Always include `Bash(echo:*)` (the
      `; echo "exit=$?"` tail), file edits `Edit(<repo>/**)`,
      `Edit(<repo-parent>/wt-*/**)` (mmo-run worktrees) and
      `Edit(<repo>/.claude/worktrees/**)` (sub-agent worktrees) unless the
      session runs in auto or acceptEdits mode; the helper
      `Bash(python <home>/.claude/skills/otomode/scripts/otomode.py:*)`; the
      lane tools `Bash(MMO_LOG=<repo>/.otomode/lanes.jsonl MMO_TASK=*)`; and
      `Read(<home>/.claude/skills/**)`. Everything not allowed now is
      denied later, so be generous within the repo. Ask whether to add them
      to `.claude/settings.local.json`.
   4. Anything off limits (files, directories, services, vendors). Every
      ready lane in the lineup may be used unless the user says otherwise.
   5. A time budget per task in minutes (default 45); a lane past it is stopped.
   6. Sub-agent worktrees start from the default branch unless
      `worktree.baseRef` is `"head"`; if unset, offer to add
      `"worktree": {"baseRef": "head"}` to `.claude/settings.local.json`.
   7. If the work tree is dirty: leave it, or include it in the first commit?
3. After the answer: add the approved allow rules (and `worktree.baseRef` if
   accepted) to `.claude/settings.local.json` (merge, never replace; use the
   Write or Edit tool, not a shell heredoc, so the user sees one approval). If
   a write is refused, say which approval is needed and stop; do not turn the
   hook on with setup unfinished. (`on` writes `.otomode/` and `QUESTIONS.md`
   into `.git/info/exclude` itself; never edit that file.) Create the branch
   `otomode/<YYYY-MM-DD-HHMM>` from HEAD unless told otherwise. Then run
   `TOOL mmo-roster show --file <repo>/.otomode/roster.json` (`MMO_TASK=smoke`,
   no model call): if that still prompts, the allow rule does not match the
   command form; fix it now, not at 3 a.m.
4. Run the quick check once on the new branch; note an existing failure in
   OTOMODE.md, so a later one is known to be the run's.
5. Write `OTOMODE.md` at the repo root (format below), with the lineup on the
   `Lanes:` line minus vetoed lanes, and commit it as `otomode: plan`. Copy
   lane and model names from `mmo-roster lineup` / `ready` as they print
   (`<lane> <model>`, a space, no slash); never compose or shorten them.
6. Turn the hook on: `$OTO on --project "<repo root>" --hours <N>`. It
   refuses without a `Lanes:` line naming a lane (`--force`: do not) or a
   session id (`--all-sessions` only if the user asks).
7. Schedule the watchdog with CronCreate: cron `17 * * * *`, recurring, prompt
   `otomode watchdog`; then `$OTO cron --watchdog <id>` (the state is the
   reliable record) and the id in OTOMODE.md.
8. Say in one line that otomode is on and until when; start working.

### OTOMODE.md

```markdown
# Otomode run
Started: <time> · Ends: <time> · Branch: otomode/<stamp> · Usage stop: 85%
Watchdog cron: <id> · Resume cron: <id or none>
Quick check: `<cmd>` · Full check: `<cmd>` · Roster: <time>
Lanes: strong=<lane> <model>,opus · middle=<lane> <model>,sonnet · cheap=<lane> <model>,... · bulk=...,haiku · out: <lane> (limit <HH:MM>)

## Rules from the user
- <off limits, vetoed lanes, dirty tree decision>

## Tasks
| # | Task | Check | Files | Lane | Min | Status | Tries | Commit | Notes |
|---|------|-------|-------|------|-----|--------|-------|--------|-------|
| T1 | ... | `go test ./internal/x/...` | `internal/x/*` | cheap: <lane> | 45 | todo | 0 | | |

## Log
- <HH:MM from $OTO log> T1 started (cheap: <lane> <model>, worktree ...)
```

`Files` is the task's `--allow` list for mmo-check, `Min` its time budget,
`Lane` the tier and lane now on it. Status: `todo`, `running`, `done`,
`blocked`, `failed`. Update the table after every step; log with `$OTO log`.

## 2. Work loop

Before each task: the usage gate (section 3) and the deadline check (past
`Ends`: no new tasks, go to step 7). For each `todo` task, in order:

1. Give the task a tier (orchestra skill: strong, middle, cheap, bulk) and
   take the first lane of that tier on the `Lanes:` line: external lanes
   first, a Claude sub-agent only when none of that tier is left (strong
   tier: Opus first).
   - An `mmo-run` lane: write the brief to `<repo>/.otomode/T<n>.brief.md`,
     `git worktree add <repo-parent>/wt-<lane>-T<n> -b otomode-<lane>/T<n> otomode/<stamp>`
     (one command per task, no loop) and start it with Bash
     `run_in_background` (if that is unavailable, run lanes one at a time in
     the foreground; never call a tool whose schema is not loaded, load it with
     ToolSearch first): `TOOL mmo-run <lane> -m <model> --mode rw -C <repo-parent>/wt-<lane>-T<n> --base otomode/<stamp> --brief <repo>/.otomode/T<n>.brief.md --out <repo>/.otomode/T<n>.out.md -t <Min*60> --idle 600 --max-turns 80`
     (`MMO_TASK=T<n>`). Exit 9: stale worktree; recreate it (not a try).
     Exit 6 (limit), 7 (auth) or 8 (model rejected): that lane is out (until a
     re-probe shows it back), the others stay: move it to `out:` on `Lanes:`
     with time and reason, and rerun the task on the next lane of the same
     tier (not a try). Exit 4 or any other non-zero exit: a failed try.
   - A Claude sub-agent (`opus`, `sonnet`, `haiku`), with
     `isolation: "worktree"`: run `$OTO lane T<n> <model>`; the watchdog stops
     it past `Min` (a failed try).
   Every lane change is a `$OTO log` line (`T<n> lane <old> -> <new>: <why>`).
2. Write the brief. For Claude lanes its **first line** is: "First run
   `git merge otomode/<stamp>` in your worktree; if that fails, stop and say
   so." Then: goal, exact files, steps, the check command, the repo's rules,
   and: "Do not commit, push or ask questions. Use the Bash tool, not
   PowerShell, only simple commands; never pipe a check without `set -o
   pipefail`. Changing or deleting tests, or special-casing code to make the
   check pass, is not acceptable. If the task cannot be done honestly, stop
   with `BLOCKED: <reason>`. End with at most 10 lines: what changed, files,
   check result, then DONE, FAILED: <why> or BLOCKED: <reason>; longer notes
   go to `<repo>/.otomode/T<n>.notes.md`." Independent tasks may run in
   parallel (at most 3 lanes).
3. When the lane returns, check it yourself; its word is not the check. A
   lane ending in `BLOCKED:` is not a failed try: set the task `blocked`, the
   reason in Notes and QUESTIONS.md. Otherwise run
   `TOOL mmo-check -C <worktree> --base otomode/<stamp> --cmd "<task check>" --allow <glob> --out <repo>/.otomode/T<n>.check.md`
   (one `--allow` per `Files` glob; `--red` when the task adds tests) as one
   simple command, and read the header line of the out file. Exit 0 pass: go
   to step 4. 1 fail, 4 timeout: a failed try. 3 policy (files outside
   `Files`, or protected): reject as a failed try, or keep it only with the
   reason in Notes. 5 not-red: the new test passes without the change, so it
   does not test it; a failed try. Read the report and the diff, not the
   lane's narrative; read the hunks of changed or deleted existing tests
   (`tests_changed`) before merging. A lane that stopped "waiting on
   background work" is not resumed: run mmo-check on its worktree yourself.
4. Pass: commit in the lane's worktree (`otomode T<n>: <task>`). Then
   `git log --oneline otomode/<stamp>..<lane branch>` must list only that
   commit (plus the merge from step 2); anything else means a wrong base: do
   not merge, retry instead (a try). `git cherry-pick <commit>` onto the
   otomode branch, run the **quick check** there (after every merge), then
   `$OTO merged T<n> --quick-exit <code>` with its exit code. If it failed,
   fix it now (a follow-up commit, or `git revert`, never reset) before the
   next merge. Record the hash, set `done`, `$OTO log` it.
5. Fail: increment Tries and retry with the last 40 lines of `T<n>.check.md`
   pasted verbatim into the brief. The second failed try moves the task one
   tier up (cheap to middle to strong), to that tier's first lane, external
   first. After 3 failed tries, or when the task is blocked (a needed
   permission was denied, a decision is the user's, something off limits), set
   `blocked` or `failed`, write why in Notes and QUESTIONS.md, and move on.
6. Integration gate: after every 4 merged tasks, run the **full check** on the
   otomode branch. A red full check is fixed (its own commit) or the offending
   commit reverted before any new merge.
7. When no `todo` task is left or the deadline passed: run the full check,
   write the summary into OTOMODE.md (with its result, `$OTO status`'s quick
   check line and `$OTO score`), commit it (`otomode: summary`), stop the
   watchdog only if every task is settled, and stay idle. Keep the hook on
   until the user says `otomode off`.

## 3. Usage gate

Run the gate before **every** new task and in every watchdog run. Do not skip it.

1. If `mcp__ccd_session_mgmt__get_usage` exists (desktop app; load it via
   ToolSearch), call it, take the window with the highest `percentUsed`, and
   run `$OTO gate --percent <percentUsed> --reset <resetsAt>`. Otherwise
   (CLI) run `$OTO gate`, which reads the statusline file.
2. Act on `decision`:
   - `go`: start the task.
   - `unknown` (`why` says so; print mode has no statusline file and no
     `get_usage`): one task at a time, gate again after each.
   - `stop` (85% or more): start nothing new. Let running lanes finish, verify
     and commit what is ready. Then CronCreate with `cron` = the gate's
     `resume_cron`, `recurring: false`, prompt `otomode resume`; run
     `$OTO cron --resume <id>`, write the id, `resume_at` and the percent into
     OTOMODE.md, and stop. If the gate's note says the reset is after the run
     ends, write the summary instead.

## 4. `otomode resume`

Run `$OTO status`. If off, do nothing. Otherwise rebuild from OTOMODE.md and
`.otomode/`, run `TOOL mmo-roster show --file <repo>/.otomode/roster.json`; on
exit 3 probe again and rewrite `Lanes:` (a lane that is back returns; log the
change). Gate, and continue from the first unsettled task. A task left
`running` is checked first: if its worktree has a change, verify it (loop
step 3); otherwise restart it (it counts as a try).

## 5. `otomode watchdog` (hourly cron)

Quick and cheap, no new work unless the loop has stalled:

1. `$OTO status`: if off, CronDelete the watchdog and stop.
2. Usage gate. Over 85% with no resume cron scheduled: schedule it.
3. No lane running, tasks `todo`, usage fine, no resume cron pending: the
   loop stalled; continue it (as in resume).
4. A lane past its task's `Min` budget, or idle-waiting on its own background
   work: read its output. Work done: verify it yourself (loop step 3); not
   done: stop it (TaskStop) and count a failed try.
5. Roster older than 12 hours, or a lane in `out:`: re-probe as in resume.
   Past `Ends`: no new tasks; finish step 7 of the work loop. `$OTO log` a line.

## 6. End: `otomode off`

In this order:

1. `$OTO off` first, so the hook stops denying before anything else. Keep its
   `cleanup_left_for_you`, `denials_by_class` and `suggested_allow_rules`.
2. CronDelete the watchdog and any resume cron (CronList to find them).
3. A short report, under 15 lines: tasks done (commit hashes), blocked or
   failed with the reason, the branch name, the full check's result, the
   `quick_check` line, denials per class with the suggested allow rules, which
   lane did each task and each lane change (from the log), first-try passes
   from `$OTO score`, usage at the end. Nothing is pushed or merged. Then a
   **Cleanup left for you** block, one exact command per line: the
   `cleanup_left_for_you` housekeeping and the removal of the worktrees and
   lane branches this run created (`git worktree remove <path>`,
   `git branch -D <branch>`).
4. Then ask the saved questions from QUESTIONS.md: group them, skip ones that
   no longer matter or are in the cleanup block, and ask with AskUserQuestion
   (up to 4 per call) where there are clear options, as plain text otherwise.
   Offer to redo the blocked tasks with the answers.

## `otomode status`

`$OTO status`, then three lines: tasks by status, usage and denials, next cron.
