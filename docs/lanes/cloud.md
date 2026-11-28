# Cloud agents (mmo-cloud)

Status: **experimental**. Everything below was written from vendor documentation read on 2026-11-28.
None of it has been run against a real account. The offline tests (`skills/orchestra/scripts/test-mmo-cloud.sh`)
prove that mmo-cloud sends what the docs describe and reads what the docs describe; they cannot prove
the docs are complete. Where a response field was not pinned down, mmo-cloud reads it defensively and
reports it, and a vendor state it does not know becomes `failed` (`note=unknown_vendor_state`), never success.

All three supported agents need the repository on GitHub and the branch pushed before `start`.
None of them works on a local-only repository.

## Common contract

| Command | Does |
|---|---|
| `list` | Offline. Which agents have their key variables set, whether they take a cap and a cancel. |
| `start <agent> --brief F --repo OWNER/NAME [--base B] [--cap N] --state S` | Creates the remote run, writes the state file, prints `<!-- mmo-cloud agent=... status=started id=... cap=... -->`. |
| `status --state S` | One poll. Header carries the normalized status and the raw vendor state (`vendor=`). |
| `wait --state S -t SECONDS [--every SECONDS]` | Polls (default every 60 s) until a terminal state, or exit 4 at the timeout. `-t` is required. |
| `result --state S` | Prints `pr=` and `branch=` lines. Exit 5 when there is neither. Never merges or checks out. |
| `cancel --state S` | Only where the vendor documents a cancel; otherwise exit 2. |

Normalized states: `queued`, `running`, `waiting` (the agent asks a question; a stop for an unattended
conductor), `done`, `failed`, `limit`, `auth`, `cancelled`, `expired`.

Exit codes: 0 ok (status also returns 0 for queued/running), 2 usage, 3 failed/cancelled/expired,
4 timeout, 5 no PR or branch, 6 limit, 7 auth or missing key, 10 waiting.

HTTP errors: 401 and 403 are `auth`; 402, 429 and Cursor's `plan_required` / `rate_limit_exceeded` are `limit`;
anything else is `failed`. A network error is `failed`.

The state file holds agent, session id, run id (Cursor), vendor URL, repo, base, start time, cap and the
last status. Keys are read from the environment on every call and never written, printed or logged; any
key text a vendor echoes back in an error body is replaced with `***`.

The brief is sent as the prompt with one line appended: the repository, the base branch, and "put your
work on a new branch and open a pull request; do not merge it".

## Devin (Cognition), API v3

- Needs: `DEVIN_API_KEY` (service-user credential, `cog_` prefix) and `DEVIN_ORG_ID` (`org-...`), the
  variable names the Devin docs use. The repo must be connected to the Devin organization. Plan: any
  plan with API access; billing is ACUs (enterprise) or included quota plus credits (self-serve).
- start: `POST /v3/organizations/{org}/sessions` with `prompt`, `max_acu_limit` and `title`. The session id
  is read from `session_id`, `devin_id` or `id` (the v3 create response shape was not captured; v1 returns `session_id`).
- status: `GET /v3/organizations/{org}/sessions/{id}`. `status_detail` wins over `status`:

  | Devin | mmo-cloud |
  |---|---|
  | status `new`, `claimed` | queued |
  | status `running`, `resuming`; detail `working` | running |
  | detail `waiting_for_user`, `waiting_for_approval`; status `suspended` with no other detail | waiting |
  | detail `finished`; status `exit` | done |
  | detail `error`; status `error` | failed |
  | detail `usage_limit_exceeded`, `out_of_credits`, `out_of_quota`, `no_quota_allocation`, `payment_declined`, `org_usage_limit_exceeded`, `user_usage_limit_exceeded`, `total_session_limit_exceeded`, `contract_expired` | limit |
  | detail `user_request` | cancelled |
  | detail `inactivity` | expired |

- result: `pull_requests[].pr_url`. Devin does not document a branch name field, so no `branch=` line.
- cap: `--cap N` is required and sent as `max_acu_limit`. No wall-time cap is documented.
- cancel: `DELETE /v3/organizations/{org}/sessions/{id}` ("Terminate Session").
- Unverified: the `repos` field is a list whose element shape was not captured, so mmo-cloud does not
  send it and names the repo in the prompt instead. What Devin reports when the ACU cap is reached is
  not documented (probably one of the limit details). Base URL override: `MMO_DEVIN_BASE`.

