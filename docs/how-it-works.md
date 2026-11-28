# How it works

[Back to the README](../README.md)

The main agent is the conductor: it decides who plays which part, writes the brief, and reviews what comes back.
The skills give it a routing policy, and the scripts make the dangerous parts boring:
one runner for every provider, hard status codes, a worktree guard for anything that writes,
an offline preflight, and a blind council for decisions.

```mermaid
flowchart LR
    U([You]) --> C{{Conductor<br/>main agent}}
    C -- "hard work" --> O[Claude Opus]
    C -- "routine work" --> S[Claude Sonnet]
    C -- "bulk" --> H[Claude Haiku]
    C -- "brief" --> R[[mmo-run]]
    R --> G1[GPT sol<br/>execute]
    R --> G2[GPT astra<br/>2nd opinion]
    R --> G3[GPT luna<br/>bulk]
    R --> K[Kimi<br/>cheap execution]
    R --> D[DeepSeek<br/>3rd opinion / bulk]
    C -- "decision" --> CO[[mmo-council<br/>3 lanes, blind]]
    CO --> G2 & K & D
    G1 & G2 & G3 & K & D --> V{status ok?<br/>check passes?<br/>diff clean?}
    O & S & H --> V
    V -- yes --> M[merge / answer]
    V -- no --> F[fallback lane<br/>or tell the user]
```

## The skills

| Skill | What it does |
|---|---|
| [`orchestra`](../skills/orchestra/SKILL.md) | The policy: when not to delegate, who gets which job, brief rules, gates, fallbacks. Holds the scripts and brief templates. |
| [`council`](../skills/council/SKILL.md) | Same question to three model families, read-only, answers shuffled to letters before you judge them. |
| [`advisor`](../skills/advisor/SKILL.md) | The other way round: a cheaper session model does one long task and asks a stronger lane for short advice. |
| [`chatgpt-lane`](../skills/chatgpt-lane/SKILL.md) | GPT through the Codex CLI: gpt-6.1-sol, gpt-6-astra, gpt-6-luna. |
| [`kimi-lane`](../skills/kimi-lane/SKILL.md) | Kimi through the Kimi Code CLI. |
| [`deepseek-lane`](../skills/deepseek-lane/SKILL.md) | DeepSeek v4-pro and flash through the Kimi Code CLI. |
| [`cloud-lane`](../skills/cloud-lane/SKILL.md) | Experimental: Devin, Cursor cloud agents and Copilot agent tasks through `mmo-cloud`. |
| [`otomode`](../skills/otomode/SKILL.md) | Unattended runs while you are away. See [otomode.md](otomode.md). |

Claude tiers run as the host agent's own sub-agents (`Agent` tool with an explicit model), so they need no script.
Every other lane is one adapter file; the full list is in [lanes](lanes/README.md).

## Routing

Pick the cheapest lane that will pass the check. Move up only when a lane fails the check, not on a hunch.
This is the table from [`skills/orchestra/SKILL.md`](../skills/orchestra/SKILL.md):

| Job | Tier | Brief style |
|---|---|---|
| Hard design, tricky bug, unfamiliar code | Strong: Claude Opus sub-agent; a top GPT or Gemini lane at high effort | Goal + constraints, let it plan |
| Routine feature, clear bug, refactor with tests | Middle: Claude Sonnet sub-agent, gpt-6.1-sol, or a comparable agent CLI | Steps, files, done-check |
| Easy, well-specified, testable work | Cheap: DeepSeek, Kimi, Qwen, GLM, a small GPT | Numbered steps, exact files, exact check |
| Bulk mechanical work (labeling, renames, cleanup) | Bulk: Claude Haiku, gpt-6-luna, deepseek-flash, a local model | Rules + format + examples |
| Second opinion, "what are we missing" | A strong model from another family than the conductor's, read-only | The question + the evidence, ask for disagreement |
| A decision with no single right answer | Council (3 families, blind) | Same question to all |
| Long self-contained work while local lanes are busy | Cloud agent, only on pushed code | A brief that needs nothing from this machine |

The table names tiers, not one fixed model, because what is ready differs per machine: `mmo-run --list`
shows the lanes that are. A task starts at the cheapest tier that fits and moves one tier up after it
fails its check twice. With `MMO_LOG` set, `mmo-score` shows each lane's first-try pass rate on your own
work, which is the number to route by.

