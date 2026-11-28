# 2026-11-28: OpenCode, Grok, DeepSeek, Antigravity, Cursor and API lanes

Same tasks, same runner, same grading (`bench/run.sh`, `bench/grade.py`). One run per cell.
Scores are fractions (bugfix = hidden tests passed of 6, reasoning = answers right of 3, bulk = labels right of 60).
Raw answers and diffs are in this folder; scores in `results.tsv`. The Antigravity, Cursor and API lanes were run
in separate sessions outside this checkout and added afterwards; they have no `.rc` files, and only the lanes
that ran through `bench/run.sh` with a git worktree have `.diff` files.

| Lane | bugfix | reasoning | bulk | seconds b / r / k | total s | tasks | note |
|---|---|---|---|---|---|---|---|
| api:ablit/abliterated-model-large-flash | - | 1.00 | 1.00 | - / 2 / 5 | 7 | 2 |  |
| api:openrouter/particle-ai/particle-1:free | - | 1.00 | 1.00 | - / 2 / 6 | 8 | 2 |  |
| api:ablit/abliterated-model-large-v2 | - | 1.00 | 1.00 | - / 5 / 11 | 16 | 2 |  |
| api:openrouter/baidu/ernie-5.5-flash-preview:free | - | 1.00 | 1.00 | - / 5 / 12 | 17 | 2 |  |
| api:ablit/abliterated-model | - | 1.00 | 1.00 | - / 9 / 21 | 30 | 2 |  |
| deepseek/deepseek-flash | 1.00 | 1.00 | 1.00 | 15 / 6 / 10 | 31 | 3 |  |
| opencode/deepseek-v4.1-flash-free | 1.00 | 1.00 | 1.00 | 22 / 7 / 10 | 39 | 3 |  |
| opencode/beam-free | 1.00 | 1.00 | 1.00 | 21 / 8 / 15 | 44 | 3 |  |
| agy/claude-opus-5-5-high | 1.00 | 1.00 | 1.00 | 25 / 8 / 12 | 45 | 3 |  |
| agy/claude-sonnet-5-5-high | 1.00 | 1.00 | 1.00 | 30 / 8 / 10 | 48 | 3 |  |
| api:openrouter/nvidia/nemotron-3.5-super-vl:free | - | 1.00 | 1.00 | - / 12 / 37 | 49 | 2 |  |
| agy/gemini-4-hydrogen-high | 1.00 | 1.00 | 1.00 | 32 / 16 / 20 | 68 | 3 |  |
| agy/gpt-oss-120b-medium | 1.00 | 1.00 | 1.00 | 41 / 10 / 18 | 69 | 3 |  |
| opencode/big-pickle | 1.00 | 1.00 | 1.00 | 34 / 10 / 26 | 70 | 3 |  |
| grok-4.6 | 1.00 | 1.00 | 1.00 | 33 / 15 / 23 | 71 | 3 |  |
| grok-4.7-build-fast | 1.00 | 1.00 | 1.00 | 37 / 17 / 28 | 82 | 3 |  |
| opencode/hy4-flash-free | 1.00 | 1.00 | 1.00 | 55 / 12 / 16 | 83 | 3 |  |
| grok-4.5 | 1.00 | 1.00 | 1.00 | 50 / 14 / 22 | 86 | 3 |  |
| cursor/composer-2.5 | 1.00 | 1.00 | 1.00 | 56 / 19 / 12 | 87 | 3 |  |
| opencode/nemotron-3.5-super-vl-free | 1.00 | 1.00 | 1.00 | 41 / 13 / 35 | 89 | 3 |  |
| opencode/iceman-free | 1.00 | 1.00 | 1.00 | 41 / 24 / 30 | 95 | 3 |  |
| deepseek/deepseek-v4-pro | 1.00 | 1.00 | 1.00 | 89 / 12 / 27 | 128 | 3 |  |
| agy/gemini-4-argon-high | 1.00 | 1.00 | 1.00 | 63 / 27 / 41 | 131 | 3 |  |
| grok-4.7 | 1.00 | 1.00 | 1.00 | 50 / 24 / 58 | 132 | 3 |  |
| agy/gemini-pro-orchestrator | 1.00 | 1.00 | 1.00 | 67 / 32 / 36 | 135 | 3 |  |
| agy/gemini-4-neon-high | 1.00 | 1.00 | 1.00 | 74 / 28 / 35 | 137 | 3 |  |
| api:openrouter/nvidia/nemotron-3-ultra-550b-a55b:free | - | 1.00 | 1.00 | - / 26 / 119 | 145 | 2 |  |
| api:openrouter/recursive/flint-v1.0:free | - | 1.00 | 1.00 | - / 23 / 133 | 156 | 2 |  |
| api:openrouter/nvidia/nemotron-3.5-lightning:free | - | 1.00 | 1.00 | - / 10 / 147 | 157 | 2 |  |
| opencode/mimo-v2.6-flash-free | 1.00 | 1.00 | 1.00 | 80 / 32 / 65 | 177 | 3 |  |
| opencode/seaglass-alpha-free | 1.00 | 1.00 | 1.00 | 94 / 18 / 81 | 193 | 3 |  |
| cursor/auto | 1.00 | 1.00 | 1.00 | 156 / 23 / 23 | 202 | 3 | timing approximate (overlapping run) |
| opencode/flint-40b-free | 1.00 | 1.00 | 1.00 | 46 / 53 / 156 | 255 | 3 |  |
| agy/gemini-4-carbon-high | 1.00 | 1.00 | 1.00 | 226 / 71 / 133 | 430 | 3 |  |
| opencode/nemotron-3.5-lightning-free | 0.83 | 1.00 | 1.00 | 63 / 21 / 34 | 118 | 3 | hidden tests 5/6 |
| api:openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free | - | 0.67 | 1.00 | - / 17 / 41 | 58 | 2 | reasoning 2/3 (q1 answered 23, gold 22) |
| agy/gemini-3.8-flash-high | 1.00 | 1.00 | 0.00 | 223 / 39 / 30 | 292 | 3 | bulk: empty answer, a tool permission was auto-denied in headless mode |
| api:openrouter/liquid/lfm-3-1.7b:free | - | 1.00 | 0.00 | - / 17 / 31 | 48 | 2 | bulk: empty answer |
| api:openrouter/google/gemma-4-26b-a4b-it:free | - | 0.00 | 0.00 | - / 1 / 0 | 1 | 2 | rate limit (HTTP 429) |
| api:openrouter/google/gemma-4-31b-it:free | - | 0.00 | 0.00 | - / 0 / 1 | 1 | 2 | rate limit (HTTP 429) |
| opencode/tidepool-alpha-free | 0.00 | 0.00 | 0.00 | 4 / 4 / 4 | 12 | 3 | model unavailable (provider error) |

