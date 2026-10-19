# Çalışma Notları

Projede yapılan her adım burada tarihiyle tutulur.

---

## 06.10.2026 – Proje planlaması

**Yapılanlar:**
- Proje fikri tartışıldı: TİD işaretlerini metne ve sese, konuşmayı TİD'e çeviren iki yönlü sistem.
- `YOL_HARITASI.md` oluşturuldu (amaç, mimari, teknolojiler, aşamalar, beklentiler).
- `CLAUDE.md` oluşturuldu (çalışma kuralları).
- `CALISMA_NOTLARI.md` oluşturuldu (bu dosya).

**Alınan kararlar ve gerekçeleri:**
- **Dil: Python, arayüz: PySide6.** Görüntü işleme ve derin öğrenme kütüphaneleri Python'da en olgun hâlde.
- **İskelet (anahtar nokta) tabanlı yaklaşım, ham video değil.** Az veriyle çalışır, arka plan ve ışıktan
  daha az etkilenir, RTX 3050'de gerçek zamanlı çalışır.
- **El + vücut + yüz birlikte (MediaPipe Holistic).** TİD'de işaretin anlamı elin vücuda göre konumuna,
  hareketine ve yüz ifadesine (ör. baş sallama = olumsuzluk) bağlıdır.
- **Normalizasyon: omuz ortası merkez, omuz genişliği ölçek.** Kişinin boyundan ve kameraya uzaklığından bağımsızlık.
- **Gloss → Türkçe için LLM API.** TİD dilbilgisi Türkçeden farklı (ekler, zaman kipleri yok), bu yüzden
  doğal cümle kurmak için dil modeli kullanılıyor. İnternet olmazsa kural tabanlı yedek çalışacak.
- **Kelime dağarcığı sık kullanıma göre (~100 kelime) seçilecek, cümlelere göre değil.** Böylece sistem
  önceden görmediği cümleleri de çevirebilir. Dağarcıkta olmayan kelimeler alfabeyle hecelenir.

**Sıradaki adım:** Aşama 0 – Ortam kurulumu.

---

## 06.10.2026 – Aşama 0: Sistem kontrolü

**Yapılanlar:** Bilgisayardaki yazılım ve donanım sürümleri kontrol edildi (sadece okuma, hiçbir şey kurulmadı).

| Bileşen | Durum |
|---|---|
| Python | 3.11.3 – uygun (MediaPipe ve PyTorch destekliyor) |
| GPU | NVIDIA GeForce RTX 3050, 4 GB VRAM |
| NVIDIA sürücüsü | 512.78 – en fazla CUDA 11.6 destekliyor → **güncellenmesi gerekiyor** |
| CUDA Toolkit (nvcc) | Yok – gerekmiyor, PyTorch kendi CUDA kütüphanelerini getirir |
| Conda | Yok – Python'un kendi `venv` modülü kullanılacak |
| Git | 2.51.2 – var |

**Tespit:** Güncel PyTorch sürümleri en az CUDA 11.8 / 12.x istiyor, mevcut sürücü bunu desteklemiyor.
Sürücü güncellenmeden PyTorch GPU'yu kullanamaz.

---

## 07.10.2026 – Sürücü güncelleme denemesi (beklemede)

**Durum:** NVIDIA sürücüsü indirilemedi.
- NVIDIA App → Game Ready sürücüsü indirilirken hata alındı ("daha sonra tekrar deneyiniz").
- nvidia.com/drivers sitesi bilgisayardan açılmadı ("bağlantınız kesildi").
- Aynı Wi-Fi ağındaki telefondan site açılıyor → sorun ağda değil, **bilgisayarda** (olası nedenler: DNS önbelleği,
  VPN/proxy/antivirüs, hosts dosyası, IPv6).

**Karar:** Sorun evdeki Wi-Fi ağında tekrar denenecek. Çözülmezse teşhis komutları çalıştırılacak
veya sürücü telefondan indirilip bilgisayara aktarılacak.

---

## 07.10.2026 – Sürücü güncellendi ✅

- NVIDIA sürücüsü **617.42** (Game Ready) kuruldu. Kurulum dosyası nvidia.com üzerinden indirildi.
- `nvidia-smi` kontrolü: sürücü 617.42, desteklenen CUDA sürümü **13.4**, RTX 3050 4 GB görünüyor.
- Artık güncel PyTorch sürümleri GPU ile kullanılabilir (CUDA 12.x / 13.x).

