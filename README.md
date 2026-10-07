# SignBridge – Türk İşaret Dili Çevirmeni

> Türk İşaret Dili (TİD) ↔ Türkçe metin ve ses arasında gerçek zamanlı, iki yönlü çeviri sistemi.
> Görüntü İşleme dersi dönem projesi. **Geliştirme aşamasında.**

## Ne yapıyor?

**İşaret → Metin + Ses**
Kamera görüntüsünden el, vücut ve yüz anahtar noktaları çıkarılır; TİD kelime işaretleri ve parmak alfabesi
harfleri tanınır. Tanınan işaret dizisi (gloss) bir dil modeliyle doğal Türkçe cümleye çevrilir, ekranda
gösterilir ve seslendirilir.

```
BEN BUGÜN HASTA DERS GELMEK DEĞİL  →  "Ben bugün hasta olduğum için derse gelmeyeceğim."
```

**Ses → Metin + İşaret**
Konuşma metne çevrilir; bilinen kelimeler için TİD işaret videoları, bilinmeyen kelimeler için parmak
alfabesi ile heceleme gösterilir.

## Yöntem (özet)

```
Kamera → Ön işleme → MediaPipe (el + vücut + yüz) → Filtreleme → Normalizasyon
       → Segmentasyon → Dizi modeli (BiLSTM / Transformer / ST-GCN) → Gloss → LLM → Metin + Ses
```

Ayrıntılı mimari ve aşamalar: [docs/YOL_HARITASI.md](docs/YOL_HARITASI.md)

## Teknolojiler

Python · OpenCV · MediaPipe · PyTorch (CUDA) · scikit-learn · faster-whisper · PySide6

## Proje Yapısı

```
├── data/            # toplanan veri setleri (alfabe, kelime) ve işaret görselleri
├── models/          # MediaPipe modelleri ve eğitilmiş modeller
├── src/             # kaynak kod
├── experiments/     # karşılaştırma ve ablation deneyleri
├── report/          # rapor ve grafikler
└── docs/            # yol haritası, çalışma notları, kaynaklar
```

## Kurulum

```bash
python -m venv .venv
.venv\Scripts\activate
pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cu130
pip install -r requirements.txt
```

## Durum

- [x] Ortam kurulumu
- [ ] Parmak alfabesi tanıma
- [ ] Kelime işareti tanıma
- [ ] Dil katmanı (gloss ↔ Türkçe)
- [ ] Konuşma ↔ metin
- [ ] Arayüz

## Not

Bu proje geliştirilirken yapay zeka destekli kodlama araçlarından yararlanılmıştır.
