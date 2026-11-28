<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="multi-model-orchestra 标志：一位系着红色领结、举起指挥棒的卡通指挥家">
</p>

<h1 align="center">multi-model-orchestra</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Claude-D97757?style=flat-square&logo=claude&logoColor=white" alt="Claude" height="22">
  <img src="https://img.shields.io/badge/GPT%20(Codex)-10A37F?style=flat-square" alt="GPT (Codex)" height="22">
  <img src="https://img.shields.io/badge/DeepSeek-4D6BFE?style=flat-square&logo=deepseek&logoColor=white" alt="DeepSeek" height="22">
  <img src="https://img.shields.io/badge/Kimi-1B1B1B?style=flat-square&logo=kimi&logoColor=white" alt="Kimi" height="22">
  <img src="https://img.shields.io/badge/Grok-000000?style=flat-square" alt="Grok" height="22">
  <img src="https://img.shields.io/badge/OpenCode-211E1E?style=flat-square&logo=opencode&logoColor=white" alt="OpenCode" height="22">
  <img src="https://img.shields.io/badge/Gemini-8E75B2?style=flat-square&logo=googlegemini&logoColor=white" alt="Gemini" height="22">
  <img src="https://img.shields.io/badge/Cursor-000000?style=flat-square&logo=cursor&logoColor=white" alt="Cursor" height="22">
  <img src="https://img.shields.io/badge/OpenRouter-6467F2?style=flat-square&logo=openrouter&logoColor=white" alt="OpenRouter" height="22">
  <img src="https://img.shields.io/badge/NVIDIA-76B900?style=flat-square&logo=nvidia&logoColor=white" alt="NVIDIA" height="22">
  <img src="https://img.shields.io/badge/Baidu-2932E1?style=flat-square&logo=baidu&logoColor=white" alt="Baidu" height="22">
  <br>
  <sub>模型已通过 lane 运行并在 <a href="benchmark.md">benchmark</a> 中评分的厂商。名称和标志归其各自所有者所有，不代表任何背书。</sub>
</p>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · 简体中文 · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>让一个昂贵的模型担任指挥，让更便宜的模型演奏，并在使用每一个答案之前先检查它。</b><br>
适用于 Claude Code（或任何会读取 <code>SKILL.md</code> 文件的工具）的 skill，把工作分派给 Claude Opus、Sonnet 和 Haiku、OpenAI GPT、Kimi、DeepSeek，以及你手头的任何 agent CLI 或 API：OpenCode、Grok、Gemini、Qwen、Cursor、Copilot、OpenRouter、本地模型等。<br>
主 agent 负责规划、撰写 brief 并审查；其他模型负责干活，它们返回的任何内容在通过检查之前都不会被信任。</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="MIT 许可证"></a>
  <img src="https://img.shields.io/badge/lanes-32%20CLIs%20and%20APIs-2563EB" alt="32 个 lane：agent CLI 和 API">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="运行于 bash，Windows 上使用 Git Bash">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="GitHub stars"></a>
</p>

<p align="center"><b><a href="#快速开始">安装</a></b> · <a href="lanes/README.md">Lanes</a> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

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
      <code>mmo-run</code> 是适用于所有 lane 的唯一 runner，带有严格的状态码，每次调用都有超时。会写入的 lane 只在包含你所在分支的 git worktree 中运行，绝不在你的主 checkout 中运行。
    </td>
    <td width="25%" valign="top">
      <b>检查</b><br>
      指挥家亲自用 <code>mmo-check</code> 运行检查并通读整个 diff：被改动的测试、brief 之外的文件，以及没有这项改动也能通过的检查，都会被标记出来。lane 说的「完成」只是一个声明，不是结果。
    </td>
  </tr>
</table>

## 真实数据

| 内容 | 结果 | 详情 |
|---|---|---|
| <!-- AB-RESULTS --> A/B：orchestra skill 对比普通的 "use subagents"（`claude-fable-5-2`，每组 2 次运行） | 质量相同：四次运行全部通过 36/36 隐藏测试，可见测试保持完好（任务集过于简单，无法区分质量） | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B 每次运行的成本 | skill 平均 $1.88，对照组 $3.21，约便宜 40%，区间不重叠。节省来自 sub-agent 在 Sonnet 上运行，而不是继承 Fable。速度没有提升（3.2 对 3.5 分钟） | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B 的局限 | 一句「use Sonnet subagents」的提示（2026-11-28，2 次运行，36/36，平均 $1.49，sub-agent 在 Sonnet 上运行）没有 skill 也拿到了全部节省；A 和 B 是在更早的一天运行的，因此这不是受控对比。 `total_cost_usd` 是按标价估算的替代指标，不是套餐用量 | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
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
- 「这次迁移请你自己来做；开始之前和宣布完成之前，都用 advisor skill 向 GPT 咨询一下。」
- 「otomode 6h：这四个任务，每个都用 `go test ./...` 检查。」

## 兼容的工具

