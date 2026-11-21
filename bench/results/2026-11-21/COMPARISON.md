# 2026-11-21 vs 2026-11-11

Same tasks, same runner, same grading (`bench/run.sh`, `bench/grade.py`). One run per cell.
Claude tiers were not re-run this time. Raw answers and diffs are in this folder; scores in `results.tsv`.

| Lane | bugfix (hidden) | reasoning | bulk | wall time (s) b / r / k | vs 2026-11-11 |
|---|---|---|---|---|---|
| GPT gpt-6.1-sol | unavailable | unavailable | unavailable | : | was 6/6, 3/3, 60/60. Now `model_not_found` (see below) |
| GPT gpt-6-astra | unavailable | unavailable | unavailable | : | was 6/6, 3/3, 60/60. Now `model_not_found` |
| GPT gpt-5.6-terra (new, effort medium) | 6/6 | 3/3 | 60/60 | 63 / 17 / 21 | new id, not in the last run |
| GPT gpt-6-luna (effort low) | 6/6 | 0/3 | 58/60 | 55 / 9 / 12 | bugfix fixed (was: visible tests fail); reasoning worse (2/3 -> 0/3); bulk 56 -> 58 |
| GPT gpt-5.6-luna (new, effort low) | 6/6 | 3/3 | 59/60 | 57 / 13 / 17 | new id |
| Kimi k3.1-pro | 6/6 | 3/3 | 60/60 | 51 / 23 / 30 | same scores, roughly 1.5-2x slower |
| DeepSeek v4-pro | 6/6 | 3/3 | 60/60 | 95 / 18 / 30 | same scores, slower (bugfix 49 -> 95 s) |
| DeepSeek flash | 6/6 | 3/3 | 60/60 | 17 / 14 / 16 | same scores, still the fastest lane |

## What changed

- **The GPT ids changed under us.** On 2026-11-21 the ChatGPT account behind the Codex CLI rejects
  `gpt-6.1-sol` and `gpt-6-astra` with HTTP 400 `model_not_found` ("not supported when using Codex
  with a ChatGPT account"). `gpt-5.6-sol` is rejected the same way. The ids that answer on this plan
  today are `gpt-5.6-terra`, `gpt-6-luna` and `gpt-5.6-luna`, so the GPT rows ran on those. The skill
  docs still name sol and astra as defaults; on a plan like this one, the lane fails fast with a
  status, which is the intended behaviour, but the routing table needs a working fallback id.
- **Runner finding: one error, two statuses.** The same `model_not_found` error came back as
  `status=failed` on the bugfix and reasoning briefs and as `status=limit` on the bulk brief.
  `mmo-run` greps stderr for limit words (`429`, `402`, `quota` ...), and Codex echoes the brief on
  stderr; the bulk brief contains HTTP log lines with those numbers. A `limit` status sends the
  conductor to the fallback lane, which is the right move here anyway, but the label is wrong.
  The fix is to match limit words only in the CLI's own error lines, not in the echoed prompt.
- **gpt-6-luna is noisy on reasoning.** Three runs today: 1/3 and 0/3 on the stable CLI,
  3/3 on the pre-release build (last time 2/3). Its bugfix passed both stable-CLI runs today (6/6)
  where it broke the visible tests last time. Small tasks,
  one run per cell: read luna as "needs a check every time", not as better or worse.
- **Everything else held.** Kimi k3.1-pro and both DeepSeek lanes scored the same as on 2026-11-11.
  Wall times were higher across the board (shared provider load, time of day; not investigated).
- **A different Codex binary broke the write lane.** A first attempt with a newer pre-release
  Codex build (0.167 alpha) ran the read-only tasks fine but stalled in the write sandbox: the
  bugfix lanes took 555-776 s and reported that Python was not on PATH and file edits hung (terra
  still landed a correct fix; both luna ids did not). The table uses the stable CLI (0.163.0) for all
  GPT rows. If you run this on a pre-release Codex, check the write lane first.

## Not re-run

- Claude Opus / Sonnet / Haiku: skipped this time (see `bench/ab/` for a Claude-side experiment).
- Kimi k3.1-pro-highspeed: not in the default lanes; it was `limit` (not on this plan) last time.
