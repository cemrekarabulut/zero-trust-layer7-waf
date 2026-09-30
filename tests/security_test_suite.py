"""
=============================================================================
ZERO TRUST LABORATUVARI - GÜVENLİK TEST ARACI (SECURITY TEST SUITE)
=============================================================================
DİKKAT: Bu araç bir saldırı (hacking) aracı DEĞİLDİR. 
Geliştirilen Web Uygulama Güvenlik Duvarı'nın (WAF) SQLi ve XSS mutasyonlarına 
karşı dayanıklılığını ölçmek için tasarlanmış yerel bir regresyon test aracıdır.

GÜVENLİK KİLİDİ: Bu kod (Loopback Lock) sadece 127.0.0.1 ve localhost 
üzerinde çalışacak şekilde sınırlandırılmıştır. Dış ağlara kapalıdır.
=============================================================================
"""
from report import json_rapor_olustur, html_rapor_olustur
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import argparse
import sys

# --- 1. TEST PAYLOADLARI (WAF DAYANIKLILIK TESTİ) ---
SQLI_PAYLOADLARI = [
    "' OR '1'='1",
    "'",
    "' OR '1'='1' --",
    "admin'--",
    "' oR '1'='1",                   # Büyük/Küçük harf karma (Case Evasion)
    "%27%20OR%20%271%27%3D%271",     # URL Encoding (IDS Bypass Testi)
    "' OR/**/'1'='1"                 # SQL Yorum satırı hilesi
]

SQL_HATA_IMZALARI = [
    "sql syntax",
    "sqlite3.operationalerror",
    "sql hatası",
    "unrecognized token",
]

XSS_ISARETLEYICI = "XSS_TEST_12345"
XSS_PAYLOADLARI = [
    f"<script>alert('{XSS_ISARETLEYICI}')</script>",
    f"<sCrIpT>alert('{XSS_ISARETLEYICI}')</ScRiPt>",            
    f"%3Cscript%3Ealert('{XSS_ISARETLEYICI}')%3C%2Fscript%3E",  
    f"<img src=x onerror=alert('{XSS_ISARETLEYICI}')>"          
]


def formlari_kesfet(url):
    cevap = requests.get(url, timeout=5)
    corba = BeautifulSoup(cevap.text, "html.parser")

    bulunan_formlar = []
    for form in corba.find_all("form"):
        form_bilgisi = {
            "action": urljoin(url, form.get("action") or url),
            "method": (form.get("method") or "GET").upper(),
            "inputlar": []
        }
        for input_etiketi in form.find_all(["input", "textarea"]):
            input_adi = input_etiketi.get("name")
            if input_adi:
                form_bilgisi["inputlar"].append(input_adi)

        if form_bilgisi["inputlar"]:
            bulunan_formlar.append(form_bilgisi)

    return bulunan_formlar

def sayfadaki_linkleri_bul(url, corba):
    hedef_domain = urlparse(url).hostname
    linkler = set()
    for link_etiketi in corba.find_all("a", href=True):
        tam_url = urljoin(url, link_etiketi["href"])
        link_domain = urlparse(tam_url).hostname
        if link_domain == hedef_domain:
            linkler.add(tam_url)
    return linkler

def siteyi_gez(baslangic_url, max_derinlik=2):
    ziyaret_edildi = set()
    gezilecekler = {baslangic_url}
    tum_sayfalar = []
    derinlik = 0

    while gezilecekler and derinlik < max_derinlik:
        yeni_gezilecekler = set()
        for url in gezilecekler:
            if url in ziyaret_edildi:
                continue

            ziyaret_edildi.add(url)
            print(f"[TEST KAPSAMI] {url} haritalanıyor...")
            try:
                cevap = requests.get(url, timeout=5)
                corba = BeautifulSoup(cevap.text, "html.parser")
                tum_sayfalar.append(url)
                yeni_linkler = sayfadaki_linkleri_bul(url, corba)
                yeni_gezilecekler.update(yeni_linkler - ziyaret_edildi)
            except requests.RequestException as hata:
                print(f"  [UYARI] {url} adresine erişilemedi: {hata}")

        gezilecekler = yeni_gezilecekler
        derinlik += 1

    return tum_sayfalar

def form_gonder(form, veri):
    try:
        if form["method"] == "POST":
            return requests.post(form["action"], data=veri, timeout=5)
        else:
            return requests.get(form["action"], params=veri, timeout=5)
    except requests.exceptions.RequestException:
        return None

