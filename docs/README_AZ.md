<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="multi-model-orchestra loqosu: qırmızı kəpənək qalstuklu, dirijor çubuğunu qaldıran cizgi filmi dirijoru">
</p>

<h1 align="center">multi-model-orchestra</h1>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · Azərbaycanca · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Bir bahalı model dirijorluq etsin, daha ucuz modellər ifa etsin, hər cavab istifadə olunmazdan əvvəl yoxlanılsın.</b><br>
Claude Code (və ya <code>SKILL.md</code> fayllarını oxuyan istənilən alət) üçün skill-lər: işi Claude Opus, Sonnet və Haiku-ya, OpenAI GPT-yə, Kimi-yə və DeepSeek-ə həvalə edir.<br>
Əsas agent planlaşdırır, brief-ləri yazır və nəzərdən keçirir; işi digər modellər görür və onların qaytardığı heç nəyə yoxlamadan keçməyincə etibar edilmir.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="MIT lisenziyası"></a>
  <img src="https://img.shields.io/badge/models-Claude%20·%20GPT%20·%20Kimi%20·%20DeepSeek-2563EB" alt="Claude, GPT, Kimi və DeepSeek lane-ləri">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="bash üzərində işləyir, Windows-da Git Bash">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="GitHub ulduzları"></a>
</p>

<p align="center"><b><a href="#sürətli-başlanğıc">Quraşdırma</a></b> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

<p align="center">
  <img src="../assets/orchestra-comic.png" alt="Dirijor bir xətanı modelə verir, diff istəyir və kor council çağırır" width="860">
  <br>
  <sub>Dirijor partiyaları paylayır, diff istəyir və cavab mühakimə məsələsi olanda kor council çağırır.</sub>
</p>

<table>
  <tr>
    <td width="25%" valign="top">
      <b>Yönləndir</b><br>
      Hər iş çətinliyinə görə yoxlamadan keçə bilən ən ucuz pilləyə gedir. Lane yalnız yoxlamadan keçməyəndən sonra yuxarı çıxır, hiss əsasında yox.
    </td>
    <td width="25%" valign="top">
      <b>Brief</b><br>
      Hər pillə özünə ən uyğun brief-i alır: Opus üçün məqsəd və məhdudiyyətlər, daha ucuz lane-lər üçün nömrələnmiş addımlar və dəqiq fayllar. Lane yalnız brief-i görür, ona görə brief yad bir adam üçün yazılır.
    </td>
    <td width="25%" valign="top">
      <b>İşlət</b><br>
      <code>mmo-run</code> bütün provayderlər üçün yeganə runner-dir: sərt status kodları və hər çağırışda zaman aşımı var. Yazan lane-lər yalnız git worktree-də işləyir, əsas checkout-da heç vaxt.
    </td>
    <td width="25%" valign="top">
      <b>Yoxla</b><br>
      Yoxlamanı dirijor özü işlədir və diff-in hamısını oxuyur. Lane-in "bitdi" deməsi iddiadır, nəticə deyil.
    </td>
  </tr>
</table>

## Real rəqəmlər

