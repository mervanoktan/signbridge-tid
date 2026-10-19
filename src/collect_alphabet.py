"""
SignBridge - TİD parmak alfabesi veri toplama aracı (Aşama 1)

Kameradan TİD alfabe harflerini kaydeder:
  - Her örnek için iki elin 21'er anahtar noktası  -> data/alphabet/landmarks.csv
  - Ellerin bulunduğu bölgenin kırpılmış görüntüsü -> data/alphabet/images/<harf>/<ornek_id>.jpg

Kullanım:
  python src/collect_alphabet.py --kamera-listele             # bağlı kameraları listele
  python src/collect_alphabet.py --kisi mervan                # varsayılan kamera (0)
  python src/collect_alphabet.py --kisi mervan --kamera 1     # başka bir kamera (ör. Iriun)
  python src/collect_alphabet.py --kisi mervan --harf C       # C harfinden başla
  python src/collect_alphabet.py --kisi mervan --baskin-el sol  # tek elli harfleri sol elle yap

Tuşlar:
  SPACE : kaydı başlat (3 sn geri sayım + 5 sn kayıt)
  S / X : kaydı onayla / iptal et
  N / P : sonraki / önceki harf
  Q     : çıkış
"""

import argparse
import csv
import time
from datetime import datetime
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision
from PIL import Image, ImageDraw, ImageFont

# --- Ayarlar ----------------------------------------------------------------

PROJE = Path(__file__).resolve().parent.parent
MODEL_YOLU = PROJE / "models" / "mediapipe" / "hand_landmarker.task"
VERI_KLASORU = PROJE / "data" / "alphabet"
CSV_YOLU = VERI_KLASORU / "landmarks.csv"
GORUNTU_KLASORU = VERI_KLASORU / "images"

HARFLER = list("ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ")  # 29 harf
TEK_ELLI_HARFLER = set("CILOPUV")  # geri kalanlar iki elle yapılır (docs/KAYNAKLAR.md)

GERI_SAYIM_SN = 3
KAYIT_SN = 5
KARE_ATLAMA = 2       # her 2 karede bir örnek al (ardışık kareler neredeyse aynı)
HEDEF_ORNEK = 300     # harf başına hedef örnek sayısı
GORUNTU_BOYUTU = 224  # kırpılan el görüntüsünün boyutu (CNN deneyi için)

# El iskeletini çizmek için 21 noktanın birbirine bağlantıları
EL_BAGLANTILARI = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # başparmak
    (0, 5), (5, 6), (6, 7), (7, 8),          # işaret parmağı
    (5, 9), (9, 10), (10, 11), (11, 12),     # orta parmak
    (9, 13), (13, 14), (14, 15), (15, 16),   # yüzük parmağı
    (13, 17), (17, 18), (18, 19), (19, 20),  # serçe parmak
    (0, 17),                                 # avuç
]


# --- El tespiti -------------------------------------------------------------

def el_dedektoru_olustur():
    """MediaPipe HandLandmarker modelini video modunda, iki el için hazırlar."""
    secenekler = vision.HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(MODEL_YOLU)),
        running_mode=vision.RunningMode.VIDEO,  # kareler arası takip yapar, daha hızlı ve kararlı
        num_hands=2,                            # TİD alfabesi çoğunlukla iki elle yapılır
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    return vision.HandLandmarker.create_from_options(secenekler)


def elleri_ayir(sonuc):
    """MediaPipe sonucunu {'sol': (21, 3) dizi veya None, 'sag': ...} sözlüğüne çevirir."""
    bulunanlar = []
    for noktalar, taraf in zip(sonuc.hand_landmarks, sonuc.handedness):
        dizi = np.array([[p.x, p.y, p.z] for p in noktalar], dtype=np.float32)
        # ÖNEMLİ: Testte sağ el kaldırıldığında MediaPipe "Left" etiketi verdi, yani bizim kurulumumuzda
        # (ayna çevrilmiş görüntü) etiketler ters geliyor. Bu yüzden "Left" etiketini sağ el olarak alıyoruz.
        etiket = "sag" if taraf[0].category_name == "Left" else "sol"
        bulunanlar.append((etiket, dizi))

    # ÖNEMLİ: MediaPipe bazen iki ele aynı etiketi verir. Bu durumda ellerin görüntüdeki
    # konumuna bakarız: ayna görüntüsünde sol el ekranın sol tarafında kalır.
    if len(bulunanlar) == 2 and bulunanlar[0][0] == bulunanlar[1][0]:
        bulunanlar.sort(key=lambda b: b[1][:, 0].mean())
        bulunanlar = [("sol", bulunanlar[0][1]), ("sag", bulunanlar[1][1])]

    eller = {"sol": None, "sag": None}
    for etiket, dizi in bulunanlar:
        eller[etiket] = dizi
    return eller


