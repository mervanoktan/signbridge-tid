# Kullanılan Yöntemler, Algoritmalar ve Kütüphaneler

Projede hangi yöntemin, algoritmanın ve kütüphanenin **nerede** ve **neden** kullanıldığının özeti.
Her aşama tamamlandıkça güncellenir. Rapor ve sunum için doğrudan kullanılabilir.

---

## 1. Genel yaklaşım: Görüntü → Anahtar noktalar → Sınıflandırma

```
Kamera görüntüsü ──► MediaPipe (el anahtar noktaları) ──► Özellik çıkarma ──► Sınıflandırıcı ──► Harf
   (görüntü işleme)       (hazır derin öğrenme modeli)       (geometri)          (MLP / RF)
```

Görüntünün kendisini doğrudan bir sınıflandırıcıya vermek yerine, önce görüntüden **elin iskeletini (21 nokta)**
çıkarıyoruz, sonra bu noktaları sınıflandırıyoruz. Buna **iskelet (anahtar nokta) tabanlı tanıma** denir.

**Neden bu yaklaşım?**
| | Görüntü tabanlı (CNN) | İskelet tabanlı (bizim yöntem) |
|---|---|---|
| Girdi boyutu | 224×224×3 = 150.528 sayı | 131 sayı |
| Gereken veri | Çok (binlerce kişi, farklı ortamlar) | Az |
| Arka plan / ışık / ten rengi / kıyafet | Çok etkilenir | Az etkilenir (MediaPipe bunları zaten eler) |
| Hız | GPU'da bile ağır | CPU'da gerçek zamanlı |
| Eğitim süresi | Dakikalar–saatler | Saniyeler |

---

## 2. Kullanılan algoritmalar

### 2.1 MediaPipe Hand Landmarker (el tespiti) – hazır model
- **Ne yapar:** Görüntüde elleri bulur, her el için 21 anahtar noktanın (x, y, z) koordinatını verir; elin sol mu sağ mı olduğunu tahmin eder.
- **Nasıl çalışır:** İki aşamalı bir derin öğrenme modelidir:
  1. **Avuç dedektörü (palm detector):** Görüntünün tamamında avuç bölgesini bulur (tek atışlık bir nesne dedektörü).
  2. **El noktası modeli (hand landmark model):** Bulunan bölgede 21 noktayı tahmin eder (CNN tabanlı regresyon).
  Video modunda bir sonraki karede eli baştan aramak yerine önceki konumundan **takip eder**, bu yüzden hızlıdır.
- **Biz eğitmedik**, Google'ın hazır modelini kullanıyoruz (`models/mediapipe/hand_landmarker.task`).

### 2.2 Özellik çıkarma (geometrik normalizasyon) – `src/features.py`
- **Öteleme (translation):** Her elin noktalarından bilek noktası çıkarılır → elin ekrandaki konumundan bağımsızlık.
- **Ölçekleme (scaling):** Noktalar el boyutuna (bilek – orta parmak kökü mesafesi) bölünür → kameraya uzaklıktan bağımsızlık.
- **Eller arası ilişki:** Sağ bileğin sol bileğe göre konumu → iki elli harflerde ellerin duruşu.
- Sonuç: Her örnek için **131 boyutlu özellik vektörü** (63 sol el + 63 sağ el + 2 el var/yok + 3 eller arası).

### 2.3 MLP – Çok Katmanlı Algılayıcı (asıl sınıflandırıcı) – `src/train_alphabet.py`
- **Türü:** Yapay Sinir Ağı (**ANN – Artificial Neural Network**), tam bağlantılı (fully connected) ileri beslemeli ağ.
  **CNN değil.** CNN (evrişimli sinir ağı) görüntü gibi ızgara yapısındaki veriler için kullanılır; bizim girdimiz
  bir görüntü değil, 131 sayılık bir vektör olduğu için MLP doğru seçimdir.
- **Mimari:** `131 → 256 → 128 → 28`
  - Gizli katmanlarda **ReLU** aktivasyonu
  - **Batch Normalization:** Her katmanın çıktısını normalize eder, eğitimi hızlandırır ve kararlı hâle getirir
  - **Dropout (%30):** Eğitimde nöronların bir kısmını rastgele kapatır, ezberlemeyi (overfitting) önler
  - Çıkış katmanı: 28 harf için skor; **Softmax + Cross-Entropy** kaybı
