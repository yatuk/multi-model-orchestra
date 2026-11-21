<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="логотип multi-model-orchestra: мультиплікаційний диригент із червоною краваткою-метеликом, який здіймає паличку">
</p>

<h1 align="center">multi-model-orchestra</h1>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · Українська · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Нехай диригує одна дорога модель, грають дешевші, а кожну відповідь перевіряють, перш ніж її використати.</b><br>
Skills для Claude Code (або будь-чого, що читає файли <code>SKILL.md</code>), які передають роботу Claude Opus, Sonnet і Haiku, OpenAI GPT, Kimi та DeepSeek.<br>
Головний агент планує, пише briefs і рецензує; решта моделей виконують роботу, і нічому з того, що вони повертають, не довіряють, доки воно не пройде перевірку.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="Ліцензія MIT"></a>
  <img src="https://img.shields.io/badge/models-Claude%20·%20GPT%20·%20Kimi%20·%20DeepSeek-2563EB" alt="Lanes Claude, GPT, Kimi і DeepSeek">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="Працює на bash, у Windows через Git Bash">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="Зірки на GitHub"></a>
</p>

<p align="center"><b><a href="#швидкий-старт">Встановлення</a></b> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

<p align="center">
  <img src="../assets/orchestra-comic.png" alt="Диригент передає баг моделі, просить diff і скликає сліпий council" width="860">
  <br>
  <sub>Диригент роздає партії, просить diff і скликає сліпий council, коли відповідь залежить від судження.</sub>
</p>

<table>
  <tr>
    <td width="25%" valign="top">
      <b>Маршрутизація</b><br>
      Кожне завдання за складністю йде на найдешевший рівень, який може пройти його перевірку. Lane піднімається на вищий рівень лише після провалу перевірки, а не за інтуїцією.
    </td>
    <td width="25%" valign="top">
      <b>Brief</b><br>
      Кожен рівень отримує brief, з яким працює найкраще: мета й обмеження для Opus, пронумеровані кроки й точні файли для дешевших lanes. Lane бачить лише brief, тож його пишуть для стороннього.
    </td>
    <td width="25%" valign="top">
      <b>Запуск</b><br>
      <code>mmo-run</code> це єдиний runner для всіх провайдерів, із жорсткими кодами статусу й тайм-аутом на кожен виклик. Lanes, що пишуть, запускаються лише в git worktree, ніколи у вашому основному checkout.
    </td>
    <td width="25%" valign="top">
      <b>Перевірка</b><br>
      Диригент сам запускає перевірку й читає весь diff. Слово lane "готово" це твердження, а не результат.
    </td>
  </tr>
</table>

## Реальні цифри

