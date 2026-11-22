<p align="center">
  <img src="docs/assets/logo.png" width="160" height="160" alt="multi-model-orchestra logo: a cartoon conductor with a red bow tie raising a baton">
</p>

<h1 align="center">multi-model-orchestra</h1>

<p align="center"><sub>English · <a href="docs/README_TR.md">Türkçe</a> · <a href="docs/README_UK.md">Українська</a> · <a href="docs/README_ZH.md">简体中文</a> · <a href="docs/README_ZH-TW.md">繁體中文</a> · <a href="docs/README_DE.md">Deutsch</a> · <a href="docs/README_FR.md">Français</a> · <a href="docs/README_ES.md">Español</a> · <a href="docs/README_JA.md">日本語</a> · <a href="docs/README_KO.md">한국어</a> · <a href="docs/README_AZ.md">Azərbaycanca</a> · <a href="docs/README_UZ.md">Oʻzbekcha</a> · <a href="docs/README_KK.md">Қазақша</a> · <a href="docs/README_KY.md">Кыргызча</a> · <a href="docs/README_TK.md">Türkmençe</a> · <a href="docs/README_CRH.md">Qırımtatarca</a> · <a href="docs/README_UG.md">ئۇيغۇرچە</a> · <a href="docs/README_PT.md">Português</a> · <a href="docs/README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Let one expensive model conduct, cheaper models play, and check every answer before it's used.</b><br>
Skills for Claude Code (or anything that reads <code>SKILL.md</code> files) that hand work to Claude Opus, Sonnet and Haiku, OpenAI GPT, Kimi and DeepSeek.<br>
The main agent plans, writes the briefs and reviews; the other models do the work, and nothing they return is trusted until it passes a check.</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="MIT license"></a>
  <img src="https://img.shields.io/badge/models-Claude%20·%20GPT%20·%20Kimi%20·%20DeepSeek-2563EB" alt="Claude, GPT, Kimi and DeepSeek lanes">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="Runs on bash, Git Bash on Windows">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="GitHub stars"></a>
</p>

<p align="center"><b><a href="#quick-start">Install</a></b> · <a href="docs/otomode.md">otomode</a> · <a href="docs/how-it-works.md#council">Council</a> · <a href="docs/benchmark.md">Benchmark</a> · <a href="docs/faq.md">FAQ</a></p>

<p align="center">
  <img src="assets/orchestra-comic.png" alt="A conductor hands a bug to a model, asks for the diff, and runs a blind council" width="860">
  <br>
  <sub>The conductor hands out the parts, asks for the diff, and calls a blind council when the answer is a judgment call.</sub>
</p>

<table>
  <tr>
    <td width="25%" valign="top">
      <b>Route</b><br>
      Each job goes to the cheapest tier that can pass its check, by difficulty. A lane moves up only after it fails the check, not on a hunch.
    </td>
    <td width="25%" valign="top">
      <b>Brief</b><br>
      Each tier gets the brief it works best with: goal and constraints for Opus, numbered steps and exact files for the cheaper lanes. A lane sees only the brief, so it is written for a stranger.
    </td>
    <td width="25%" valign="top">
      <b>Run</b><br>
      <code>mmo-run</code> is the one runner for every provider, with hard status codes and a timeout on every call. Writing lanes run only in a git worktree, never in your main checkout.
    </td>
    <td width="25%" valign="top">
      <b>Check</b><br>
      The conductor runs the check itself and reads the whole diff. A lane's "done" is a claim, not a result.
    </td>
  </tr>
</table>

## Real numbers

