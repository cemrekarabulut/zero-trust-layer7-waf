# 🔐 Güvenlik Politikası

Bu depo, **eğitim amaçlı** bir güvenlik laboratuvarıdır: bilerek zafiyetli bir Flask uygulaması, onu koruyan bir Layer-7 WAF ve WAF'ı doğrulayan yerel bir test paketi içerir.

> [!IMPORTANT]
> Bu proje bir saldırı aracı **değildir** ve üretim ortamında kullanılmak için tasarlanmamıştır. Hiçbir bileşeni başkasına ait sistemlere karşı kullanılmamalıdır.

---

## 🧱 Desteklenen Sürümler

| Sürüm | Destek |
|---|:---:|
| `main` dalı (en güncel) | ✅ |
| Eski commit'ler / fork'lar | ❌ |

---

## 🎯 Bilinçli Zafiyetler (rapor etmeye gerek yok)

Aşağıdakiler laboratuvarın **amacıdır**, hata değildir. Bunları güvenlik bildirimi olarak göndermene gerek yok.

| Konum | Bilinçli zafiyet / eksiklik |
|---|---|
| `/giris` | Parametresiz (string birleştirmeli) SQL sorgusu → SQL Injection |
| `/yorum` | Kullanıcı girdisinin kaçışsız HTML olarak basılması → XSS |
| Seed verisi | Düz metin parolalar |
| Uygulama geneli | Kimlik doğrulama, oturum yönetimi, CSRF koruması ve hız sınırlama yok |
| Sunucu | Flask geliştirme sunucusu (production WSGI değil) |
| WAF | Kısa, imza tabanlı bir kara liste. Atlatılabilir olması beklenir |

---

## ✅ Kapsam İçi Bildirimler

Şunları **gizli olarak** bildirmeni rica ederim:

- **Test paketindeki loopback kilidinin atlatılması.** Kilit bir güvenlik sınırı değil, kötüye kullanımı zorlaştıran bir önlemdir. Yine de aracın `127.0.0.1` / `localhost` dışına istek göndermesine yol açan her hata kapsam içidir.
- **Uygulamanın yerel makine dışına açılmasına** neden olan yapılandırma ya da kod hataları (ör. `0.0.0.0`'a bağlanma).
- **Depoda yanlışlıkla bulunan hassas veri:** token, anahtar, gerçek IP adresi, kişisel veri, gerçek log kaydı.
- **Bağımlılıklarda bilinen zafiyetler** (`requirements.txt` içindeki paketler).
- Test paketinin veya rapor üreticinin **kendi güvenliğini** etkileyen hatalar (ör. rapor çıktısında zararlı içerik işleme).

## 💡 Kapsam Dışı Ama Memnuniyetle Karşılanır

- **WAF atlatma bulguları ve iyileştirme önerileri.** WAF bilerek basit tutulmuştur. Bunlar için gizli bildirime gerek yok, normal bir **Issue** veya **Pull Request** açabilirsin. Öğretici katkılar hoş karşılanır.

## ❌ Kapsam Dışı

- Yukarıdaki tabloda listelenen bilinçli zafiyetler
- Flask geliştirme sunucusu uyarıları
- Hizmet reddi (DoS) senaryoları ve sosyal mühendislik
- Bu projenin araçlarıyla **üçüncü taraf sistemlere** yapılan her türlü test. Bu proje bunu desteklemez ve teşvik etmez

---

## 📬 Nasıl Bildirirsin?

Lütfen kapsam içi konular için **herkese açık Issue açma**. Şu yollardan birini kullan:

1. **GitHub özel bildirim (tercih edilen):** deponun **Security → Report a vulnerability** sekmesi
   `https://github.com/cemrekarabulut>/web-security-lab/security/advisories/new`
2. **E-posta:** `<cemrekarabulut03@gmail.com>`

Bildirimde şunlar olursa süreç hızlanır:

- Sorunun kısa açıklaması ve etkisi
- Etkilenen dosya / commit
- Yeniden üretme adımları (yalnızca kendi yerel ortamında)
- Varsa düzeltme önerisi

### ⏱️ Süreç

Bu, tek geliştiricili bir eğitim projesidir; aşağıdakiler **en iyi çaba** hedefleridir, garanti değildir.

| Aşama | Hedef |
|---|---|
| İlk yanıt | 7 gün içinde |
| Değerlendirme ve sınıflandırma | 14 gün içinde |
| Düzeltme veya yanıt | 30 gün içinde |

İstersen bildirimin, düzeltme yayınlandığında teşekkür bölümünde anılır.

---

## 🧭 Sorumlu Kullanım Kuralları

Bu depoyu kullanarak aşağıdakileri kabul etmiş olursun:

1. **Sadece kendi makinende** veya izole, sana ait bir test ağında çalıştır.
2. Uygulamayı **`127.0.0.1` dışında bir adrese bağlama** ve asla internete açma. Bilerek zafiyetlidir.
3. Test paketini **sahibi olmadığın veya yazılı izin almadığın** hiçbir sisteme yöneltme. Loopback kilidini kaldırmaya ya da atlamaya çalışma.
4. Payload'ları ve teknikleri **başkalarına zarar vermek** için yeniden kullanma.
5. Yetkisiz erişim birçok ülkede suçtur (Türkiye'de TCK 243–244 dahil). Sorumluluk tamamen kullanıcıya aittir.

Yazılım **"olduğu gibi"** sunulur; herhangi bir garanti verilmez.

---

## 🧹 Depo Hijyeni

- `venv/`, `*.db`, üretilen raporlar ve `__pycache__/` `.gitignore` ile dışarıda tutulur.
- Depoya gerçek IP adresi, kişisel veri, token veya gerçek log **konmaz**. Örnek raporlar yalnızca yerel (`127.0.0.1`) çıktılardan oluşur.
- Yanlışlıkla hassas veri fark edersen lütfen yukarıdaki kanaldan bildir.

---

*Bu belge, projeyi etik ve şeffaf biçimde sunmak için hazırlanmıştır. Sorun ya da öneri için teşekkürler. 🙏*