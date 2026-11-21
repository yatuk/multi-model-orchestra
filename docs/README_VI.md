<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="logo multi-model-orchestra: một nhạc trưởng hoạt hình đeo nơ đỏ đang giơ cao chiếc đũa chỉ huy">
</p>

<h1 align="center">multi-model-orchestra</h1>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · Tiếng Việt</sub></p>

<p align="center"><b>Để một mô hình đắt tiền chỉ huy, các mô hình rẻ hơn biểu diễn, và mọi câu trả lời đều được kiểm tra trước khi dùng.</b><br>
Các skill cho Claude Code (hoặc bất kỳ công cụ nào đọc tệp <code>SKILL.md</code>) giao việc cho Claude Opus, Sonnet và Haiku, OpenAI GPT, Kimi và DeepSeek.<br>
Agent chính lập kế hoạch, viết brief và xem xét kết quả; các mô hình khác làm việc, và không có gì chúng trả về được tin cậy cho đến khi vượt qua một bước kiểm tra.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="Giấy phép MIT"></a>
  <img src="https://img.shields.io/badge/models-Claude%20·%20GPT%20·%20Kimi%20·%20DeepSeek-2563EB" alt="Các lane Claude, GPT, Kimi và DeepSeek">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="Chạy trên bash, Git Bash trên Windows">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="Sao trên GitHub"></a>
</p>

<p align="center"><b><a href="#bắt-đầu-nhanh">Cài đặt</a></b> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

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
      <code>mmo-run</code> là runner duy nhất cho mọi nhà cung cấp, với mã trạng thái nghiêm ngặt và timeout trên mỗi lệnh gọi. Các lane có ghi dữ liệu chỉ chạy trong một git worktree, không bao giờ trong checkout chính của bạn.
    </td>
    <td width="25%" valign="top">
      <b>Kiểm tra</b><br>
      Nhạc trưởng tự chạy bước kiểm tra và đọc toàn bộ diff. Chữ "xong" của một lane là một lời khẳng định, không phải kết quả.
    </td>
  </tr>
</table>

## Số liệu thực tế

| Nội dung | Kết quả | Chi tiết |
|---|---|---|
| <!-- AB-RESULTS --> A/B: skill orchestra so với "use subagents" thông thường (`claude-fable-5-2`, 2 lần chạy mỗi nhánh) | Chất lượng như nhau: cả bốn lần chạy đều đạt 36/36 bài kiểm tra ẩn, các bài kiểm tra hiển thị còn nguyên (bộ tác vụ quá dễ để phân biệt chất lượng) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B chi phí mỗi lần chạy | Skill trung bình $1.88 so với $3.21, ít hơn khoảng 40%, các khoảng không chồng lên nhau. Khoản tiết kiệm đến từ việc các sub-agent chạy trên Sonnet thay vì kế thừa Fable. Không tăng tốc (3.2 so với 3.5 phút) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B giới hạn | Một prompt một dòng "use Sonnet subagents" chưa được thử và có thể đạt được phần lớn khoản tiết kiệm. `total_cost_usd` là chỉ số đại diện theo giá niêm yết, không phải mức dùng của gói | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
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
- "otomode 6h: these four tasks, each checked with `go test ./...`."

## Hoạt động với

| Công cụ | Dùng cho | Yêu cầu |
|---|---|---|
| Claude Code | Các skill, và các tầng Claude Opus / Sonnet / Haiku làm sub-agent | Skill được cài trong `~/.claude/skills` (hoặc `.claude/skills` của một dự án); không cần gì khác |
| Codex CLI | Các lane GPT | `codex` trong PATH, đã đăng nhập bằng ChatGPT |
| Kimi Code CLI | Các lane Kimi và DeepSeek | `kimi` trong PATH, đã đăng nhập; với DeepSeek, cần một mô hình `deepseek/*` trong `config.toml` của Kimi Code |

ID mô hình GPT: trên một số gói ChatGPT, Codex CLI hiện cung cấp các id khác (ví dụ gpt-5.6-terra hoặc gpt-6-luna)
và từ chối những id còn lại. Các tệp skill nêu giá trị mặc định; hãy thử các id mà gói của bạn chấp nhận trước khi định tuyến việc tới đó
(`mmo-preflight` để xem các CLI, rồi một brief `mmo-run` một dòng cho mỗi id). Xem [Model ids](how-it-works.md#model-ids).

## Xem thêm

Các tài liệu dưới đây bằng tiếng Anh.

- [How it works](how-it-works.md): bảng định tuyến, runner, mã trạng thái, mô hình an toàn, council.
- [otomode](otomode.md): các lần chạy không giám sát khi bạn vắng mặt.
- [Benchmark](benchmark.md): benchmark các lane và thử nghiệm A/B, cùng cách chạy cả hai.
- [FAQ](faq.md): bao gồm cả so sánh với các dự án tương tự.
- Bài viết (tiếng Thổ Nhĩ Kỳ): [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), về việc dùng một mô hình vòng lặp chính đắt tiền làm nhạc trưởng và để nó làm việc không giám sát.

## Cấu trúc thư mục

```
skills/
  orchestra/   SKILL.md, scripts/ (mmo-run, mmo-council, mmo-preflight, mmo_extract.py), templates/
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, otomode, benchmark, faq, translations
```

## Giấy phép

MIT, xem [LICENSE](../LICENSE). Hình minh họa trong README được tạo bằng gpt-image-2 qua Codex CLI.