- **Eğitim:** **Adam** optimizasyon algoritması (öğrenme oranı 0,001, weight decay 0,0001), batch boyutu 128
- **Early stopping:** Doğrulama başarısı 15 epoch boyunca artmazsa eğitim durur, en iyi ağırlıklar saklanır.
- **Veri artırma (data augmentation):** Her epoch'ta eğitim örnekleri ±10° döndürülür ve küçük gürültü eklenir.

### 2.4 Random Forest (karşılaştırma için klasik yöntem)
- **Türü:** Klasik makine öğrenmesi; çok sayıda **karar ağacının** oylamasıyla karar veren topluluk (ensemble) yöntemi.
- 300 ağaç. Aynı 131 boyutlu özellikleri kullanır.
- **Neden:** Derin öğrenme modelinin klasik bir yönteme göre fark yaratıp yaratmadığını göstermek için (raporda karşılaştırma).

### 2.5 Değerlendirme yöntemi
- **Kayıt bazlı bölme:** Her harfin 6 kaydından 1'i test, 1'i doğrulama, kalanı eğitim. Aynı kaydın kareleri hiçbir zaman
  hem eğitimde hem testte bulunmaz (veri sızıntısı / data leakage önlemi).
- **Metrikler:** Doğruluk (accuracy), harf bazında precision / recall / F1, **karışıklık matrisi** (confusion matrix).

---

## 3. Kütüphaneler

| Kütüphane | Sürüm | Nerede | Neden bu kütüphane? |
|---|---|---|---|
| **Python** | 3.11 | Tümü | Görüntü işleme ve yapay zeka kütüphanelerinin en olgun olduğu dil |
| **OpenCV** | 5.0 | Kamera, görüntü işleme, çizim | Görüntü işlemede standart, hızlı (C++ tabanlı) |
| **MediaPipe** | 1.1 | El anahtar noktaları | Gerçek zamanlı, iki el desteği, CPU'da hızlı, ücretsiz |
| **NumPy** | 2.4 | Koordinat hesapları | Sayısal dizilerle hızlı vektör/matris işlemleri |
| **pandas** | 3.0 | CSV okuma/yazma | Tablo şeklindeki veriyi kolay işleme |
| **Pillow** | – | Ekrana Türkçe yazı | OpenCV Türkçe karakter (Ç, Ğ, İ, Ş) çizemiyor |
| **PyTorch** | 2.14 (CUDA 13.0) | MLP modeli | Esnek, GPU (RTX 3050) desteği, araştırmada en yaygın derin öğrenme kütüphanesi |
| **scikit-learn** | 1.9 | Random Forest, metrikler | Klasik ML algoritmaları ve değerlendirme araçları için standart |
| **matplotlib** | 3.11 | Grafikler | Rapor için karışıklık matrisi ve eğitim grafikleri |

**Neden TensorFlow/Keras değil de PyTorch?** İkisi de olurdu. PyTorch'un kodu daha sade ve Python'a daha yakın,
araştırma projelerinde daha yaygın, CUDA kurulumu da daha kolay.

---

## 4. İleride kullanılacaklar (plan)

| Aşama | Yöntem | Neden |
|---|---|---|
| Kelime tanıma | MediaPipe Holistic (el + vücut + yüz) | TİD kelimelerinde vücut ve yüz hareketi de anlam taşır |
| Kelime tanıma | BiLSTM / Transformer / ST-GCN | Kelimeler hareketlidir; zaman içindeki diziyi işleyen modeller gerekir |
| Karşılaştırma deneyi | **CNN** (MobileNet) – kırpılmış el görüntüleri | İskelet tabanlı yöntemi görüntü tabanlı yöntemle karşılaştırmak için |
| Dil katmanı | LLM API | TİD gloss dizisini doğal Türkçe cümleye çevirmek için |
| Konuşma → metin | faster-whisper | Türkçe başarısı yüksek, GPU'da hızlı |