| 工具 | 用途 | 需要 |
|---|---|---|
| Claude Code | skill，以及作为 sub-agent 的 Claude Opus / Sonnet / Haiku 层级 | skill 已安装在 `~/.claude/skills`（或项目的 `.claude/skills`）；无需其他东西 |
| Codex CLI | GPT lane | `codex` 在 PATH 中，并已用 ChatGPT 登录 |
| Kimi Code CLI | Kimi 和 DeepSeek lane | `kimi` 在 PATH 中并已登录；DeepSeek 需要在 Kimi Code 的 `config.toml` 中配置一个 `deepseek/*` 模型 |
| OpenCode | 它已登录的任何提供商（DeepSeek、OpenRouter、Ollama、其免费模型） | `opencode` 在 PATH 中 |
| Grok CLI | Grok lane | `grok` 在 PATH 中并已登录 |
| Cursor CLI | Cursor lane | `cursor-agent` 在 PATH 中并已登录 |
| Antigravity CLI | Antigravity lane | `agy` 在 PATH 中并已登录 |
| Copilot CLI | Copilot lane | `copilot` 在 PATH 中并已登录 |
| 另外 19 个 agent CLI | Gemini CLI, Qwen Code, Amp, Droid, Auggie, Kiro, Cline, Kilo, Vibe, Crush, Goose, Aider, Pi, Devin, CodeBuddy, Letta Code, Qoder, gptme, llm | CLI 在 PATH 中并已登录。依据各 CLI 的文档编写，维护者尚未实际运行过：[这意味着什么](lanes/README.md#what-checked-means) |
| 完全没有 CLI | `api` lane：任何兼容 OpenAI 的端点（OpenRouter、DeepSeek、Groq、本地 Ollama 等），用于征求意见和批量工作 | Python 3，以及放在环境变量中的密钥 |
| 云端 agent（实验性） | 通过 `mmo-cloud` 使用 Devin、Cursor 云端 agent、Copilot agent 任务 | 厂商密钥，以及已推送到 agent 可访问位置的代码 |

`mmo-run --list` 会列出每个 lane，以及它在你的机器上是否就绪。各 lane 的详情：[lanes](lanes/README.md)。

GPT 模型 id：在某些 ChatGPT 套餐上，Codex CLI 现在提供的是不同的 id（例如 gpt-5.6-terra 或 gpt-6-luna），
并拒绝其他 id。skill 文件中写明了默认值；在把工作路由过去之前，请先对你的套餐接受的 id 做冒烟测试
（先用 `mmo-preflight` 查看 CLI，然后对每个 id 运行一条只有一行的 `mmo-run` brief）。参见 [Model ids](how-it-works.md#model-ids)。

## 10 分钟提交第一个 PR

这些事大多不需要任何准备：

- **阅读你所用语言的 README**，修正读起来像机器翻出来的地方。全部 19 种译文都是由模型生成的（[克里米亚鞑靼语](https://github.com/yatuk/multi-model-orchestra/issues/1)、[维吾尔语](https://github.com/yatuk/multi-model-orchestra/issues/2)、[土库曼语](https://github.com/yatuk/multi-model-orchestra/issues/3)、[哈萨克语](https://github.com/yatuk/multi-model-orchestra/issues/4)、[其余语言](https://github.com/yatuk/multi-model-orchestra/issues/5)）。
- **粘贴一行错误信息**，也就是某个 CLI 给你的（限流、登录过期、未知模型），好让 runner 能把它区分出来（[#10](https://github.com/yatuk/multi-model-orchestra/issues/10)）。
- **在 macOS 或 Linux 上运行测试**，并说明哪里出了问题（[#8](https://github.com/yatuk/multi-model-orchestra/issues/8)）。
- **为你使用的 CLI 添加一个 lane**（[Gemini CLI](https://github.com/yatuk/multi-model-orchestra/issues/6)、[Aider](https://github.com/yatuk/multi-model-orchestra/issues/7)），或者[为下一个投票](https://github.com/yatuk/multi-model-orchestra/discussions/12)。

全部列表：[good first issues](https://github.com/yatuk/multi-model-orchestra/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)。你如何路由自己的工作，欢迎分享到 [Show your routing setup](https://github.com/yatuk/multi-model-orchestra/discussions/11)。参见 [CONTRIBUTING](../CONTRIBUTING.md)。

## 更多

以下文档为英文。

- [How it works](how-it-works.md)：路由表、runner、状态码、检查 lane、安全模型、council。
- [Lanes](lanes/README.md)：每个 lane、它被检验到了什么程度，以及如何添加新的 lane。
- [otomode](otomode.md)：你不在时的无人值守运行。
- [Benchmark](benchmark.md)：lane benchmark 和 A/B 测试，以及如何运行这两者。
- [Cost](cost.md)：八个成本杠杆，以及强制执行或衡量每一项的命令。
- [FAQ](faq.md)：包括与类似项目的比较。
- [Failures seen](failures.md)：每种故障的表现，以及是什么修复了它。
- 文章（土耳其语）：[Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md)，讲述如何让昂贵的主循环模型担任指挥，并放手让它无人值守地工作。

## 目录结构

```
skills/
  orchestra/   SKILL.md, lanes.md, templates/, scripts/ (mmo-run, mmo-check, mmo-council, mmo-score,
               mmo-cloud, mmo-preflight, providers/ with one file per lane)
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/  cloud-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, lanes/, otomode, benchmark, faq, translations
```

## 许可证

MIT，见 [LICENSE](../LICENSE)。README 插图由 gpt-image-2 通过 Codex CLI 生成。
