"""Tarama sonuçlarını JSON ve HTML rapor formatına dönüştürür."""

import json
import time

def json_rapor_olustur(sonuclar, hedef_url, dosya_adi="rapor.json"):
    rapor = {
        "hedef": hedef_url,
        "tarama_zamani": time.strftime("%Y-%m-%d %H:%M:%S"),
        "toplam_zafiyet": len(sonuclar),
        "bulgular": sonuclar
    }
    with open(dosya_adi, "w", encoding="utf-8") as dosya:
        json.dump(rapor, dosya, ensure_ascii=False, indent=2)
    print(f"[+] JSON rapor kaydedildi: {dosya_adi}")
    return rapor


def html_rapor_olustur(rapor, dosya_adi="rapor.html"):
    risk_renkleri = {
        "Critical": "#dc2626",
        "High": "#ea580c",
        "Medium": "#ca8a04",
        "Low": "#65a30d"
    }

    bulgu_satirlari = ""
    for b in rapor["bulgular"]:
        renk = risk_renkleri.get(b["risk"], "#6b7280")
        bulgu_satirlari += f"""
        <tr>
            <td><span style="background:{renk}; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em;">{b['risk']}</span></td>
            <td>{b['tur']}</td>
            <td><code>{b['url']}</code></td>
            <td><code>{b['payload']}</code></td>
        </tr>
        """

    if not bulgu_satirlari:
        bulgu_satirlari = '<tr><td colspan="4" style="text-align:center; color:#666;">Zafiyet bulunamadı 🎉</td></tr>'

    html_icerik = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>Güvenlik Tarama Raporu</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #0f1117; color: #e6e6e6; padding: 40px; }}
            h1 {{ color: #ef4444; }}
            .ozet {{ background: #1a1d27; padding: 20px; border-radius: 10px; margin-bottom: 30px; }}
            .ozet-sayi {{ font-size: 2em; font-weight: bold; color: #f59e0b; }}
            table {{ width: 100%; border-collapse: collapse; background: #1a1d27; border-radius: 10px; overflow: hidden; }}
            th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #2a2d3a; }}
            th {{ background: #22252f; color: #999; font-size: 0.85em; text-transform: uppercase; }}
            code {{ background: #2a2d3a; padding: 2px 6px; border-radius: 4px; font-size: 0.85em; }}
        </style>
    </head>
    <body>
        <h1>🛡️ Güvenlik Tarama Raporu</h1>
        <div class="ozet">
            <div>Hedef: <code>{rapor['hedef']}</code></div>
            <div>Tarama Zamanı: {rapor['tarama_zamani']}</div>
            <div style="margin-top:10px;">Toplam Bulgu: <span class="ozet-sayi">{rapor['toplam_zafiyet']}</span></div>
        </div>
        <table>
            <tr><th>Risk</th><th>Zafiyet Türü</th><th>URL</th><th>Payload</th></tr>
            {bulgu_satirlari}
        </table>
    </body>
    </html>
    """

    with open(dosya_adi, "w", encoding="utf-8") as dosya:
        dosya.write(html_icerik)
    print(f"[+] HTML rapor kaydedildi: {dosya_adi}")