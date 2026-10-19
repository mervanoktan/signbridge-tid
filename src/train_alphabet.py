"""
SignBridge - Alfabe modeli eğitimi (Aşama 2)

landmarks.csv'deki örneklerle iki model eğitir ve karşılaştırır:
  - MLP (çok katmanlı yapay sinir ağı, PyTorch)  -> asıl model
  - Random Forest (scikit-learn)                -> klasik makine öğrenmesi ile karşılaştırma

Çıktılar:
  models/alphabet/harf_mlp.pt                  eğitilmiş MLP + harf listesi
  report/figures/alfabe_karisiklik_matrisi.png karışıklık matrisi (test seti)
  report/figures/alfabe_egitim_grafigi.png     eğitim kaybı ve doğrulama başarısı
  report/alfabe_sonuclar.json                  sayısal sonuçlar

Kullanım:
  python src/train_alphabet.py
"""

import json
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # pencere açmadan dosyaya çiz
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from torch import nn

from features import OZELLIK_BOYUTU, csv_ozellikleri

PROJE = Path(__file__).resolve().parent.parent
CSV_YOLU = PROJE / "data" / "alphabet" / "landmarks.csv"
MODEL_YOLU = PROJE / "models" / "alphabet" / "harf_mlp.pt"
SEKIL_KLASORU = PROJE / "report" / "figures"
SONUC_YOLU = PROJE / "report" / "alfabe_sonuclar.json"

HARF_SIRASI = list("ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ")
TOHUM = 42           # rastgelelik tohumu: aynı kod her çalıştığında aynı sonucu versin
EPOCH = 80
SABIR = 15           # doğrulama başarısı bu kadar epoch artmazsa eğitimi durdur (early stopping)
BATCH = 128


# --- Model ------------------------------------------------------------------

