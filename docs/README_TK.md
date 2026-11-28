<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="multi-model-orchestra logotipi: gyzyl kebelek galstuklı, dirižýor taýagyny galdyran multfilm dirižýory">
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
  <sub>Modelleri lane arkaly işledilen we <a href="benchmark.md">benchmark</a>-da baha berlen öndürijiler. Atlar we logotipler eýelerine degişlidir; hiç hili makullama göz öňünde tutulmaýar.</sub>
</p>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · Türkmençe · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Bir gymmat model dirižýorlyk etsin, arzan modeller çalsyn, her jogap ulanylmazdan öň barlansyn.</b><br>
Claude Code (ýa-da <code>SKILL.md</code> faýllaryny okaýan islendik gural) üçin skill-ler: işi Claude Opus, Sonnet we Haiku-a, OpenAI GPT-ä, Kimi-ä, DeepSeek-e we eliňizdäki islendik agent CLI-a ýa-da API-a tabşyrýar: OpenCode, Grok, Gemini, Qwen, Cursor, Copilot, OpenRouter, ýerli modeller we başgalar.<br>
Esasy agent meýilleşdirýär, brief-leri ýazýar we gözden geçirýär; işi beýleki modeller edýär we olaryň gaýtaran zadyna barlagdan geçmänkä ynanylmaýar.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="MIT ygtyýarnamasy"></a>
  <img src="https://img.shields.io/badge/lanes-32%20CLIs%20and%20APIs-2563EB" alt="32 lane: agent CLI-lary we API-ler">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="bash-da işleýär, Windows-da Git Bash">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="GitHub ýyldyzlary"></a>
</p>

<p align="center"><b><a href="#çalt-başlangyç">Gurnama</a></b> · <a href="lanes/README.md">Lanes</a> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

<p align="center">
  <img src="../assets/orchestra-comic.png" alt="Dirižýor bir ýalňyşlygy modele berýär, diff soraýar we kör council çagyrýar" width="860">
  <br>
  <sub>Dirižýor partiýalary paýlaýar, diff soraýar we jogap pikir ýöretmeli mesele bolanda kör council çagyrýar.</sub>
</p>

<table>
  <tr>
    <td width="25%" valign="top">
      <b>Ugrukdyr</b><br>
      Her iş kynlygyna görä barlagdan geçip biljek iň arzan basgançaga gidýär. Lane diňe barlagdan geçmänsoň ýokary çykýar, duýgy bilen däl.
    </td>
    <td width="25%" valign="top">
      <b>Brief</b><br>
      Her basgançak özüne iň laýyk brief-i alýar: Opus üçin maksat we çäklendirmeler, arzan lane-ler üçin belgilenen ädimler we takyk faýllar. Lane diňe brief-i görýär, şonuň üçin brief nätanyş adam üçin ýazylýar.
    </td>
    <td width="25%" valign="top">
      <b>Işlet</b><br>
      <code>mmo-run</code> ähli lane-ler üçin ýeke-täk runner-dir: berk ýagdaý kodlary we her çagyrylyşda wagt çägi bar. Ýazýan lane-ler diňe siziň branch-yňyzy öz içine alýan git worktree-de işleýär, esasy checkout-da hiç haçan.
    </td>
    <td width="25%" valign="top">
      <b>Barla</b><br>
      Barlagy dirižýor özi <code>mmo-check</code> bilen işledýär we diff-iň hemmesini okaýar: degilen testler, brief-den daşky faýllar we üýtgetmesiz hem geçip biljek barlag bellenýär. Lane-iň "taýýar" diýmegi dawadyr, netije däl.
    </td>
  </tr>
</table>

## Hakyky sanlar