# --- Kayıt ------------------------------------------------------------------

def csv_basliklari():
    basliklar = ["ornek_id", "kisi", "harf", "el_sayisi"]
    for el in ("sol", "sag"):
        basliklar.append(f"{el}_var")
        for i in range(21):
            basliklar += [f"{el}_{i}_x", f"{el}_{i}_y", f"{el}_{i}_z"]
    return basliklar


def satir_olustur(ornek_id, kisi, harf, eller):
    """Bir örneği CSV satırına çevirir. Görünmeyen elin yerine sıfır yazılır."""
    el_sayisi = sum(e is not None for e in eller.values())
    satir = [ornek_id, kisi, harf, el_sayisi]
    for el in ("sol", "sag"):
        if eller[el] is None:
            satir += [0] + [0.0] * 63
        else:
            satir += [1] + eller[el].flatten().round(5).tolist()
    return satir


def el_bolgesini_kirp(kare, eller):
    """Ellerin tamamını içeren kare bir bölgeyi kesip GORUNTU_BOYUTU'na küçültür."""
    h, w = kare.shape[:2]
    noktalar = np.vstack([e for e in eller.values() if e is not None])
    xs, ys = noktalar[:, 0] * w, noktalar[:, 1] * h

    kenar = max(xs.max() - xs.min(), ys.max() - ys.min()) * 1.3  # %30 kenar payı
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    x1, y1 = int(max(cx - kenar / 2, 0)), int(max(cy - kenar / 2, 0))
    x2, y2 = int(min(cx + kenar / 2, w)), int(min(cy + kenar / 2, h))

    kirpik = kare[y1:y2, x1:x2]
    if kirpik.size == 0:
        return None
    return cv2.resize(kirpik, (GORUNTU_BOYUTU, GORUNTU_BOYUTU))


def goruntu_kaydet(goruntu, yol):
    # ÖNEMLİ: cv2.imwrite Windows'ta Türkçe karakter içeren yollara (Ç, Ş, Ğ...) yazamıyor.
    # Bu yüzden görüntüyü önce bellekte JPEG'e çevirip sonra dosyaya yazıyoruz.
    yol.parent.mkdir(parents=True, exist_ok=True)
    basarili, veri = cv2.imencode(".jpg", goruntu)
    if basarili:
        veri.tofile(str(yol))


def tamponu_kaydet(tampon):
    """Onaylanan kaydın örneklerini CSV'ye, görüntülerini klasöre yazar."""
    yeni_dosya = not CSV_YOLU.exists()
    CSV_YOLU.parent.mkdir(parents=True, exist_ok=True)
    with open(CSV_YOLU, "a", encoding="utf-8", newline="") as f:
        yazici = csv.writer(f)
        if yeni_dosya:
            yazici.writerow(csv_basliklari())
        for satir, goruntu in tampon:
            yazici.writerow(satir)
            if goruntu is not None:
                ornek_id, harf = satir[0], satir[2]
                goruntu_kaydet(goruntu, GORUNTU_KLASORU / harf / f"{ornek_id}.jpg")


def mevcut_sayilar(kisi):
    """Daha önce bu kişi için her harften kaç örnek toplandığını sayar."""
    sayilar = {h: 0 for h in HARFLER}
    if CSV_YOLU.exists():
        with open(CSV_YOLU, encoding="utf-8", newline="") as f:
            for satir in csv.DictReader(f):
                if satir["kisi"] == kisi and satir["harf"] in sayilar:
                    sayilar[satir["harf"]] += 1
    return sayilar


# --- Ekran ------------------------------------------------------------------

