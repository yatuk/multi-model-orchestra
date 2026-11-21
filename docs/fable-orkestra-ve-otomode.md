# Fable 5.2 ile orkestra ve otomode: pahalı modeli şef yapmak

Claude Fable 5.2 çok iyi bir model, ama pahalı. Her satırı ona yazdırırsanız haftalık limit iki günde biter. Bu yazı, Fable'ı orkestra şefi gibi kullanmanın yolunu anlatıyor. Fable planı, brief'leri ve son kararı yazar; işin kendisini daha ucuz modeller yapar. Ardından `otomode` ile aynı düzen siz başında yokken de çalışır.

Anlattıklarım bu repodaki skill'lerle kurulu bir düzenden: `orchestra`, `council`, `chatgpt-lane`, `kimi-lane`, `deepseek-lane` ve `otomode`. Örnekler gerçek bir günden. Bir Go + React monorepo'da dokuz alt ajan aynı anda çalıştı; birleştirmeler, testler ve commit'ler ana oturumdan yönetildi.

## 1. Temel kural: Fable'ın token'ı karar satın alır, iş gücü değil

Bütün düzen tek cümleye dayanıyor. Ana döngüdeki pahalı model şunları yapar:

- işi parçalara ayırır ve hangi parçanın kime gideceğine karar verir,
- her parça için brief yazar,
- dönen işi kontrol eder (diff'i okur, testi kendisi koşar),
- birleştirir ve kullanıcıya rapor eder.

Geri kalan her şey, onu taşıyabilecek en ucuz katmana gider. Benim kullandığım dağılım şöyle:

| İş | Kime | Brief nasıl |
|---|---|---|
| Mimari, zor karar, birleştirme, son rapor | Ana döngü (Fable) | yok |
| Orta-zor: çok dosyalı iş, gerçek hata ayıklama | Opus alt ajan | Gevşek: amaç, bağlam, sınırlar, "bitti" neye benzer |
| Kolay-orta: kapsamı belli düzenleme, kalıp kopyalama | Sonnet alt ajan | Biraz daha sıkı: dosyalar, adımlar, çıktı biçimi |
| İyi tanımlanmış kolay iş, ucuza | DeepSeek (Kimi CLI üzerinden) | Adım adım, eksiksiz |
| GPT tarafında yürütme | gpt-6.1-sol (Codex CLI) | Adım adım, hiçbir şey örtük değil |
| İkinci görüş | gpt-6-astra | Soru ve kanıt, bir meslektaşa sorar gibi |
| Binlerce satırlık temizlik | Haiku, gpt-6-luna, deepseek-flash | Kesin kural seti, örnekli, küçük partiler |

İki kuralı atlamayın:

1. **Her alt ajana modeli açıkça verin.** `model:` yazmazsanız alt ajan ana döngünün modelini, yani Fable'ı devralır. Dokuz paralel ajan dokuz Fable olur ve limit bir öğleden sonrada gider.
2. **Alt ajanın raporu bir iddiadır.** "Testler geçti" yazması testin geçtiğini göstermez. Diff'i okuyun, kontrol komutunu kendiniz koşun.

## 2. Brief: kalite tavanı brief'tir

Aynı işi Opus'a ve sol'a aynı brief'le verirseniz biri iyi, biri kötü çıkar. Fark modelde değil, brief'in o modele uyup uymamasında.

**Opus'a** amaç ve kısıtları verip yolu ona bırakın. Fazla ayrıntı, parasını ödediğiniz muhakemeyi elinden alır. Bir örnek:

> Hedef: başarısız her gözden geçirme kalemi Bulgular akışında görünsün, sonraki okuma geçince kapansın, kalem istisnası bulguyu istisnalı yapsın. CIS bulguları iki kez sayılmasın (testle göster). Puan ve kararlar değişmesin. Mevcut bulgu yolunu yeniden kullan, yenisini icat etme.

**Sonnet'e** dosyaları, adımları ve dokunmaması gereken yerleri yazın. Takılırsa doğaçlama yapmasın, dursun ve rapor etsin.

**DeepSeek ve sol** asker gibidir: brief'te ne yazıyorsa onu yapar, fazlasını yapmaz. Numaralı adımlar, tam dosya yolları, her adımın kabul ölçütü ve kapsam dışı listesi gerekir. Açık bir tasarım sorusunu onlara bırakmayın; kararı önce verin, sonra kararı teslim edin. O günkü DeepSeek işi (EOL tablosunu konsoldan geçersiz kılma) bu yüzden ilk denemede geçti: brief ayar anahtarını, girdi biçimini, hangi fonksiyonun nereye ekleneceğini ve altı test vakasını tek tek yazıyordu. DeepSeek bir sapmayı da kendisi raporladı: tablodaki üretici adları `paloalto` değil `panos` idi, yardım metnini buna göre düzeltti.

Uzun brief'i dosyaya yazın, isteme yalnız dosyanın yolunu koyun. Paralel ajanlarda ortak kuralları (yasaklar, test komutları, commit biçimi) tek bir `common-brief.md` dosyasında toplamak her brief'i kısaltır.

## 3. Paralellik: en fazla, ama çakışmadan

Hız paralellikten gelir; sınır dosya çakışmasıdır. Ajanları başlatmadan önce her işin dokunacağı dosyaları çıkarın:

- Aynı dosyaya iki ajan yazacaksa ya birini bekletin ya da birine "bu dosyaya dokunma, kancaya ihtiyacın olursa raporla, birleştirirken ben eklerim" deyin.
- Her yazan ajan kendi git worktree'sinde çalışsın (Claude alt ajanlarında `isolation: "worktree"`, dış CLI'larda `git worktree add`).
- Paket dosyaları gibi tek kaynaklı dosyalara (`package.json`, kilit dosyası) yalnız bir ajan dokunsun.

