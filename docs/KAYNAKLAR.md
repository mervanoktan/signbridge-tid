# Kaynaklar ve Araştırma Notları

## TİD Parmak Alfabesi

**Temel bilgiler:**
- TİD parmak alfabesi **29 harften** oluşur (Türk alfabesindeki harflerin hepsi). Son şekli TDK'nın
  Türk İşaret Dili çalışmalarında verilmiştir.
- ASL, Alman ve Fransız işaret dillerinden farklı olarak **iki elle** yapılır.
  Kaynaklara göre **C, I, L, O, P, U, V** dışındaki harfler çift elle yapılır.
  → Alfabe modelimiz **iki elin** noktalarını birlikte işlemeli.
- İki elli parmak alfabesi 1940'ların başında kullanılmaya başlanmıştır.
- Bazı harflerin hareket içerip içermediği (dinamik harf) referans görseller/videolar üzerinden kontrol edilecek.

**Referans kaynaklar:**
| Kaynak | İçerik | Kullanım |
|---|---|---|
| [Güncel Türk İşaret Dili Sözlüğü (Aile ve Sosyal Hizmetler Bakanlığı)](https://tidsozluk.aile.gov.tr/) | 116 sağır TİD kullanıcısından derlenmiş derlem, ~2000 kelime, video tabanlı | Kelime işaretleri için birincil referans |
| [EGO – Türk İşaret Dili Alfabesi](https://isaretdili.ego.gov.tr/turk-isaret-dili-alfabesi/) | Alfabe görseli + yazdırılabilir PDF + eğitim videoları | Alfabe harfleri için referans |
| [MEB – Türk İşaret Dili Sözlüğü (PDF)](https://orgm.meb.gov.tr/icdep/content/upload/catalogs/turk-isaret-dili-sozlugu-20211219170540.pdf) | Resimli sözlük | Ek referans |
| [TDK – Türk İşaret Dili Sözlüğü](https://tdk.gov.tr/icerik/basindan/turk-isaret-dili-sozlugu/) | Resmi kurum bilgisi | Arka plan bilgisi |

> Bu kaynaklardaki görseller ve videolar telif hakkıyla korunur. Sadece öğrenme ve doğrulama için
> kullanılacak; uygulamada gösterilecek işaret görselleri/videoları kendi kayıtlarımızdan üretilecek.

## Hazır TİD Veri Setleri

| Veri seti | İçerik | Format / Erişim | Kullanım planı |
|---|---|---|---|
| [TurkSign446 (Zenodo)](https://zenodo.org/records/17267293) · [kod](https://github.com/akaraci/TurkSign446-TSL-Recognition) | 446 kelime (133 statik, 313 dinamik), 10 kişi × 10 tekrar = 44.600 video | **MediaPipe Holistic noktaları** (kare başına 1.662 özellik, NumPy), 8,7 GB, **CC BY 4.0**, kayıt gerektirmiyor | Kelime aşamasının ana veri kaynağı |
| [AUTSL (ChaLearn)](https://chalearnlap.cvc.uab.cat/dataset/40/description/) · [makale](https://arxiv.org/abs/2008.00932) | 226 günlük kelime, 43 kişi, ~36.000 video | RGB + derinlik video (512×512), CodaLab kaydı ve kullanım şartları gerekli | Ek kelimeler, farklı kişilerde test |
| [Turkish Sign Language (Fingerspelling) – Kaggle](https://www.kaggle.com/datasets/feronial/turkish-sign-languagefinger-spelling/metadata) | 2.974 alfabe fotoğrafı | Görüntü, Kaggle hesabı gerekli | Alfabe modelini başka kişilerde test |
| [E-TSL](https://arxiv.org/html/2405.02984v1) | Akıcı (sürekli) TİD cümleleri, eğitim içerikli | Video | İleri çalışma |

> TurkSign446'daki 1.662 özellik eski MediaPipe Holistic formatına karşılık geliyor
> (vücut 33×4 + yüz 468×3 + iki el 2×21×3). Bizim canlı sistemimiz yeni Tasks API'yi kullanıyor (yüz 478 nokta).
> Özellik çıkarımında sadece seçili noktaları kullanacağımız için iki format eşleştirilebilir; sol/sağ el ve ayna
> görüntüsü varsayımları ayrıca kontrol edilecek.

## İlgili Akademik Çalışmalar

- [Detection of Turkish Sign Language Using Deep Learning and Image Processing Methods (Applied AI, 2021)](https://www.tandfonline.com/doi/full/10.1080/08839514.2021.1982184)
  – 29 harf, 10.223 görüntü; filtreleme, morfoloji ve segmentasyon ile ön işleme.
- [Real-Time Detection of Turkish Sign Language Letters and Numbers with Deep Learning (APJESS)](https://dergipark.org.tr/en/pub/apjess/article/1495405)
  – Gerçek zamanlı harf ve rakam tanıma.
- [Pose-Based Static Sign Language Recognition with Deep Learning for Turkish, Arabic, and American Sign Languages](https://pmc.ncbi.nlm.nih.gov/articles/PMC12846149/)
  – Poz (anahtar nokta) tabanlı statik işaret tanıma; bizim yaklaşımımıza yakın.
- [Double handed dynamic Turkish Sign Language recognition using Leap Motion with meta learning](https://www.sciencedirect.com/science/article/abs/pii/S0957417423009557)
  – İki elli dinamik TİD kelimeleri, az örnekle öğrenme (meta learning).
- [Turkish fingerspelling recognition system using Generalized Hough Transform](https://www.researchgate.net/publication/220645279_Turkish_fingerspelling_recognition_system_using_Generalized_Hough_Transform_interest_regions_and_local_descriptors)
  – Klasik görüntü işleme yöntemleriyle TİD heceleme tanıma (karşılaştırma için).
- [Phonological and Morphological Aspects of Lexicalized Fingerspelling in TİD](https://www.researchgate.net/publication/290054124_Phonological_and_Morphological_Aspects_of_Lexicalized_Fingerspelling_in_Turkish_Sign_Language_TID)
  – TİD parmak alfabesinin dilbilimsel özellikleri.

## İndirilen Dosyalar

| Dosya | Kaynak | Not |
|---|---|---|
| `docs/references/turk-isaret-dili-alfabesi.pdf` (10,4 MB) | [EGO – TİD Alfabesi PDF](https://isaretdili.ego.gov.tr/wp-content/uploads/2021/08/turk-isaret-dili-alfabesi2.pdf) | 29 harfin çizimleri. Telifli, git'e eklenmez. |

## Modeller

| Dosya | Kaynak |
|---|---|
| `models/mediapipe/hand_landmarker.task` | [Google MediaPipe – Hand Landmarker (float16)](https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task) |
