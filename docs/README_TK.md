<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="multi-model-orchestra logotipi: gyzyl kebelek galstuklı, dirižýor taýagyny galdyran multfilm dirižýory">
</p>

<h1 align="center">multi-model-orchestra</h1>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · Türkmençe · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Bir gymmat model dirižýorlyk etsin, arzan modeller çalsyn, her jogap ulanylmazdan öň barlansyn.</b><br>
Claude Code (ýa-da <code>SKILL.md</code> faýllaryny okaýan islendik gural) üçin skill-ler: işi Claude Opus, Sonnet we Haiku-a, OpenAI GPT-ä, Kimi-ä we DeepSeek-e tabşyrýar.<br>
Esasy agent meýilleşdirýär, brief-leri ýazýar we gözden geçirýär; işi beýleki modeller edýär we olaryň gaýtaran zadyna barlagdan geçmänkä ynanylmaýar.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="MIT ygtyýarnamasy"></a>
  <img src="https://img.shields.io/badge/models-Claude%20·%20GPT%20·%20Kimi%20·%20DeepSeek-2563EB" alt="Claude, GPT, Kimi we DeepSeek lane-leri">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="bash-da işleýär, Windows-da Git Bash">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="GitHub ýyldyzlary"></a>
</p>

<p align="center"><b><a href="#çalt-başlangyç">Gurnama</a></b> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

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
      <code>mmo-run</code> ähli üpjün edijiler üçin ýeke-täk runner-dir: berk ýagdaý kodlary we her çagyrylyşda wagt çägi bar. Ýazýan lane-ler diňe git worktree-de işleýär, esasy checkout-da hiç haçan.
    </td>
    <td width="25%" valign="top">
      <b>Barla</b><br>
      Barlagy dirižýor özi işledýär we diff-iň hemmesini okaýar. Lane-iň "taýýar" diýmegi dawadyr, netije däl.
    </td>
  </tr>
</table>

## Hakyky sanlar

| Näme | Netije | Jikme-jiklik |
|---|---|---|
| <!-- AB-RESULTS --> A/B: orchestra skill-i bilen ýönekeý "use subagents" deňeşdirmesi (`claude-fable-5-2`, her golda 2 işlediliş) | Hil birmeňzeş: dört işlediliş hem 36/36 gizlin test, görünýän testlere degilmedi (meseleler toplumy hili tapawutlandyrmak üçin gaty ýeňil) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B her işledilişiň bahasy | Skill ortaça $1.88, deňeşdirme goly $3.21; takmynan 40% az, aralyklar çakyşmaýar. Tygşytlylyk sub-agent-leriň Fable-i miras almagyň deregine Sonnet-de işlemeginden gelýär. Tizlik artykmaçlygy ýok (3.2 min garşy 3.5 min) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B çäkleri | Bir setirlik "use Sonnet subagents" haýyşy synalmady we tygşytlylygyň köpüsini berip biler. `total_cost_usd` sanaw bahasyna esaslanan çaklama ölçegidir, tarif ulanylyşy däl | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
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
- "otomode 6h: şu dört tabşyryk, her biri `go test ./...` bilen barlansyn."

## Bilelikde işleýän gurallary

| Gural | Näme üçin | Gerek bolanlar |
|---|---|---|
| Claude Code | Skill-ler we sub-agent hökmünde Claude Opus / Sonnet / Haiku basgançaklary | Skill-leriň `~/.claude/skills` (ýa-da taslamanyň `.claude/skills`) bukjasyna gurnalmagy; başga hiç zat |
| Codex CLI | GPT lane-leri | PATH-da `codex`, ChatGPT bilen girilen |
| Kimi Code CLI | Kimi we DeepSeek lane-leri | PATH-da `kimi`, girilen; DeepSeek üçin Kimi Code-yň `config.toml` faýlynda `deepseek/*` modeli |

GPT model id-leri: käbir ChatGPT tariflerinde Codex CLI indi başga id-leri hödürleýär (mysal üçin gpt-5.6-terra ýa-da gpt-6-luna)
we beýlekileri ret edýär. Deslapky bahalar skill faýllarynda ýazylan; işi ol ýere ugrukdyrmazdan öň tarifiňiziň kabul
edýän id-lerini synagdan geçiriň (CLI-lary görmek üçin `mmo-preflight`, soň her id üçin bir setirlik `mmo-run` brief-i).
Seret: [Model ids](how-it-works.md#model-ids).

## Has köp

Aşakdaky resminamalar iňlis dilinde.

- [How it works](how-it-works.md): ugrukdyrma tablisasy, runner, ýagdaý kodlary, howpsuzlyk modeli, council.
- [otomode](otomode.md): siz ýokka gözegçiliksiz işledilişler.
- [Benchmark](benchmark.md): lane benchmark-y we A/B synagy, ikisiniň hem nädip işledilýändigi bilen.
- [FAQ](faq.md): meňzeş taslamalar bilen deňeşdirme goşmak bilen.
- Makala (türkçe): [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), gymmat esasy aýlaw modelini dirižýor hökmünde ulanmak we ony gözegçiliksiz işe goýbermek barada.

## Bukja gurluşy

```
skills/
  orchestra/   SKILL.md, scripts/ (mmo-run, mmo-council, mmo-preflight, mmo_extract.py), templates/
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, otomode, benchmark, faq, translations
```

## Ygtyýarnama

MIT, seret: [LICENSE](../LICENSE). README suraty Codex CLI arkaly gpt-image-2 bilen döredildi.
