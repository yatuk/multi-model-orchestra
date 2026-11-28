---
name: cloud-lane
description: EXPERIMENTAL. Hand a self-contained brief to an asynchronous cloud coding agent (Devin, Cursor cloud agents, GitHub Copilot cloud agent) through mmo-cloud and get back a pull request or branch to check. Use for long, self-contained work while local lanes are busy or at their limits. Needs the orchestra skill's scripts and a vendor key in the environment.
---

# Cloud lane (experimental)

Written from vendor documentation and not yet run against real accounts. Treat every result with
more suspicion than a local lane's, and tell the user when you use it. Details per agent: `docs/lanes/cloud.md`.

## Before you start

- These agents work on a copy of the repo on a host they can reach (GitHub). The branch you name
  must be pushed first. Pushing is the user's call, never the conductor's: ask, do not push.
- The brief goes to that vendor. No secrets, tokens, internal hostnames or personal data in it.
- `../orchestra/scripts/mmo-cloud list` shows which agents have their keys set (offline).

## Run

```bash
S=../orchestra/scripts
$S/mmo-cloud start devin --brief brief.md --repo OWNER/NAME --base lane/base --cap 10 --state out/devin.json
$S/mmo-cloud wait   --state out/devin.json -t 5400 --every 120
$S/mmo-cloud result --state out/devin.json      # pr=... and branch=... lines
$S/mmo-cloud cancel --state out/devin.json      # devin and cursor only
```

- Devin needs `--cap` (ACU limit, sent to Devin). Cursor and Copilot have no cap to send: `start`
  says so, and your `wait -t` plus `cancel` are the only bounds. Copilot cannot be cancelled by script.
- `wait` timing out (exit 4) does not stop the remote run. Decide: wait again, or cancel.
- `status=waiting` (exit 10) means the agent asked a question. Unattended, that is a stop: cancel it
  or tell the user; do not answer it from the vendor's page on the user's behalf.

## The result is a claim

Same gates as any lane (orchestra section 5):
1. Fetch the branch into its own worktree: `git fetch origin <branch> && git worktree add ../wt-cloud-<task> FETCH_HEAD`.
2. Run the check yourself (`mmo-check`, the tests named in the brief). The agent saying it passed proves nothing.
3. Read the whole diff against the base. Reject edits outside the brief, weakened tests, new dependencies.
4. Never merge from the vendor's UI and never let the vendor merge. Merging stays with the user's normal flow.

## When to use it, when not

Use: long, self-contained work with an outside check (a feature with tests, a migration) while the
local lanes are busy or at their limits.

Do not use: anything that needs local secrets or services, work that is not pushed, a quick answer,
or a job the user has not agreed to send to that vendor.

## Failures

`limit` (exit 6): credits, quota or rate limit; switch lanes, do not retry in a loop. `auth` (exit 7):
the key variable is missing or rejected; tell the user which one. `failed`, `cancelled`, `expired`
(exit 3): read the vendor page link in the state file, then shrink the brief or move it to a local lane.
