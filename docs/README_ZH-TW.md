<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="multi-model-orchestra 標誌：一位繫著紅色領結、舉起指揮棒的卡通指揮家">
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
  <sub>模型已透過 lane 執行並在 <a href="benchmark.md">benchmark</a> 中評分的廠商。名稱與標誌歸其各自擁有者所有，不代表任何背書。</sub>
</p>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · 繁體中文 · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>讓一個昂貴的模型擔任指揮，讓更便宜的模型演奏，並在使用每一個答案之前先檢查它。</b><br>
適用於 Claude Code（或任何會讀取 <code>SKILL.md</code> 檔案的工具）的 skill，把工作交給 Claude Opus、Sonnet 和 Haiku、OpenAI GPT、Kimi、DeepSeek，以及你手上任何的 agent CLI 或 API：OpenCode、Grok、Gemini、Qwen、Cursor、Copilot、OpenRouter、本機模型等。<br>
主 agent 負責規劃、撰寫 brief 並審查；其他模型負責做事，它們回傳的任何內容在通過檢查之前都不會被信任。</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="MIT 授權"></a>
  <img src="https://img.shields.io/badge/lanes-32%20CLIs%20and%20APIs-2563EB" alt="32 個 lane：agent CLI 與 API">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="執行於 bash，Windows 上使用 Git Bash">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="GitHub stars"></a>
</p>

<p align="center"><b><a href="#快速開始">安裝</a></b> · <a href="lanes/README.md">Lanes</a> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

<p align="center">
  <img src="../assets/orchestra-comic.png" alt="指揮家把一個 bug 交給某個模型，索取 diff，並召開一場盲審 council" width="860">
  <br>
  <sub>指揮家分發聲部，索取 diff，並在答案屬於判斷題時召開盲審 council。</sub>
</p>

<table>
  <tr>
    <td width="25%" valign="top">
      <b>路由</b><br>
      每項工作依難度交給能通過其檢查的最便宜的層級。lane 只有在未通過檢查之後才會升級，而不是憑直覺。
    </td>
    <td width="25%" valign="top">
      <b>Brief</b><br>
      每個層級拿到最適合它的 brief：給 Opus 的是目標與限制，給較便宜 lane 的是編號步驟和確切的檔案。lane 只看得到 brief，所以 brief 要寫給一個完全陌生的人。
    </td>
    <td width="25%" valign="top">
      <b>執行</b><br>
      <code>mmo-run</code> 是適用於所有 lane 的唯一 runner，具備嚴格的狀態碼，每次呼叫都有逾時。會寫入的 lane 只在包含你所在分支的 git worktree 中執行，絕不在你的主 checkout 中執行。
    </td>
    <td width="25%" valign="top">
      <b>檢查</b><br>
      指揮家親自用 <code>mmo-check</code> 執行檢查並通讀整份 diff：被改動的測試、brief 以外的檔案，以及沒有這項改動也能通過的檢查，都會被標記出來。lane 說的「完成」只是一項宣稱，不是結果。
    </td>
  </tr>
</table>

## 真實數據

