<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="multi-model-orchestra logosu: kırmızı papyonlu, baget kaldıran çizgi film şef">
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
  <sub>Modelleri bir lane üzerinden çalıştırılmış ve <a href="benchmark.md">benchmark</a>'ta puanlanmış sağlayıcılar. Adlar ve logolar sahiplerine aittir; herhangi bir onay ima edilmez.</sub>
</p>

<p align="center"><sub><a href="../README.md">English</a> · Türkçe · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Pahalı model şeflik etsin, ucuz modeller çalsın, her cevap kullanılmadan önce kontrol edilsin.</b><br>
Claude Code (ya da <code>SKILL.md</code> dosyalarını okuyan herhangi bir ajan) için, işi Claude Opus, Sonnet ve Haiku'ya, OpenAI GPT'ye, Kimi'ye, DeepSeek'e ve elinizdeki her ajan CLI'ına ya da API'ye devreden skill'ler: OpenCode, Grok, Gemini, Qwen, Cursor, Copilot, OpenRouter, yerel modeller ve daha fazlası.<br>
Ana ajan planlar, brief'leri yazar ve gözden geçirir; işi diğer modeller yapar ve dönen hiçbir şeye bir kontrolden geçmeden güvenilmez.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="MIT lisansı"></a>
  <img src="https://img.shields.io/badge/lanes-32%20CLIs%20and%20APIs-2563EB" alt="32 lane: ajan CLI'ları ve API'ler">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="bash üzerinde çalışır, Windows'ta Git Bash">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="GitHub yıldızları"></a>
</p>

<p align="center"><b><a href="#hızlı-başlangıç">Kurulum</a></b> · <a href="lanes/README.md">Lanes</a> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">SSS</a></p>

<p align="center">
  <img src="../assets/orchestra-comic.png" alt="Bir şef bir hatayı bir modele verir, diff'i ister ve kör bir council toplar" width="860">
  <br>
  <sub>Şef partileri dağıtır, diff'i ister, cevap bir yargı meselesiyse kör bir council toplar.</sub>
</p>

<table>
  <tr>
    <td width="25%" valign="top">
      <b>Yönlendir</b><br>
      Her iş, zorluğuna göre, kontrolünü geçebilecek en ucuz katmana gider. Bir lane ancak kontrolü geçemezse bir üst katmana çıkar, sezgiyle değil.
    </td>
    <td width="25%" valign="top">
      <b>Brief</b><br>
      Her katman en iyi çalıştığı brief'i alır: Opus'a amaç ve kısıtlar, ucuz lane'lere numaralı adımlar ve tam dosya yolları. Lane yalnız brief'i görür, o yüzden brief bir yabancıya yazılır.
    </td>
    <td width="25%" valign="top">
      <b>Çalıştır</b><br>
      <code>mmo-run</code> her lane için tek runner'dır; katı durum kodları ve her çağrıda bir zaman aşımı vardır. Yazan lane'ler yalnız branch'inizi içeren bir git worktree'de çalışır, ana checkout'unuzda asla.
    </td>
    <td width="25%" valign="top">
      <b>Kontrol et</b><br>
      Kontrolü şef kendisi <code>mmo-check</code> ile koşar ve diff'in tamamını okur: dokunulan testler, brief dışındaki dosyalar ve değişiklik olmadan da geçecek bir kontrol işaretlenir. Bir lane'in "bitti" demesi bir iddiadır, sonuç değil.
    </td>
  </tr>
</table>

## Gerçek rakamlar

