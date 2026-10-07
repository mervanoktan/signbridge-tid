# TİD Çevirmen – Yol Haritası

Görüntü İşleme dersi dönem projesi.

## 1. Amaç

Kamera görüntüsünden **Türk İşaret Dili (TİD)** işaretlerini gerçek zamanlı tanıyıp metne ve sese çeviren,
ters yönde de konuşmayı işaret diline (işaret videoları + alfabe ile heceleme) çeviren iki yönlü bir sistem.

## 2. Sistemin İki Modu

### Mod A – İşaret → Metin + Ses
1. Kamera görüntüsü alınır, eller / vücut / yüz anahtar noktaları çıkarılır.
2. Kelime işaretleri (dizi modeli) ve alfabe harfleri (heceleme modu) tanınır.
3. Tanınan işaretler bir **gloss dizisi** oluşturur. Örnek: `BEN BUGÜN HASTA DERS GELMEK DEĞİL`
4. Dil katmanı (LLM API) gloss dizisini doğal Türkçe cümleye çevirir:
   "Ben bugün hasta olduğum için derse gelmeyeceğim."
5. Cümle ekranda gösterilir ve sesli okunur (TTS).

### Mod B – Ses → Metin + İşaret
1. Mikrofondan konuşma alınır, metne çevrilir (faster-whisper).
2. Dil katmanı Türkçe cümleyi gloss dizisine çevirir. Sadece sistemin bildiği kelimeler kullanılır.
3. Bilinen kelimeler için işaret videoları, bilinmeyen kelimeler için alfabe görselleri (heceleme) sırayla gösterilir.

## 3. Mimari (Mod A)

```
Kamera (30 FPS)
   ↓
Ön işleme ............ CLAHE ile ışık düzeltme, ayna çevirme
   ↓
Anahtar noktalar ..... MediaPipe Holistic (2 el + üst vücut + seçili yüz noktaları)
   ↓
Filtreleme ........... One Euro / Kalman filtresi (titreme azaltma)
   ↓
Normalizasyon ........ merkez = omuz ortası, ölçek = omuz genişliği
   ↓
Özellik vektörü ...... el şekli + elin vücuda göre konumu + hız + yüz/baş özellikleri
   ↓
Segmentasyon ......... hareket enerjisi / optik akış + "boşta" sınıfı
   ↓
Dizi modeli .......... BiLSTM → Transformer → ST-GCN (karşılaştırmalı)
   ↓
Gloss dizisi → LLM → Türkçe cümle → Ekran + TTS
```

Alfabe tanıma ayrı bir modelle (landmark tabanlı MLP) yapılır. Arayüzde "Kelime modu" ile "Heceleme modu" arasında geçiş yapılır.

## 4. Teknolojiler

| Görev | Araç |
|---|---|
| Dil / ortam | Python, (GPU: RTX 3050 – CUDA) |
| Görüntü işleme | OpenCV |
| Anahtar nokta tespiti | MediaPipe Holistic / Tasks |
| Derin öğrenme | PyTorch |
| Konuşma → metin | faster-whisper |
| Metin → konuşma | edge-tts (online), pyttsx3 (offline yedek) |
| Dil katmanı | LLM API (Claude Haiku 4.5 / Sonnet 5.5) + kural tabanlı çevrimdışı yedek |
| Arayüz | PySide6 |
| Değerlendirme / grafik | scikit-learn, matplotlib |

## 5. Aşamalar

### Bölüm 1 – Alfabe (çekirdek)
- [x] **Aşama 0** – Ortam kurulumu (Python, CUDA, kütüphaneler) — klasör yapısı Aşama 1 ile birlikte kurulacak
- [ ] **Aşama 1** – Alfabe veri toplama aracı (landmark + el görüntüsü kaydı)
- [ ] **Aşama 2** – Alfabe modeli eğitimi (MLP) + değerlendirme (confusion matrix, doğruluk)
- [ ] **Aşama 3** – Gerçek zamanlı alfabe tanıma + kararlılık filtresi + kelime oluşturma
- [ ] **Aşama 4** – Ses çıkışı (TTS)

