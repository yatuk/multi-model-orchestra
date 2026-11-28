<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="logo multi-model-orchestra: một nhạc trưởng hoạt hình đeo nơ đỏ đang giơ cao chiếc đũa chỉ huy">
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
  <sub>Các nhà cung cấp có mô hình đã được chạy qua một lane và chấm điểm trong <a href="benchmark.md">benchmark</a>. Tên và logo thuộc về chủ sở hữu của chúng; không hàm ý bảo trợ nào.</sub>
</p>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · Tiếng Việt</sub></p>

<p align="center"><b>Để một mô hình đắt tiền chỉ huy, các mô hình rẻ hơn biểu diễn, và mọi câu trả lời đều được kiểm tra trước khi dùng.</b><br>
Các skill cho Claude Code (hoặc bất kỳ công cụ nào đọc tệp <code>SKILL.md</code>) giao việc cho Claude Opus, Sonnet và Haiku, OpenAI GPT, Kimi, DeepSeek và bất kỳ CLI agent hay API nào bạn có: OpenCode, Grok, Gemini, Qwen, Cursor, Copilot, OpenRouter, mô hình cục bộ và nhiều hơn nữa.<br>
Agent chính lập kế hoạch, viết brief và xem xét kết quả; các mô hình khác làm việc, và không có gì chúng trả về được tin cậy cho đến khi vượt qua một bước kiểm tra.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="Giấy phép MIT"></a>
  <img src="https://img.shields.io/badge/lanes-32%20CLIs%20and%20APIs-2563EB" alt="32 lane: CLI agent và API">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="Chạy trên bash, Git Bash trên Windows">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="Sao trên GitHub"></a>
</p>

<p align="center"><b><a href="#bắt-đầu-nhanh">Cài đặt</a></b> · <a href="lanes/README.md">Lanes</a> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

<p align="center">
  <img src="../assets/orchestra-comic.png" alt="Một nhạc trưởng giao một lỗi cho một mô hình, yêu cầu diff và triệu tập một council ẩn danh" width="860">
  <br>
  <sub>Nhạc trưởng phát các bè, yêu cầu diff và triệu tập một council ẩn danh khi câu trả lời là chuyện phán đoán.</sub>
</p>

<table>
  <tr>
    <td width="25%" valign="top">
      <b>Định tuyến</b><br>
      Mỗi việc đi tới tầng rẻ nhất có thể vượt qua bước kiểm tra của nó, tùy theo độ khó. Một lane chỉ lên tầng cao hơn sau khi trượt bước kiểm tra, không phải theo cảm tính.
    </td>
    <td width="25%" valign="top">
      <b>Brief</b><br>
      Mỗi tầng nhận brief mà nó làm việc tốt nhất: mục tiêu và ràng buộc cho Opus, các bước đánh số và tệp chính xác cho các lane rẻ hơn. Một lane chỉ thấy brief, nên brief được viết cho một người xa lạ.
    </td>
    <td width="25%" valign="top">
      <b>Chạy</b><br>
      <code>mmo-run</code> là runner duy nhất cho mọi lane, với mã trạng thái nghiêm ngặt và timeout trên mỗi lệnh gọi. Các lane có ghi dữ liệu chỉ chạy trong một git worktree chứa nhánh của bạn, không bao giờ trong checkout chính của bạn.
    </td>
    <td width="25%" valign="top">
      <b>Kiểm tra</b><br>
      Nhạc trưởng tự chạy bước kiểm tra bằng <code>mmo-check</code> và đọc toàn bộ diff: các bài kiểm tra bị đụng tới, tệp nằm ngoài brief và một bước kiểm tra vẫn qua dù không có thay đổi đều bị đánh dấu. Chữ "xong" của một lane là một lời khẳng định, không phải kết quả.
    </td>
  </tr>
</table>

## Số liệu thực tế