**Sıradaki adım:** Sanal ortam (`venv`) kurulumu ve paketlerin yüklenmesi.

---

## 07.10.2026 – Sanal ortam ve paket kurulumu ✅

**Yapılanlar:**
- Proje klasöründe `.venv` sanal ortamı oluşturuldu (Python 3.11.3), pip güncellendi.
- PyTorch'un resmi paket deposunda mevcut CUDA sürümleri kontrol edildi (cu126, cu128, cu129, cu130).
  Sürücü CUDA 13.4'ü desteklediği için en güncel olan **torch 2.14.1 + CUDA 13.0** seçildi.
- Kurulan paketler: torch 2.14.1+cu130, opencv-python 5.0.0, mediapipe 1.1.0, numpy 2.4.6,
  pandas 3.0.6, scikit-learn 1.9.1, matplotlib 3.11.2.
- `requirements.txt` oluşturuldu.

**Test sonuçları:**
- PyTorch GPU'yu görüyor: `NVIDIA GeForce RTX 3050 Laptop GPU`, GPU üzerinde matris çarpımı testi başarılı.
- Tüm paketler hatasız içe aktarılıyor.

**Önemli tespit – MediaPipe API değişikliği:**
- MediaPipe 1.1.0'da eski `mp.solutions` (ör. `mp.solutions.holistic`) arayüzü **kaldırılmış**.
- Yerine yeni **Tasks API** var: `HandLandmarker`, `PoseLandmarker`, `FaceLandmarker`, `HolisticLandmarker`.
- Tasks API, `.task` uzantılı model dosyalarını ayrıca indirmeyi gerektiriyor (ilgili aşamada indirilecek).
- İnternetteki eski örnek kodların çoğu `mp.solutions` kullandığı için bizim kodumuzda doğrudan çalışmaz.

**Sıradaki adım:** Klasör yapısının oluşturulması ve Aşama 1 – Alfabe veri toplama aracı.

---

## 07.10.2026 – Proje yapısı, git ve TİD alfabe araştırması

**Yapılanlar:**
- Klasör yapısı oluşturuldu: `data/`, `models/`, `src/`, `experiments/`, `report/`, `docs/`.
  Boş klasörlerin git'te görünmesi için içlerine `.gitkeep` dosyası kondu.
- `YOL_HARITASI.md` ve `CALISMA_NOTLARI.md` dosyaları `docs/` klasörüne taşındı.
- `README.md` yazıldı (GitHub/portföy sayfası için proje tanıtımı).
- `.gitignore` yazıldı: sanal ortam, önbellek dosyaları, `.env` (API anahtarı), telifli referanslar git'e eklenmez.
- MediaPipe el modeli indirildi: `models/mediapipe/hand_landmarker.task` (7,46 MB, Google resmi deposu).
- TİD parmak alfabesi araştırıldı, sonuçlar `docs/KAYNAKLAR.md` dosyasına yazıldı.
- Git deposu başlatıldı (`main` dalı). Atılan ilk commit kullanıcının isteğiyle geri alındı:
  **commit'leri kullanıcı kendisi atacak**, Claude sadece komutları ve commit mesajını önerecek.

**Araştırmadan çıkan önemli bilgi:**
- TİD parmak alfabesi 29 harf ve **iki elle** yapılıyor (C, I, L, O, P, U, V hariç).
  → Alfabe modelinde iki elin noktaları birlikte kullanılacak (`num_hands=2`). Tek el gören bir model yetersiz kalır.
- Birincil referanslar: Aile ve Sosyal Hizmetler Bakanlığı Güncel TİD Sözlüğü (kelimeler), EGO TİD Alfabesi (harfler).

**Kararlar:**
- Proje ve GitHub repo adı: **SignBridge** (`signbridge-tid`). README başlığı güncellendi.
- `CLAUDE.md` (Claude Code çalışma kuralları) `.gitignore`'a eklendi, GitHub'a gönderilmeyecek, sadece yerelde kalacak.
- Toplanan veri setinin GitHub'a konup konmayacağına Aşama 1'de karar verilecek.
- Uygulamada gösterilecek işaret görselleri telif sorunu olmaması için kendi kayıtlarımızdan üretilecek.

---