| What | Result | Details |
|---|---|---|
| <!-- AB-RESULTS --> A/B: orchestra skill vs. plain "use subagents" (`claude-fable-5-2`, 2 runs per arm) | Same quality: all four runs 36/36 hidden tests, visible tests intact (the task set is too easy to separate quality) | [benchmark.md](docs/benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B cost per run | Skill $1.88 vs $3.21 mean, about 40% less, ranges do not overlap. The saving comes from sub-agents running on Sonnet instead of inheriting Fable. No speed gain (3.2 vs 3.5 min) | [RESULTS.md](bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B limits | A one-line "use Sonnet subagents" prompt was not tested and may capture most of the saving. `total_cost_usd` is a list-price proxy, not plan usage | [faq.md](docs/faq.md#why-not-just-tell-the-model-to-use-subagents) |
| Lane benchmark, 2026-11-21 (bugfix with hidden tests, exact-answer reasoning, 60-line bulk labeling) | Kimi k3.1-pro, DeepSeek v4-pro, DeepSeek flash and gpt-5.6-terra: 6/6, 3/3, 60/60. gpt-6-luna: 6/6, 0/3, 58/60. gpt-6.1-sol and gpt-6-astra: ~6/6, ~3/3, ~60/60 (estimated: not served on that plan, scores from the 2026-11-11 run) | [benchmark.md](docs/benchmark.md) |
| otomode, one 5-hour unattended run | 13 tasks, one commit each; weekly limit went from 25% to 31%; 6 prompts denied and logged. One run, not a benchmark | [otomode.md](docs/otomode.md#one-real-run) |

> [!WARNING]
> Briefs leave your machine: every lane sends its brief to that model's vendor. Never put secrets, tokens or
> personal data in a brief. otomode's hook denies prompts and refuses delete, deploy, push and send commands,
> but it matches patterns: it is a guard rail, not a sandbox.

## Quick start

Paste this into your agent and let it install the skills:

```text
Install multi-model-orchestra: clone https://github.com/yatuk/multi-model-orchestra,
run ./install.sh --link in it, then run ~/.claude/skills/orchestra/scripts/mmo-preflight
and tell me which lanes are ready.
```

Or yourself. Needs bash, git, `timeout` and Python 3; on Windows, use Git Bash.

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link          # into ~/.claude/skills; --dir PATH for a project
~/.claude/skills/orchestra/scripts/mmo-preflight
```

`mmo-preflight` never calls a model. It tells you which lanes exist on this machine, so the conductor routes around the missing ones.
For otomode, run `python ~/.claude/skills/otomode/scripts/otomode.py install` once to register its hook.

Then ask, for example:

- "Fix the failing tests in `internal/auth`. Follow the orchestra skill."
- "Get a second opinion from GPT on this migration plan before I merge it."
- "Ask the council: should we split this service or keep one process?"
- "otomode 6h: these four tasks, each checked with `go test ./...`."

## Works with

| Tool | Used for | Needs |
|---|---|---|
| Claude Code | The skills, and the Claude Opus / Sonnet / Haiku tiers as sub-agents | Skills installed in `~/.claude/skills` (or a project's `.claude/skills`); nothing else |
| Codex CLI | GPT lanes | `codex` on PATH, signed in with ChatGPT |
| Kimi Code CLI | Kimi and DeepSeek lanes | `kimi` on PATH, signed in; for DeepSeek, a `deepseek/*` model in Kimi Code's `config.toml` |

GPT model ids: on some ChatGPT plans the Codex CLI now serves different ids (for example gpt-5.6-terra or gpt-6-luna)
and rejects others. The skill files name the defaults; smoke-test the ids your plan accepts before routing work there
(`mmo-preflight` to see the CLIs, then a one-line `mmo-run` brief per id). See [Model ids](docs/how-it-works.md#model-ids).

## First PR in 10 minutes

No setup needed for most of these:

- **Read the README in your language** and fix what sounds machine made. All 19 translations were made by a model ([Crimean Tatar](https://github.com/yatuk/multi-model-orchestra/issues/1), [Uyghur](https://github.com/yatuk/multi-model-orchestra/issues/2), [Turkmen](https://github.com/yatuk/multi-model-orchestra/issues/3), [Kazakh](https://github.com/yatuk/multi-model-orchestra/issues/4), [the rest](https://github.com/yatuk/multi-model-orchestra/issues/5)).
- **Paste an error line** a CLI gave you (rate limit, expired login, unknown model) so the runner can tell it apart ([#10](https://github.com/yatuk/multi-model-orchestra/issues/10)).
- **Run the tests on macOS or Linux** and say what broke ([#8](https://github.com/yatuk/multi-model-orchestra/issues/8)).
- **Add a lane** for the CLI you use ([Gemini CLI](https://github.com/yatuk/multi-model-orchestra/issues/6), [Aider](https://github.com/yatuk/multi-model-orchestra/issues/7)), or [vote for the next one](https://github.com/yatuk/multi-model-orchestra/discussions/12).

All of them: [good first issues](https://github.com/yatuk/multi-model-orchestra/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22). How you route your own work is welcome in [Show your routing setup](https://github.com/yatuk/multi-model-orchestra/discussions/11). See [CONTRIBUTING](CONTRIBUTING.md).

## More

- [How it works](docs/how-it-works.md): routing table, runner, status codes, safety model, council.
- [otomode](docs/otomode.md): unattended runs while you are away.
- [Benchmark](docs/benchmark.md): lane benchmark and the A/B test, with how to run both.
- [FAQ](docs/faq.md): including how this compares to similar projects.
- Write-up (Turkish): [Fable 5.2 ile orkestra ve otomode](docs/fable-orkestra-ve-otomode.md), on running an expensive main-loop model as the conductor and leaving it to work unattended.

## Layout

```
skills/
  orchestra/   SKILL.md, scripts/ (mmo-run, mmo-council, mmo-preflight, mmo_extract.py), templates/
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, otomode, benchmark, faq, translations
```

## License

MIT, see [LICENSE](LICENSE). The README illustration was generated with gpt-image-2 through the Codex CLI.
