#!/usr/bin/python3
"""BasicPortScanner v2.0 - Çok iş parçacıklı basit TCP port tarayıcı."""

import argparse
import socket
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

BANNER = r"""
    ____             __     _____
   / __ \____  _____/ /_   / ___/_________ _____  ____  ___  _____
  / /_/ / __ \/ ___/ __/   \__ \/ ___/ __ `/ __ \/ __ \/ _ \/ ___/
 / ____/ /_/ / /  / /_    ___/ / /__/ /_/ / / / / / / /  __/ /
/_/    \____/_/   \__/   /____/\___/\__,_/_/ /_/_/ /_/\___/_/

------------------- Made by CyberClay ------------------- v2.0 ---
"""

MIN_PORT, MAX_PORT = 1, 65535

# Sık kullanılan portlar (hızlı tarama için)
COMMON_PORTS = [
    20, 21, 22, 23, 25, 53, 67, 68, 69, 80, 110, 111, 119, 123, 135, 137,
    138, 139, 143, 161, 162, 179, 389, 443, 445, 465, 514, 515, 587, 631,
    636, 873, 993, 995, 1080, 1194, 1433, 1521, 1723, 2049, 2082, 2083,
    2181, 2375, 2376, 3000, 3128, 3306, 3389, 5000, 5060, 5432, 5601, 5900,
    5985, 5986, 6379, 6443, 8000, 8008, 8080, 8081, 8443, 8888, 9000, 9090,
    9200, 9300, 11211, 27017,
]

# ANSI renkleri (terminal desteklemiyorsa kapatılır)
USE_COLOR = sys.stdout.isatty()


def renk(metin, kod):
    return f"\033[{kod}m{metin}\033[0m" if USE_COLOR else metin


def yesil(m):
    return renk(m, "32")


def kirmizi(m):
    return renk(m, "31")


def sari(m):
    return renk(m, "33")


def parse_ports(spec):
    """'22,80,100-200' gibi bir ifadeyi sıralı port listesine çevirir."""
    spec = spec.strip().lower()
    if spec in ("top", "common", "yaygin", "yaygın"):
        return sorted(COMMON_PORTS)
    if spec in ("all", "hepsi", "-"):
        return list(range(MIN_PORT, MAX_PORT + 1))

    ports = set()
    for parca in spec.split(","):
        parca = parca.strip()
        if not parca:
            continue
        if "-" in parca:
            bas, bit = parca.split("-", 1)
            bas, bit = int(bas), int(bit)
            if bas > bit:
                bas, bit = bit, bas
        else:
            bas = bit = int(parca)
        if bas < MIN_PORT or bit > MAX_PORT:
            raise ValueError(f"Port {MIN_PORT}-{MAX_PORT} aralığında olmalı: {parca}")
        ports.update(range(bas, bit + 1))
    if not ports:
        raise ValueError("Hiç port belirtilmedi.")
    return sorted(ports)


def servis_adi(port):
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "bilinmiyor"


def banner_al(soket):
    """Açık porttan servis bilgisini (banner) okumaya çalışır."""
    soket.settimeout(1.5)
    try:
        veri = soket.recv(1024)
    except OSError:
        veri = b""
    if not veri:
        # Bazı servisler (HTTP gibi) önce istemcinin konuşmasını bekler
        try:
            soket.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
            veri = soket.recv(1024)
        except OSError:
            return ""
    satirlar = veri.decode(errors="ignore").strip().splitlines()
    return satirlar[0][:80] if satirlar else ""