## 09.10.2026 – Aşama 1: Veri toplama aracı, alfabe referansı, kelime listesi

**Kamera durumu:**
- Kullanılan bilgisayarda kamera yok, iPhone kamera olarak kullanılacak.
- Windows'un "Bağlı Kamera" özelliği sadece Android'de çalıştığı için **Iriun Webcam** önerildi
  (iPhone + Windows uygulaması). Kurulum ve bağlantı testi evde yapılacak.
- Kod kamera kaynağından bağımsız yazıldı: `--kamera 0/1/2` (bağlı kamera) veya `--kamera http://...` (video adresi).

**Yapılanlar:**
1. **EGO TİD alfabe PDF'i indirildi** → `docs/references/turk-isaret-dili-alfabesi.pdf` (10,4 MB, git'e eklenmez).
   PDF incelendi: 29 harf. C–Ç, G–Ğ, S–Ş, O–Ö, U–Ü, I–İ çiftleri birbirine çok benziyor → modelin en çok
   karıştıracağı harfler bunlar olabilir, değerlendirmede özellikle bakılacak.
2. **`src/collect_alphabet.py` yazıldı** (veri toplama aracı):
   - MediaPipe HandLandmarker (Tasks API), video modu, iki el.
   - Ayna görüntüsü, BGR→RGB dönüşümü, sol/sağ el ayrımı (aynı etiket gelirse x konumuna göre).
   - SPACE → 3 sn geri sayım → 5 sn kayıt → S/X ile onay/iptal. N/P ile harf değiştirme.
   - Her 2 karede bir örnek; gereken el sayısı (tek elli harfler: C, I, L, O, P, U, V) görünmüyorsa kayıt yok.
   - Çıktı: `data/alphabet/landmarks.csv` (132 sütun: kimlik, kişi, harf, el sayısı, 2 × (var + 63 koordinat))
     ve `data/alphabet/images/<harf>/<ornek_id>.jpg` (224×224 el görüntüsü, CNN deneyi için).
   - Türkçe karakter sorunları çözüldü: yazılar Pillow ile, dosyalar `imencode + tofile` ile yazılıyor.
   - `--kamera-listele` seçeneği eklendi.
3. **Kamerasız test yapıldı** (geçici test betiği, projeye eklenmedi): model yükleme, CSV satırı (132 sütun),
   el kırpma (224×224), Türkçe yazı çizimi, aynı etiketli iki elin ayrılması, Türkçe klasöre kayıt ve sayma → hepsi başarılı.
   Bu bilgisayarda kamera olmadığı için `--kamera-listele` "Hiç kamera bulunamadı" verdi (beklenen).
4. **`docs/KELIME_LISTESI.md` yazıldı:** 10 kategoride 108 kelime + BOŞTA sınıfı. 30 kelime "öncelik 1"
   (demo cümlelerini karşılar). El dışı işaret içeren kelimeler (olumsuzluk, soru, duygu) işaretlendi. Onay bekliyor.
5. **`docs/OGRENME_REHBERI.md` oluşturuldu:** Sunuma hazırlık için kod açıklamaları; önemli kısımlar "⭐ ÖNEMLİ",
   olası hoca soruları "💬" ile işaretli. Her aşamada güncellenecek.

**Sıradaki adım:** Evde Iriun kurulumu → kamera testi → alfabe verisinin toplanması.

---

## 09.10.2026 – İlk kamera testi ve deneme kaydı (A harfi)

**Kamera:** Iriun Webcam (iPhone) bağlandı, Windows'ta **Kamera 0** olarak görünüyor.

**Deneme kaydı sonucu:** A harfi için 1 kayıt → **9 örnek**, 9 görüntü. CSV 132 sütun, görüntüler CSV ile birebir eşleşiyor.
Kayıt mekanizması doğru çalışıyor, ancak üç sorun tespit edildi:
1. **Örnek sayısı az (beklenen ~60, gelen 9).** Kare hızı sorunsuz (~24 FPS), ama 5 sn'lik kaydın ~4 sn'sinde
   iki el birlikte tespit edilememiş. Olası neden: A harfinde eller birbirine değiyor/üst üste biniyor,
   MediaPipe ellerden birini kaybediyor.
2. **Kayıt sırasında ellerin rolü değişmiş:** İlk örneklerde üstteki el bir taraftan, son örneklerde diğer taraftan geliyor.
   Aynı harf hep aynı el düzeniyle yapılmalı, yoksa model iki farklı şekil öğrenir.