Not everything should be delegated. The conductor does the job itself when it takes fewer steps than the brief,
needs conversation context that does not fit on a page, touches secrets or anything irreversible,
or the user is waiting on a quick answer.

### The roster

`mmo-run --list` says a CLI is installed, not that it answers. `mmo-roster probe` sends one tiny read-only brief
per installed lane and model, four at a time, once each, and writes `.mmo/roster.json`: which lanes are READY, the
tier each one suits (strong, middle, cheap, bulk, or opinion for lanes without tools), and for the rest the reason
and the fix. `mmo-roster ready --tier cheap` lists a tier best first (external lanes before Claude sub-agents, then
the measured first-try pass rate once a lane has five checked tasks), `mmo-roster lineup` prints the short block
the conductor shows the user before handing out work, and `show` exits 3 when the roster is older than 12 hours.

### Model ids

The skill files name the default model ids (gpt-6.1-sol, gpt-6-astra and gpt-6-luna in
[`chatgpt-lane`](../skills/chatgpt-lane/SKILL.md)). On some ChatGPT plans the Codex CLI now serves different
model ids and rejects others. On the plan used for the [2026-11-21 benchmark](benchmark.md), `gpt-6.1-sol`,
`gpt-6-astra` and `gpt-5.6-sol` came back as HTTP 400 `model_not_found`, while `gpt-5.6-terra`, `gpt-6-luna`
and `gpt-5.6-luna` answered.

Smoke-test the ids before you route real work to a lane. `mmo-preflight` is offline and only tells you which
CLIs are installed; then send a one-line brief through `mmo-run` with each `-m` you plan to use. A rejected id
shows up as a non-`ok` status, not as a silent answer.

## The runner

```bash
mmo-run <lane> --brief FILE --out FILE
        [-m MODEL] [-e EFFORT] [--mode ro|rw] [-C DIR] [-t SECONDS] [--idle SECONDS]
        [--loop N] [--max-turns N] [--base REF] [--allow-main]
mmo-run --list
```

Every lane, whatever the vendor, ends the same way: an output file whose first line is

```
<!-- mmo provider=kimi model=kimi-code/k3.1-pro mode=rw status=ok exit=0 seconds=36 base=1a2b3c4d5 changed=2 -->
```

`base` is the commit the lane started from, `changed` the number of files it touched, and `committed=yes`
appears when a lane made a commit it was told not to make.

Examples:

```bash
scripts/mmo-preflight                       # offline: which lanes are installed
scripts/mmo-run codex   -m gpt-6.1-sol -e high --mode rw -C ../wt-auth --brief brief.md --out out/auth.md
scripts/mmo-run deepseek -m deepseek/deepseek-v4-pro --mode ro --brief q.md --out out/ds.md
```

### Status codes

| Exit | Status | Meaning |
|---|---|---|
| 0 | ok | An answer is in the file. Still check it. |
| 2 | usage | Wrong arguments to `mmo-run`. |
| 3 | failed | The CLI failed; the last stderr lines are in the file. |
| 4 | timeout, stalled, looping | Killed after `-t` seconds, after printing nothing for `--idle` seconds, or (`looping`) after the same tool call or error line came N times in a row with `--loop N`. Only lanes that stream JSON lines are covered; plain-text lanes are not. |
| 5 | empty | The CLI exited 0 but gave no final answer. |
| 6 | limit | Quota, balance, rate limit or plan. Use the fallback lane. When the message says when it comes back, the header has `retry_after=<UTC time>` and `mmo-roster` skips the lane until then. With `--max-cost`, a claude lane that stops at the ceiling is also `limit`, with `ceiling=cost` in the header. |
| 7 | auth | The CLI needs a fresh sign-in. Tell the user. |
| 8 | model | The model id was rejected (`model_not_found`). Switch to an id that answers; waiting will not help. |
| 9 | base | `--base REF` was given and the worktree does not contain it. The lane was not started. |

## Checking a lane

```bash
mmo-check -C ../wt-auth --cmd "go test ./internal/auth/..." \
          --allow "internal/auth/*" --red --out out/auth.check.md
```