def sqli_tara_form(form):
    sonuclar = []
    print(f"\n[*] SQLi Testleri Başlıyor: {form['action']} — alanlar: {form['inputlar']}")

    for payload in SQLI_PAYLOADLARI:
        veri = {alan: payload for alan in form["inputlar"]}
        cevap = form_gonder(form, veri)
        
        if not cevap:
            continue
            
        cevap_metni = cevap.text.lower()

        if cevap.status_code == 403:
            continue

        for imza in SQL_HATA_IMZALARI:
            if imza in cevap_metni:
                print(f"  [🚨 ZAFİYET BULUNDU] Hata tabanlı SQLi (WAF Bypass)! Payload: {payload}")
                sonuclar.append({
                    "tur": "SQL Injection (hata tabanlı)",
                    "url": form["action"],
                    "payload": payload,
                    "risk": "Critical"
                })
                break

        if "başarılı" in cevap_metni or "success" in cevap_metni:
            print(f"  [🚨 ZAFİYET BULUNDU] Mantık tabanlı SQLi (WAF Bypass)! Payload: {payload}")
            sonuclar.append({
                "tur": "SQL Injection (mantık tabanlı)",
                "url": form["action"],
                "payload": payload,
                "risk": "Critical"
            })

    return sonuclar

def xss_tara_form(form):
    sonuclar = []
    print(f"\n[*] XSS Testleri Başlıyor: {form['action']} — alanlar: {form['inputlar']}")

    for payload in XSS_PAYLOADLARI:
        veri = {alan: payload for alan in form["inputlar"]}
        cevap = form_gonder(form, veri)

        if not cevap or cevap.status_code == 403:
            continue 

        if payload in cevap.text or XSS_ISARETLEYICI in cevap.text:
            print(f"  [🚨 ZAFİYET BULUNDU] Yansıyan XSS (WAF Bypass)! Payload: {payload}")
            sonuclar.append({
                "tur": "XSS (yansıyan)",
                "url": form["action"],
                "payload": payload,
                "risk": "High"
            })

    return sonuclar

def siteyi_tara(baslangic_url, rapor_olustur=True, crawl=True):
    print(f"\n{'='*60}\nOTOMATİK GÜVENLİK TESTİ BAŞLIYOR: {baslangic_url}\n{'='*60}")
    taranacak_sayfalar = siteyi_gez(baslangic_url) if crawl else [baslangic_url]

    tum_sonuclar = []
    for sayfa in taranacak_sayfalar:
        formlar = formlari_kesfet(sayfa)
        if not formlar:
            continue
        print(f"\n[+] {sayfa} sayfasında {len(formlar)} test noktası bulundu.")
        for form in formlar:
            tum_sonuclar.extend(sqli_tara_form(form))
            tum_sonuclar.extend(xss_tara_form(form))

    print(f"\n{'='*60}")
    if len(tum_sonuclar) == 0:
        print("[BAŞARILI] Sömürülebilir zafiyet bulunamadı (0 bulgu).")
    else:
        print(f"[BAŞARISIZ] WAF Atlatıldı! Toplam {len(tum_sonuclar)} zafiyet sömürülebilir durumda.")
    print(f"{'='*60}\n")

    if rapor_olustur:
        rapor = json_rapor_olustur(tum_sonuclar, hedef_url=baslangic_url)
        html_rapor_olustur(rapor)

    return tum_sonuclar

def argumanlari_oku():
    parser = argparse.ArgumentParser(description="Zero Trust WAF Dayanıklılık Test Aracı")
    parser.add_argument("--no-crawl", action="store_true", help="Sadece verilen URL'yi test et")
    parser.add_argument("--url", action="append", required=True, help="Test edilecek hedef URL")
    # VARSAYILAN RAPOR YOLU DÜZELTİLDİ:
    parser.add_argument("--output", default="reports/test_raporu", help="Çıktı rapor konumu")
    parser.add_argument("--no-report", action="store_true", help="Sadece terminale yaz, rapor üretme")
    return parser.parse_args()

if __name__ == "__main__":
    argumanlar = argumanlari_oku()

    # =======================================================================
    # 🔒 LOOPBACK (LOCALHOST) GÜVENLİK KİLİDİ (YAMANDI)
    # URL Parsing Bypass zafiyetine karşı '.hostname' kullanıldı.
    # =======================================================================
    for hedef in argumanlar.url:
        hedef_domain = urlparse(hedef).hostname 
        
        if hedef_domain not in ["127.0.0.1", "localhost", "::1"]:
            print("\n[🔴 GÜVENLİK İHLALİ DENEMESİ]")
            print(f"Bu test aracı sadece etik test amacıyla sınırlandırılmıştır.")
            print(f"'{hedef_domain}' hedefine test yapılmasına izin verilmiyor.")
            print("Sadece 'localhost', '127.0.0.1' veya '::1' hedefleri kabul edilmektedir.\n")
            sys.exit(1)
    # =======================================================================

    tum_sonuclar = []
    for hedef in argumanlar.url:
        sonuclar = siteyi_tara(hedef, rapor_olustur=False, crawl=not argumanlar.no_crawl)
        tum_sonuclar.extend(sonuclar)

    if not argumanlar.no_report:
        rapor = json_rapor_olustur(tum_sonuclar, hedef_url=", ".join(argumanlar.url), dosya_adi=f"{argumanlar.output}.json")
        html_rapor_olustur(rapor, dosya_adi=f"{argumanlar.output}.html")