3. **Sol/sağ etiketleri ters olabilir:** Ekranın sağ tarafındaki el "sol" olarak kaydedilmiş. Iriun'un ayna ayarı
   ya da MediaPipe'ın etiket varsayımından kaynaklanabilir. Tek el testiyle doğrulanacak.

**İkinci deneme:** 50 örnek, iki el baştan sona kesintisiz göründü, el düzeni sabit kaldı → başarılı.
Kalan küçük sorunlar: üstteki el kadrajın üst kenarına çok yakın (parmak uçları kesiliyor), kayıt boyunca el konumu çok az değişiyor
(çeşitlilik için yaklaşma/uzaklaşma/kayma önerildi).

**Sol/sağ testi:** Sağ el kaldırılınca iskelet mavi (= "sol") çıktı → **etiketler ters**.
- **Düzeltme:** `elleri_ayir` içinde MediaPipe'ın "Left" etiketi artık sağ el olarak alınıyor.
- Ekrana her elin bileğinin yanına **SOL / SAĞ** yazısı eklendi (etiketleri gözle kontrol etmek için).
- Mevcut veri düzeltildi (CSV önce yedeklendi):
  - İlk denemenin 9 hatalı örneği CSV'den ve `images/A/` klasöründen silindi (kullanıcı onayıyla).
  - Kalan 50 örnekte `sol_*` ve `sag_*` sütunları yer değiştirildi.
  - Kontrol: düzeltme sonrası sol el ekranın solunda (ort. x = 0,48), sağ el sağında (ort. x = 0,70) → ayna görüntüsüyle tutarlı.
- Kamerasız testler tekrar çalıştırıldı, hepsi başarılı.

**A harfi tamamlandı:** 6 kayıt, 329 örnek, tüm örneklerde iki el görünüyor, sol el hep solda.
3 kayıtta üstteki elin parmak uçları kadraj dışına taşmış (MediaPipe tahminle tamamlıyor) → ellerin daha aşağıda tutulması önerildi.

**Harf değiştirme hatası:**
- Kullanıcı tek elli C harfinde örnek toplanmadığını bildirdi. İnceleme: program aslında hâlâ **A** harfindeydi
  (A iki el istediği için tek elle örnek alınmıyordu). N tuşu algılanmamıştı.
- Bu yüzden 19:06'daki 3 kayıt (168 örnek) **A etiketiyle kaydedilmiş ama aslında B harfi** (görüntülerden doğrulandı:
  iki elin parmak uçları birleşik, A'dan tamamen farklı).
- Olası neden: Caps Lock/Shift açıkken `N` büyük harf olarak geliyor, kod sadece küçük `n`'yi kontrol ediyordu.
- **Düzeltmeler:**
  - Tuşlar artık büyük/küçük harf duyarsız.
  - Harf değişince terminale de yazılıyor (`Harf: B`).
  - `--harf` seçeneği eklendi: program istenen harften başlatılabiliyor (ör. `--harf C`).

**Aynı programın iki kopyası çalışıyordu:** Kullanıcının isteğiyle durdurulduğunda arka planda iki `collect_alphabet.py`
süreci bulundu (ikisi de aynı kamerayı kullanıyordu). Ekrandaki karışıklığın nedeni büyük ihtimalle buydu. İkisi de kapatıldı.
→ Program her seferinde **tek pencere** olarak açılmalı; yeniden başlatmadan önce eski pencere Q ile kapatılmalı.

**Veri düzeltmesi (CSV önce yedeklendi):** 19:06'daki 168 örnek A'dan **B**'ye çevrildi, görüntüleri `images/B/` klasörüne taşındı.
Sonuç: A = 329, B = 168.

**Tek elli harfler için iyileştirme:**
- Önceden tek elli harflerde "en az 1 el" yeterliydi; diğer el kadrajdaysa o da kaydediliyordu (tutarsız veri).
- Artık tek elli harflerde sadece **baskın el** (varsayılan sağ, `--baskin-el sol` ile değiştirilebilir) kullanılıyor,
  diğer el yok sayılıyor ve ekranda çizilmiyor. Baskın el görünmüyorsa kayıt alınmıyor.