`mmo-check` is the conductor's own run of the task's check, in the lane's worktree. Its report starts with

```
<!-- mmo-check status=pass exit=0 seconds=12 changed=3 outside=0 protected=0 tests_changed=1 deps_changed=0 red_exit=1 -->
```

and lists the files touched outside `--allow`, existing tests that were changed or deleted, and changed
dependency manifests. `--protect GLOB` makes any touch of those files a failed check. With `--red` the check
also runs on the base code plus only the new or changed tests, and must fail there: a check that passes
without the change says nothing about the change. Exit codes: 0 pass, 1 fail, 3 policy, 4 timeout, 5 not-red.
The red run has no installed dependencies unless the command installs them, so read its log before trusting it.

## Safety model

- **Writes only in a worktree.** `--mode rw` refuses to run unless `-C` is a linked git worktree. A lane cannot edit your main checkout by accident.
- **The right base.** `--base REF` refuses a worktree that does not contain your branch, so a lane cannot quietly work on stale code.
- **Read-only means read-only.** A CLI that can be held read-only by its own flags is (Codex's sandbox, a read-tools-only list). One that cannot (Kimi Code, OpenCode, Amp and others edit in print mode even when asked not to) runs read-only jobs in a throwaway detached worktree; anything it writes is thrown away and flagged `ro_violation=yes`.
- **A failed lane is not an answer.** No falling through to "the model said nothing, so it's fine". The council records a failed lane as *not an answer, not a vote*.
- **Always a timeout, never a prompt.** Every CLI runs under `timeout -k 10` with stdin closed or fed only the brief, so nothing hangs on a question. The limits (`-t`, `--idle`, `--max-turns`) are set by the caller; a lane cannot raise them.
- **Briefs leave your machine.** The skills say it plainly: never put secrets or personal data in a brief.

## Gates before an answer is used

1. The status header says `ok`. Anything else is not an answer.
2. The conductor ran the check itself with `mmo-check`. A lane saying DONE proves nothing.
3. For writing lanes: the whole diff is read. Edits outside the allowed files, deleted or weakened tests, new dependencies and silenced warnings are rejected.
4. For opinions: arguments are weighed, not votes. Two models agreeing is a hint, not proof.
5. Lanes are merged one at a time with the quick check after each; the full suite runs after every few merges, not only at the end.

## Council

For decisions where reasonable models disagree, the [`council`](../skills/council/SKILL.md) skill sends the
same question to three lanes from different families (GPT, Kimi and DeepSeek by default), read-only and in parallel.

```bash
../orchestra/scripts/mmo-council --question q.md --outdir council/ -C <repo>
```

The answers come back as `answer-A.md`, `answer-B.md`, ... with the letters shuffled; you read them before you
open `key.txt`, so you judge the reasoning and not the brand. A lane marked FAILED in `status.txt` is not an
answer and not a vote. If fewer than two lanes answered, it is not called a council.

## Advisor

The [`advisor`](../skills/advisor/SKILL.md) skill turns the setup around for one long task that does not split:
the session's own, cheaper model does the work and asks a stronger lane, from any vendor, for short advice.

```bash
../orchestra/scripts/mmo-advise --moment done --question q.md --diff main -C <repo> --lane codex:gpt-6-astra
```

There are three moments: `plan` (before committing to an approach), `stuck` (the same error again) and `done`
(before saying so). Each sends one read-only brief through `mmo-run`, from an empty folder, and gets back a verdict
line (`PROCEED`, `CHANGE: ...` or `STOP: ...`) and at most 12 lines and 1,500 characters of reasons (the full answer
is saved next to `--out`). An answer with no verdict (exit 11) and a failed lane are both reported as no advice.

No tools is a hard guarantee only for a lane with no tools at all (`notools` in `mmo-run --list`, such as
`api:<endpoint>:<model>`; the header says `tools=none`). Any other lane keeps its tools and runs read-only in an
empty folder with nothing of your project in it (`tools=read-only, empty folder`); `--strict-no-tools` refuses
those. A budget of 6 consultations and 60,000 characters sent per session (exit 10 when used up, kept under a
lock so parallel calls cannot both pass; `mmo-advise status` shows it), size caps on the evidence and the diff,
and a refusal of key-like text keep it the cheap part of the run.