| Що | Результат | Деталі |
|---|---|---|
| <!-- AB-RESULTS --> A/B: skill orchestra проти простого "use subagents" (`claude-fable-5-2`, 2 запуски на гілку) | Однакова якість: усі чотири запуски 36/36 прихованих тестів, видимі тести не зачеплено (набір завдань надто легкий, щоб розрізнити якість) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B вартість за запуск | Skill $1.88 проти $3.21 у середньому, приблизно на 40% менше, діапазони не перетинаються. Заощадження дає те, що sub-agents працюють на Sonnet, а не успадковують Fable. Виграшу в швидкості немає (3.2 проти 3.5 хв) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B обмеження | Однорядковий промпт "use Sonnet subagents" не тестували, і він може дати більшу частину заощадження. `total_cost_usd` це показник за прайсовою ціною, а не використання тарифного плану | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
| Benchmark lanes, 2026-11-21 (виправлення бага з прихованими тестами, міркування з точною відповіддю, масове маркування 60 рядків) | Kimi k3.1-pro, DeepSeek v4-pro, DeepSeek flash і gpt-5.6-terra: 6/6, 3/3, 60/60. gpt-6-luna: 6/6, 0/3, 58/60. gpt-6.1-sol і gpt-6-astra: ~6/6, ~3/3, ~60/60 (оцінка: на цьому плані недоступні, бали із запуску 2026-11-11) | [benchmark.md](benchmark.md) |
| otomode, один 5-годинний запуск без нагляду | 13 завдань, по одному commit на кожне; тижневий ліміт зріс із 25% до 31%; 6 запитів відхилено й записано в журнал. Один запуск, не benchmark | [otomode.md](otomode.md#one-real-run) |

> [!WARNING]
> Briefs залишають вашу машину: кожен lane надсилає свій brief постачальнику цієї моделі. Ніколи не кладіть у brief секрети,
> токени чи персональні дані. Hook otomode відхиляє запити та відмовляється виконувати команди видалення, deploy,
> push і надсилання, але працює за шаблонами: це обмежувач, а не sandbox.

## Швидкий старт

Вставте це у свого агента й дозвольте йому встановити skills:

```text
Install multi-model-orchestra: clone https://github.com/yatuk/multi-model-orchestra,
run ./install.sh --link in it, then run ~/.claude/skills/orchestra/scripts/mmo-preflight
and tell me which lanes are ready.
```

Або самостійно. Потрібні bash, git, `timeout` і Python 3; у Windows використовуйте Git Bash.

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link          # into ~/.claude/skills; --dir PATH for a project
~/.claude/skills/orchestra/scripts/mmo-preflight
```

`mmo-preflight` ніколи не викликає модель. Він показує, які lanes є на цій машині, щоб диригент обходив відсутні.
Для otomode один раз виконайте `python ~/.claude/skills/otomode/scripts/otomode.py install`, щоб зареєструвати його hook.

Потім просіть, наприклад:

- "Fix the failing tests in `internal/auth`. Follow the orchestra skill."
- "Get a second opinion from GPT on this migration plan before I merge it."
- "Ask the council: should we split this service or keep one process?"
- "otomode 6h: these four tasks, each checked with `go test ./...`."

## Працює з

| Інструмент | Для чого | Потрібно |
|---|---|---|
| Claude Code | Skills і рівні Claude Opus / Sonnet / Haiku як sub-agents | Skills, встановлені в `~/.claude/skills` (або в `.claude/skills` проєкту); більше нічого |
| Codex CLI | Lanes GPT | `codex` у PATH, вхід через ChatGPT |
| Kimi Code CLI | Lanes Kimi і DeepSeek | `kimi` у PATH, виконано вхід; для DeepSeek модель `deepseek/*` у `config.toml` Kimi Code |

Ідентифікатори моделей GPT: на деяких планах ChatGPT Codex CLI тепер віддає інші id (наприклад gpt-5.6-terra або gpt-6-luna)
і відхиляє решту. Файли skills називають типові значення; перш ніж спрямовувати туди роботу, перевірте, які id приймає ваш план
(`mmo-preflight`, щоб побачити CLI, потім однорядковий brief для `mmo-run` на кожен id). Див. [Model ids](how-it-works.md#model-ids).

## Ще

Наведені нижче документи англійською.

- [How it works](how-it-works.md): таблиця маршрутизації, runner, коди статусу, модель безпеки, council.
- [otomode](otomode.md): запуски без нагляду, поки вас немає.
- [Benchmark](benchmark.md): benchmark lanes і A/B-тест, з інструкціями, як запустити обидва.
- [FAQ](faq.md): зокрема порівняння зі схожими проєктами.
- Стаття (турецькою): [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), про використання дорогої моделі головного циклу як диригента та про те, щоб залишати її працювати без нагляду.

## Структура

```
skills/
  orchestra/   SKILL.md, scripts/ (mmo-run, mmo-council, mmo-preflight, mmo_extract.py), templates/
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, otomode, benchmark, faq, translations
```

## Ліцензія

MIT, див. [LICENSE](../LICENSE). Ілюстрацію README згенеровано за допомогою gpt-image-2 через Codex CLI.