| 內容 | 結果 | 詳情 |
|---|---|---|
| <!-- AB-RESULTS --> A/B：orchestra skill 對比單純的 "use subagents"（`claude-fable-5-2`，每組 2 次執行） | 品質相同：四次執行全部通過 36/36 隱藏測試，可見測試保持完好（任務集過於簡單，無法區分品質） | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B 每次執行的成本 | skill 平均 $1.88，對照組 $3.21，約便宜 40%，區間不重疊。節省來自 sub-agent 在 Sonnet 上執行，而不是繼承 Fable。速度沒有提升（3.2 對 3.5 分鐘） | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B 的限制 | 一句「use Sonnet subagents」的提示（2026-11-28，2 次執行，36/36，平均 $1.49，sub-agent 在 Sonnet 上執行）沒有 skill 也拿到了全部節省；A 和 B 是在更早的一天執行的，因此這不是受控對比。 `total_cost_usd` 是依定價估算的替代指標，不是方案用量 | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
| lane benchmark，2026-11-21（附隱藏測試的 bug 修復、精確答案推理、60 行批次標註） | Kimi k3.1-pro、DeepSeek v4-pro、DeepSeek flash 和 gpt-5.6-terra：6/6、3/3、60/60。gpt-6-luna：6/6、0/3、58/60。gpt-6.1-sol 和 gpt-6-astra：約 6/6、約 3/3、約 60/60（估計值：該方案未提供，分數取自 2026-11-11 的執行） | [benchmark.md](benchmark.md) |
| otomode，一次 5 小時的無人值守執行 | 13 個任務，每個一次 commit；每週額度從 25% 升到 31%；6 次提示被拒絕並記錄。僅一次執行，不是 benchmark | [otomode.md](otomode.md#one-real-run) |

> [!WARNING]
> brief 會離開你的機器：每個 lane 都會把它的 brief 傳送給該模型的廠商。切勿在 brief 中放入機密、token
> 或個人資料。otomode 的 hook 會拒絕提示，並拒絕刪除、部署、push 和傳送類指令，
> 但它是靠模式比對的：它是護欄，不是沙箱。

## 快速開始

把下面這段貼給你的 agent，讓它來安裝這些 skill：

```text
Install multi-model-orchestra: clone https://github.com/yatuk/multi-model-orchestra,
run ./install.sh --link in it, then run ~/.claude/skills/orchestra/scripts/mmo-preflight
and tell me which lanes are ready.
```

或是自己動手。需要 bash、git、`timeout` 和 Python 3；在 Windows 上請使用 Git Bash。

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link          # into ~/.claude/skills; --dir PATH for a project
~/.claude/skills/orchestra/scripts/mmo-preflight
```

`mmo-preflight` 從不呼叫任何模型。它會告訴你這台機器上有哪些 lane，讓指揮家繞開缺少的那些。
對於 otomode，請執行一次 `python ~/.claude/skills/otomode/scripts/otomode.py install` 來註冊它的 hook。

接著就可以這樣提問，例如：

- 「修復 `internal/auth` 中失敗的測試。遵循 orchestra skill。」
- 「在我合併之前，就這份遷移計畫向 GPT 徵求第二意見。」
- 「問問 council：我們應該拆分這個服務，還是維持單一程序？」
- 「這次遷移請你自己來做；開始之前和宣告完成之前，都用 advisor skill 向 GPT 諮詢一下。」
- 「otomode 6h：這四個任務，每個都用 `go test ./...` 檢查。」

## 相容的工具

| 工具 | 用途 | 需要 |
|---|---|---|
| Claude Code | skill，以及作為 sub-agent 的 Claude Opus / Sonnet / Haiku 層級 | skill 已安裝在 `~/.claude/skills`（或專案的 `.claude/skills`）；無需其他東西 |
| Codex CLI | GPT lane | `codex` 在 PATH 中，並已用 ChatGPT 登入 |
| Kimi Code CLI | Kimi 和 DeepSeek lane | `kimi` 在 PATH 中並已登入；DeepSeek 需要在 Kimi Code 的 `config.toml` 中設定一個 `deepseek/*` 模型 |
| OpenCode | 它已登入的任何供應商（DeepSeek、OpenRouter、Ollama、其免費模型） | `opencode` 在 PATH 中 |
| Grok CLI | Grok lane | `grok` 在 PATH 中並已登入 |
| Cursor CLI | Cursor lane | `cursor-agent` 在 PATH 中並已登入 |
| Antigravity CLI | Antigravity lane | `agy` 在 PATH 中並已登入 |
| Copilot CLI | Copilot lane | `copilot` 在 PATH 中並已登入 |
| 另外 19 個 agent CLI | Gemini CLI, Qwen Code, Amp, Droid, Auggie, Kiro, Cline, Kilo, Vibe, Crush, Goose, Aider, Pi, Devin, CodeBuddy, Letta Code, Qoder, gptme, llm | CLI 在 PATH 中並已登入。依據各 CLI 的文件撰寫，維護者尚未實際執行過：[這代表什麼](lanes/README.md#what-checked-means) |
| 完全沒有 CLI | `api` lane：任何相容 OpenAI 的端點（OpenRouter、DeepSeek、Groq、本機 Ollama 等），用於徵求意見和批次工作 | Python 3，以及放在環境變數中的金鑰 |
| 雲端 agent（實驗性） | 透過 `mmo-cloud` 使用 Devin、Cursor 雲端 agent、Copilot agent 任務 | 廠商金鑰，以及已推送到 agent 可存取位置的程式碼 |

`mmo-run --list` 會列出每個 lane，以及它在你的機器上是否就緒。各 lane 的詳情：[lanes](lanes/README.md)。

GPT 模型 id：在某些 ChatGPT 方案上，Codex CLI 現在提供的是不同的 id（例如 gpt-5.6-terra 或 gpt-6-luna），
並拒絕其他 id。skill 檔案中寫明了預設值；在把工作路由過去之前，請先對你的方案接受的 id 做冒煙測試
（先用 `mmo-preflight` 查看 CLI，然後對每個 id 執行一條只有一行的 `mmo-run` brief）。參見 [Model ids](how-it-works.md#model-ids)。

## 10 分鐘內完成第一個 PR

這些事大多不需要任何準備：

- **閱讀你所用語言的 README**，修正讀起來像機器翻出來的地方。全部 19 種譯文都是由模型產生的（[克里米亞韃靼語](https://github.com/yatuk/multi-model-orchestra/issues/1)、[維吾爾語](https://github.com/yatuk/multi-model-orchestra/issues/2)、[土庫曼語](https://github.com/yatuk/multi-model-orchestra/issues/3)、[哈薩克語](https://github.com/yatuk/multi-model-orchestra/issues/4)、[其餘語言](https://github.com/yatuk/multi-model-orchestra/issues/5)）。
- **貼上一行錯誤訊息**，也就是某個 CLI 給你的（速率限制、登入過期、未知模型），好讓 runner 能把它區分出來（[#10](https://github.com/yatuk/multi-model-orchestra/issues/10)）。
- **在 macOS 或 Linux 上執行測試**，並說明哪裡出了問題（[#8](https://github.com/yatuk/multi-model-orchestra/issues/8)）。
- **為你使用的 CLI 新增一個 lane**（[Gemini CLI](https://github.com/yatuk/multi-model-orchestra/issues/6)、[Aider](https://github.com/yatuk/multi-model-orchestra/issues/7)），或是[為下一個投票](https://github.com/yatuk/multi-model-orchestra/discussions/12)。

全部清單：[good first issues](https://github.com/yatuk/multi-model-orchestra/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)。你如何路由自己的工作，歡迎分享到 [Show your routing setup](https://github.com/yatuk/multi-model-orchestra/discussions/11)。參見 [CONTRIBUTING](../CONTRIBUTING.md)。

## 更多

以下文件為英文。

- [How it works](how-it-works.md)：路由表、runner、狀態碼、檢查 lane、安全模型、council。
- [Lanes](lanes/README.md)：每個 lane、它被驗證到什麼程度，以及如何新增一個 lane。
- [otomode](otomode.md)：你不在時的無人值守執行。
- [Benchmark](benchmark.md)：lane benchmark 和 A/B 測試，以及如何執行這兩者。
- [Cost](cost.md)：八個成本槓桿，以及強制執行或衡量每一項的指令。
- [FAQ](faq.md)：包括與類似專案的比較。
- [Failures seen](failures.md)：每種失敗的樣貌，以及是什麼修好了它。
- 文章（土耳其語）：[Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md)，談如何讓昂貴的主迴圈模型擔任指揮，並放手讓它無人值守地工作。

## 目錄結構

```
skills/
  orchestra/   SKILL.md, lanes.md, templates/, scripts/ (mmo-run, mmo-check, mmo-council, mmo-score,
               mmo-cloud, mmo-preflight, providers/ with one file per lane)
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/  cloud-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, lanes/, otomode, benchmark, faq, translations
```

## 授權

MIT，見 [LICENSE](../LICENSE)。README 插圖由 gpt-image-2 透過 Codex CLI 產生。
