<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="multi-model-orchestra logotipi: qizil kapalak boʻyinbogʻ taqqan, tayoqchasini koʻtargan multfilm dirijyori">
</p>

<h1 align="center">multi-model-orchestra</h1>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · Oʻzbekcha · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Bitta qimmat model dirijyorlik qilsin, arzonroq modellar chalsin, har bir javob ishlatilishidan oldin tekshirilsin.</b><br>
Claude Code (yoki <code>SKILL.md</code> fayllarini oʻqiydigan istalgan agent) uchun ishni Claude Opus, Sonnet va Haiku, OpenAI GPT, Kimi va DeepSeek modellariga topshiradigan koʻnikmalar (skills).<br>
Asosiy agent rejalashtiradi, briflarni yozadi va koʻrib chiqadi; ishni boshqa modellar bajaradi, ular qaytargan hech narsaga esa tekshiruvdan oʻtmaguncha ishonilmaydi.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="MIT litsenziyasi"></a>
  <img src="https://img.shields.io/badge/models-Claude%20·%20GPT%20·%20Kimi%20·%20DeepSeek-2563EB" alt="Claude, GPT, Kimi va DeepSeek yoʻlaklari">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="bash bilan ishlaydi, Windowsda Git Bash">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="GitHub yulduzlari"></a>
</p>

<p align="center"><b><a href="#tez-boshlash">Oʻrnatish</a></b> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">Savol-javob</a></p>

<p align="center">
  <img src="../assets/orchestra-comic.png" alt="Dirijyor xatoni modelga beradi, diff soʻraydi va anonim kengash chaqiradi" width="860">
  <br>
  <sub>Dirijyor partiyalarni taqsimlaydi, diff soʻraydi, javob baholashni talab qilganda esa anonim kengash (council) chaqiradi.</sub>
</p>

<table>
  <tr>
    <td width="25%" valign="top">
      <b>Yoʻnaltirish</b><br>
      Har bir ish murakkabligiga qarab oʻz tekshiruvidan oʻta oladigan eng arzon darajaga yuboriladi. Yoʻlak (lane) yuqori darajaga taxmin bilan emas, faqat tekshiruvdan oʻtolmaganidan keyingina koʻtariladi.
    </td>
    <td width="25%" valign="top">
      <b>Brif</b><br>
      Har bir daraja oʻzi uchun eng yaxshi ishlaydigan brifni oladi: Opusga maqsad va cheklovlar, arzonroq yoʻlaklarga raqamlangan qadamlar va aniq fayllar. Yoʻlak faqat brifni koʻradi, shuning uchun u begona odam uchun yoziladi.
    </td>
    <td width="25%" valign="top">
      <b>Ishga tushirish</b><br>
      <code>mmo-run</code> barcha provayderlar uchun yagona ishga tushirgich (runner): qatʼiy holat kodlari bor va har bir chaqiruvda kutish vaqti cheklanadi. Yozadigan yoʻlaklar faqat git worktree ichida ishlaydi, hech qachon asosiy checkoutingizda emas.
    </td>
    <td width="25%" valign="top">
      <b>Tekshirish</b><br>
      Tekshiruvni dirijyorning oʻzi ishga tushiradi va diffni toʻliq oʻqiydi. Yoʻlakning "tayyor" deyishi natija emas, shunchaki daʼvo.
    </td>
  </tr>
</table>

## Haqiqiy raqamlar

