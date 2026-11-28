<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="multi-model-orchestra loqosu: qırmızı kəpənək qalstuklu, dirijor çubuğunu qaldıran cizgi filmi dirijoru">
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
  <sub>Modelləri lane vasitəsilə işlədilmiş və <a href="benchmark.md">benchmark</a>-da qiymətləndirilmiş vendorlar. Adlar və loqolar sahiblərinə məxsusdur; heç bir dəstək nəzərdə tutulmur.</sub>
</p>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · Azərbaycanca · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Bir bahalı model dirijorluq etsin, daha ucuz modellər ifa etsin, hər cavab istifadə olunmazdan əvvəl yoxlanılsın.</b><br>
Claude Code (və ya <code>SKILL.md</code> fayllarını oxuyan istənilən alət) üçün skill-lər: işi Claude Opus, Sonnet və Haiku-ya, OpenAI GPT-yə, Kimi-yə, DeepSeek-ə və əlinizdə olan istənilən agent CLI-ya ya da API-yə həvalə edir: OpenCode, Grok, Gemini, Qwen, Cursor, Copilot, OpenRouter, lokal modellər və s.<br>
Əsas agent planlaşdırır, brief-ləri yazır və nəzərdən keçirir; işi digər modellər görür və onların qaytardığı heç nəyə yoxlamadan keçməyincə etibar edilmir.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="MIT lisenziyası"></a>
  <img src="https://img.shields.io/badge/lanes-32%20CLIs%20and%20APIs-2563EB" alt="32 lane: agent CLI-ları və API-lər">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="bash üzərində işləyir, Windows-da Git Bash">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="GitHub ulduzları"></a>
</p>

<p align="center"><b><a href="#sürətli-başlanğıc">Quraşdırma</a></b> · <a href="lanes/README.md">Lanes</a> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

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
      <code>mmo-run</code> bütün lane-lər üçün yeganə runner-dir: sərt status kodları və hər çağırışda zaman aşımı var. Yazan lane-lər yalnız branch-ınızı özündə saxlayan git worktree-də işləyir, əsas checkout-da heç vaxt.
    </td>
    <td width="25%" valign="top">
      <b>Yoxla</b><br>
      Yoxlamanı dirijor özü <code>mmo-check</code> ilə işlədir və diff-in hamısını oxuyur: toxunulmuş testlər, brief-dən kənar fayllar və dəyişiklik olmadan da keçəcək yoxlama işarələnir. Lane-in "bitdi" deməsi iddiadır, nəticə deyil.
    </td>
  </tr>
</table>

## Real rəqəmlər

| Nə | Nəticə | Təfərrüat |
|---|---|---|
| <!-- AB-RESULTS --> A/B: orchestra skill-i ilə sadə "use subagents" müqayisəsi (`claude-fable-5-2`, hər qolda 2 icra) | Keyfiyyət eynidir: dörd icranın hamısı 36/36 gizli test, görünən testlərə toxunulmayıb (tapşırıq toplusu keyfiyyəti ayırd etmək üçün çox asandır) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B icra başına xərc | Skill orta hesabla $1.88, müqayisə qolu $3.21; təxminən 40% az, aralıqlar üst-üstə düşmür. Qənaət sub-agent-lərin Fable-ı miras almaq əvəzinə Sonnet-də işləməsindən gəlir. Sürət qazancı yoxdur (3.2 dəq qarşı 3.5 dəq) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B məhdudiyyətləri | Bir sətirlik "use Sonnet subagents" istəyi (2026-11-28, 2 icra, 36/36, orta $1.49, sub-agent-lər Sonnet-də) qənaətin hamısını skill olmadan əldə etdi; A və B daha əvvəlki gündə işlədilib, ona görə bu nəzarətli müqayisə deyil. `total_cost_usd` siyahı qiymətinə əsaslanan əvəzedici ölçüdür, plan istifadəsi deyil | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
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
- "Bu migrasiyanı özün et; başlamazdan əvvəl və bitdi deməzdən əvvəl GPT ilə advisor skill-indən istifadə et."
- "otomode 6h: bu dörd tapşırıq, hər biri `go test ./...` ilə yoxlansın."

## Birgə işlədiyi alətlər