| Ne | Sonuç | Ayrıntı |
|---|---|---|
| <!-- AB-RESULTS --> A/B: orchestra skill'i ile düz "use subagents" karşılaştırması (`claude-fable-5-2`, kol başına 2 koşu) | Kalite aynı: dört koşunun hepsi 36/36 gizli test, görünür testlere dokunulmadı (görev seti kaliteyi ayırt edemeyecek kadar kolay) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B koşu başına maliyet | Skill ortalama $1.88, karşı kol $3.21; yaklaşık %40 daha az, aralıklar çakışmıyor. Tasarruf, alt ajanların Fable'ı devralmak yerine Sonnet'te çalışmasından geliyor. Hız kazancı yok (3.2'ye karşı 3.5 dk) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B sınırları | Tek satırlık "use Sonnet subagents" istemi (2026-11-28, 2 koşu, 36/36, ortalama $1.49, alt ajanlar Sonnet'te) tasarrufun tamamını skill olmadan yakaladı; A ve B daha önceki bir günde koşuldu, bu yüzden kontrollü bir karşılaştırma değil. `total_cost_usd` liste fiyatından bir vekil ölçüdür, plan kullanımı değildir | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
| Lane benchmark'ı, 2026-11-21 (gizli testli hata düzeltme, kesin cevaplı akıl yürütme, 60 satırlık toplu etiketleme) | Kimi k3.1-pro, DeepSeek v4-pro, DeepSeek flash ve gpt-5.6-terra: 6/6, 3/3, 60/60. gpt-6-luna: 6/6, 0/3, 58/60. gpt-6.1-sol ve gpt-6-astra: ~6/6, ~3/3, ~60/60 (tahmini: o planda sunulmuyor, puanlar 2026-11-11 koşusundan) | [benchmark.md](benchmark.md) |
| otomode, 5 saatlik tek gözetimsiz koşu | 13 görev, her biri tek commit; haftalık limit %25'ten %31'e çıktı; 6 istem reddedildi ve kaydedildi. Bir koşu, benchmark değil | [otomode.md](otomode.md#one-real-run) |

> [!WARNING]
> Brief'ler makinenizden çıkar: her lane brief'ini o modelin sağlayıcısına gönderir. Bir brief'e asla sır, token
> ya da kişisel veri koymayın. otomode'un kancası istemleri reddeder ve silme, deploy, push ve gönderme komutlarını
> geri çevirir, ama kalıp eşleştirir: bir korkuluktur, sandbox değildir.

## Hızlı başlangıç

Bunu ajanınıza yapıştırın, skill'leri o kursun:

```text
Install multi-model-orchestra: clone https://github.com/yatuk/multi-model-orchestra,
run ./install.sh --link in it, then run ~/.claude/skills/orchestra/scripts/mmo-preflight
and tell me which lanes are ready.
```

Ya da kendiniz kurun. bash, git, `timeout` ve Python 3 gerekir; Windows'ta Git Bash kullanın.

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link          # ~/.claude/skills içine; bir proje için --dir PATH
~/.claude/skills/orchestra/scripts/mmo-preflight
```

`mmo-preflight` hiçbir modeli çağırmaz. Bu makinede hangi lane'lerin bulunduğunu söyler; şef eksik olanların etrafından dolaşır.
otomode için kancasını kaydetmek üzere bir kez `python ~/.claude/skills/otomode/scripts/otomode.py install` çalıştırın.

Sonra örneğin şunları isteyin:

- "`internal/auth` içindeki kırık testleri düzelt. orchestra skill'ini izle."
- "Bu migration planını birleştirmeden önce GPT'den ikinci görüş al."
- "Council'a sor: bu servisi bölelim mi, tek süreç mi kalsın?"
- "Bu migration'ı kendin yap; başlamadan önce ve bitti demeden önce GPT ile advisor skill'ini kullan."
- "otomode 6h: şu dört görev, her biri `go test ./...` ile kontrol edilsin."

## Birlikte çalıştığı araçlar

| Araç | Ne için | Gerekenler |
|---|---|---|
| Claude Code | Skill'ler ve alt ajan olarak Claude Opus / Sonnet / Haiku katmanları | Skill'lerin `~/.claude/skills` (ya da bir projenin `.claude/skills`) içine kurulması; başka bir şey değil |
| Codex CLI | GPT lane'leri | PATH'te `codex`, ChatGPT ile giriş yapılmış |
| Kimi Code CLI | Kimi ve DeepSeek lane'leri | PATH'te `kimi`, giriş yapılmış; DeepSeek için Kimi Code'un `config.toml` dosyasında bir `deepseek/*` modeli |
| OpenCode | Giriş yaptığı her sağlayıcı (DeepSeek, OpenRouter, Ollama, ücretsiz modelleri) | PATH'te `opencode` |
| Grok CLI | Grok lane'leri | PATH'te `grok`, giriş yapılmış |
| Cursor CLI | Cursor lane'leri | PATH'te `cursor-agent`, giriş yapılmış |
| Antigravity CLI | Antigravity lane'leri | PATH'te `agy`, giriş yapılmış |
| Copilot CLI | Copilot lane'leri | PATH'te `copilot`, giriş yapılmış |
| 19 ajan CLI'ı daha | Gemini CLI, Qwen Code, Amp, Droid, Auggie, Kiro, Cline, Kilo, Vibe, Crush, Goose, Aider, Pi, Devin, CodeBuddy, Letta Code, Qoder, gptme, llm | PATH'te CLI, giriş yapılmış. Her CLI'ın belgelerinden yazıldı ve bakımcı tarafından henüz koşulmadı: [bunun anlamı](lanes/README.md#what-checked-means) |
| Hiç CLI yok | `api` lane'i: görüş ve toplu işler için OpenAI uyumlu her uç nokta (OpenRouter, DeepSeek, Groq, yerel bir Ollama, ...) | Python 3 ve bir ortam değişkeninde anahtar |
| Bulut ajanları (deneysel) | `mmo-cloud` üzerinden Devin, Cursor bulut ajanları, Copilot ajan görevleri | Bir sağlayıcı anahtarı ve ajanın erişebileceği yere gönderilmiş kod |

`mmo-run --list` her lane'i ve bu makinede hazır olup olmadığını gösterir. Lane başına ayrıntılar: [docs/lanes](lanes/README.md).

GPT model id'leri: bazı ChatGPT planlarında Codex CLI artık farklı id'ler sunuyor (örneğin gpt-5.6-terra ya da
gpt-6-luna) ve diğerlerini reddediyor. Varsayılanlar skill dosyalarında yazar; işi oraya yönlendirmeden önce planınızın
kabul ettiği id'leri deneyin (CLI'ları görmek için `mmo-preflight`, sonra her id için tek satırlık bir `mmo-run` brief'i).
Bkz. [Model ids](how-it-works.md#model-ids).

## 10 dakikada ilk PR

Çoğu için kurulum gerekmez:

- **Kendi dilinizdeki README'yi okuyun** ve makine yazımı gibi duran yerleri düzeltin. 19 çevirinin hepsini bir model yaptı ([Kırım Tatarcası](https://github.com/yatuk/multi-model-orchestra/issues/1), [Uygurca](https://github.com/yatuk/multi-model-orchestra/issues/2), [Türkmence](https://github.com/yatuk/multi-model-orchestra/issues/3), [Kazakça](https://github.com/yatuk/multi-model-orchestra/issues/4), [gerisi](https://github.com/yatuk/multi-model-orchestra/issues/5)).
- **Bir CLI'ın verdiği hata satırını yapıştırın** (hız sınırı, süresi dolmuş giriş, bilinmeyen model) ki runner onu ayırt edebilsin ([#10](https://github.com/yatuk/multi-model-orchestra/issues/10)).
- **Testleri macOS ya da Linux'ta koşun** ve neyin bozulduğunu yazın ([#8](https://github.com/yatuk/multi-model-orchestra/issues/8)).
- **Kullandığınız CLI için bir lane ekleyin** ([Gemini CLI](https://github.com/yatuk/multi-model-orchestra/issues/6), [Aider](https://github.com/yatuk/multi-model-orchestra/issues/7)), ya da [sıradakine oy verin](https://github.com/yatuk/multi-model-orchestra/discussions/12).

Hepsi: [good first issues](https://github.com/yatuk/multi-model-orchestra/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22). Kendi işinizi nasıl yönlendirdiğinizi [Show your routing setup](https://github.com/yatuk/multi-model-orchestra/discussions/11) bölümünde paylaşabilirsiniz. Bkz. [CONTRIBUTING](../CONTRIBUTING.md).

## Daha fazlası

Aşağıdaki belgeler İngilizcedir.

- [How it works](how-it-works.md): yönlendirme tablosu, runner, durum kodları, bir lane'i kontrol etme, güvenlik modeli, council.
- [Lanes](lanes/README.md): her lane, ne kadar kontrol edildiği ve yenisinin nasıl ekleneceği.
- [otomode](otomode.md): siz yokken gözetimsiz koşular.
- [Benchmark](benchmark.md): lane benchmark'ı ve A/B testi, ikisinin nasıl koşulacağıyla birlikte.
- [Cost](cost.md): sekiz maliyet kaldıracı ve her birini uygulayan ya da ölçen komutlar.
- [FAQ](faq.md): benzer projelerle karşılaştırma dahil.
- [Failures seen](failures.md): her birinin neye benzediği ve neyin düzelttiği.
- Türkçe yazı: [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), pahalı bir ana döngü modelini şef olarak kullanmak ve onu gözetimsiz çalışmaya bırakmak üzerine.

## Dizin yapısı

```
skills/
  orchestra/   SKILL.md, lanes.md, templates/, scripts/ (mmo-run, mmo-check, mmo-council, mmo-score,
               mmo-cloud, mmo-preflight, providers/ with one file per lane)
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/  cloud-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: anahtar, kanca, kullanım kapısı; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; A/B testi için ab/
docs/          how-it-works, lanes/, otomode, benchmark, faq, çeviriler
```

## Lisans

MIT, bkz. [LICENSE](../LICENSE). README illüstrasyonu Codex CLI üzerinden gpt-image-2 ile üretildi.