O gün çakışmaların hepsi tahmin edilen yerlerde çıktı: her ajanın "Durum" satırını güncellediği plan belgeleri ve OpenAPI belgesinin parmak izi. Kodda hiç çakışma olmadı. Plan belgesi çakışması iki tarafın "yapıldı" notunu birleştirerek çözülür. Parmak izi çakışmasında iki tarafın değeri de yanlıştır: birleşik belgenin izini yeniden hesaplamanız gerekir.

Bir ajan bitince yeni açılan işleri hemen başlatın. Ajan sırasının boş beklemesi, paralelliğin kazandırdığı zamanı geri verir.

## 4. Doğrulama: alt ajan hedefli test koşar, şef tam takımı

Tam test takımı (benim projede yaklaşık 40 dakika) her ajanda koşulursa makine kilitlenir ve ajanlar birbirini bekler. Düzen şöyle:

- Her ajan yalnız kendi paketlerinin testlerini, gofmt/vet'i ve gerekiyorsa ön yüz typecheck'ini koşar.
- Şef her birleştirmeden sonra derlemeyi ve vet'i koşar, çakışma çözdüğü yerin testini tekrar eder.
- Bütün birleştirmeler bitince tam takım bir kez koşar.

## 5. Council: tek modelin görüşü yetmeyince

Bir tasarım kararında ya da kök neden tahmininde `mmo-council` aynı soruyu üç farklı model ailesine (GPT, Kimi, DeepSeek) salt okunur sorar. Cevaplar harflere karıştırılır ve şef hangisinin kimden geldiğini bilmeden yargılar. Bu kör okuma, şefin kendi tahminini onaylayan cevaba kaymasını önler. Council'a sonucu değil, soruyu ve kanıtı verin.

## 6. otomode: siz yokken aynı düzen

Uzun bir işi bırakıp gitmek istediğinizde asıl tehlike, ajanın bir izin isteminde saatlerce beklemesi ya da sorduğu soruya cevap gelmeyince durmasıdır. `otomode` bunu tersine çevirir: her şey başta bir kez sorulur, sonra hiçbir şey beklenmez.

### Başlangıç: tek soru turu

`otomode 5h` yazınca şef tek bir mesajda beş şeyi sorar:

1. Görevler, öncelik sırasıyla.
2. Her görevin "bitti" kontrolü: çıkış kodu karar veren bir komut (test, build, lint).
3. Gereken izinler. Şef ayar dosyalarını okur, görevlerden komutları çıkarır ve eksik izin kurallarını listeler (`Bash(go test:*)`, worktree'ler için `Edit(...)`, runner betiği).
4. Yasak alanlar ve DeepSeek kullanılıp kullanılamayacağı.
5. Çalışma ağacı kirliyse ne yapılacağı.

Önerileri hazır yazarsanız kullanıcı tek kelimeyle ("evet") onaylar. Onaydan sonra:

- izinler `.claude/settings.local.json` dosyasına eklenir,
- `otomode/<tarih>` dalı açılır,
- görev tablosu `OTOMODE.md` içine yazılıp ilk commit olur,
- kanca açılır,
- saatlik bekçi cron'u kurulur.

### Kanca: her istemi reddet, kaydet

Kanca `~/.claude/settings.json` içinde bir kez tanımlıdır ve otomode kapalıyken hiçbir şey yapmaz. Açıkken, yalnız o oturum için:

- her izin istemini, `AskUserQuestion`'ı ve plan modu geçişini reddeder ve `QUESTIONS.md` dosyasına yazar;
- silme, dağıtım, push ve gönderme komutlarını doğrudan reddeder (rm, git push, reset --hard, kubectl, ssh, POST istekleri, posta);
- adı send, post, delete, submit, upload olan MCP araçlarını da reddeder.

Reddedilen şey yeniden denenecek bir hata değildir. Şef nedeni okur, güvenli varsayılanı seçer ya da görevi "blocked" diye işaretleyip devam eder. O gün bir ajan, kapsam belirsiz kaldığında hangi yolu seçeceğini sordu (bulgusu olmayan birim geçti mi sayılsın, değerlendirilemedi mi). Soru `QUESTIONS.md`'ye düştü, iş planın önerisiyle devam etti.

### Çalışma döngüsü

Her görev için:

1. **Kullanım kapısı:** `otomode.py gate` beş saatlik ve haftalık pencerelerin yüksek olanına bakar. %85'i geçtiyse yeni iş başlamaz.
2. **Şerit seçimi:** önce DeepSeek (kolay, iyi tanımlıysa), yoksa Sonnet, çok dosyalıysa Opus. DeepSeek limit ya da bakiye yüzünden 6 koduyla çıkarsa o görev ve sonrakiler Claude şeritlerine geçer.
3. **Kontrol:** şef diff'i okur ve görevin kontrol komutunu worktree'de kendisi koşar.
4. **Commit:** geçerse otomode dalına tek başına girer, konu satırında görev kimliği bulunur (`otomode T3: ...`). Geçmezse hata çıktısı brief'e eklenip bir üst katmanla tekrar denenir. Üç denemeden sonra görev "failed" olur, nedeni not edilir ve sıradakine geçilir.
5. **Kayıt:** `OTOMODE.md` tablosu ve günlüğü her adımda güncellenir. Oturum sıkıştırılsa ya da yeniden başlasa bile şef kaldığı yeri bu dosyadan bulur.

### Limit ve bekçi

Kapı "stop" derse şef çalışan şeritlerin bitmesini bekler, hazır olanı commit eder ve limitin sıfırlanmasından birkaç dakika sonrası için tek seferlik bir `otomode resume` cron'u kurar. Saatlik bekçi döngü takıldı mı, 90 dakikayı geçen bir şerit var mı, süre doldu mu diye bakar.

Kullanım yüzdesi masaüstü uygulamasında `get_usage` aracından gelir. CLI'da durum satırı betiği (`statusline.py`) Claude Code'un gönderdiği `rate_limits` bilgisini bir dosyaya yazar, kapı oradan okur.

### Bitiş: `otomode off`

Sıra önemli:

1. Önce kanca kapanır; yoksa raporu yazarken sorulan soru da reddedilir.
2. Cron'lar silinir.
3. On beş satırı geçmeyen bir rapor yazılır: biten görevler ve commit'leri, takılanlar ve nedenleri, dal adı, bırakılan worktree'ler, reddedilen istem sayısı.
4. `QUESTIONS.md`'deki sorular gruplanıp sorulur.

Hiçbir şey push edilmez. Dal sizi bekler.

## 7. Kurulum

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link
~/.claude/skills/orchestra/scripts/mmo-preflight
python ~/.claude/skills/otomode/scripts/otomode.py install   # kancayı ~/.claude/settings.json'a ekler
```

Fable ana döngüsü için yönlendirme tablosunu kendi `CLAUDE.md` dosyanıza ya da bir skill'e koyun. Kural basit: her alt ajan çağrısında model açık yazılsın, işi taşıyabilecek en ucuz katman seçilsin, tereddütte ucuz olan denenip sonucu kontrol edilsin.

## 8. Öğrendiklerim, kısaca

- Paralellik çoğu zaman modelden daha büyük kazanç getirir. Dokuz orta boy iş aynı anda, tek tek koşmanın birkaç katı hızlı biter.
- Çakışmalar planlanabilir: ortak belgeler ve üretilmiş dosyalar (parmak izi, örnek JSON) çakışır, kod pek çakışmaz.
- Ucuz modeller kötü değildir, brief'e karşı dürüsttür. Brief'te yazmayan şey yapılmaz.
- Alt ajanın "geçti" demesi kontrol değildir. Şefin işi birleştirmeden önce bakmaktır.
- otomode'da asıl iş baştaki soru turudur. İzin listesi cömert değilse gece yarısı her şey reddedilir ve sabah boş bir dal bulursunuz.
