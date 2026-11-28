<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="multi-model-orchestra のロゴ：赤い蝶ネクタイをして指揮棒を掲げる漫画風の指揮者">
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
  <sub>モデルを lane 経由で実行し、<a href="benchmark.md">benchmark</a> で採点したベンダー。名称とロゴはそれぞれの所有者に帰属し、推奨や承認を示すものではありません。</sub>
</p>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · 日本語 · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>高価なモデルに指揮を任せ、安価なモデルに演奏させ、使う前にすべての回答を検証する。</b><br>
Claude Code（または <code>SKILL.md</code> ファイルを読むあらゆるツール）向けの skill で、作業を Claude Opus・Sonnet・Haiku、OpenAI GPT、Kimi、DeepSeek、そして手元にあるあらゆる agent CLI や API（OpenCode、Grok、Gemini、Qwen、Cursor、Copilot、OpenRouter、ローカルモデルなど）に振り分けます。<br>
メインの agent が計画を立て、brief を書き、レビューします。実際の作業は他のモデルが行い、返ってきたものはチェックを通るまで信用されません。</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="MIT ライセンス"></a>
  <img src="https://img.shields.io/badge/lanes-32%20CLIs%20and%20APIs-2563EB" alt="32 の lane：agent CLI と API">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="bash で動作、Windows では Git Bash">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="GitHub stars"></a>
</p>

<p align="center"><b><a href="#クイックスタート">インストール</a></b> · <a href="lanes/README.md">Lanes</a> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

<p align="center">
  <img src="../assets/orchestra-comic.png" alt="指揮者がバグをモデルに渡し、diff を求め、ブラインドの council を開く" width="860">
  <br>
  <sub>指揮者はパートを割り振り、diff を求め、答えが判断を要するものならブラインドの council を開きます。</sub>
</p>

<table>
  <tr>
    <td width="25%" valign="top">
      <b>ルーティング</b><br>
      各ジョブは、難易度に応じて、チェックを通過できる最も安価な階層に渡されます。lane が上の階層に上がるのはチェックに失敗した後だけで、勘では上がりません。
    </td>
    <td width="25%" valign="top">
      <b>Brief</b><br>
      各階層には、最も力を発揮できる brief を渡します。Opus には目標と制約、安価な lane には番号付きの手順と正確なファイルです。lane が見られるのは brief だけなので、brief は初対面の相手に向けて書きます。
    </td>
    <td width="25%" valign="top">
      <b>実行</b><br>
      <code>mmo-run</code> はすべての lane に対する唯一の runner で、厳格なステータスコードと、呼び出しごとのタイムアウトを備えています。書き込みを行う lane は あなたのブランチを含む git worktree の中でのみ実行され、メインの checkout では決して実行されません。
    </td>
    <td width="25%" valign="top">
      <b>チェック</b><br>
      指揮者が自分で <code>mmo-check</code> を使ってチェックを実行し、diff 全体を読みます。変更されたテスト、brief の範囲外のファイル、変更がなくても通ってしまうチェックは、すべて警告されます。lane の「完了」は主張であって、結果ではありません。
    </td>
  </tr>
</table>

## 実測値

