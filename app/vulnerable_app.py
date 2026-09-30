from flask import Flask, request, render_template_string
import sqlite3
from flask import request, abort
import urllib.parse

app = Flask(__name__)

# 🛡️ BASİT WAF (Web Application Firewall) KURALLARI
WAF_IMZALARI = ["<script>", "or '1'='1", "admin'--", "<img", "/**/"]

@app.before_request
def otonom_waf_korumasi():
    """Gelen her isteği, sayfaya ulaşmadan önce yakalayıp tarayan güvenlik katmanı."""
    
    # Gelen istekteki (GET veya POST) tüm değerleri al
    gelen_degerler = list(request.args.values()) + list(request.form.values())
    
    for deger in gelen_degerler:
        # 1. Bypass engelleme: Hepsini küçük harfe çevir (Case evasion koruması)
        deger_kucuk = deger.lower()
        
        # 2. Bypass engelleme: URL Encode edilmiş payloadları geri çöz (URL evasion koruması)
        deger_cozulmus = urllib.parse.unquote(deger_kucuk)
        
        # WAF imzalarını kontrol et
        for imza in WAF_IMZALARI:
            if imza in deger_kucuk or imza in deger_cozulmus:
                print(f"\n[🛡️ WAF] SALDIRI BLOKLANDI! Yakalanan İmza: {imza}")
                abort(403)  # Uygulamaya gitmesine izin vermeden 403 Forbidden hatası fırlat

def veritabani_hazirla():
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT,
            sifre TEXT
        )
    """)
    cursor.execute("DELETE FROM kullanicilar")
    cursor.execute("INSERT INTO kullanicilar (kullanici_adi, sifre) VALUES ('admin', 'GizliSifre123!')")
    cursor.execute("INSERT INTO kullanicilar (kullanici_adi, sifre) VALUES ('cemre', 'parola456')")
    conn.commit()
    conn.close()

veritabani_hazirla()

# --- ANA SAYFA VE HAKKINDA ---
@app.route("/")
def anasayfa():
    return """
        <h1>Test Uygulaması Ana Sayfa</h1>
        <ul>
            <li><a href="/giris">Giriş Sayfası (SQLi Testi)</a></li>
            <li><a href="/yorum">Yorum Sayfası (XSS Testi)</a></li>
            <li><a href="/hakkinda">Hakkında</a></li>
        </ul>
    """

@app.route("/hakkinda")
def hakkinda():
    return """
        <h1>Hakkında</h1>
        <p>Bu uygulama güvenlik açıklarını test etmek için hazırlanmış zafiyetli laboratuvardır.</p>
        <a href="/">Ana Sayfaya Dön</a>
    """

# --- 1. ZAFİYET: SQL INJECTION (GİRİŞ) ---
@app.route("/giris", methods=["GET", "POST"])
def giris():
    mesaj = ""
    if request.method == "POST":
        kullanici = request.form.get("kullanici_adi", "")
        sifre = request.form.get("sifre", "")

        conn = sqlite3.connect("test.db")
        cursor = conn.cursor()
        
        # ZAFİYET: Parametreli sorgu yerine doğrudan string formatlama (SQLi)
        sorgu = f"SELECT * FROM kullanicilar WHERE kullanici_adi = '{kullanici}' AND sifre = '{sifre}'"
        try:
            cursor.execute(sorgu)
            kullanici_kaydi = cursor.fetchone()
            if kullanici_kaydi:
                mesaj = f"<p style='color:green;'>Giriş başarılı! Hoş geldin {kullanici_kaydi[1]}</p>"
            else:
                mesaj = "<p style='color:red;'>Hatalı kullanıcı adı veya şifre!</p>"
        except Exception as e:
            mesaj = f"<p style='color:red;'>Veritabanı Hatası: {e}</p>"
        finally:
            conn.close()

    return f"""
        <h2>Kullanıcı Girişi</h2>
        {mesaj}
        <form method="POST" action="/giris">
            <label>Kullanıcı Adı:</label><br>
            <input type="text" name="kullanici_adi"><br><br>
            <label>Şifre:</label><br>
            <input type="password" name="sifre"><br><br>
            <input type="submit" value="Giriş Yap">
        </form>
        <br><a href="/">Ana Sayfa</a>
    """

# --- 2. ZAFİYET: STORED / REFLECTED XSS (YORUM) ---
yorumlar = ["İlk örnek yorum!"]

@app.route("/yorum", methods=["GET", "POST"])
def yorum():
    if request.method == "POST":
        yeni_yorum = request.form.get("yorum_metni", "")
        if yeni_yorum:
            yorumlar.append(yeni_yorum)

    # ZAFİYET: render_template_string ile kaçışsız (unescaped) ham HTML basımı
    yorum_listesi_html = "".join([f"<li>{y}</li>" for y in yorumlar])

    sablon = f"""
        <h2>Ziyaretçi Defteri / Yorumlar</h2>
        <form method="POST" action="/yorum">
            <textarea name="yorum_metni" rows="3" cols="40" placeholder="Yorumunuzu yazın..."></textarea><br><br>
            <input type="submit" value="Yorum Gönder">
        </form>
        <h3>Önceki Yorumlar:</h3>
        <ul>
            {yorum_listesi_html}
        </ul>
        <br><a href="/">Ana Sayfa</a>
    """
    return render_template_string(sablon)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False) 
    # Sadece kendi bilgisayarımızdan erişilebilir