| Nə | Nəticə | Təfərrüat |
|---|---|---|
| <!-- AB-RESULTS --> A/B: orchestra skill-i ilə sadə "use subagents" müqayisəsi (`claude-fable-5-2`, hər qolda 2 icra) | Keyfiyyət eynidir: dörd icranın hamısı 36/36 gizli test, görünən testlərə toxunulmayıb (tapşırıq toplusu keyfiyyəti ayırd etmək üçün çox asandır) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B icra başına xərc | Skill orta hesabla $1.88, müqayisə qolu $3.21; təxminən 40% az, aralıqlar üst-üstə düşmür. Qənaət sub-agent-lərin Fable-ı miras almaq əvəzinə Sonnet-də işləməsindən gəlir. Sürət qazancı yoxdur (3.2 dəq qarşı 3.5 dəq) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B məhdudiyyətləri | Bir sətirlik "use Sonnet subagents" istəyi sınanmayıb və qənaətin çoxunu verə bilər. `total_cost_usd` siyahı qiymətinə əsaslanan əvəzedici ölçüdür, plan istifadəsi deyil | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
| Lane benchmark-ı, 2026-11-21 (gizli testli xəta düzəlişi, dəqiq cavablı əsaslandırma, 60 sətirlik kütləvi etiketləmə) | Kimi k3.1-pro, DeepSeek v4-pro, DeepSeek flash və gpt-5.6-terra: 6/6, 3/3, 60/60. gpt-6-luna: 6/6, 0/3, 58/60. gpt-6.1-sol və gpt-6-astra: ~6/6, ~3/3, ~60/60 (təxmini: həmin planda təqdim olunmur, xallar 2026-11-11 icrasından) | [benchmark.md](benchmark.md) |
| otomode, 5 saatlıq bir nəzarətsiz icra | 13 tapşırıq, hər biri bir commit; həftəlik limit 25%-dən 31%-ə qalxdı; 6 sorğu rədd edildi və qeyd olundu. Bir icradır, benchmark deyil | [otomode.md](otomode.md#one-real-run) |

> [!WARNING]
> Brief-lər maşınınızdan çıxır: hər lane öz brief-ini həmin modelin vendoruna göndərir. Brief-ə heç vaxt sirr, token
> və ya şəxsi məlumat qoymayın. otomode-un hook-u sorğuları rədd edir, silmə, deploy, push və göndərmə əmrlərindən
> imtina edir, lakin nümunə uyğunlaşdırır: bu qoruyucu çəpərdir, sandbox deyil.

## Sürətli başlanğıc

Bunu agent-inizə yapışdırın, skill-ləri o quraşdırsın:

```text
Install multi-model-orchestra: clone https://github.com/yatuk/multi-model-orchestra,
run ./install.sh --link in it, then run ~/.claude/skills/orchestra/scripts/mmo-preflight
and tell me which lanes are ready.
```

Və ya özünüz quraşdırın. bash, git, `timeout` və Python 3 lazımdır; Windows-da Git Bash istifadə edin.

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link          # into ~/.claude/skills; --dir PATH for a project
~/.claude/skills/orchestra/scripts/mmo-preflight
```

`mmo-preflight` heç bir modeli çağırmır. O, bu maşında hansı lane-lərin olduğunu bildirir; dirijor çatışmayanları yan keçərək yönləndirir.
otomode üçün hook-unu qeydiyyatdan keçirmək məqsədilə bir dəfə `python ~/.claude/skills/otomode/scripts/otomode.py install` işlədin.

Sonra məsələn, bunları xahiş edin:

- "`internal/auth` daxilindəki sınıq testləri düzəlt. orchestra skill-ini izlə."
- "Birləşdirməzdən əvvəl bu migrasiya planı barədə GPT-dən ikinci rəy al."
- "Council-dan soruş: bu servisi bölək, yoxsa bir proses qalsın?"
- "otomode 6h: bu dörd tapşırıq, hər biri `go test ./...` ilə yoxlansın."

## Birgə işlədiyi alətlər

| Alət | Nə üçün | Tələb olunan |
|---|---|---|
| Claude Code | Skill-lər və sub-agent kimi Claude Opus / Sonnet / Haiku pillələri | Skill-lərin `~/.claude/skills` (və ya layihənin `.claude/skills`) qovluğuna quraşdırılması; başqa heç nə |
| Codex CLI | GPT lane-ləri | PATH-da `codex`, ChatGPT ilə daxil olunmuş |
| Kimi Code CLI | Kimi və DeepSeek lane-ləri | PATH-da `kimi`, daxil olunmuş; DeepSeek üçün Kimi Code-un `config.toml` faylında `deepseek/*` modeli |

GPT model id-ləri: bəzi ChatGPT planlarında Codex CLI artıq fərqli id-lər təqdim edir (məsələn gpt-5.6-terra və ya gpt-6-luna)
və digərlərini rədd edir. Defoltlar skill fayllarında yazılıb; işi ora yönləndirməzdən əvvəl planınızın qəbul etdiyi
id-ləri sınaqdan keçirin (CLI-ları görmək üçün `mmo-preflight`, sonra hər id üçün bir sətirlik `mmo-run` brief-i).
Bax: [Model ids](how-it-works.md#model-ids).

## Daha çox

Aşağıdakı sənədlər ingilis dilindədir.

- [How it works](how-it-works.md): yönləndirmə cədvəli, runner, status kodları, təhlükəsizlik modeli, council.
- [otomode](otomode.md): siz olmayanda nəzarətsiz icralar.
- [Benchmark](benchmark.md): lane benchmark-ı və A/B testi, hər ikisinin necə işlədiləcəyi ilə birlikdə.
- [FAQ](faq.md): oxşar layihələrlə müqayisə daxil olmaqla.
- Yazı (türk dilində): [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), bahalı əsas dövrə modelini dirijor kimi işlətmək və onu nəzarətsiz işə buraxmaq haqqında.

## Qovluq quruluşu

```
skills/
  orchestra/   SKILL.md, scripts/ (mmo-run, mmo-council, mmo-preflight, mmo_extract.py), templates/
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, otomode, benchmark, faq, translations
```

## Lisenziya

MIT, bax: [LICENSE](../LICENSE). README illüstrasiyası Codex CLI vasitəsilə gpt-image-2 ilə yaradılıb.
