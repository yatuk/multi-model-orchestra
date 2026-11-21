<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="multi-model-orchestra логотипі: қызыл көбелек галстук таққан, таяқшасын көтерген мультфильм дирижері">
</p>

<h1 align="center">multi-model-orchestra</h1>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · Қазақша · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Бір қымбат модель дирижерлық етсін, арзанырақ модельдер ойнасын, әр жауап қолданылмас бұрын тексерілсін.</b><br>
Claude Code (немесе <code>SKILL.md</code> файлдарын оқитын кез келген агент) үшін жұмысты Claude Opus, Sonnet және Haiku, OpenAI GPT, Kimi және DeepSeek модельдеріне тапсыратын дағдылар (skills).<br>
Негізгі агент жоспарлайды, брифтерді жазады және тексереді; жұмысты басқа модельдер атқарады, ал олар қайтарған ештеңеге тексеруден өтпейінше сенім артылмайды.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="MIT лицензиясы"></a>
  <img src="https://img.shields.io/badge/models-Claude%20·%20GPT%20·%20Kimi%20·%20DeepSeek-2563EB" alt="Claude, GPT, Kimi және DeepSeek жолдары">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="bash-та жұмыс істейді, Windows-та Git Bash">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="GitHub жұлдыздары"></a>
</p>

<p align="center"><b><a href="#жылдам-бастау">Орнату</a></b> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">Сұрақ-жауап</a></p>

<p align="center">
  <img src="../assets/orchestra-comic.png" alt="Дирижер қатені модельге береді, diff сұрайды және анонимді кеңес шақырады" width="860">
  <br>
  <sub>Дирижер партияларды таратады, diff сұрайды, ал жауап пайымдауды қажет еткенде анонимді кеңес (council) шақырады.</sub>
</p>

<table>
  <tr>
    <td width="25%" valign="top">
      <b>Бағыттау</b><br>
      Әр жұмыс қиындығына қарай өз тексеруінен өте алатын ең арзан деңгейге жіберіледі. Жол (lane) жоғары деңгейге болжаммен емес, тек тексеруден өтпей қалғаннан кейін ғана көтеріледі.
    </td>
    <td width="25%" valign="top">
      <b>Бриф</b><br>
      Әр деңгей өзі үшін ең тиімді брифті алады: Opus-қа мақсат пен шектеулер, арзанырақ жолдарға нөмірленген қадамдар мен нақты файлдар. Жол тек брифті ғана көреді, сондықтан ол бейтаныс адамға арналып жазылады.
    </td>
    <td width="25%" valign="top">
      <b>Іске қосу</b><br>
      <code>mmo-run</code> барлық провайдерлер үшін жалғыз іске қосқыш (runner): қатаң күй кодтары бар және әр шақыруда күту уақыты шектеледі. Жазатын жолдар тек git worktree ішінде жұмыс істейді, ешқашан негізгі checkout-та емес.
    </td>
    <td width="25%" valign="top">
      <b>Тексеру</b><br>
      Тексеруді дирижердің өзі іске қосады және diff-ті толық оқиды. Жолдың «дайын» деуі нәтиже емес, жай ғана мәлімдеме.
    </td>
  </tr>
</table>

## Нақты сандар