| Alət | Nə üçün | Tələb olunan |
|---|---|---|
| Claude Code | Skill-lər və sub-agent kimi Claude Opus / Sonnet / Haiku pillələri | Skill-lərin `~/.claude/skills` (və ya layihənin `.claude/skills`) qovluğuna quraşdırılması; başqa heç nə |
| Codex CLI | GPT lane-ləri | PATH-da `codex`, ChatGPT ilə daxil olunmuş |
| Kimi Code CLI | Kimi və DeepSeek lane-ləri | PATH-da `kimi`, daxil olunmuş; DeepSeek üçün Kimi Code-un `config.toml` faylında `deepseek/*` modeli |
| OpenCode | Daxil olduğu istənilən provayder (DeepSeek, OpenRouter, Ollama, pulsuz modelləri) | PATH-da `opencode` |
| Grok CLI | Grok lane-ləri | PATH-da `grok`, daxil olunmuş |
| Cursor CLI | Cursor lane-ləri | PATH-da `cursor-agent`, daxil olunmuş |
| Antigravity CLI | Antigravity lane-ləri | PATH-da `agy`, daxil olunmuş |
| Copilot CLI | Copilot lane-ləri | PATH-da `copilot`, daxil olunmuş |
| 19 digər agent CLI-ı | Gemini CLI, Qwen Code, Amp, Droid, Auggie, Kiro, Cline, Kilo, Vibe, Crush, Goose, Aider, Pi, Devin, CodeBuddy, Letta Code, Qoder, gptme, llm | PATH-da CLI, daxil olunmuş. Hər CLI-ın sənədlərinə əsasən yazılıb və maintainer tərəfindən hələ işlədilməyib: [bunun mənası](lanes/README.md#what-checked-means) |
| Heç bir CLI yoxdur | `api` lane-i: rəy və kütləvi işlər üçün istənilən OpenAI ilə uyğun endpoint (OpenRouter, DeepSeek, Groq, lokal Ollama, ...) | Python 3 və mühit dəyişənində açar |
| Bulud agent-ləri (təcrübi) | `mmo-cloud` vasitəsilə Devin, Cursor bulud agent-ləri, Copilot agent tapşırıqları | Vendor açarı və agent-in çata biləcəyi yerə göndərilmiş kod |

`mmo-run --list` hər lane-i və onun bu maşında hazır olub-olmadığını göstərir. Lane üzrə təfərrüat: [docs/lanes](lanes/README.md).

GPT model id-ləri: bəzi ChatGPT planlarında Codex CLI artıq fərqli id-lər təqdim edir (məsələn gpt-5.6-terra və ya gpt-6-luna)
və digərlərini rədd edir. Defoltlar skill fayllarında yazılıb; işi ora yönləndirməzdən əvvəl planınızın qəbul etdiyi
id-ləri sınaqdan keçirin (CLI-ları görmək üçün `mmo-preflight`, sonra hər id üçün bir sətirlik `mmo-run` brief-i).
Bax: [Model ids](how-it-works.md#model-ids).

## 10 dəqiqəyə ilk PR

Çoxu üçün heç bir quraşdırma lazım deyil:

- **Öz dilinizdəki README-ni oxuyun** və maşın yazısına bənzəyən yerləri düzəldin. Bütün 19 tərcüməni model edib ([Krım tatarcası](https://github.com/yatuk/multi-model-orchestra/issues/1), [Uyğurca](https://github.com/yatuk/multi-model-orchestra/issues/2), [Türkmənçə](https://github.com/yatuk/multi-model-orchestra/issues/3), [Qazaxca](https://github.com/yatuk/multi-model-orchestra/issues/4), [qalanları](https://github.com/yatuk/multi-model-orchestra/issues/5)).
- **CLI-ın verdiyi xəta sətrini yapışdırın** (sürət limiti, vaxtı bitmiş giriş, naməlum model), runner onu ayırd edə bilsin ([#10](https://github.com/yatuk/multi-model-orchestra/issues/10)).
- **Testləri macOS-da və ya Linux-da işlədin** və nəyin sındığını yazın ([#8](https://github.com/yatuk/multi-model-orchestra/issues/8)).
- **İstifadə etdiyiniz CLI üçün lane əlavə edin** ([Gemini CLI](https://github.com/yatuk/multi-model-orchestra/issues/6), [Aider](https://github.com/yatuk/multi-model-orchestra/issues/7)), və ya [növbətiyə səs verin](https://github.com/yatuk/multi-model-orchestra/discussions/12).

Hamısı: [good first issues](https://github.com/yatuk/multi-model-orchestra/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22). Öz işinizi necə yönləndirdiyinizi [Show your routing setup](https://github.com/yatuk/multi-model-orchestra/discussions/11) bölməsində bölüşə bilərsiniz. Bax: [CONTRIBUTING](../CONTRIBUTING.md).

## Daha çox

Aşağıdakı sənədlər ingilis dilindədir.

- [How it works](how-it-works.md): yönləndirmə cədvəli, runner, status kodları, lane-i yoxlama, təhlükəsizlik modeli, council.
- [Lanes](lanes/README.md): hər lane, nə dərəcədə yoxlanıldığı və yenisinin necə əlavə olunacağı.
- [otomode](otomode.md): siz olmayanda nəzarətsiz icralar.
- [Benchmark](benchmark.md): lane benchmark-ı və A/B testi, hər ikisinin necə işlədiləcəyi ilə birlikdə.
- [Cost](cost.md): səkkiz xərc rıçaqı və hər birini tətbiq edən və ya ölçən əmrlər.
- [FAQ](faq.md): oxşar layihələrlə müqayisə daxil olmaqla.
- [Failures seen](failures.md): hər birinin necə göründüyü və nəyin onu düzəltdiyi.
- Yazı (türk dilində): [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), bahalı əsas dövrə modelini dirijor kimi işlətmək və onu nəzarətsiz işə buraxmaq haqqında.

## Qovluq quruluşu

```
skills/
  orchestra/   SKILL.md, lanes.md, templates/, scripts/ (mmo-run, mmo-check, mmo-council, mmo-score,
               mmo-cloud, mmo-preflight, providers/ with one file per lane)
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/  cloud-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, lanes/, otomode, benchmark, faq, translations
```

## Lisenziya

MIT, bax: [LICENSE](../LICENSE). README illüstrasiyası Codex CLI vasitəsilə gpt-image-2 ilə yaradılıb.
