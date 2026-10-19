"""
SignBridge - Özellik çıkarma (Aşama 2)

MediaPipe'ın ham el noktalarını modelin kullanacağı özellik vektörüne çevirir.
Hem eğitimde (CSV'den) hem de canlı tanımada (kameradan) aynı fonksiyon kullanılır.

Özellik vektörü (131 sayı):
  - Sol el şekli   : 63  (21 nokta x 3; bileğe göre konum, el boyutuna göre ölçek)
  - Sağ el şekli   : 63
  - El var mı      : 2   (sol, sağ: 1 veya 0)
  - Eller arası    : 3   (sağ bileğin sol bileğe göre konumu, el boyutuna göre ölçek)
"""

import numpy as np

OZELLIK_BOYUTU = 63 + 63 + 2 + 3


def el_boyutu(noktalar):
    """Bilek (0) ile orta parmak kökü (9) arasındaki mesafe. Elin ölçeği olarak kullanılır."""
    return max(np.linalg.norm(noktalar[9, :2] - noktalar[0, :2]), 1e-6)


def el_ozelligi(noktalar):
    """(21, 3) el noktalarını konumdan ve ölçekten bağımsız 63 sayıya çevirir."""
    # ÖNEMLİ: Bileği orijine taşıyoruz (konumdan bağımsızlık) ve el boyutuna bölüyoruz
    # (kameraya uzaklıktan bağımsızlık). Böylece aynı harf ekranın neresinde ve
    # hangi mesafede yapılırsa yapılsın aynı sayıları üretir.
    goreli = noktalar - noktalar[0]
    return (goreli / el_boyutu(noktalar)).flatten()


def ozellik_cikar(sol, sag):
    """sol, sag: (21, 3) dizi veya None  ->  (131,) özellik vektörü."""
    parcalar = []
    for el in (sol, sag):
        parcalar.append(el_ozelligi(el) if el is not None else np.zeros(63))
    parcalar.append([float(sol is not None), float(sag is not None)])

    # ÖNEMLİ: İki elli harflerde ellerin birbirine göre duruşu da ayırt edicidir
    # (ör. A ve H'de el şekilleri benzer, ellerin konumu farklı).
    if sol is not None and sag is not None:
        olcek = (el_boyutu(sol) + el_boyutu(sag)) / 2
        parcalar.append((sag[0] - sol[0]) / olcek)
    else:
        parcalar.append(np.zeros(3))

    return np.concatenate(parcalar).astype(np.float32)


def csv_ozellikleri(df):
    """landmarks.csv'den okunan tabloyu (n, 131) özellik matrisine çevirir."""
    sol = df[[f"sol_{i}_{a}" for i in range(21) for a in "xyz"]].to_numpy().reshape(-1, 21, 3)
    sag = df[[f"sag_{i}_{a}" for i in range(21) for a in "xyz"]].to_numpy().reshape(-1, 21, 3)
    sol_var = df["sol_var"].to_numpy() == 1
    sag_var = df["sag_var"].to_numpy() == 1

    X = np.zeros((len(df), OZELLIK_BOYUTU), dtype=np.float32)
    for i in range(len(df)):
        X[i] = ozellik_cikar(sol[i] if sol_var[i] else None, sag[i] if sag_var[i] else None)
    return X