| Nội dung | Kết quả | Chi tiết |
|---|---|---|
| <!-- AB-RESULTS --> A/B: skill orchestra so với "use subagents" thông thường (`claude-fable-5-2`, 2 lần chạy mỗi nhánh) | Chất lượng như nhau: cả bốn lần chạy đều đạt 36/36 bài kiểm tra ẩn, các bài kiểm tra hiển thị còn nguyên (bộ tác vụ quá dễ để phân biệt chất lượng) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B chi phí mỗi lần chạy | Skill trung bình $1.88 so với $3.21, ít hơn khoảng 40%, các khoảng không chồng lên nhau. Khoản tiết kiệm đến từ việc các sub-agent chạy trên Sonnet thay vì kế thừa Fable. Không tăng tốc (3.2 so với 3.5 phút) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B giới hạn | Một prompt một dòng "use Sonnet subagents" (2026-11-28, 2 lần chạy, 36/36, trung bình $1.49, sub-agent trên Sonnet) đã đạt được toàn bộ khoản tiết kiệm mà không cần skill; A và B chạy vào một ngày trước đó, nên đây không phải phép so sánh có kiểm soát. `total_cost_usd` là chỉ số đại diện theo giá niêm yết, không phải mức dùng của gói | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
| Benchmark các lane, 2026-11-21 (sửa lỗi có bài kiểm tra ẩn, suy luận có đáp án chính xác, gán nhãn hàng loạt 60 dòng) | Kimi k3.1-pro, DeepSeek v4-pro, DeepSeek flash và gpt-5.6-terra: 6/6, 3/3, 60/60. gpt-6-luna: 6/6, 0/3, 58/60. gpt-6.1-sol và gpt-6-astra: ~6/6, ~3/3, ~60/60 (ước tính: không có trên gói đó, điểm lấy từ lần chạy 2026-11-11) | [benchmark.md](benchmark.md) |
| otomode, một lần chạy không giám sát kéo dài 5 giờ | 13 tác vụ, mỗi tác vụ một commit; giới hạn hằng tuần tăng từ 25% lên 31%; 6 lời nhắc bị từ chối và được ghi lại. Một lần chạy, không phải benchmark | [otomode.md](otomode.md#one-real-run) |

> [!WARNING]
> Brief rời khỏi máy của bạn: mỗi lane gửi brief của nó tới nhà cung cấp của mô hình đó. Không bao giờ đưa bí mật, token
> hay dữ liệu cá nhân vào brief. Hook của otomode từ chối các lời nhắc và chặn các lệnh xóa, deploy,
> push và gửi, nhưng nó hoạt động theo đối sánh mẫu: đó là lan can bảo vệ, không phải sandbox.

## Bắt đầu nhanh

Dán đoạn này vào agent của bạn và để nó cài các skill:

```text
Install multi-model-orchestra: clone https://github.com/yatuk/multi-model-orchestra,
run ./install.sh --link in it, then run ~/.claude/skills/orchestra/scripts/mmo-preflight
and tell me which lanes are ready.
```

Hoặc tự làm. Cần bash, git, `timeout` và Python 3; trên Windows, hãy dùng Git Bash.

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link          # into ~/.claude/skills; --dir PATH for a project
~/.claude/skills/orchestra/scripts/mmo-preflight
```

`mmo-preflight` không bao giờ gọi mô hình. Nó cho bạn biết những lane nào có trên máy này, để nhạc trưởng định tuyến tránh các lane còn thiếu.
Với otomode, hãy chạy một lần `python ~/.claude/skills/otomode/scripts/otomode.py install` để đăng ký hook của nó.

Sau đó hãy yêu cầu, chẳng hạn:

- "Fix the failing tests in `internal/auth`. Follow the orchestra skill."
- "Get a second opinion from GPT on this migration plan before I merge it."
- "Ask the council: should we split this service or keep one process?"
- "Do this migration yourself; use the advisor skill with GPT before you start and before you say done."
- "otomode 6h: these four tasks, each checked with `go test ./...`."

## Hoạt động với

| Công cụ | Dùng cho | Yêu cầu |
|---|---|---|
| Claude Code | Các skill, và các tầng Claude Opus / Sonnet / Haiku làm sub-agent | Skill được cài trong `~/.claude/skills` (hoặc `.claude/skills` của một dự án); không cần gì khác |
| Codex CLI | Các lane GPT | `codex` trong PATH, đã đăng nhập bằng ChatGPT |
| Kimi Code CLI | Các lane Kimi và DeepSeek | `kimi` trong PATH, đã đăng nhập; với DeepSeek, cần một mô hình `deepseek/*` trong `config.toml` của Kimi Code |
| OpenCode | Bất kỳ nhà cung cấp nào nó đã đăng nhập (DeepSeek, OpenRouter, Ollama, các mô hình miễn phí của nó) | `opencode` trong PATH |
| Grok CLI | Các lane Grok | `grok` trong PATH, đã đăng nhập |
| Cursor CLI | Các lane Cursor | `cursor-agent` trong PATH, đã đăng nhập |
| Antigravity CLI | Các lane Antigravity | `agy` trong PATH, đã đăng nhập |
| Copilot CLI | Các lane Copilot | `copilot` trong PATH, đã đăng nhập |
| 19 CLI agent khác | Gemini CLI, Qwen Code, Amp, Droid, Auggie, Kiro, Cline, Kilo, Vibe, Crush, Goose, Aider, Pi, Devin, CodeBuddy, Letta Code, Qoder, gptme, llm | CLI trong PATH, đã đăng nhập. Được viết dựa trên tài liệu của từng CLI và người bảo trì chưa chạy thử: [ý nghĩa là gì](lanes/README.md#what-checked-means) |
| Không cần CLI | Lane `api`: mọi endpoint tương thích OpenAI (OpenRouter, DeepSeek, Groq, Ollama cục bộ, ...) cho ý kiến và công việc hàng loạt | Python 3 và một khóa trong biến môi trường |
| Agent đám mây (thử nghiệm) | Devin, agent đám mây của Cursor, tác vụ agent của Copilot qua `mmo-cloud` | Một khóa của nhà cung cấp, và mã được đẩy lên nơi agent có thể truy cập |

`mmo-run --list` hiển thị mọi lane và cho biết nó đã sẵn sàng trên máy bạn chưa. Chi tiết từng lane: [docs/lanes](lanes/README.md).

ID mô hình GPT: trên một số gói ChatGPT, Codex CLI hiện cung cấp các id khác (ví dụ gpt-5.6-terra hoặc gpt-6-luna)
và từ chối những id còn lại. Các tệp skill nêu giá trị mặc định; hãy thử các id mà gói của bạn chấp nhận trước khi định tuyến việc tới đó
(`mmo-preflight` để xem các CLI, rồi một brief `mmo-run` một dòng cho mỗi id). Xem [Model ids](how-it-works.md#model-ids).

## PR đầu tiên trong 10 phút

Hầu hết không cần cài đặt gì:

- **Đọc README bằng ngôn ngữ của bạn** và sửa những chỗ nghe như máy dịch. Cả 19 bản dịch đều do một mô hình tạo ra ([tiếng Tatar Crimea](https://github.com/yatuk/multi-model-orchestra/issues/1), [tiếng Duy Ngô Nhĩ](https://github.com/yatuk/multi-model-orchestra/issues/2), [tiếng Turkmen](https://github.com/yatuk/multi-model-orchestra/issues/3), [tiếng Kazakh](https://github.com/yatuk/multi-model-orchestra/issues/4), [các bản còn lại](https://github.com/yatuk/multi-model-orchestra/issues/5)).
- **Dán một dòng lỗi** mà CLI trả về (vượt giới hạn tốc độ, đăng nhập hết hạn, mô hình không xác định) để runner phân biệt được nó ([#10](https://github.com/yatuk/multi-model-orchestra/issues/10)).
- **Chạy các bài kiểm tra trên macOS hoặc Linux** và cho biết cái gì hỏng ([#8](https://github.com/yatuk/multi-model-orchestra/issues/8)).
- **Thêm một lane** cho CLI bạn dùng ([Gemini CLI](https://github.com/yatuk/multi-model-orchestra/issues/6), [Aider](https://github.com/yatuk/multi-model-orchestra/issues/7)), hoặc [bỏ phiếu cho lane tiếp theo](https://github.com/yatuk/multi-model-orchestra/discussions/12).

Tất cả: [good first issues](https://github.com/yatuk/multi-model-orchestra/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22). Cách bạn định tuyến công việc của riêng mình được chào đón tại [Show your routing setup](https://github.com/yatuk/multi-model-orchestra/discussions/11). Xem [CONTRIBUTING](../CONTRIBUTING.md).

## Xem thêm

Các tài liệu dưới đây bằng tiếng Anh.

- [How it works](how-it-works.md): bảng định tuyến, runner, mã trạng thái, kiểm tra một lane, mô hình an toàn, council.
- [Lanes](lanes/README.md): từng lane, mức độ đã được kiểm tra và cách thêm một lane.
- [otomode](otomode.md): các lần chạy không giám sát khi bạn vắng mặt.
- [Benchmark](benchmark.md): benchmark các lane và thử nghiệm A/B, cùng cách chạy cả hai.
- [Cost](cost.md): tám đòn bẩy chi phí, cùng các lệnh áp dụng hoặc đo từng đòn bẩy.
- [FAQ](faq.md): bao gồm cả so sánh với các dự án tương tự.
- [Failures seen](failures.md): mỗi lỗi trông như thế nào và điều gì đã khắc phục nó.
- Bài viết (tiếng Thổ Nhĩ Kỳ): [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), về việc dùng một mô hình vòng lặp chính đắt tiền làm nhạc trưởng và để nó làm việc không giám sát.

## Cấu trúc thư mục

```
skills/
  orchestra/   SKILL.md, lanes.md, templates/, scripts/ (mmo-run, mmo-check, mmo-council, mmo-score,
               mmo-cloud, mmo-preflight, providers/ with one file per lane)
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/  cloud-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, lanes/, otomode, benchmark, faq, translations
```

## Giấy phép

MIT, xem [LICENSE](../LICENSE). Hình minh họa trong README được tạo bằng gpt-image-2 qua Codex CLI.
