<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="multi-model-orchestra 标志：一位系着红色领结、举起指挥棒的卡通指挥家">
</p>

<h1 align="center">multi-model-orchestra</h1>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · 简体中文 · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>让一个昂贵的模型担任指挥，让更便宜的模型演奏，并在使用每一个答案之前先检查它。</b><br>
适用于 Claude Code（或任何会读取 <code>SKILL.md</code> 文件的工具）的 skill，把工作分派给 Claude Opus、Sonnet 和 Haiku、OpenAI GPT、Kimi 以及 DeepSeek。<br>
主 agent 负责规划、撰写 brief 并审查；其他模型负责干活，它们返回的任何内容在通过检查之前都不会被信任。</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="MIT 许可证"></a>
  <img src="https://img.shields.io/badge/models-Claude%20·%20GPT%20·%20Kimi%20·%20DeepSeek-2563EB" alt="Claude、GPT、Kimi 和 DeepSeek 的 lane">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="运行于 bash，Windows 上使用 Git Bash">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="GitHub stars"></a>
</p>

<p align="center"><b><a href="#快速开始">安装</a></b> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

<p align="center">
  <img src="../assets/orchestra-comic.png" alt="指挥家把一个 bug 交给某个模型，索要 diff，并召开一次盲审 council" width="860">
  <br>
  <sub>指挥家分发声部，索要 diff，并在答案属于判断题时召开盲审 council。</sub>
</p>

<table>
  <tr>
    <td width="25%" valign="top">
      <b>路由</b><br>
      每项工作按难度交给能通过其检查的最便宜的层级。lane 只有在未通过检查之后才会升级，而不是凭直觉。
    </td>
    <td width="25%" valign="top">
      <b>Brief</b><br>
      每个层级拿到最适合它的 brief：给 Opus 的是目标与约束，给较便宜 lane 的是编号步骤和确切的文件。lane 只能看到 brief，所以 brief 要写给一个完全陌生的人。
    </td>
    <td width="25%" valign="top">
      <b>运行</b><br>
      <code>mmo-run</code> 是适用于所有提供商的唯一 runner，带有严格的状态码，每次调用都有超时。会写入的 lane 只在 git worktree 中运行，绝不在你的主 checkout 中运行。
    </td>
    <td width="25%" valign="top">
      <b>检查</b><br>
      指挥家亲自运行检查并通读整个 diff。lane 说的「完成」只是一个声明，不是结果。
    </td>
  </tr>
</table>

## 真实数据

| 内容 | 结果 | 详情 |
|---|---|---|
| <!-- AB-RESULTS --> A/B：orchestra skill 对比普通的 "use subagents"（`claude-fable-5-2`，每组 2 次运行） | 质量相同：四次运行全部通过 36/36 隐藏测试，可见测试保持完好（任务集过于简单，无法区分质量） | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B 每次运行的成本 | skill 平均 $1.88，对照组 $3.21，约便宜 40%，区间不重叠。节省来自 sub-agent 在 Sonnet 上运行，而不是继承 Fable。速度没有提升（3.2 对 3.5 分钟） | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B 的局限 | 一句「use Sonnet subagents」的提示没有测试过，可能就能拿到大部分节省。`total_cost_usd` 是按标价估算的替代指标，不是套餐用量 | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
| lane benchmark，2026-11-21（带隐藏测试的 bug 修复、精确答案推理、60 行批量标注） | Kimi k3.1-pro、DeepSeek v4-pro、DeepSeek flash 和 gpt-5.6-terra：6/6、3/3、60/60。gpt-6-luna：6/6、0/3、58/60。gpt-6.1-sol 和 gpt-6-astra：约 6/6、约 3/3、约 60/60（估计值：该套餐未提供，分数取自 2026-11-11 的运行） | [benchmark.md](benchmark.md) |
| otomode，一次 5 小时的无人值守运行 | 13 个任务，每个一次 commit；每周额度从 25% 升到 31%；6 次提示被拒绝并记录。仅一次运行，不是 benchmark | [otomode.md](otomode.md#one-real-run) |

> [!WARNING]
> brief 会离开你的机器：每个 lane 都会把它的 brief 发送给该模型的厂商。切勿在 brief 中放入机密、token
> 或个人数据。otomode 的 hook 会拒绝提示，并拒绝删除、部署、push 和发送类命令，
> 但它是靠模式匹配的：它是护栏，不是沙箱。

## 快速开始

把下面这段粘贴给你的 agent，让它来安装这些 skill：

```text
Install multi-model-orchestra: clone https://github.com/yatuk/multi-model-orchestra,
run ./install.sh --link in it, then run ~/.claude/skills/orchestra/scripts/mmo-preflight
and tell me which lanes are ready.
```

或者自己动手。需要 bash、git、`timeout` 和 Python 3；在 Windows 上请使用 Git Bash。

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link          # into ~/.claude/skills; --dir PATH for a project
~/.claude/skills/orchestra/scripts/mmo-preflight
```

`mmo-preflight` 从不调用任何模型。它会告诉你这台机器上有哪些 lane，让指挥家绕开缺失的那些。
对于 otomode，请运行一次 `python ~/.claude/skills/otomode/scripts/otomode.py install` 来注册它的 hook。

然后就可以这样提问，例如：

- 「修复 `internal/auth` 中失败的测试。遵循 orchestra skill。」
- 「在我合并之前，就这份迁移方案向 GPT 征求第二意见。」
- 「问问 council：我们应该拆分这个服务，还是保持单进程？」
- 「otomode 6h：这四个任务，每个都用 `go test ./...` 检查。」

## 兼容的工具

| 工具 | 用途 | 需要 |
|---|---|---|
| Claude Code | skill，以及作为 sub-agent 的 Claude Opus / Sonnet / Haiku 层级 | skill 已安装在 `~/.claude/skills`（或项目的 `.claude/skills`）；无需其他东西 |
| Codex CLI | GPT lane | `codex` 在 PATH 中，并已用 ChatGPT 登录 |
| Kimi Code CLI | Kimi 和 DeepSeek lane | `kimi` 在 PATH 中并已登录；DeepSeek 需要在 Kimi Code 的 `config.toml` 中配置一个 `deepseek/*` 模型 |

GPT 模型 id：在某些 ChatGPT 套餐上，Codex CLI 现在提供的是不同的 id（例如 gpt-5.6-terra 或 gpt-6-luna），
并拒绝其他 id。skill 文件中写明了默认值；在把工作路由过去之前，请先对你的套餐接受的 id 做冒烟测试
（先用 `mmo-preflight` 查看 CLI，然后对每个 id 运行一条只有一行的 `mmo-run` brief）。参见 [Model ids](how-it-works.md#model-ids)。

## 更多

以下文档为英文。

- [How it works](how-it-works.md)：路由表、runner、状态码、安全模型、council。
- [otomode](otomode.md)：你不在时的无人值守运行。
- [Benchmark](benchmark.md)：lane benchmark 和 A/B 测试，以及如何运行这两者。
- [FAQ](faq.md)：包括与类似项目的比较。
- 文章（土耳其语）：[Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md)，讲述如何让昂贵的主循环模型担任指挥，并放手让它无人值守地工作。

## 目录结构

```
skills/
  orchestra/   SKILL.md, scripts/ (mmo-run, mmo-council, mmo-preflight, mmo_extract.py), templates/
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, otomode, benchmark, faq, translations
```

## 许可证

MIT，见 [LICENSE](../LICENSE)。README 插图由 gpt-image-2 通过 Codex CLI 生成。