| 項目 | 結果 | 詳細 |
|---|---|---|
| <!-- AB-RESULTS --> A/B：orchestra skill と素の "use subagents" の比較（`claude-fable-5-2`、各群 2 回実行） | 品質は同等：4 回すべてで隠しテスト 36/36、見えるテストも無傷（タスクセットが易しすぎて品質の差は測れない） | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B の 1 回あたりのコスト | skill は平均 $1.88、比較群は $3.21 で、約 40% 安く、範囲は重なりません。節約の源は、sub-agent が Fable を引き継がず Sonnet で動くことです。速度の向上はありません（3.2 分 対 3.5 分） | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B の限界 | 一行の「use Sonnet subagents」というプロンプト（2026-11-28、2 回実行、36/36、平均 $1.49、sub-agent は Sonnet で動作）は、skill なしで節約の全部を得ました。A と B はそれより前の日に実行したため、統制された比較ではありません。 `total_cost_usd` は定価ベースの代理指標で、プランの使用量ではありません | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
| lane benchmark、2026-11-21（隠しテスト付きのバグ修正、厳密解の推論、60 行の一括ラベル付け） | Kimi k3.1-pro、DeepSeek v4-pro、DeepSeek flash、gpt-5.6-terra：6/6、3/3、60/60。gpt-6-luna：6/6、0/3、58/60。gpt-6.1-sol と gpt-6-astra：約 6/6、約 3/3、約 60/60（推定値：そのプランでは提供されておらず、スコアは 2026-11-11 の実行より） | [benchmark.md](benchmark.md) |
| otomode、5 時間の無人実行 1 回 | 13 タスク、各 1 commit。週間上限は 25% から 31% に上昇。6 件のプロンプトを拒否して記録。1 回の実行であり、benchmark ではありません | [otomode.md](otomode.md#one-real-run) |

> [!WARNING]
> brief はあなたのマシンの外に出ます。各 lane は自分の brief をそのモデルのベンダーに送信します。brief には
> 秘密情報、token、個人データを絶対に入れないでください。otomode の hook はプロンプトを拒否し、
> 削除、デプロイ、push、送信のコマンドを拒否しますが、パターンマッチで判定しています。これはガードレールであり、サンドボックスではありません。

## クイックスタート

次の文章をあなたの agent に貼り付けて、skill をインストールさせます。

```text
Install multi-model-orchestra: clone https://github.com/yatuk/multi-model-orchestra,
run ./install.sh --link in it, then run ~/.claude/skills/orchestra/scripts/mmo-preflight
and tell me which lanes are ready.
```

自分で行うこともできます。bash、git、`timeout`、Python 3 が必要です。Windows では Git Bash を使ってください。

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link          # into ~/.claude/skills; --dir PATH for a project
~/.claude/skills/orchestra/scripts/mmo-preflight
```

`mmo-preflight` はモデルを一切呼び出しません。このマシンにどの lane があるかを教えるので、指揮者は存在しないものを避けてルーティングします。
otomode では、hook を登録するために `python ~/.claude/skills/otomode/scripts/otomode.py install` を一度実行してください。

そのあとは、たとえば次のように頼みます。

- 「`internal/auth` の失敗しているテストを直して。orchestra skill に従って。」
- 「このマイグレーション計画をマージする前に、GPT にセカンドオピニオンをもらって。」
- 「council に聞いて：このサービスを分割すべきか、1 プロセスのままにすべきか。」
- 「このマイグレーションはあなた自身でやって。始める前と完了と言う前に、advisor skill で GPT に相談して。」
- 「otomode 6h：この 4 つのタスク、それぞれ `go test ./...` でチェックして。」

## 対応ツール

| ツール | 用途 | 必要なもの |
|---|---|---|
| Claude Code | skill、および sub-agent としての Claude Opus / Sonnet / Haiku の階層 | skill が `~/.claude/skills`（またはプロジェクトの `.claude/skills`）にインストールされていること。ほかには何も不要 |
| Codex CLI | GPT の lane | PATH 上の `codex`、ChatGPT でサインイン済み |
| Kimi Code CLI | Kimi と DeepSeek の lane | PATH 上の `kimi`、サインイン済み。DeepSeek には Kimi Code の `config.toml` に `deepseek/*` モデルが必要 |
| OpenCode | サインイン済みのあらゆるプロバイダー（DeepSeek、OpenRouter、Ollama、無料モデル） | PATH 上の `opencode` |
| Grok CLI | Grok の lane | PATH 上の `grok`、サインイン済み |
| Cursor CLI | Cursor の lane | PATH 上の `cursor-agent`、サインイン済み |
| Antigravity CLI | Antigravity の lane | PATH 上の `agy`、サインイン済み |
| Copilot CLI | Copilot の lane | PATH 上の `copilot`、サインイン済み |
| ほか 19 個の agent CLI | Gemini CLI, Qwen Code, Amp, Droid, Auggie, Kiro, Cline, Kilo, Vibe, Crush, Goose, Aider, Pi, Devin, CodeBuddy, Letta Code, Qoder, gptme, llm | PATH 上の CLI、サインイン済み。各 CLI のドキュメントをもとに書いたもので、メンテナーはまだ実行していません：[その意味](lanes/README.md#what-checked-means) |
| CLI がまったくない場合 | `api` lane：OpenAI 互換のあらゆるエンドポイント（OpenRouter、DeepSeek、Groq、ローカルの Ollama など）を、意見取得や一括作業に使います | Python 3 と、環境変数に入れたキー |
| クラウド agent（実験的） | `mmo-cloud` 経由の Devin、Cursor のクラウド agent、Copilot の agent タスク | ベンダーのキーと、agent が到達できる場所に push 済みのコード |

`mmo-run --list` はすべての lane と、それがあなたのマシンで使える状態かどうかを表示します。lane ごとの詳細：[lanes](lanes/README.md)。

GPT のモデル id：一部の ChatGPT プランでは、Codex CLI が現在は別の id（たとえば gpt-5.6-terra や gpt-6-luna）を提供し、
それ以外を拒否します。skill ファイルにはデフォルトが書かれています。作業をそちらへルーティングする前に、
自分のプランが受け付ける id をスモークテストしてください（`mmo-preflight` で CLI を確認し、各 id に対して 1 行の `mmo-run` brief を実行します）。
[Model ids](how-it-works.md#model-ids) を参照してください。

## 10 分で最初の PR

これらの多くは、事前の準備が不要です。

- **自分の言語の README を読んで**、機械が書いたように聞こえる部分を直してください。19 の翻訳はすべてモデルが作りました（[クリミア・タタール語](https://github.com/yatuk/multi-model-orchestra/issues/1)、[ウイグル語](https://github.com/yatuk/multi-model-orchestra/issues/2)、[トルクメン語](https://github.com/yatuk/multi-model-orchestra/issues/3)、[カザフ語](https://github.com/yatuk/multi-model-orchestra/issues/4)、[その他](https://github.com/yatuk/multi-model-orchestra/issues/5)）。
- **CLI が返したエラー行を貼り付けて**ください（レート制限、期限切れのログイン、不明なモデル）。runner が区別できるようになります（[#10](https://github.com/yatuk/multi-model-orchestra/issues/10)）。
- **macOS または Linux でテストを実行して**、何が壊れたか教えてください（[#8](https://github.com/yatuk/multi-model-orchestra/issues/8)）。
- **使っている CLI の lane を追加して**ください（[Gemini CLI](https://github.com/yatuk/multi-model-orchestra/issues/6)、[Aider](https://github.com/yatuk/multi-model-orchestra/issues/7)）。あるいは[次の候補に投票](https://github.com/yatuk/multi-model-orchestra/discussions/12)してください。

一覧：[good first issues](https://github.com/yatuk/multi-model-orchestra/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)。ご自身のルーティングの工夫は [Show your routing setup](https://github.com/yatuk/multi-model-orchestra/discussions/11) で歓迎します。[CONTRIBUTING](../CONTRIBUTING.md) も参照してください。

## さらに詳しく

以下のドキュメントは英語です。

- [How it works](how-it-works.md)：ルーティング表、runner、ステータスコード、lane のチェック、安全モデル、council。
- [Lanes](lanes/README.md)：すべての lane、どこまで検証されているか、新しい lane の追加方法。
- [otomode](otomode.md)：あなたが不在の間の無人実行。
- [Benchmark](benchmark.md)：lane benchmark と A/B テスト、およびその実行方法。
- [Cost](cost.md)：8 つのコストレバーと、それぞれを強制または計測するコマンド。
- [FAQ](faq.md)：類似プロジェクトとの比較を含みます。
- [Failures seen](failures.md)：見られた失敗それぞれの様子と、何で直ったか。
- 解説記事（トルコ語）：[Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md)。高価なモデルをメインループの指揮者として動かし、無人で作業させる方法について。

## ディレクトリ構成

```
skills/
  orchestra/   SKILL.md, lanes.md, templates/, scripts/ (mmo-run, mmo-check, mmo-council, mmo-score,
               mmo-cloud, mmo-preflight, providers/ with one file per lane)
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/  cloud-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, lanes/, otomode, benchmark, faq, translations
```

## ライセンス

MIT。[LICENSE](../LICENSE) を参照してください。README のイラストは、Codex CLI 経由で gpt-image-2 により生成しました。
