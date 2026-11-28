---
name: advisor
description: The inverse of the conductor setup. The session's own, cheaper model does one long task end to end and asks a stronger model, from any vendor, for short read-only advice at three moments only (before committing to a plan, when an error keeps coming back, before saying done). Use when the task does not split into checkable jobs and the session model is the cheaper one. Needs the orchestra skill's scripts.
---

# Advisor

You are the executor. You do the work, call the tools and talk to the user. The advisor is a stronger
model that only sees one short brief at a time, never calls tools, and never talks to the user.

## When to use it, and when not

- Use it for one long, multi-step task that does not split, when your own model is the cheaper one
  (Sonnet, Haiku, DeepSeek, a small GPT) and a stronger lane is ready (`mmo-run --list`).
- Not for short tasks: the advice costs more than it saves. Not for work that splits into checkable
  jobs: there the strong model should conduct and the cheaper ones build (`orchestra`).
- Inside Claude Code with a Claude advisor, the built-in `/advisor` is simpler. This skill is for
  crossing vendors, or for hosts that do not have it.
- The advisor must be stronger than your own model. For `done`, prefer another family than yours:
  it does not share your blind spots about your own change.

## The three moments

These are the only automatic consultations. The fourth is the user asking for one.

1. **plan**: before you commit to an approach. The task and your intended approach.
2. **stuck**: when the same error comes back after a real fix attempt. The task, what you tried, and
   the error output word for word.
3. **done**: before you tell the user it is finished. The task as asked and the diff.

```bash
../orchestra/scripts/mmo-advise --moment plan  --question q.md --lane codex:gpt-6-astra
../orchestra/scripts/mmo-advise --moment stuck --question q.md --evidence test.log -C <repo>
../orchestra/scripts/mmo-advise --moment done  --question q.md --diff main -C <repo>
```

The lane is `--lane`, else `MMO_ADVISOR`, else a ready strong lane from `mmo-roster` if it is installed
(the first one with no tools at all, if one is listed, else the first). Nothing else is guessed: with
none of these it stops and asks for `--lane`.

"The advisor uses no tools" is a hard guarantee only for a lane with no tools (`mmo-run --list` shows
READ-ONLY `notools`, for example `api:<endpoint>:<model>`); the result header says `tools=none`. Any other
lane (`sandbox`, `throwaway`) still has its tools: it runs read-only in an empty temp folder with nothing of
your project in it, and the header says `tools=read-only, empty folder`. `--strict-no-tools` (or
`MMO_ADVISE_STRICT=1`) refuses such a lane with exit 2.

## Reading the answer

The answer is a verdict line (`PROCEED`, `CHANGE: <one line>` or `STOP: <one line>`) and at most 12
lines of reasons, at most 1,500 characters in all (`--max-chars`; the full answer is kept next to `--out`
as `<name>.full.md`, or in `.mmo/advise-<moment>.full.md`). An answer without a verdict is rejected
(exit 11, an empty answer is exit 5); a failed lane passes its status and exit code through (see
orchestra section 6; 6 is the lane's own limit). Neither is advice. Decide on your own, or try another
strong lane once.

- Advice is a claim, not an order. `CHANGE` and `STOP` are reasons to look. Check what can be checked
  (run the test, read the file, try the experiment it names) before you act on it.
- If the check says the advisor is wrong, go on and say why in one line.
- Tell the user in one line when you consulted and what came back, for example:
  `Asked gpt-6-astra before starting (plan): CHANGE: back off between retries. Checked, adopted.`

## Ceilings

- Budget: 6 consultations and 60,000 characters of brief sent per session (`MMO_SESSION`, default
  today's date), counted in `.mmo/advise.json` behind a lock, so parallel calls cannot both pass. Over
  budget it refuses with exit 10 before the lane is called (a smaller `--diff` or less evidence fits
  again). A lane that never started gives both back. `mmo-advise status` shows what is used and left.
  Raise it on purpose (`--budget N`, `--budget-chars N`, `MMO_ADVISE_BUDGET`,
  `MMO_ADVISE_BUDGET_CHARS`; 0 turns the character budget off), not to get a second opinion on an
  answer you did not like.
- Evidence is capped at 12k characters (logs keep the tail, specs the head), the diff at 10k, each
  with a visible truncation note. Send the lines that matter, not the whole log.
- Never put secrets, tokens or personal data in the question or the evidence: the brief goes to
  another vendor. Text that looks like a key is refused before anything is sent.
- With `MMO_LOG` set, each consultation adds one line (`kind: "advise"`).