| Näme | Netije | Jikme-jiklik |
|---|---|---|
| <!-- AB-RESULTS --> A/B: orchestra skill-i bilen ýönekeý "use subagents" deňeşdirmesi (`claude-fable-5-2`, her golda 2 işlediliş) | Hil birmeňzeş: dört işlediliş hem 36/36 gizlin test, görünýän testlere degilmedi (meseleler toplumy hili tapawutlandyrmak üçin gaty ýeňil) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B her işledilişiň bahasy | Skill ortaça $1.88, deňeşdirme goly $3.21; takmynan 40% az, aralyklar çakyşmaýar. Tygşytlylyk sub-agent-leriň Fable-i miras almagyň deregine Sonnet-de işlemeginden gelýär. Tizlik artykmaçlygy ýok (3.2 min garşy 3.5 min) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B çäkleri | Bir setirlik "use Sonnet subagents" haýyşy (2026-11-28, 2 işlediliş, 36/36, ortaça $1.49, sub-agent-ler Sonnet-de) tygşytlylygyň hemmesini skill-siz berdi; A we B has ozalky günde işledildi, şonuň üçin bu gözegçilikli deňeşdirme däl. `total_cost_usd` sanaw bahasyna esaslanan çaklama ölçegidir, tarif ulanylyşy däl | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
| Lane benchmark-y, 2026-11-21 (gizlin testli ýalňyşlygy düzetmek, takyk jogaply pikir ýöretmek, 60 setirlik köpçülikleýin belgilemek) | Kimi k3.1-pro, DeepSeek v4-pro, DeepSeek flash we gpt-5.6-terra: 6/6, 3/3, 60/60. gpt-6-luna: 6/6, 0/3, 58/60. gpt-6.1-sol we gpt-6-astra: ~6/6, ~3/3, ~60/60 (çak edilen: şol tarifde hödürlenmeýär, utgalar 2026-11-11 işledilişinden) | [benchmark.md](benchmark.md) |
| otomode, 5 sagatlyk gözegçiliksiz bir işlediliş | 13 tabşyryk, her biri bir commit; hepdelik çäk 25%-den 31%-e çykdy; 6 haýyş ret edildi we ýazga alyndy. Bir işledilişdir, benchmark däl | [otomode.md](otomode.md#one-real-run) |

> [!WARNING]
> Brief-ler kompýuteriňizden çykýar: her lane öz brief-ini şol modeliň öndürijisine iberýär. Brief-e hiç haçan syr, token
> ýa-da şahsy maglumat goýmaň. otomode-yň hook-y haýyşlary ret edýär we pozmak, deploy, push we ibermek buýruklaryny
> yzyna gaýtarýar, emma nusga deňeşdirýär: ol gorag çarçuwasydyr, sandbox däl.

## Çalt başlangyç

Muny agent-iňize ýelmäň, skill-leri ol gurnasyn:

```text
Install multi-model-orchestra: clone https://github.com/yatuk/multi-model-orchestra,
run ./install.sh --link in it, then run ~/.claude/skills/orchestra/scripts/mmo-preflight
and tell me which lanes are ready.
```

Ýa-da özüňiz gurnaň. bash, git, `timeout` we Python 3 gerek; Windows-da Git Bash ulanyň.

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link          # into ~/.claude/skills; --dir PATH for a project
~/.claude/skills/orchestra/scripts/mmo-preflight
```

`mmo-preflight` hiç bir modeli çagyrmaýar. Ol bu kompýuterde haýsy lane-leriň bardygyny aýdýar; dirižýor ýetmeýänleriň daşyndan aýlanyp ugrukdyrýar.
otomode üçin hook-yny hasaba almak maksady bilen bir gezek `python ~/.claude/skills/otomode/scripts/otomode.py install` işlediň.

Soň mysal üçin şulary haýyş ediň:

- "`internal/auth` içindäki döwük testleri düzet. orchestra skill-ini yzarla."
- "Birleşdirmezden öň bu migrasiýa meýilnamasy barada GPT-den ikinji pikir al."
- "Council-dan sora: bu serwisi böleliňmi, ýa-da bir proses galsynmy?"
- "Bu migrasiýany özüň et; başlamazdan öň we taýýar diýmezden öň GPT bilen advisor skill-ini ulan."
- "otomode 6h: şu dört tabşyryk, her biri `go test ./...` bilen barlansyn."

## Bilelikde işleýän gurallary

| Gural | Näme üçin | Gerek bolanlar |
|---|---|---|
| Claude Code | Skill-ler we sub-agent hökmünde Claude Opus / Sonnet / Haiku basgançaklary | Skill-leriň `~/.claude/skills` (ýa-da taslamanyň `.claude/skills`) bukjasyna gurnalmagy; başga hiç zat |
| Codex CLI | GPT lane-leri | PATH-da `codex`, ChatGPT bilen girilen |
| Kimi Code CLI | Kimi we DeepSeek lane-leri | PATH-da `kimi`, girilen; DeepSeek üçin Kimi Code-yň `config.toml` faýlynda `deepseek/*` modeli |
| OpenCode | Girilen islendik üpjün ediji (DeepSeek, OpenRouter, Ollama, öz mugt modelleri) | PATH-da `opencode` |
| Grok CLI | Grok lane-leri | PATH-da `grok`, girilen |
| Cursor CLI | Cursor lane-leri | PATH-da `cursor-agent`, girilen |
| Antigravity CLI | Antigravity lane-leri | PATH-da `agy`, girilen |
| Copilot CLI | Copilot lane-leri | PATH-da `copilot`, girilen |
| 19 sany başga agent CLI | Gemini CLI, Qwen Code, Amp, Droid, Auggie, Kiro, Cline, Kilo, Vibe, Crush, Goose, Aider, Pi, Devin, CodeBuddy, Letta Code, Qoder, gptme, llm | PATH-da CLI, girilen. Her CLI-yň resminamalaryna görä ýazylan we maintainer tarapyndan entek işledilmedik: [munuň manysy](lanes/README.md#what-checked-means) |
| Hiç hili CLI ýok | `api` lane-i: pikir we köpçülikleýin işler üçin islendik OpenAI bilen gabat gelýän endpoint (OpenRouter, DeepSeek, Groq, ýerli Ollama, ...) | Python 3 we töwerek üýtgeýjisindäki açar |
| Bulut agentleri (synag) | `mmo-cloud` arkaly Devin, Cursor bulut agentleri, Copilot agent tabşyryklary | Öndürijiniň açary we agentiň ýetip biljek ýerine iberilen kod |

`mmo-run --list` her lane-i we onuň bu kompýuterde taýýardygyny ýa-da däldigini görkezýär. Lane boýunça jikme-jiklik: [docs/lanes](lanes/README.md).

GPT model id-leri: käbir ChatGPT tariflerinde Codex CLI indi başga id-leri hödürleýär (mysal üçin gpt-5.6-terra ýa-da gpt-6-luna)
we beýlekileri ret edýär. Deslapky bahalar skill faýllarynda ýazylan; işi ol ýere ugrukdyrmazdan öň tarifiňiziň kabul
edýän id-lerini synagdan geçiriň (CLI-lary görmek üçin `mmo-preflight`, soň her id üçin bir setirlik `mmo-run` brief-i).
Seret: [Model ids](how-it-works.md#model-ids).

## 10 minutda ilkinji PR

Köpüsi üçin hiç hili gurnama gerek däl:

- **Öz diliňizdäki README-ni okaň** we maşyn ýazan ýaly ýaňlanýan ýerleri düzediň. 19 terjimäniň hemmesini model etdi ([Gyrym tatarçasy](https://github.com/yatuk/multi-model-orchestra/issues/1), [Uýgurça](https://github.com/yatuk/multi-model-orchestra/issues/2), [Türkmençe](https://github.com/yatuk/multi-model-orchestra/issues/3), [Gazakça](https://github.com/yatuk/multi-model-orchestra/issues/4), [galanlary](https://github.com/yatuk/multi-model-orchestra/issues/5)).
- **CLI-yň beren ýalňyşlyk setirini ýelmäň** (çäk, möhleti geçen giriş, näbelli model), runner ony tapawutlandyryp bilsin ([#10](https://github.com/yatuk/multi-model-orchestra/issues/10)).
- **Testleri macOS ýa-da Linux-da işlediň** we nämäniň döwlendigini ýazyň ([#8](https://github.com/yatuk/multi-model-orchestra/issues/8)).
- **Ulanýan CLI-yňyz üçin lane goşuň** ([Gemini CLI](https://github.com/yatuk/multi-model-orchestra/issues/6), [Aider](https://github.com/yatuk/multi-model-orchestra/issues/7)), ýa-da [indiki üçin ses beriň](https://github.com/yatuk/multi-model-orchestra/discussions/12).

Hemmesi: [good first issues](https://github.com/yatuk/multi-model-orchestra/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22). Öz işiňizi nädip ugrukdyrýandygyňyzy [Show your routing setup](https://github.com/yatuk/multi-model-orchestra/discussions/11) bölüminde paýlaşyp bilersiňiz. Seret: [CONTRIBUTING](../CONTRIBUTING.md).

## Has köp

Aşakdaky resminamalar iňlis dilinde.

- [How it works](how-it-works.md): ugrukdyrma tablisasy, runner, ýagdaý kodlary, lane-i barlamak, howpsuzlyk modeli, council.
- [Lanes](lanes/README.md): her lane, ol nähili derejede barlanandygy we täzesini nädip goşmaly.
- [otomode](otomode.md): siz ýokka gözegçiliksiz işledilişler.
- [Benchmark](benchmark.md): lane benchmark-y we A/B synagy, ikisiniň hem nädip işledilýändigi bilen.
- [Cost](cost.md): çykdajynyň sekiz tutawajy we olaryň her birini ýerine ýetirýän ýa-da ölçeýän buýruklar.
- [FAQ](faq.md): meňzeş taslamalar bilen deňeşdirme goşmak bilen.
- [Failures seen](failures.md): olaryň her biriniň nähili görünýändigi we nämäniň düzedendigi.
- Makala (türkçe): [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), gymmat esasy aýlaw modelini dirižýor hökmünde ulanmak we ony gözegçiliksiz işe goýbermek barada.

## Bukja gurluşy

```
skills/
  orchestra/   SKILL.md, lanes.md, templates/, scripts/ (mmo-run, mmo-check, mmo-council, mmo-score,
               mmo-cloud, mmo-preflight, providers/ with one file per lane)
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/  cloud-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, lanes/, otomode, benchmark, faq, translations
```

## Ygtyýarnama

MIT, seret: [LICENSE](../LICENSE). README suraty Codex CLI arkaly gpt-image-2 bilen döredildi.
