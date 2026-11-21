<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="multi-model-orchestra logotipi: qızıl kelebek qalstuk taqqan, tayaqçığını kötergen multfilm dirijeri">
</p>

<h1 align="center">multi-model-orchestra</h1>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · Qırımtatarca · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Bir paalı model dirijerlik etsin, ucuzraq modeller çalsın, er bir cevap qullanılmazdan evel teşkerilsin.</b><br>
Claude Code (ya da <code>SKILL.md</code> fayllarını oquğan er angi agent) içün işni Claude Opus, Sonnet ve Haiku'ğa, OpenAI GPT'ge, Kimi'ge ve DeepSeek'ke bergen skill'ler.<br>
Esas agent planlay, brief'lerni yaza ve közden keçire; işni diger modeller yapa, olarnıñ qaytarğan iç bir şeyine teşkerüvden keçmegence işanılmay.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="MIT litsenziyası"></a>
  <img src="https://img.shields.io/badge/models-Claude%20·%20GPT%20·%20Kimi%20·%20DeepSeek-2563EB" alt="Claude, GPT, Kimi ve DeepSeek lane'leri">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="bash üzerinde çalışa, Windows'ta Git Bash">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="GitHub yıldızları"></a>
</p>

<p align="center"><b><a href="#tez-başlanğıç">Qurulım</a></b> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">Sual-cevap</a></p>

<p align="center">
  <img src="../assets/orchestra-comic.png" alt="Dirijer bir hatanı modelge bere, diff'ni soray ve kör bir council toplay" width="860">
  <br>
  <sub>Dirijer partiyalarnı tağıta, diff'ni soray, cevap bir qıymet kesüv meselesi olsa, kör bir council toplay.</sub>
</p>

<table>
  <tr>
    <td width="25%" valign="top">
      <b>Yönelt</b><br>
      Er iş, zorluğına köre, öz teşkerüvinden keçip olğan eñ ucuz seviyege yiberile. Bir lane yuqarı seviyege tahmin ile degil, ancaq teşkerüvden keçalmağan soñ köterile.
    </td>
    <td width="25%" valign="top">
      <b>Brief</b><br>
      Er seviye özüne eñ yahşı kelgen brief'ni ala: Opus'qa maqsat ve sıñırlamalar, ucuzraq lane'lerge nomeralanğan adımlar ve tam fayl yolları. Lane ancaq brief'ni köre, bunıñ içün brief yabancı bir adamğa yazıla.
    </td>
    <td width="25%" valign="top">
      <b>Başlat</b><br>
      <code>mmo-run</code> er bir tedarikçi içün yekâne runner: qatı durum kodları ve er çağırışta vaqıt sıñırı bar. Yazğan lane'ler ancaq git worktree içinde çalışa, siziñ esas checkout'ıñızda asla.
    </td>
    <td width="25%" valign="top">
      <b>Teşker</b><br>
      Teşkerüvni dirijerniñ özü başlata ve diff'niñ episini oquy. Lane'niñ "bitti" degeni bir iddia, netice degil.
    </td>
  </tr>
</table>

## Aqiqiy raqamlar