def font_yukle(boyut):
    for ad in ("arial.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(ad, boyut)
        except OSError:
            pass
    return ImageFont.load_default()


def yazi_yaz(kare, yazilar):
    """OpenCV Türkçe karakter yazamadığı için yazıları Pillow ile çizer.
    yazilar: [(metin, (x, y), font, (R, G, B)), ...]"""
    resim = Image.fromarray(cv2.cvtColor(kare, cv2.COLOR_BGR2RGB))
    ciz = ImageDraw.Draw(resim)
    for metin, konum, font, renk in yazilar:
        ciz.text(konum, metin, font=font, fill=renk, stroke_width=2, stroke_fill=(0, 0, 0))
    return cv2.cvtColor(np.array(resim), cv2.COLOR_RGB2BGR)


def iskelet_ciz(kare, eller):
    h, w = kare.shape[:2]
    renkler = {"sol": (255, 140, 0), "sag": (0, 200, 255)}  # BGR: sol el mavi, sağ el turuncu
    for el, noktalar in eller.items():
        if noktalar is None:
            continue
        pts = (noktalar[:, :2] * [w, h]).astype(int)
        for a, b in EL_BAGLANTILARI:
            cv2.line(kare, tuple(pts[a]), tuple(pts[b]), renkler[el], 2)
        for p in pts:
            cv2.circle(kare, tuple(p), 4, (255, 255, 255), -1)


# --- Kamera -----------------------------------------------------------------

def kamera_ac(kaynak):
    """Kaynak bir sayıysa (0, 1, 2...) bilgisayara bağlı kamerayı, değilse video adresini açar."""
    if kaynak.isdigit():
        kamera = cv2.VideoCapture(int(kaynak), cv2.CAP_DSHOW)
    else:
        kamera = cv2.VideoCapture(kaynak)
    kamera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    kamera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    return kamera


def kameralari_listele():
    print("Kameralar aranıyor...")
    bulundu = False
    for i in range(6):
        kamera = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        basarili, kare = kamera.read()
        if basarili:
            print(f"  Kamera {i}: çalışıyor ({kare.shape[1]}x{kare.shape[0]})")
            bulundu = True
        kamera.release()
    if not bulundu:
        print("  Hiç kamera bulunamadı.")


# --- Ana program ------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="TİD parmak alfabesi veri toplama aracı")
    ap.add_argument("--kisi", default="mervan", help="kaydı yapan kişinin adı")
    ap.add_argument("--kamera", default="0", help="kamera numarası veya video adresi")
    ap.add_argument("--goruntu-kaydetme", action="store_true", help="el görüntülerini kaydetme")
    ap.add_argument("--kamera-listele", action="store_true", help="bağlı kameraları listele")
    ap.add_argument("--harf", default="A", help="başlangıç harfi (ör. --harf C)")
    ap.add_argument("--baskin-el", choices=["sag", "sol"], default="sag",
                    help="tek elli harflerde (C, I, L, O, P, U, V) kullanılan el")
    args = ap.parse_args()

    if args.kamera_listele:
        kameralari_listele()
        return

    kamera = kamera_ac(args.kamera)
    if not kamera.isOpened():
        print(f"Kamera açılamadı: {args.kamera}  (--kamera-listele ile kameraları görebilirsin)")
        return

    dedektor = el_dedektoru_olustur()
    sayilar = mevcut_sayilar(args.kisi)
    font_buyuk, font_kucuk = font_yukle(44), font_yukle(24)

    harf_no = HARFLER.index(args.harf.upper()) if args.harf.upper() in HARFLER else 0
    durum = "BEKLE"          # BEKLE -> GERI_SAYIM -> KAYIT -> ONAY -> BEKLE
    durum_baslangic = 0.0
    tampon = []              # onay bekleyen örnekler: (csv satırı, kırpılmış görüntü)
    kare_sayaci = 0
    onceki_zaman_ms = -1

    cv2.namedWindow("SignBridge - Veri Toplama", cv2.WINDOW_NORMAL)

    while True:
        basarili, kare = kamera.read()
        if not basarili:
            print("Kameradan görüntü alınamadı.")
            break

        # ÖNEMLİ: Görüntüyü yatayda çeviriyoruz (ayna görüntüsü). Hem kullanıcı kendini ayna gibi
        # görür, hem de MediaPipe'ın sol/sağ el etiketleri gerçek ellerle eşleşir.
        kare = cv2.flip(kare, 1)
        temiz_kare = kare.copy()  # görüntü kaydı için, üzerine çizim yapılmamış hâli

        # ÖNEMLİ: OpenCV görüntüyü BGR, MediaPipe RGB sırasıyla bekler.
        rgb = cv2.cvtColor(kare, cv2.COLOR_BGR2RGB)
        mp_goruntu = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        zaman_ms = max(int(time.monotonic() * 1000), onceki_zaman_ms + 1)  # video modu artan zaman ister
        onceki_zaman_ms = zaman_ms
        eller = elleri_ayir(dedektor.detect_for_video(mp_goruntu, zaman_ms))

        harf = HARFLER[harf_no]
        tek_elli = harf in TEK_ELLI_HARFLER
        if tek_elli:
            # ÖNEMLİ: Tek elli harflerde sadece baskın el (varsayılan: sağ) kullanılır. Diğer el kadrajda
            # görünse bile yok sayılır; böylece her örnekte aynı el aynı sütunlarda kayıtlı olur.
            diger_el = "sol" if args.baskin_el == "sag" else "sag"
            eller[diger_el] = None
            eller_tamam = eller[args.baskin_el] is not None
            gereken_yazisi = f"Gereken: {'SAĞ' if args.baskin_el == 'sag' else 'SOL'} el"
        else:
            eller_tamam = eller["sol"] is not None and eller["sag"] is not None
            gereken_yazisi = "Gereken: iki el"

        # --- Durum makinesi ---
        simdi = time.monotonic()
        if durum == "GERI_SAYIM" and simdi - durum_baslangic >= GERI_SAYIM_SN:
            durum, durum_baslangic, kare_sayaci = "KAYIT", simdi, 0
        elif durum == "KAYIT":
            if simdi - durum_baslangic >= KAYIT_SN:
                durum = "ONAY"
            else:
                kare_sayaci += 1
                # ÖNEMLİ: Sadece gereken sayıda el görünüyorsa ve her KARE_ATLAMA karede bir kayıt alınır.
                if eller_tamam and kare_sayaci % KARE_ATLAMA == 0:
                    ornek_id = f"{args.kisi}_{datetime.now():%Y%m%d_%H%M%S_%f}"
                    goruntu = None if args.goruntu_kaydetme else el_bolgesini_kirp(temiz_kare, eller)
                    tampon.append((satir_olustur(ornek_id, args.kisi, harf, eller), goruntu))

        # --- Ekran ---
        iskelet_ciz(kare, eller)
        h, w = kare.shape[:2]
        beyaz, yesil, kirmizi, sari = (255, 255, 255), (80, 255, 80), (255, 80, 80), (255, 220, 0)

        if durum == "BEKLE":
            durum_yazisi, durum_rengi = "SPACE: kaydı başlat", beyaz
        elif durum == "GERI_SAYIM":
            kalan = GERI_SAYIM_SN - int(simdi - durum_baslangic)
            durum_yazisi, durum_rengi = f"Hazırlan... {kalan}", sari
        elif durum == "KAYIT":
            durum_yazisi, durum_rengi = f"KAYIT  ●  {len(tampon)} örnek", kirmizi
        else:
            durum_yazisi, durum_rengi = f"{len(tampon)} örnek toplandı.  S: kaydet   X: iptal", sari

        # Her elin bileğinin yanına SOL / SAĞ yazısı (etiketlerin doğruluğunu gözle kontrol etmek için)
        el_yazilari = []
        for el, noktalar in eller.items():
            if noktalar is not None:
                bilek = (int(noktalar[0, 0] * w) + 10, int(noktalar[0, 1] * h) + 10)
                el_yazilari.append(("SOL" if el == "sol" else "SAĞ", bilek, font_kucuk, sari))

        kare = yazi_yaz(kare, el_yazilari + [
            (f"Harf: {harf}   ({harf_no + 1}/{len(HARFLER)})", (20, 15), font_buyuk, beyaz),
            (f"Kişi: {args.kisi}    Kayıtlı: {sayilar[harf]} / {HEDEF_ORNEK}", (20, 70), font_kucuk, beyaz),
            (f"{gereken_yazisi}  ({'TAMAM' if eller_tamam else 'EKSİK'})", (20, h - 110), font_kucuk,
             yesil if eller_tamam else kirmizi),
            (durum_yazisi, (20, h - 75), font_kucuk, durum_rengi),
            ("N: sonraki   P: önceki   SPACE: kayıt   Q: çıkış", (20, h - 40), font_kucuk, beyaz),
        ])
        cv2.imshow("SignBridge - Veri Toplama", kare)

        # --- Tuşlar ---
        tus = cv2.waitKey(1) & 0xFF
        if ord("A") <= tus <= ord("Z"):
            tus += 32  # Caps Lock / Shift açıkken basılan büyük harfleri küçük harfe çevir
        if tus == ord("q"):
            break
        if durum == "BEKLE":
            if tus == ord(" "):
                durum, durum_baslangic, tampon = "GERI_SAYIM", time.monotonic(), []
            elif tus == ord("n"):
                harf_no = (harf_no + 1) % len(HARFLER)
                print(f"Harf: {HARFLER[harf_no]}")
            elif tus == ord("p"):
                harf_no = (harf_no - 1) % len(HARFLER)
                print(f"Harf: {HARFLER[harf_no]}")
        elif durum == "ONAY":
            if tus == ord("s"):
                tamponu_kaydet(tampon)
                sayilar[harf] += len(tampon)
                print(f"{harf}: {len(tampon)} örnek kaydedildi (toplam {sayilar[harf]})")
                durum, tampon = "BEKLE", []
            elif tus == ord("x"):
                print(f"{harf}: kayıt iptal edildi")
                durum, tampon = "BEKLE", []

    kamera.release()
    dedektor.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