### Bölüm 2 – Kelime işaretleri (ileri)
- [ ] **Aşama 5** – ~100 kelimelik dağarcığın belirlenmesi (kategorilere göre) + AUTSL veri setinin incelenmesi
- [ ] **Aşama 6** – Kelime veri toplama aracı (Holistic iskelet dizileri, kelime başına ~40 tekrar)
- [ ] **Aşama 7** – Ön işleme: normalizasyon, filtreleme, veri artırma
- [ ] **Aşama 8** – Segmentasyon: hareket enerjisi / optik akış, dinlenme pozisyonu
- [ ] **Aşama 9** – Dizi modelleri: BiLSTM, Transformer, ST-GCN + karşılaştırma
- [ ] **Aşama 10** – Ablation deneyi: "sadece el" vs "el + vücut + yüz"
- [ ] **Aşama 11** – Bilinmeyen işaret tespiti (güven eşiği) + az örnekle yeni kelime ekleme (few-shot)

### Bölüm 3 – Dil ve ses katmanı
- [ ] **Aşama 12** – LLM ile gloss ↔ Türkçe çeviri + çevrimdışı kural tabanlı yedek
- [ ] **Aşama 13** – Konuşma → metin (faster-whisper)
- [ ] **Aşama 14** – Metin → işaret gösterimi (kelime videoları + alfabe ile heceleme)

### Bölüm 4 – Birleştirme ve teslim
- [ ] **Aşama 15** – PySide6 arayüzü (iki mod, tek uygulama)
- [ ] **Aşama 16** – Karşılaştırma deneyi: klasik segmentasyon (HSV, kontur) / CNN vs landmark yöntemi
- [ ] **Aşama 17** – Rapor, sunum, demo videosu

## 6. Klasör Yapısı (taslak)

```
Dil_proje/
├── data/
│   ├── alphabet/       # alfabe verisi
│   ├── words/          # kelime işareti dizileri
│   └── signs/          # Mod B için işaret videoları ve alfabe görselleri
│       ├── alphabet/
│       └── words/
├── models/
│   ├── mediapipe/      # MediaPipe .task model dosyaları
│   ├── alphabet/       # eğitilmiş alfabe modeli
│   └── words/          # eğitilmiş kelime modeli
├── src/
│   ├── collect_alphabet.py
│   ├── collect_words.py
│   ├── features.py
│   ├── train_alphabet.py
│   ├── train_words.py
│   ├── recognizer.py
│   ├── segmenter.py
│   ├── language.py     # LLM gloss ↔ Türkçe
│   ├── tts.py
│   ├── stt.py
│   └── app.py
├── experiments/        # karşılaştırma / ablation deneyleri
├── report/
│   └── figures/        # rapor grafikleri
├── docs/
│   ├── YOL_HARITASI.md
│   ├── CALISMA_NOTLARI.md
│   ├── KAYNAKLAR.md
│   └── references/     # telifli referans materyaller (git'e eklenmez)
├── README.md
├── CLAUDE.md
├── requirements.txt
└── .gitignore
```

## 7. Gerçekçi Beklentiler

**Hedeflenen:**
- Statik alfabe harflerinde test doğruluğu %95+
- ~100 kelimelik dağarcıkla serbest cümlelerin çevrilmesi
- Dağarcıkta olmayan kelimelerin alfabeyle hecelenmesi
- Birkaç örnekle sisteme yeni kelime eklenebilmesi
- 20–30 FPS gerçek zamanlı çalışma

**Kısıtlar:**
- Sistem sadece eğitildiği işaretleri tanır, sınırsız TİD tanıma bugün de çözülmemiş bir araştırma problemidir.
- Az sayıda kişiden toplanan veriyle, farklı kişilerde doğruluk düşebilir.
- Gloss → Türkçe çeviride zaman kipi belirsizlikleri olabilir (LLM bağlamdan tahmin eder).
- Ses → işaret yönü tam bir TİD çevirisi değildir, kelime videoları + heceleme ile yapılır.

## 8. Açık Kararlar

- [x] TİD alfabesi için güvenilir referans kaynağı → `docs/KAYNAKLAR.md`
- [ ] ~100 kelimelik dağarcık listesi
- [ ] AUTSL lisansı ve kelime içeriği