- İki elli harflerde artık "toplam 2 el" değil, **hem sol hem sağ elin** ayrı ayrı görünmesi şartı aranıyor.
- Ekrandaki "Eller: 1/2" yazısı yerine "Gereken: SAĞ el (TAMAM/EKSİK)" ya da "Gereken: iki el (TAMAM/EKSİK)" gösteriliyor.

---

## 10.10.2026 – Veri kontrolü: A–E harfleri

| Harf | Örnek | Kayıt | El | Kadraj dışına taşan nokta içeren örnek |
|---|---|---|---|---|
| A | 329 | 6 | iki | %24 |
| B | 331 | 6 | iki | %2 |
| C | 343 | 7 | sadece sağ ✅ | %0 |
| Ç | 327 | 6 | iki | **%94** |
| D | 352 | 6 | iki | %2 |
| E | 350 | 6 | iki | **%43** (2 kayıt tamamen) |

- Toplam 2.032 örnek, 2.032 görüntü; hepsi doğru harf klasöründe ve CSV ile eşleşiyor.
- **Tek el düzeltmesi çalışıyor:** C harfinde sol el hiç kaydedilmemiş, sağ el her örnekte var.
- Tüm harflerde sol el solda, sağ el sağda; el düzeni kayıtlar arasında tutarlı.
- **Sorun:** Ç ve E'de alttaki elin bileği kadrajın alt kenarından taşıyor (görüntülerden doğrulandı). MediaPipe görünmeyen
  noktaları tahminle tamamlıyor; veri kullanılabilir ama bilek ileride normalizasyonun referans noktası olacağı için
  tahmin hatası modeli etkileyebilir. Kalan harflerde bileklerin de kadrajda olması istendi. Ç ve E şimdilik yeniden
  kaydedilmeyecek; model eğitiminde bu harflerin başarısı düşük çıkarsa yeniden kaydedilecek.

---

## 19.10.2026 – Karar: harflerin ikinci şekilleri