def port_tara(ip, port, zaman_asimi, banner):
    """Tek bir portu tarar. Açıksa (port, banner) döndürür, değilse None."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soket:
        soket.settimeout(zaman_asimi)
        if soket.connect_ex((ip, port)) != 0:
            return None
        return port, banner_al(soket) if banner else ""


def tarama(ip, portlar, zaman_asimi=1.0, is_parcacigi=200, banner=False):
    """Portları paralel tarar ve açık portların listesini döndürür."""
    acik = []
    kilit = threading.Lock()
    toplam = len(portlar)
    bitti = 0

    havuz = ThreadPoolExecutor(max_workers=is_parcacigi)
    try:
        isler = [havuz.submit(port_tara, ip, p, zaman_asimi, banner) for p in portlar]
        for is_ in as_completed(isler):
            sonuc = is_.result()
            with kilit:
                bitti += 1
                if sonuc:
                    port, bnr = sonuc
                    acik.append(sonuc)
                    satir = f"  [+] {port:<6}/tcp  açık   {servis_adi(port):<15}"
                    if bnr:
                        satir += f" {bnr}"
                    temizle = "\r" + " " * 40 + "\r" if USE_COLOR else ""
                    print(temizle + yesil(satir))
                if USE_COLOR and (bitti % 50 == 0 or bitti == toplam):
                    print(f"\r  İlerleme: {bitti}/{toplam} ({bitti * 100 // toplam}%)",
                          end="", flush=True)
    except KeyboardInterrupt:
        # Kuyruktaki işleri iptal et, beklemeden çık
        havuz.shutdown(wait=False, cancel_futures=True)
        raise
    havuz.shutdown()
    if USE_COLOR:
        print()
    return sorted(acik)


def hedef_coz(hedef):
    hedef = hedef.strip()
    if not hedef:
        raise ValueError("Hedef boş olamaz.")
    return socket.gethostbyname(hedef)


def sonuclari_kaydet(dosya, hedef, ip, acik):
    with open(dosya, "w", encoding="utf-8") as f:
        f.write(f"Hedef: {hedef} ({ip})\n")
        f.write(f"Tarih: {datetime.now():%Y-%m-%d %H:%M:%S}\n\n")
        f.write("PORT\tSERVİS\tBANNER\n")
        for port, bnr in acik:
            f.write(f"{port}/tcp\t{servis_adi(port)}\t{bnr}\n")


def interaktif_ayarlar():
    """Argüman verilmezse kullanıcıdan ayarları sorar."""
    print("Özel bir port aralığı/listesi girmek için; [1]")
    print("İlk 1000 portu taramak için;            [2]")
    print("Yaygın portları taramak için (hızlı);   [3]")
    print("Tüm portları taramak için (1-65535);    [4]\n")

    while True:
        secim = input("Tarama türünü giriniz: ").strip()
        if secim in ("1", "2", "3", "4"):
            break
        print(kirmizi("Geçersiz seçim, 1-4 arasında bir değer giriniz."))

    hedef = input("IP adresi veya alan adı giriniz: ")

    if secim == "1":
        while True:
            spec = input("Portları girin (örn: 22,80,443 veya 1-1024): ")
            try:
                portlar = parse_ports(spec)
                break
            except ValueError as e:
                print(kirmizi(f"Hatalı giriş: {e}"))
    elif secim == "2":
        portlar = list(range(1, 1001))
    elif secim == "3":
        portlar = sorted(COMMON_PORTS)
    else:
        portlar = list(range(MIN_PORT, MAX_PORT + 1))

    banner = input("Servis banner bilgisi alınsın mı? [e/H]: ").strip().lower() in ("e", "evet", "y")
    return hedef, portlar, banner


def argumanlari_al():
    p = argparse.ArgumentParser(
        description="BasicPortScanner v2.0 - Çok iş parçacıklı TCP port tarayıcı",
        epilog="Örnek: python3 scanner.py scanme.nmap.org -p 1-1024 -t 300 -b",
    )
    p.add_argument("hedef", nargs="?", help="IP adresi veya alan adı (verilmezse interaktif mod)")
    p.add_argument("-p", "--ports", default="1-1000",
                   help="Portlar: '22,80,443', '1-1024', 'top' (yaygın) veya 'all' (varsayılan: 1-1000)")
    p.add_argument("-t", "--threads", type=int, default=200, help="İş parçacığı sayısı (varsayılan: 200)")
    p.add_argument("--timeout", type=float, default=1.0, help="Bağlantı zaman aşımı, saniye (varsayılan: 1.0)")
    p.add_argument("-b", "--banner", action="store_true", help="Açık portlardan banner bilgisi al")
    p.add_argument("-o", "--output", help="Sonuçları dosyaya kaydet")
    p.add_argument("--no-color", action="store_true", help="Renkli çıktıyı kapat")
    return p.parse_args()


def main():
    global USE_COLOR
    args = argumanlari_al()
    if args.no_color:
        USE_COLOR = False

    print(BANNER)

    if args.hedef:
        hedef, banner = args.hedef, args.banner
        try:
            portlar = parse_ports(args.ports)
        except ValueError as e:
            print(kirmizi(f"Hatalı port belirtimi: {e}"))
            sys.exit(2)
    else:
        hedef, portlar, banner = interaktif_ayarlar()

    if args.threads < 1 or args.timeout <= 0:
        print(kirmizi("İş parçacığı sayısı ve zaman aşımı pozitif olmalıdır."))
        sys.exit(2)

    ip = hedef_coz(hedef)
    print("-" * 66)
    print(f"  Hedef      : {hedef} ({ip})")
    print(f"  Port sayısı: {len(portlar)}")
    print(f"  Başlangıç  : {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("-" * 66)

    baslangic = time.perf_counter()
    acik = tarama(ip, portlar, args.timeout, min(args.threads, len(portlar)), banner)
    sure = time.perf_counter() - baslangic

    print("-" * 66)
    if acik:
        print(yesil(f"  {len(acik)} açık port bulundu."))
    else:
        print(sari("  Açık port bulunamadı."))
    print(f"  Tarama {sure:.2f} saniyede tamamlandı.")

    if args.output:
        sonuclari_kaydet(args.output, hedef, ip, acik)
        print(f"  Sonuçlar '{args.output}' dosyasına kaydedildi.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgramdan Çıkılıyor...")
        sys.exit(130)
    except socket.gaierror:
        print(kirmizi("Adres çözümlenemedi, IP adresini/alan adını düzgün girdiğinizden emin olunuz."))
        sys.exit(1)
    except ValueError as e:
        print(kirmizi(f"Hata: {e}"))
        sys.exit(1)
    except OSError as e:
        print(kirmizi(f"Bağlantı başarısız: {e}"))
        sys.exit(1)
