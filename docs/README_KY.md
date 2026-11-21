<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="multi-model-orchestra логотиби: кызыл көпөлөк галстук тагынган, таякчасын көтөргөн мультфильм дирижёру">
</p>

<h1 align="center">multi-model-orchestra</h1>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · Кыргызча · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Бир кымбат модель дирижёрлук кылсын, арзаныраак моделдер ойносун, ар бир жооп колдонулганга чейин текшерилсин.</b><br>
Claude Code (же <code>SKILL.md</code> файлдарын окуган каалаган агент) үчүн ишти Claude Opus, Sonnet жана Haiku, OpenAI GPT, Kimi жана DeepSeek моделдерине тапшырган көндүмдөр (skills).<br>
Негизги агент пландайт, брифтерди жазат жана карап чыгат; ишти башка моделдер аткарат, ал эми алар кайтарган эч нерсеге текшерүүдөн өтмөйүнчө ишенилбейт.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="MIT лицензиясы"></a>
  <img src="https://img.shields.io/badge/models-Claude%20·%20GPT%20·%20Kimi%20·%20DeepSeek-2563EB" alt="Claude, GPT, Kimi жана DeepSeek жолдору">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="bash менен иштейт, Windows-то Git Bash">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="GitHub жылдыздары"></a>
</p>

<p align="center"><b><a href="#тез-баштоо">Орнотуу</a></b> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">Суроо-жооп</a></p>

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
      <code>mmo-run</code> бардык провайдерлер үчүн жалгыз иштеткич (runner): катуу абал коддору бар жана ар бир чакырууда күтүү убактысы чектелет. Жазуучу жолдор git worktree ичинде гана иштейт, эч качан негизги checkout-уңузда эмес.
    </td>
    <td width="25%" valign="top">
      <b>Текшерүү</b><br>
      Текшерүүнү дирижёрдун өзү иштетет жана diff-ти толук окуйт. Жолдун «бүттү» дегени натыйжа эмес, жөн гана ырастоо.
    </td>
  </tr>
</table>

## Чыныгы сандар

| Эмне | Натыйжа | Толугураак |
|---|---|---|
| <!-- AB-RESULTS --> A/B: orchestra көндүмү менен жөнөкөй "use subagents" салыштыруу (`claude-fable-5-2`, ар бир тарапка 2 иштетүү) | Сапаты бирдей: төрт иштетүүнүн баары 36/36 жашыруун тест, көрүнгөн тесттерге тийилген жок (тапшырмалар топтому сапатты ажыратууга өтө жеңил) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B бир иштетүүнүн баасы | Көндүм орточо $1.88, экинчи тарап $3.21, болжол менен 40% арзан, диапазондор кесилишпейт. Үнөмдөө ички агенттердин Fable-ды мурастабай, Sonnet-те иштешинен келет. Ылдамдыкта утуш жок (3.2 жана 3.5 мүн) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B чектөөлөрү | Бир саптык "use Sonnet subagents" сурамы сыналган эмес, ал үнөмдүн көпчүлүгүн бере алышы мүмкүн. `total_cost_usd` пландын колдонулушу эмес, прейскуранттык баа боюнча кыйыр көрсөткүч | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
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
- "otomode 6h: бул төрт тапшырма, ар бири `go test ./...` менен текшерилсин."

## Кайсы куралдар менен иштейт

| Курал | Эмне үчүн | Эмне керек |
|---|---|---|
| Claude Code | Көндүмдөр жана ички агенттер катары Claude Opus / Sonnet / Haiku деңгээлдери | Көндүмдөр `~/.claude/skills` (же долбоордун `.claude/skills`) ичине орнотулган; башка эч нерсе керек эмес |
| Codex CLI | GPT жолдору | PATH ичинде `codex`, ChatGPT аркылуу кирген |
| Kimi Code CLI | Kimi жана DeepSeek жолдору | PATH ичинде `kimi`, кирген; DeepSeek үчүн Kimi Code-дун `config.toml` файлында `deepseek/*` модели |

GPT модель id-лери: айрым ChatGPT пландарында Codex CLI азыр башка id-лерди берет (мисалы, gpt-5.6-terra же gpt-6-luna)
жана башкаларын кабыл албайт. Демейки маанилер көндүм файлдарында жазылган; ишти ал жакка багыттоодон мурун планыңыз кабыл алган
id-лерди кыскача сынап көрүңүз (CLI-ларды көрүү үчүн `mmo-preflight`, андан кийин ар бир id үчүн бир саптык `mmo-run` брифи). Караңыз: [Model ids](how-it-works.md#model-ids).

## Дагы

Төмөнкү документтер англис тилинде (акыркысынан башка).

- [How it works](how-it-works.md): багыттоо таблицасы, иштеткич, абал коддору, коопсуздук модели, кеңеш (council).
- [otomode](otomode.md): сиз жок кезде көзөмөлсүз иштетүүлөр.
- [Benchmark](benchmark.md): жолдордун бенчмаркы жана A/B тести, экөөнү кантип иштетүү керектиги менен.
- [FAQ](faq.md): окшош долбоорлор менен салыштырууну кошо алганда.
- Түрк тилиндеги макала: [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), кымбат негизги цикл моделин дирижёр катары колдонуу жана аны көзөмөлсүз иштөөгө калтыруу жөнүндө.

## Түзүлүшү

```
skills/
  orchestra/   SKILL.md, scripts/ (mmo-run, mmo-council, mmo-preflight, mmo_extract.py), templates/
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, otomode, benchmark, faq, translations
```

## Лицензия

MIT, караңыз: [LICENSE](../LICENSE). README сүрөтү Codex CLI аркылуу gpt-image-2 менен түзүлгөн.
