<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="multi-model-orchestra логотиби: кызыл көпөлөк галстук тагынган, таякчасын көтөргөн мультфильм дирижёру">
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
  <sub>Моделдери жол аркылуу иштетилген жана <a href="benchmark.md">benchmark</a>-та бааланган жеткирүүчүлөр. Аталыштар жана логотиптер ээлерине таандык; эч кандай колдоо болжолдонбойт.</sub>
</p>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · Кыргызча · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Бир кымбат модель дирижёрлук кылсын, арзаныраак моделдер ойносун, ар бир жооп колдонулганга чейин текшерилсин.</b><br>
Claude Code (же <code>SKILL.md</code> файлдарын окуган каалаган агент) үчүн ишти Claude Opus, Sonnet жана Haiku, OpenAI GPT, Kimi, DeepSeek жана сизде бар каалаган агент CLI же API-га тапшырган көндүмдөр (skills): OpenCode, Grok, Gemini, Qwen, Cursor, Copilot, OpenRouter, жергиликтүү моделдер жана башкалар.<br>
Негизги агент пландайт, брифтерди жазат жана карап чыгат; ишти башка моделдер аткарат, ал эми алар кайтарган эч нерсеге текшерүүдөн өтмөйүнчө ишенилбейт.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="MIT лицензиясы"></a>
  <img src="https://img.shields.io/badge/lanes-32%20CLIs%20and%20APIs-2563EB" alt="32 жол: агент CLI-лери жана API-лер">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="bash менен иштейт, Windows-то Git Bash">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="GitHub жылдыздары"></a>
</p>

<p align="center"><b><a href="#тез-баштоо">Орнотуу</a></b> · <a href="lanes/README.md">Lanes</a> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">Суроо-жооп</a></p>

<p align="center">
  <img src="../assets/orchestra-comic.png" alt="Дирижёр катаны моделге берет, diff сурайт жана аноним кеңешти чакырат" width="860">
  <br>
  <sub>Дирижёр партияларды бөлүп берет, diff сурайт, ал эми жооп баа берүүнү талап кылганда аноним кеңешти (council) чакырат.</sub>
</p>

<table>
  <tr>
    <td width="25%" valign="top">
      <b>Багыттоо</b><br>
      Ар бир иш татаалдыгына жараша өз текшерүүсүнөн өтө ала турган эң арзан деңгээлге жөнөтүлөт. Жол (lane) жогорку деңгээлге божомол менен эмес, текшерүүдөн өтпөй калгандан кийин гана көтөрүлөт.
    </td>
    <td width="25%" valign="top">
      <b>Бриф</b><br>
      Ар бир деңгээл өзү үчүн эң ылайыктуу брифти алат: Opus-ка максат жана чектөөлөр, арзаныраак жолдорго номерленген кадамдар жана так файлдар. Жол брифти гана көрөт, ошондуктан ал бөтөн адам үчүн жазылат.
    </td>
    <td width="25%" valign="top">
      <b>Иштетүү</b><br>
      <code>mmo-run</code> бардык жолдор үчүн жалгыз иштеткич (runner): катуу абал коддору бар жана ар бир чакырууда күтүү убактысы чектелет. Жазуучу жолдор сиздин branch-иңизди камтыган git worktree ичинде гана иштейт, эч качан негизги checkout-уңузда эмес.
    </td>
    <td width="25%" valign="top">
      <b>Текшерүү</b><br>
      Текшерүүнү дирижёрдун өзү <code>mmo-check</code> менен иштетет жана diff-ти толук окуйт: тийилген тесттер, брифтен тышкаркы файлдар жана өзгөрүүсүз эле өтүп кете турган текшерүү белгиленет. Жолдун «бүттү» дегени натыйжа эмес, жөн гана ырастоо.
    </td>
  </tr>
</table>

## Чыныгы сандар