| Ne | Netice | Tafsilât |
|---|---|---|
| <!-- AB-RESULTS --> A/B: orchestra skill'i ile sade "use subagents" arasında qıyaslama (`claude-fable-5-2`, er qolğa 2 başlatuv) | Keyfiyet aynı: dört başlatuvnıñ episi 36/36 gizli test, körüngen testlerge toqunılmadı (vazife cıyıntığı keyfiyetni ayırmaq içün pek qolay) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B bir başlatuvnıñ fiyatı | Skill ortalama $1.88, qarşı qol $3.21, taqriben 40% az, aralıqlar üst-üste kelmey. Tasarruf alt agentlerniñ Fable'nı miras almaq yerine Sonnet'te çalışmasından kele. Tezlikte qazanç yoq (3.2 ve 3.5 daqqa) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B sıñırları | Bir satırlıq "use Sonnet subagents" ricası sınalmadı ve tasarrufnıñ çoqusını yaqalap olur. `total_cost_usd` liste fiyatından bir vekil ölçü, plan qullanımı degil | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
| Lane benchmark'ı, 2026-11-21 (gizli testli hata tüzetüv, kesik cevaplı tüşünüv, 60 satırlıq toplu etiketlev) | Kimi k3.1-pro, DeepSeek v4-pro, DeepSeek flash ve gpt-5.6-terra: 6/6, 3/3, 60/60. gpt-6-luna: 6/6, 0/3, 58/60. gpt-6.1-sol ve gpt-6-astra: ~6/6, ~3/3, ~60/60 (taqriben: o planda berilmey, ballar 2026-11-11 başlatuvından) | [benchmark.md](benchmark.md) |
| otomode, 5 saatlıq tek nezaretsiz başlatuv | 13 vazife, er birine bir commit; aftalıq limit 25%-ten 31%-ke çıqtı; 6 izin ricası red etildi ve qayd etildi. Bir başlatuv, benchmark degil | [otomode.md](otomode.md#one-real-run) |

> [!WARNING]
> Brief'ler kompyuteriñizden çıqa: er lane öz brief'ini o modelniñ tedarikçisine yibere. Brief'ke asla sır, token
> ya da şahsiy malümat qoymañız. otomode'nıñ hook'u izin ricalarını red ete ve silüv, deploy, push ve yiberüv emirlerini
> qabul etmey, amma o qalıplarnı tutuştıra: bu bir qorçalav parmaqlığı, sandbox degil.

## Tez başlanğıç

Bunı agentiñizge yapıştırıñız, skill'lerni o qursun:

```text
Install multi-model-orchestra: clone https://github.com/yatuk/multi-model-orchestra,
run ./install.sh --link in it, then run ~/.claude/skills/orchestra/scripts/mmo-preflight
and tell me which lanes are ready.
```

Ya da özüñiz quruñız. bash, git, `timeout` ve Python 3 kerek; Windows'ta Git Bash qullanıñız.

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link          # into ~/.claude/skills; --dir PATH for a project
~/.claude/skills/orchestra/scripts/mmo-preflight
```

`mmo-preflight` iç bir modelni çağırmay. O bu kompyuterde angi lane'ler bar olğanını söyley, bunıñ içün dirijer eksik olğanlarnı aylanıp keçe.
otomode içün onıñ hook'unı qayd etmek maqsadınen bir kere `python ~/.claude/skills/otomode/scripts/otomode.py install` başlatıñız.

Soñ, meselâ, şunı rica etiñiz:

- "`internal/auth` içindeki bozuq testlerni tüzet. orchestra skill'ine riayet et."
- "Bu migration planını birleştirmezden evel GPT'den ekinci fikir al."
- "Council'ge sora: bu servisni bölemizmi, yoqsa bir protsess olaraq qaldıramızmı?"
- "otomode 6h: bu dört vazife, er biri `go test ./...` ile teşkerilsin."

## Birlikte çalışqan aletler

| Alet | Ne içün | Ne kerek |
|---|---|---|
| Claude Code | Skill'ler ve alt agent olaraq Claude Opus / Sonnet / Haiku seviyeleri | Skill'lerniñ `~/.claude/skills` (ya da bir proektniñ `.claude/skills`) içine qurulması; başqa bir şey kerek degil |
| Codex CLI | GPT lane'leri | PATH'te `codex`, ChatGPT ile kirilgen |
| Kimi Code CLI | Kimi ve DeepSeek lane'leri | PATH'te `kimi`, kirilgen; DeepSeek içün Kimi Code'nıñ `config.toml` faylında bir `deepseek/*` modeli |

GPT model id'leri: bazı ChatGPT planlarında Codex CLI endi başqa id'ler bere (meselâ gpt-5.6-terra ya da gpt-6-luna)
ve digerlerini red ete. Standart qıymetler skill fayllarında yazılı; işni oraya yöneltmezden evel planıñız qabul etken
id'lerni qısqa sınap baqıñız (CLI'larnı körmek içün `mmo-preflight`, soñ er id içün bir satırlıq `mmo-run` brief'i). Baqıñız: [Model ids](how-it-works.md#model-ids).

## Daa ziyade

Aşağıdaki vesiqalar İngliz tilinde (soñkisinden ğayrı).

- [How it works](how-it-works.md): yönelüv cedveli, runner, durum kodları, telükesizlik modeli, council.
- [otomode](otomode.md): siz yoq ekende nezaretsiz başlatuvlar.
- [Benchmark](benchmark.md): lane benchmark'ı ve A/B testi, ekisini nasıl başlatmaq kerek olğanınen birlikte.
- [FAQ](faq.md): oşağan proektlernen qıyaslamanı da öz içine ala.
- Türk tilinde maqale: [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), paalı bir esas döngü modelini dirijer olaraq qullanmaq ve onı nezaretsiz çalışmağa taşlamaq aqqında.

## Fayllar tertibi

```
skills/
  orchestra/   SKILL.md, scripts/ (mmo-run, mmo-council, mmo-preflight, mmo_extract.py), templates/
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, otomode, benchmark, faq, translations
```

## Litsenziya

MIT, baqıñız: [LICENSE](../LICENSE). README resimi Codex CLI vastasınen gpt-image-2 ile yapıldı.