Sorted by mean score over the tasks the lane ran, then total seconds. Wall time columns: b = bugfix, r = reasoning,
k = bulk. The `tasks` column is 3 for lanes with tools and 2 for the API lanes (`api:ablit/...`, `api:openrouter/...`),
which have no tools and so skipped the bugfix task: their total covers reasoning and bulk only and must not be
compared with the total of a three-task lane. Lane groups: 11 free models through the `opencode` lane, 4 through the
`grok` lane, 2 through the `deepseek` lane, 9 through the `agy` (Antigravity) lane, 2 through the `cursor` lane
(`composer-2.5` and the default `auto` model), 3 abliteration.ai models and 10 free OpenRouter models through the
`api` lane. 41 lanes in all.

## Did not run (Cursor)

These models were requested through the Cursor lane but produced no answer, so they have no rows in `results.tsv`:

- muse-wonder, muse-spark, kimi-k3, kimi-k2.7-code, glm-5.2: Cursor refused them with "not included in your weekly
  usage" (plan limit).
- glm-5.3 and glm-5.3-flash: not in the Cursor CLI's model list.

## What the numbers show

- The task set is easy. Most lanes score full marks on all the tasks they ran and differ mainly on speed; the
  total time among full-score three-task lanes runs from 31 s (deepseek/deepseek-flash) to 255 s
  (opencode/flint-40b-free).
- Lanes that lost points: opencode/nemotron-3.5-lightning-free passed 5 of 6 hidden bugfix tests; the nvidia
  nemotron-3-nano-omni (OpenRouter) got 2 of 3 reasoning answers; agy/gemini-3.8-flash-high returned an empty
  bulk answer because a tool permission was auto-denied in headless mode (kept as a 0.00 row). With one run per
  cell any of these could be noise as easily as a weakness.
- Lanes that returned nothing for provider reasons: opencode/tidepool-alpha-free failed all three tasks with
  `Upstream request failed: Model is unavailable` (also on a rerun); the two OpenRouter gemma models failed on a
  rate limit (HTTP 429); liquid/lfm-3-1.7b gave a correct reasoning answer but an empty bulk answer. These are
  provider-side outcomes, not statements about the models.
- The API lanes ran two of three tasks (no tools, no bugfix), so their scores are over two tasks.
- Cursor's plan refused five models and the CLI does not list two others (see "Did not run"). The cursor/auto
  timings are approximate: two runs overlapped, and the first complete one is kept.
- These numbers do not rank the models on hard work. Free models are rate limited, slowed or withdrawn without
  notice and come and go, so times and availability will differ on another day. One run per lane.