- Bazı harflerin TİD'de iki farklı yapılış şekli var. Önerilen yöntem: her şekli ayrı **varyant** olarak kaydetmek
  (CSV'ye `varyant` sütunu, `images/<harf>_<varyant>/` klasörü, her varyant için 300 örnek, ekranda ikisi de aynı harf).
- **Kullanıcının kararı:** Önce her harf **tek şekilde ve eşit sayıda** (~300) kaydedilecek. İlk model denemesinden sonra
  ikinci şekiller eklenecek. Varyant desteği o zaman koda eklenecek; mevcut örnekler varyant 1 sayılacak.

---

## 19.10.2026 – Veri kontrolü: F–Z harfleri

- 19.10'da F'den Z'ye kayıt yapıldı. Toplam **9.370 örnek**, 9.370 görüntü (hepsi doğru klasörde, CSV ile eşleşiyor).
- Her harf 6 kayıt, 297–352 örnek. Tek elli harflerde (I, L, O, P, U, V) sadece sağ el, iki ellilerde iki el → tutarlı.
- **Ğ harfi hiç kaydedilmemiş** (büyük ihtimalle G'den sonra N'ye iki kez basılıp H'ye geçildi).
- **G harfi şüpheli:** Harf ortalamaları karşılaştırıldığında en benzer çift **G–S** (benzerlik 0,85; S–Ş: 1,01, G–Ş: 1,09).
  Görüntülerde G de S/Ş gibi iki elin "C" şeklinde birleştiği bir işaret olarak yapılmış. EGO PDF'inde ise G iki yumruğun
  üst üste konmasıyla gösteriliyor. Kullanıcıdan kaynağı kontrol etmesi istendi.
- S–Ş benzerliği beklenen bir durum (TİD'de birbirine çok benzeyen harf çifti).
- K harfinde örneklerin %38'inde bilek kadraj dışında (Ç ve E'deki gibi), şimdilik kalacak.

**Karar:** Ğ şimdilik kaydedilmeyecek; ilk model **28 harfle** eğitilecek. G'nin durumu karışıklık matrisinde
(G–S karışması) kontrol edilecek.

---

## 19.10.2026 – Hazır TİD veri setleri araştırması

- Kullanıcı hazır veri setlerinin neden kullanılmadığını sordu. Araştırma sonucu: alfabe için Kaggle'da 2.974 fotoğraflık
  bir veri seti var (bizimki 9.370 örnek); kelimeler için **TurkSign446** (446 kelime, MediaPipe Holistic noktaları hazır,
  CC BY 4.0, 8,7 GB) ve **AUTSL** (226 kelime, 43 kişi, video, kayıt gerekli) var. Ayrıntılar `docs/KAYNAKLAR.md`'de.
- Değerlendirme: Alfabe verisini kendimiz toplamamız boşa gitmedi (daha büyük, sistemimize uygun, raporda katkı).
  Ancak hazır veri setleri araştırması kayıttan önce yapılmalıydı.
- **Karar (kullanıcı önerisi):** Kelime işaretleri hazır veri setlerinden alınacak. Kelime listesi, bu veri setlerinde
  bulunan kelimelere göre güncellenecek; sadece demo için kritik ve veri setlerinde olmayan birkaç kelime kaydedilecek.
- Kaggle alfabe veri seti, alfabe modelini **başka kişilerde test etmek** için kullanılabilir.

---

## 19.10.2026 – Aşama 2: Alfabe modeli eğitimi ✅

**Yazılan dosyalar:**
- `src/features.py` – Ham noktalardan 131 boyutlu özellik vektörü: her el için bileğe göre öteleme + el boyutuna
  (bilek–orta parmak kökü) göre ölçekleme (2 × 63), el var/yok bayrakları (2), sağ bileğin sol bileğe göre konumu (3).
- `src/train_alphabet.py` – Kayıt bazlı bölme (her harfin 1 kaydı test, 1 kaydı doğrulama), iki model, değerlendirme, grafikler.
- `docs/YONTEMLER.md` – Kullanılan tüm algoritmaların ve kütüphanelerin nerede/neden kullanıldığı (rapor için).

**Kullanılan algoritmalar:**
| Algoritma | Tür | Rol |
|---|---|---|
| MediaPipe Hand Landmarker | Hazır derin öğrenme modeli (CNN tabanlı, iki aşamalı: avuç dedektörü + nokta modeli) | Görüntüden 21 el noktası |
| Geometrik normalizasyon | Öteleme + ölçekleme | Konum ve mesafeden bağımsız özellik |
| **MLP** (131→256→128→28) | **Yapay sinir ağı (ANN), CNN değil** – BatchNorm, ReLU, Dropout %30, Adam, Cross-Entropy, early stopping, veri artırma (±10° döndürme + gürültü) | Asıl sınıflandırıcı |
| Random Forest (300 ağaç) | Klasik makine öğrenmesi (topluluk yöntemi) | Karşılaştırma |

**Neden CNN değil MLP:** Modele giden veri görüntü değil 131 sayılık vektör; CNN ızgara yapısındaki (görüntü) veriler için.
Görüntüden nokta çıkarma işini MediaPipe (içinde CNN var) yapıyor. CNN, kırpılmış el görüntüleriyle karşılaştırma
deneyinde (Aşama 16) kullanılacak.

**Kütüphaneler:** PyTorch (MLP, GPU), scikit-learn (Random Forest, metrikler), NumPy/pandas (veri), matplotlib (grafikler).
Gerekçeler `docs/YONTEMLER.md`'de.

**Sonuçlar** (28 harf, 9.370 örnek; eğitim 6.232 / doğrulama 1.568 / test 1.570):
| Model | Test başarısı | Süre |
|---|---|---|
| MLP | **%99,62** | 8,3 sn (GPU, 22 epoch'ta early stopping) |
| Random Forest | %99,62 | 1,5 sn |

- 26 harf %100. Tek hata: U'nun %11'i (6 örnek) O olarak tahmin edildi.
- G–S ve S–Ş karışmadı (G'nin şekli şüpheliydi ama kendi içinde tutarlı ve ayırt edilebilir).
- Hedef (%90) fazlasıyla aşıldı.
- **Sınırlılık:** Tüm veri tek kişiden, aynı ortamda. Başka kişilerde başarı düşebilir → Kaggle veri seti veya
  arkadaşlardan veri ile test edilmeli.

**Çıktılar:** `models/alphabet/harf_mlp.pt`, `report/figures/alfabe_karisiklik_matrisi.png`,
`report/figures/alfabe_egitim_grafigi.png`, `report/alfabe_sonuclar.json`.

**Not:** Kırpılan el görüntülerinde kullanıcının yüzü de görünüyor → `images/` klasörünün GitHub'a konmaması düşünülmeli.