| Не | Нәтиже | Толығырақ |
|---|---|---|
| <!-- AB-RESULTS --> A/B: orchestra дағдысы мен қарапайым "use subagents" салыстыру (`claude-fable-5-2`, әр тармаққа 2 іске қосу) | Сапасы бірдей: төрт іске қосудың бәрі 36/36 жасырын тест, көрінетін тесттер бүтін қалды (тапсырмалар жиыны сапаны ажыратуға тым оңай) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B бір іске қосудың құны | Дағды орта есеппен $1.88, екінші тармақ $3.21, шамамен 40% арзан, аралықтар қиылыспайды. Үнем ішкі агенттердің Fable-ды мұраға алмай, Sonnet-те жұмыс істеуінен келеді. Жылдамдықта ұтыс жоқ (3.2 және 3.5 мин) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B шектеулері | Бір жолдық "use Sonnet subagents" сұрауы сыналған жоқ, ол үнемнің басым бөлігін бере алуы мүмкін. `total_cost_usd` жоспар бойынша пайдалану емес, прейскурант бағасы бойынша жанама өлшем | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
| Жолдар бенчмаркі, 2026-11-21 (жасырын тесттері бар қатені түзету, нақты жауапты пайымдау, 60 жолдық жаппай белгілеу) | Kimi k3.1-pro, DeepSeek v4-pro, DeepSeek flash және gpt-5.6-terra: 6/6, 3/3, 60/60. gpt-6-luna: 6/6, 0/3, 58/60. gpt-6.1-sol және gpt-6-astra: ~6/6, ~3/3, ~60/60 (болжам: ол жоспарда ұсынылмайды, ұпайлар 2026-11-11 іске қосуынан алынған) | [benchmark.md](benchmark.md) |
| otomode, бір 5 сағаттық қараусыз іске қосу | 13 тапсырма, әрқайсысына бір коммит; апталық лимит 25%-дан 31%-ға өсті; 6 рұқсат сұрауы қабылданбай, журналға жазылды. Бұл бір іске қосу, бенчмарк емес | [otomode.md](otomode.md#one-real-run) |

> [!WARNING]
> Брифтер компьютеріңізден шығады: әр жол өз брифін сол модельдің жеткізушісіне жібереді. Брифке ешқашан құпияларды, токендерді
> немесе жеке деректерді салмаңыз. otomode хугі рұқсат сұрауларын қабылдамайды және жою, deploy, push және жіберу командаларын бұғаттайды,
> бірақ ол үлгілерді салыстырады: бұл оқшау орта (sandbox) емес, тек қорғаныш қоршауы.

## Жылдам бастау

Мұны агентіңізге қойыңыз, дағдыларды сол орнатсын:

```text
Install multi-model-orchestra: clone https://github.com/yatuk/multi-model-orchestra,
run ./install.sh --link in it, then run ~/.claude/skills/orchestra/scripts/mmo-preflight
and tell me which lanes are ready.
```

Немесе өзіңіз орнатыңыз. bash, git, `timeout` және Python 3 қажет; Windows-та Git Bash пайдаланыңыз.

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link          # into ~/.claude/skills; --dir PATH for a project
~/.claude/skills/orchestra/scripts/mmo-preflight
```

`mmo-preflight` ешқашан модельді шақырмайды. Ол осы компьютерде қандай жолдар бар екенін көрсетеді, сондықтан дирижер жоқтарын айналып өтеді.
otomode үшін оның хугін тіркеу мақсатында бір рет `python ~/.claude/skills/otomode/scripts/otomode.py install` іске қосыңыз.

Содан кейін, мысалы, былай сұраңыз:

- "`internal/auth` ішіндегі құлаған тесттерді түзет. orchestra дағдысын ұстан."
- "Біріктірмес бұрын осы көшіру (migration) жоспары бойынша GPT-ден екінші пікір ал."
- "Кеңестен сұра: бұл сервисті бөлеміз бе, әлде бір процесс қалдырамыз ба?"
- "otomode 6h: осы төрт тапсырма, әрқайсысы `go test ./...` арқылы тексерілсін."

## Қандай құралдармен жұмыс істейді

| Құрал | Не үшін | Не қажет |
|---|---|---|
| Claude Code | Дағдылар және ішкі агенттер ретінде Claude Opus / Sonnet / Haiku деңгейлері | Дағдылар `~/.claude/skills` (немесе жобаның `.claude/skills`) ішіне орнатылған; басқа ештеңе керек емес |
| Codex CLI | GPT жолдары | PATH ішінде `codex`, ChatGPT арқылы кірілген |
| Kimi Code CLI | Kimi және DeepSeek жолдары | PATH ішінде `kimi`, кірілген; DeepSeek үшін Kimi Code-тың `config.toml` файлында `deepseek/*` моделі |

GPT модель id-лері: кейбір ChatGPT жоспарларында Codex CLI енді басқа id-лерді ұсынады (мысалы, gpt-5.6-terra немесе gpt-6-luna)
және басқаларын қабылдамайды. Әдепкі мәндер дағды файлдарында көрсетілген; жұмысты сонда бағыттамас бұрын жоспарыңыз қабылдайтын
id-лерді қысқаша сынап көріңіз (CLI-ларды көру үшін `mmo-preflight`, содан кейін әр id үшін бір жолдық `mmo-run` брифі). Қараңыз: [Model ids](how-it-works.md#model-ids).

## Толығырақ

Төмендегі құжаттар ағылшын тілінде (соңғысынан басқа).

- [How it works](how-it-works.md): бағыттау кестесі, іске қосқыш, күй кодтары, қауіпсіздік моделі, кеңес (council).
- [otomode](otomode.md): сіз жоқ кезде қараусыз іске қосулар.
- [Benchmark](benchmark.md): жолдар бенчмаркі және A/B тесті, екеуін қалай іске қосу керектігімен бірге.
- [FAQ](faq.md): ұқсас жобалармен салыстыруды қоса алғанда.
- Түрік тіліндегі мақала: [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), қымбат негізгі цикл моделін дирижер ретінде қолдану және оны қараусыз жұмыс істеуге қалдыру туралы.

## Құрылымы

```
skills/
  orchestra/   SKILL.md, scripts/ (mmo-run, mmo-council, mmo-preflight, mmo_extract.py), templates/
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, otomode, benchmark, faq, translations
```

## Лицензия

MIT, қараңыз: [LICENSE](../LICENSE). README суреті Codex CLI арқылы gpt-image-2 көмегімен жасалған.
