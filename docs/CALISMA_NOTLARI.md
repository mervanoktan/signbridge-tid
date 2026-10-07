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