## Cursor cloud agents, API v1 (public beta)

- Needs: `CURSOR_API_KEY` (a user or service-account key; the variable name is ours, the docs do not name
  one), sent as Bearer. Cloud agents need a paid plan (Premium and up per the pricing page). GitHub repo.
- start: `POST /v1/agents` with `prompt.text`, `repos[0].url` (`https://github.com/OWNER/NAME`),
  `repos[0].startingRef` (= `--base`) and `autoCreatePR: true`. Agent id from `agent.id`, run id from
  `run.id` or `agent.latestRunId` (the exact create response shape is "agent + first run").
- status: `GET /v1/agents/{id}/runs/{runId}`:

  | Cursor run | mmo-cloud |
  |---|---|
  | `CREATING` | queued |
  | `RUNNING`, `WAITING_FOR_BACKGROUND_WORK` | running |
  | `FINISHED` | done |
  | `ERROR` | failed |
  | `CANCELLED` | cancelled |
  | `EXPIRED` | expired |

- result: `git.branches[]` = `{repoUrl, branch, prUrl}`; read from the run, else from `GET /v1/agents/{id}`
  (the docs do not say which object carries it).
- cap: none documented (no cost, no time cap). `start` says so and refuses `--cap`.
- cancel: `POST /v1/agents/{id}/runs/{runId}/cancel`.
- Unverified: no documented "waiting for a question" run state, so `waiting` never comes from Cursor.
  Base URL override: `MMO_CURSOR_BASE`.

## GitHub Copilot cloud agent, agent tasks REST (public preview)

- Needs: `COPILOT_AGENT_TOKEN` (our variable name): a fine-grained PAT or GitHub App user-to-server token
  with the "Agent tasks" permission. Installation tokens are not supported, which is why mmo-cloud does not
  fall back to `GITHUB_TOKEN`. A paid Copilot plan; the REST page says Business/Enterprise, a later changelog
  says Pro/Pro+ too (unclear which is current). You need write access; rulesets can block PR creation.
- start: `POST /agents/repos/{owner}/{repo}/tasks` with `prompt`, `create_pull_request: true`, `base_ref`,
  header `X-GitHub-Api-Version: 2026-03-10`. Task id from `id` (not pinned down in the research).
- status: `GET /agents/repos/{owner}/{repo}/tasks/{id}`:

  | Copilot state | mmo-cloud |
  |---|---|
  | `queued` | queued |
  | `in_progress` | running |
  | `completed`; `idle` with a pull or branch artifact | done |
  | `waiting_for_user`; `idle` with no artifact | waiting |
  | `failed` | failed |
  | `timed_out` | expired |
  | `cancelled` | cancelled |

- result: `artifacts[]`: type `branch` gives `branch=<head_ref>`; type `pull` gives `data.id`, printed as
  `pr=OWNER/NAME pull id N` because the docs do not say whether that id is the PR number. Look it up with
  `gh pr list --head <branch>` before trusting it.
- cap: no cost cap. The vendor stops a session at 59 minutes; `start` says so and refuses `--cap`.
- cancel: none documented; `cancel` exits 2.
- Not wrapped: `gh agent-task create/list/view` exists (gh 2.80+), but its output format is not documented,
  so a script cannot read a task id or state from it. The REST API has documented states, so mmo-cloud uses it.
  Base URL override: `MMO_COPILOT_BASE`.

## Left out, and why

- **Google Jules** (REST alpha): the session state values and any cancel endpoint were not documented on
  the pages read, so `status` could not map honestly.
- **OpenAI Codex cloud** (`codex cloud exec/status/diff/apply`): the subcommands come from source, not docs,
  and neither the output of `exec` (the task id) nor the values `status` prints are documented. It returns
  a diff to apply locally, not a branch or PR. No cancel or cap documented.
- **Claude Code cloud sessions**: no documented way for a script to poll status or read the PR URL.
- **Factory droid**: runs locally; its cloud product was not researched.