| Nima | Natija | Batafsil |
|---|---|---|
| <!-- AB-RESULTS --> A/B: orchestra koʻnikmasi va oddiy "use subagents" taqqoslanishi (`claude-fable-5-2`, har bir tomonga 2 ishga tushirish) | Sifat bir xil: toʻrtala ishga tushirish ham 36/36 yashirin test, koʻrinadigan testlar oʻzgarmagan (vazifalar toʻplami sifatni ajratish uchun juda oson) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B bir ishga tushirish narxi | Koʻnikma oʻrtacha $1.88, ikkinchi tomon $3.21, taxminan 40% arzon, oraliqlar kesishmaydi. Tejov yordamchi agentlar Fableni meros qilib olish oʻrniga Sonnetda ishlashidan kelib chiqadi. Tezlikda yutuq yoʻq (3.2 va 3.5 daq) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B cheklovlari | Bir qatorli "use Sonnet subagents" soʻrovi sinab koʻrilmagan va tejovning katta qismini bera olishi mumkin. `total_cost_usd` tarif rejasidan foydalanish emas, prays-list narxi boʻyicha bilvosita koʻrsatkich | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
| Yoʻlaklar benchmarki, 2026-11-21 (yashirin testli xatoni tuzatish, aniq javobli mulohaza, 60 qatorli ommaviy belgilash) | Kimi k3.1-pro, DeepSeek v4-pro, DeepSeek flash va gpt-5.6-terra: 6/6, 3/3, 60/60. gpt-6-luna: 6/6, 0/3, 58/60. gpt-6.1-sol va gpt-6-astra: ~6/6, ~3/3, ~60/60 (taxminiy: u rejada taqdim etilmaydi, ballar 2026-11-11 dagi ishga tushirishdan olingan) | [benchmark.md](benchmark.md) |
| otomode, bitta 5 soatlik nazoratsiz ishga tushirish | 13 vazifa, har biriga bitta commit; haftalik limit 25% dan 31% ga oshdi; 6 ta ruxsat soʻrovi rad etildi va jurnalga yozildi. Bu bitta ishga tushirish, benchmark emas | [otomode.md](otomode.md#one-real-run) |

> [!WARNING]
> Briflar kompyuteringizdan chiqib ketadi: har bir yoʻlak oʻz brifini oʻsha model yetkazib beruvchisiga yuboradi. Brifga hech qachon sirlar, tokenlar
> yoki shaxsiy maʼlumotlarni qoʻymang. otomode hooki ruxsat soʻrovlarini rad etadi va oʻchirish, deploy, push hamda yuborish buyruqlarini bloklaydi,
> lekin u andozalarni solishtiradi: bu sandbox emas, faqat himoya toʻsigʻi.

## Tez boshlash

Buni agentingizga joylashtiring, koʻnikmalarni u oʻrnatsin:

```text
Install multi-model-orchestra: clone https://github.com/yatuk/multi-model-orchestra,
run ./install.sh --link in it, then run ~/.claude/skills/orchestra/scripts/mmo-preflight
and tell me which lanes are ready.
```

Yoki oʻzingiz oʻrnating. bash, git, `timeout` va Python 3 kerak; Windowsda Git Bash ishlating.

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link          # into ~/.claude/skills; --dir PATH for a project
~/.claude/skills/orchestra/scripts/mmo-preflight
```

`mmo-preflight` hech qachon modelni chaqirmaydi. U ushbu kompyuterda qaysi yoʻlaklar borligini aytadi, shuning uchun dirijyor yoʻqlarini aylanib oʻtadi.
otomode uchun uning hookini roʻyxatdan oʻtkazish maqsadida bir marta `python ~/.claude/skills/otomode/scripts/otomode.py install` ni ishga tushiring.

Soʻngra, masalan, shunday soʻrang:

- "`internal/auth` ichidagi muvaffaqiyatsiz testlarni tuzat. orchestra koʻnikmasiga amal qil."
- "Birlashtirishdan oldin bu migratsiya rejasi boʻyicha GPTdan ikkinchi fikr ol."
- "Kengashdan soʻra: bu servisni boʻlamizmi yoki bitta jarayon qoldiramizmi?"
- "otomode 6h: mana bu toʻrt vazifa, har biri `go test ./...` bilan tekshirilsin."

## Qaysi vositalar bilan ishlaydi

| Vosita | Nima uchun | Talablar |
|---|---|---|
| Claude Code | Koʻnikmalar va yordamchi agentlar sifatida Claude Opus / Sonnet / Haiku darajalari | Koʻnikmalar `~/.claude/skills` (yoki loyihaning `.claude/skills`) ichiga oʻrnatilgan; boshqa hech narsa kerak emas |
| Codex CLI | GPT yoʻlaklari | PATHda `codex`, ChatGPT orqali kirilgan |
| Kimi Code CLI | Kimi va DeepSeek yoʻlaklari | PATHda `kimi`, kirilgan; DeepSeek uchun Kimi Code `config.toml` faylida `deepseek/*` modeli |

GPT model identifikatorlari (id): baʼzi ChatGPT tarif rejalarida Codex CLI endi boshqa id larni beradi (masalan, gpt-5.6-terra yoki gpt-6-luna)
va boshqalarini rad etadi. Standart qiymatlar koʻnikma fayllarida koʻrsatilgan; ishni u yerga yoʻnaltirishdan oldin rejangiz qabul qiladigan
id larni qisqa sinovdan oʻtkazing (CLI larni koʻrish uchun `mmo-preflight`, soʻng har bir id uchun bir qatorli `mmo-run` brifi). Qarang: [Model ids](how-it-works.md#model-ids).

## Qoʻshimcha

Quyidagi hujjatlar ingliz tilida (oxirgisidan tashqari).

- [How it works](how-it-works.md): yoʻnaltirish jadvali, ishga tushirgich, holat kodlari, xavfsizlik modeli, kengash (council).
- [otomode](otomode.md): siz yoʻqligingizda nazoratsiz ishga tushirishlar.
- [Benchmark](benchmark.md): yoʻlaklar benchmarki va A/B testi, ikkalasini qanday ishga tushirish bilan birga.
- [FAQ](faq.md): oʻxshash loyihalar bilan taqqoslash ham shu yerda.
- Turk tilidagi maqola: [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), qimmat asosiy sikl modelini dirijyor sifatida ishlatish va uni nazoratsiz ishlashga qoldirish haqida.

## Tuzilishi

```
skills/
  orchestra/   SKILL.md, scripts/ (mmo-run, mmo-council, mmo-preflight, mmo_extract.py), templates/
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, otomode, benchmark, faq, translations
```

## Litsenziya

MIT, qarang: [LICENSE](../LICENSE). README rasmi Codex CLI orqali gpt-image-2 yordamida yaratilgan.