class HarfMLP(nn.Module):
    """131 özellik -> 256 -> 128 -> harf sayısı. Her gizli katmanda BatchNorm, ReLU ve Dropout."""

    def __init__(self, giris, sinif_sayisi):
        super().__init__()
        self.ag = nn.Sequential(
            nn.Linear(giris, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(256, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128, sinif_sayisi),
        )

    def forward(self, x):
        return self.ag(x)


# --- Veri -------------------------------------------------------------------

def kayitlara_ayir(df):
    """Her örneğe hangi kayda (SPACE ile başlatılan 5 sn'lik çekim) ait olduğunu yazar.
    Aynı harfte aralarında 2 sn'den fazla boşluk olan örnekler farklı kayıt sayılır."""
    zaman = pd.to_datetime(df["ornek_id"].str.extract(r"_(\d{8}_\d{6}_\d{6})")[0],
                           format="%Y%m%d_%H%M%S_%f")
    df = df.assign(zaman=zaman).sort_values("zaman").reset_index(drop=True)
    yeni_kayit = (df["zaman"].diff().dt.total_seconds() > 2) | (df["harf"] != df["harf"].shift())
    df["kayit"] = yeni_kayit.cumsum()
    return df


def kayit_bazli_bol(df, rng):
    """ÖNEMLİ: Veriyi örnek bazında değil KAYIT bazında böler.
    Her harfin kayıtlarından 1'i test, 1'i doğrulama, kalanı eğitim için ayrılır.
    Aynı kayıttaki kareler birbirinin neredeyse aynısı olduğu için rastgele örnek bazında bölseydik
    test setinde eğitimde görülen karelerin kopyaları olurdu ve başarı olduğundan yüksek görünürdü."""
    bolum = pd.Series("egitim", index=df.index)
    for _, grup in df.groupby("harf"):
        kayitlar = rng.permutation(grup["kayit"].unique())
        bolum[df["kayit"] == kayitlar[0]] = "test"
        bolum[df["kayit"] == kayitlar[1]] = "dogrulama"
    return bolum


def veri_artir(X, rng):
    """Eğitim örneklerini her epoch'ta hafifçe değiştirir (data augmentation):
    ±10° döndürme (kamera/el eğikliği) ve küçük gürültü (MediaPipe titremesi)."""
    X = X.copy()
    n = len(X)
    aci = rng.uniform(-np.pi / 18, np.pi / 18, n)
    c, s = np.cos(aci)[:, None], np.sin(aci)[:, None]

    for bas in (0, 63):  # sol el ve sağ el blokları
        el = X[:, bas:bas + 63].reshape(n, 21, 3)
        x, y = el[..., 0].copy(), el[..., 1].copy()
        el[..., 0], el[..., 1] = c * x - s * y, s * x + c * y
        var = X[:, 126 + bas // 63][:, None, None]  # el yoksa gürültü ekleme
        el += rng.normal(0, 0.02, el.shape) * var
        X[:, bas:bas + 63] = el.reshape(n, 63)

    r = X[:, 128:131]  # eller arası vektör de aynı açıyla döner
    rx, ry = r[:, 0].copy(), r[:, 1].copy()
    r[:, 0], r[:, 1] = c[:, 0] * rx - s[:, 0] * ry, s[:, 0] * rx + c[:, 0] * ry
    return X


# --- Eğitim -----------------------------------------------------------------

def mlp_egit(X_egitim, y_egitim, X_dogr, y_dogr, sinif_sayisi, cihaz, rng):
    torch.manual_seed(TOHUM)
    model = HarfMLP(OZELLIK_BOYUTU, sinif_sayisi).to(cihaz)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    kayip_fn = nn.CrossEntropyLoss()

    Xd = torch.tensor(X_dogr, device=cihaz)
    gecmis = {"kayip": [], "dogrulama_basari": []}
    en_iyi, en_iyi_durum, sabir = 0.0, None, 0

    for epoch in range(1, EPOCH + 1):
        model.train()
        Xa = torch.tensor(veri_artir(X_egitim, rng), device=cihaz)
        ya = torch.tensor(y_egitim, device=cihaz)
        sira = torch.randperm(len(Xa), device=cihaz)
        toplam_kayip = 0.0
        for i in range(0, len(sira), BATCH):
            idx = sira[i:i + BATCH]
            optimizer.zero_grad()
            kayip = kayip_fn(model(Xa[idx]), ya[idx])
            kayip.backward()
            optimizer.step()
            toplam_kayip += kayip.item() * len(idx)

        model.eval()
        with torch.no_grad():
            basari = (model(Xd).argmax(1).cpu().numpy() == y_dogr).mean()
        gecmis["kayip"].append(toplam_kayip / len(sira))
        gecmis["dogrulama_basari"].append(float(basari))
        print(f"  epoch {epoch:3d} | kayıp {gecmis['kayip'][-1]:.4f} | doğrulama başarısı %{100 * basari:.2f}")

        # ÖNEMLİ: Early stopping - doğrulama setinde en iyi sonucu veren ağırlıkları saklarız.
        if basari > en_iyi:
            en_iyi, sabir = basari, 0
            en_iyi_durum = {k: v.detach().clone() for k, v in model.state_dict().items()}
        else:
            sabir += 1
            if sabir >= SABIR:
                print(f"  {SABIR} epoch boyunca iyileşme olmadı, eğitim durduruldu.")
                break

    model.load_state_dict(en_iyi_durum)
    return model, gecmis


# --- Grafikler --------------------------------------------------------------

def karisiklik_matrisi_ciz(y_gercek, y_tahmin, harfler, yol, baslik):
    cm = confusion_matrix(y_gercek, y_tahmin, labels=range(len(harfler)), normalize="true")
    fig, ax = plt.subplots(figsize=(11, 10))
    ax.imshow(cm, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(len(harfler)), harfler)
    ax.set_yticks(range(len(harfler)), harfler)
    ax.set_xlabel("Tahmin edilen harf")
    ax.set_ylabel("Gerçek harf")
    ax.set_title(baslik)
    for i in range(len(harfler)):
        for j in range(len(harfler)):
            if cm[i, j] >= 0.01:
                ax.text(j, i, f"{100 * cm[i, j]:.0f}", ha="center", va="center", fontsize=7,
                        color="white" if cm[i, j] > 0.5 else "black")
    fig.tight_layout()
    fig.savefig(yol, dpi=150)
    plt.close(fig)


def egitim_grafigi_ciz(gecmis, yol):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    ax1.plot(gecmis["kayip"])
    ax1.set_title("Eğitim kaybı")
    ax1.set_xlabel("Epoch")
    ax2.plot([100 * b for b in gecmis["dogrulama_basari"]])
    ax2.set_title("Doğrulama başarısı (%)")
    ax2.set_xlabel("Epoch")
    fig.tight_layout()
    fig.savefig(yol, dpi=150)
    plt.close(fig)


# --- Ana program ------------------------------------------------------------

def main():
    rng = np.random.default_rng(TOHUM)
    cihaz = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Cihaz: {cihaz}")

    df = kayitlara_ayir(pd.read_csv(CSV_YOLU))
    harfler = [h for h in HARF_SIRASI if h in set(df["harf"])]
    y = df["harf"].map({h: i for i, h in enumerate(harfler)}).to_numpy()
    X = csv_ozellikleri(df)
    bolum = kayit_bazli_bol(df, rng).to_numpy()
    e, d, t = bolum == "egitim", bolum == "dogrulama", bolum == "test"
    print(f"{len(harfler)} harf, {len(df)} örnek -> eğitim {e.sum()}, doğrulama {d.sum()}, test {t.sum()}")

    # 1) Random Forest (karşılaştırma)
    print("\n[1/2] Random Forest eğitiliyor...")
    bas = time.time()
    rf = RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=TOHUM)
    rf.fit(X[e], y[e])
    rf_basari = accuracy_score(y[t], rf.predict(X[t]))
    print(f"  Random Forest test başarısı: %{100 * rf_basari:.2f} ({time.time() - bas:.1f} sn)")

    # 2) MLP (asıl model)
    print("\n[2/2] MLP eğitiliyor...")
    bas = time.time()
    model, gecmis = mlp_egit(X[e], y[e], X[d], y[d], len(harfler), cihaz, rng)
    model.eval()
    with torch.no_grad():
        y_tahmin = model(torch.tensor(X[t], device=cihaz)).argmax(1).cpu().numpy()
    mlp_basari = accuracy_score(y[t], y_tahmin)
    print(f"  MLP test başarısı: %{100 * mlp_basari:.2f} ({time.time() - bas:.1f} sn)")

    # Harf bazında sonuçlar ve en çok karışan çiftler
    print("\nHarf bazında sonuçlar (MLP, test seti):")
    print(classification_report(y[t], y_tahmin, labels=range(len(harfler)),
                                target_names=harfler, digits=3, zero_division=0))
    cm = confusion_matrix(y[t], y_tahmin, labels=range(len(harfler)))
    np.fill_diagonal(cm, 0)
    karisanlar = sorted(((cm[i, j], harfler[i], harfler[j]) for i in range(len(harfler))
                         for j in range(len(harfler)) if cm[i, j] > 0), reverse=True)[:8]
    print("En çok karışan harfler (gerçek -> tahmin):")
    for adet, gercek, tahmin in karisanlar:
        print(f"  {gercek} -> {tahmin}: {adet} örnek")

    # Kaydet
    MODEL_YOLU.parent.mkdir(parents=True, exist_ok=True)
    SEKIL_KLASORU.mkdir(parents=True, exist_ok=True)
    torch.save({"model": model.state_dict(), "harfler": harfler, "giris": OZELLIK_BOYUTU}, MODEL_YOLU)
    karisiklik_matrisi_ciz(y[t], y_tahmin, harfler, SEKIL_KLASORU / "alfabe_karisiklik_matrisi.png",
                           f"Alfabe - MLP karışıklık matrisi (test, %{100 * mlp_basari:.1f})")
    egitim_grafigi_ciz(gecmis, SEKIL_KLASORU / "alfabe_egitim_grafigi.png")
    SONUC_YOLU.write_text(json.dumps({
        "harf_sayisi": len(harfler), "ornek": {"egitim": int(e.sum()), "dogrulama": int(d.sum()), "test": int(t.sum())},
        "test_basarisi": {"mlp": round(float(mlp_basari), 4), "random_forest": round(float(rf_basari), 4)},
        "epoch": len(gecmis["kayip"]),
        "en_cok_karisanlar": [{"gercek": g, "tahmin": p, "adet": int(a)} for a, g, p in karisanlar],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nModel: {MODEL_YOLU.relative_to(PROJE)}")
    print(f"Grafikler: {SEKIL_KLASORU.relative_to(PROJE)}")


if __name__ == "__main__":
    main()