| Эмне | Натыйжа | Толугураак |
|---|---|---|
| <!-- AB-RESULTS --> A/B: orchestra көндүмү менен жөнөкөй "use subagents" салыштыруу (`claude-fable-5-2`, ар бир тарапка 2 иштетүү) | Сапаты бирдей: төрт иштетүүнүн баары 36/36 жашыруун тест, көрүнгөн тесттерге тийилген жок (тапшырмалар топтому сапатты ажыратууга өтө жеңил) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B бир иштетүүнүн баасы | Көндүм орточо $1.88, экинчи тарап $3.21, болжол менен 40% арзан, диапазондор кесилишпейт. Үнөмдөө ички агенттердин Fable-ды мурастабай, Sonnet-те иштешинен келет. Ылдамдыкта утуш жок (3.2 жана 3.5 мүн) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B чектөөлөрү | Бир саптык "use Sonnet subagents" сурамы (2026-11-28, 2 иштетүү, 36/36, орточо $1.49, ички агенттер Sonnet-те) үнөмдүн баарын көндүмсүз эле берди; A жана B мурунку күнү иштетилген, ошондуктан бул көзөмөлдөнгөн салыштыруу эмес. `total_cost_usd` пландын колдонулушу эмес, прейскуранттык баа боюнча кыйыр көрсөткүч | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
| Жолдордун бенчмаркы, 2026-11-21 (жашыруун тесттери бар катаны оңдоо, так жооптуу ой жүгүртүү, 60 саптык массалык белгилөө) | Kimi k3.1-pro, DeepSeek v4-pro, DeepSeek flash жана gpt-5.6-terra: 6/6, 3/3, 60/60. gpt-6-luna: 6/6, 0/3, 58/60. gpt-6.1-sol жана gpt-6-astra: ~6/6, ~3/3, ~60/60 (болжолдуу: ал планда берилбейт, упайлар 2026-11-11 иштетүүсүнөн алынган) | [benchmark.md](benchmark.md) |
| otomode, бир 5 сааттык көзөмөлсүз иштетүү | 13 тапшырма, ар бирине бир коммит; жумалык лимит 25%-дан 31%-га өстү; 6 уруксат сурамы четке кагылып, журналга жазылды. Бул бир иштетүү, бенчмарк эмес | [otomode.md](otomode.md#one-real-run) |

> [!WARNING]
> Брифтер компьютериңизден чыгат: ар бир жол өз брифин ошол моделдин жеткирүүчүсүнө жөнөтөт. Брифке эч качан сырларды, токендерди
> же жеке маалыматтарды салбаңыз. otomode-дун хугу уруксат сурамдарын четке кагат жана өчүрүү, deploy, push жана жөнөтүү буйруктарын бөгөттөйт,
> бирок ал үлгүлөрдү салыштырат: бул обочолонгон чөйрө (sandbox) эмес, коргоочу тосмо гана.

## Тез баштоо

Муну агентиңизге чаптаңыз, көндүмдөрдү ал орнотсун:

```text
Install multi-model-orchestra: clone https://github.com/yatuk/multi-model-orchestra,
run ./install.sh --link in it, then run ~/.claude/skills/orchestra/scripts/mmo-preflight
and tell me which lanes are ready.
```

Же өзүңүз орнотуңуз. bash, git, `timeout` жана Python 3 керек; Windows-то Git Bash колдонуңуз.

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link          # into ~/.claude/skills; --dir PATH for a project
~/.claude/skills/orchestra/scripts/mmo-preflight
```

`mmo-preflight` эч качан моделди чакырбайт. Ал бул компьютерде кайсы жолдор бар экенин айтат, ошондуктан дирижёр жок болгондорун айланып өтөт.
otomode үчүн анын хугун каттоо максатында бир жолу `python ~/.claude/skills/otomode/scripts/otomode.py install` иштетиңиз.

Андан кийин, мисалы, мындай сураңыз:

- "`internal/auth` ичиндеги иштебей жаткан тесттерди оңдо. orchestra көндүмүн карман."
- "Бириктирээрден мурун бул көчүрүү (migration) планы боюнча GPT-ден экинчи пикир ал."
- "Кеңештен сура: бул сервисти бөлөбүзбү же бир процесс калтырабызбы?"
- "Бул көчүрүүнү (migration) өзүң жаса; баштоодон мурун жана бүттү дебестен мурун GPT менен advisor көндүмүн колдон."
- "otomode 6h: бул төрт тапшырма, ар бири `go test ./...` менен текшерилсин."

## Кайсы куралдар менен иштейт

| Курал | Эмне үчүн | Эмне керек |
|---|---|---|
| Claude Code | Көндүмдөр жана ички агенттер катары Claude Opus / Sonnet / Haiku деңгээлдери | Көндүмдөр `~/.claude/skills` (же долбоордун `.claude/skills`) ичине орнотулган; башка эч нерсе керек эмес |
| Codex CLI | GPT жолдору | PATH ичинде `codex`, ChatGPT аркылуу кирген |
| Kimi Code CLI | Kimi жана DeepSeek жолдору | PATH ичинде `kimi`, кирген; DeepSeek үчүн Kimi Code-дун `config.toml` файлында `deepseek/*` модели |
| OpenCode | Кирген каалаган провайдер (DeepSeek, OpenRouter, Ollama, өзүнүн акысыз моделдери) | PATH ичинде `opencode` |
| Grok CLI | Grok жолдору | PATH ичинде `grok`, кирген |
| Cursor CLI | Cursor жолдору | PATH ичинде `cursor-agent`, кирген |
| Antigravity CLI | Antigravity жолдору | PATH ичинде `agy`, кирген |
| Copilot CLI | Copilot жолдору | PATH ичинде `copilot`, кирген |
| Дагы 19 агент CLI | Gemini CLI, Qwen Code, Amp, Droid, Auggie, Kiro, Cline, Kilo, Vibe, Crush, Goose, Aider, Pi, Devin, CodeBuddy, Letta Code, Qoder, gptme, llm | PATH ичинде CLI, кирген. Ар бир CLI-дын документациясы боюнча жазылган жана maintainer азырынча иштетип көрө элек: [бул эмнени түшүндүрөт](lanes/README.md#what-checked-means) |
| CLI такыр жок | `api` жолу: пикир жана массалык иштер үчүн каалаган OpenAI-шайкеш endpoint (OpenRouter, DeepSeek, Groq, жергиликтүү Ollama, ...) | Python 3 жана чөйрө өзгөрмөсүндөгү ачкыч |
| Булут агенттер (экспериментал) | `mmo-cloud` аркылуу Devin, Cursor булут агенттери, Copilot агент тапшырмалары | Жеткирүүчүнүн ачкычы жана агент жете ала турган жерге жөнөтүлгөн код |

`mmo-run --list` ар бир жолду жана анын бул компьютерде даярбы-жокпу, көрсөтөт. Ар бир жол боюнча толугураак: [docs/lanes](lanes/README.md).

GPT модель id-лери: айрым ChatGPT пландарында Codex CLI азыр башка id-лерди берет (мисалы, gpt-5.6-terra же gpt-6-luna)
жана башкаларын кабыл албайт. Демейки маанилер көндүм файлдарында жазылган; ишти ал жакка багыттоодон мурун планыңыз кабыл алган
id-лерди кыскача сынап көрүңүз (CLI-ларды көрүү үчүн `mmo-preflight`, андан кийин ар бир id үчүн бир саптык `mmo-run` брифи). Караңыз: [Model ids](how-it-works.md#model-ids).

## 10 мүнөттө биринчи PR

Көбү үчүн эч кандай орнотуу керек эмес:

- **Өз тилиңиздеги README-ни окуп**, машина жазгандай угулган жерлерди оңдоңуз. 19 котормонун баарын модель жасаган ([кырымтатар тили](https://github.com/yatuk/multi-model-orchestra/issues/1), [уйгур тили](https://github.com/yatuk/multi-model-orchestra/issues/2), [түркмөн тили](https://github.com/yatuk/multi-model-orchestra/issues/3), [казак тили](https://github.com/yatuk/multi-model-orchestra/issues/4), [калгандары](https://github.com/yatuk/multi-model-orchestra/issues/5)).
- **CLI берген ката сабын чаптаңыз** (лимит, мөөнөтү бүткөн кирүү, белгисиз модель), runner аны айырмалай алсын ([#10](https://github.com/yatuk/multi-model-orchestra/issues/10)).
- **Тесттерди macOS же Linux-та иштетип**, эмне бузулганын жазыңыз ([#8](https://github.com/yatuk/multi-model-orchestra/issues/8)).
- **Өзүңүз колдонгон CLI үчүн жол кошуңуз** ([Gemini CLI](https://github.com/yatuk/multi-model-orchestra/issues/6), [Aider](https://github.com/yatuk/multi-model-orchestra/issues/7)), же [кийинкисине добуш бериңиз](https://github.com/yatuk/multi-model-orchestra/discussions/12).

Баары: [good first issues](https://github.com/yatuk/multi-model-orchestra/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22). Өз ишиңизди кантип багыттаганыңызды [Show your routing setup](https://github.com/yatuk/multi-model-orchestra/discussions/11) бөлүмүндө бөлүшсөңүз болот. Караңыз: [CONTRIBUTING](../CONTRIBUTING.md).

## Дагы

Төмөнкү документтер англис тилинде (акыркысынан башка).

- [How it works](how-it-works.md): багыттоо таблицасы, иштеткич, абал коддору, жолду текшерүү, коопсуздук модели, кеңеш (council).
- [Lanes](lanes/README.md): ар бир жол, ал канчалык текшерилгени жана жаңысын кантип кошуу керектиги.
- [otomode](otomode.md): сиз жок кезде көзөмөлсүз иштетүүлөр.
- [Benchmark](benchmark.md): жолдордун бенчмаркы жана A/B тести, экөөнү кантип иштетүү керектиги менен.
- [Cost](cost.md): чыгымдын сегиз тутканы жана ар бирин камсыз кылган же өлчөгөн буйруктар.
- [FAQ](faq.md): окшош долбоорлор менен салыштырууну кошо алганда.
- [Failures seen](failures.md): ар бири кандай көрүнөрү жана аны эмне оңдогону.
- Түрк тилиндеги макала: [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), кымбат негизги цикл моделин дирижёр катары колдонуу жана аны көзөмөлсүз иштөөгө калтыруу жөнүндө.

## Түзүлүшү

```
skills/
  orchestra/   SKILL.md, lanes.md, templates/, scripts/ (mmo-run, mmo-check, mmo-council, mmo-score,
               mmo-cloud, mmo-preflight, providers/ with one file per lane)
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/  cloud-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, lanes/, otomode, benchmark, faq, translations
```

## Лицензия

MIT, караңыз: [LICENSE](../LICENSE). README сүрөтү Codex CLI аркылуу gpt-image-2 менен түзүлгөн.
