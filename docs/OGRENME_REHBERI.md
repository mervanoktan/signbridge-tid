# Öğrenme Rehberi

Sunumdan önce sistemi ve kodu öğrenmek için hazırlanmış rehber. Her aşama tamamlandıkça yeni bölüm eklenir.

**İşaretler:**
- ⭐ **ÖNEMLİ**: Hocanın sorma ihtimali yüksek olan, mutlaka bilinmesi gereken kısımlar.
- 💬 **Olası soru**: Sunumda gelebilecek sorular ve cevapları.

Kodun içinde de önemli satırların üstünde `# ÖNEMLİ:` yorumu var.

---

## Bölüm 1 – Veri Toplama Aracı (`src/collect_alphabet.py`)

### Ne işe yarıyor?
Kameradan TİD parmak alfabesi harflerini kaydeder. Her örnek için iki elin anahtar noktalarını CSV dosyasına,
ellerin bulunduğu bölgenin görüntüsünü de klasöre yazar. Bu veri, bir sonraki aşamada modeli eğitmek için kullanılacak.

### Genel akış (her kare için)
```
Kameradan kare al
  → Ayna gibi çevir (flip)
  → BGR'den RGB'ye çevir
  → MediaPipe HandLandmarker ile elleri bul (her el için 21 nokta)
  → Elleri "sol" ve "sağ" olarak ayır
  → Kayıt modundaysak ve yeterli el görünüyorsa: örneği tampona ekle
  → İskeleti ve yazıları çiz, ekranda göster
  → Tuşları kontrol et
```

### ⭐ ÖNEMLİ 1 – MediaPipe HandLandmarker ve 21 nokta
- MediaPipe, Google'ın hazır el tespit modeli. Bir görüntüde eli bulur ve her el için **21 anahtar nokta**
  (landmark) verir: bilek (0), her parmak için 4 nokta (eklemler ve parmak ucu).
- Her noktanın **x, y, z** değeri var. x ve y görüntü genişliğine/yüksekliğine göre **0–1 arasına normalize** edilmiştir.
  z ise bileğe göre derinliği gösterir (kameraya yakınlık).
- Bir el = 21 × 3 = **63 sayı**. İki el = **126 sayı**.
- `num_hands=2`: TİD alfabesinde 29 harften 22'si **iki elle** yapıldığı için iki el tespit ediliyor.
  (Tek elle yapılanlar: C, I, L, O, P, U, V.)
- `running_mode=VIDEO`: Model her kareyi bağımsız işlemek yerine önceki karedeki eli **takip eder**.
  Bu hem daha hızlı hem de daha kararlı sonuç verir. Video modu her kare için artan bir zaman damgası ister,
  kodda `zaman_ms` bunun için var.

💬 **"Eli nasıl tespit ediyorsunuz?"**
→ MediaPipe HandLandmarker kullanıyoruz. İki aşamalı çalışır: önce bir avuç dedektörü görüntüde elin yerini bulur,
sonra o bölgede ikinci bir model 21 anahtar noktayı tahmin eder. Biz bu noktaları özellik olarak kullanıyoruz.

💬 **"Neden görüntünün kendisini değil de noktaları kullanıyorsunuz?"**
→ Noktalar arka plandan, ışıktan, ten renginden ve kıyafetten çok daha az etkilenir. 126 sayılık bir vektör,
224×224×3 = 150.528 sayılık bir görüntüden çok daha küçüktür; bu yüzden az veriyle eğitilebilir ve gerçek zamanlı çalışır.
Yine de el görüntülerini de kaydediyoruz; ileride görüntü tabanlı bir CNN ile karşılaştırma yapacağız.

### ⭐ ÖNEMLİ 2 – Ayna görüntüsü (`cv2.flip(kare, 1)`)
- Görüntü yatay eksende çevriliyor. İki nedeni var:
  1. Kullanıcı kendini **ayna gibi** görür, el hareketlerini yapmak daha doğal olur.
  2. MediaPipe'ın sol/sağ el etiketleri, girdinin ayna görüntüsü olduğunu varsayar. Çevirmezsek sol el "sağ" olarak etiketlenir.

### ⭐ ÖNEMLİ 3 – BGR → RGB dönüşümü
- OpenCV görüntüleri **BGR** (mavi-yeşil-kırmızı) sırasıyla okur; MediaPipe ise **RGB** bekler.
- Dönüşüm yapılmazsa kırmızı ve mavi kanallar yer değiştirir ve modelin doğruluğu düşer.

💬 **"OpenCV neden BGR kullanıyor?"**
→ Tarihsel bir sebep: OpenCV geliştirildiğinde kamera üreticileri ve Windows'un bitmap formatı BGR sırasını
yaygın kullanıyordu, OpenCV de bu sırayı varsayılan yaptı.

### ⭐ ÖNEMLİ 4 – Sol ve sağ elin ayrılması (`elleri_ayir`)
- MediaPipe her el için "Left" veya "Right" etiketi verir. Biz bunları CSV'de sabit sütunlara yazıyoruz:
  önce **sol el** (63 sayı), sonra **sağ el** (63 sayı). Böylece model her zaman aynı sütunda aynı eli görür.
- **Etiketlerin ters gelmesi sorunu:** Testte sağ el kaldırıldığında MediaPipe "Left" etiketi verdi (iskelet yanlış renkte çizildi).
  Yani bizim kurulumumuzda (iPhone + Iriun + ayna çevirme) etiketler ters geliyor. Kodda "Left" etiketi sağ el olarak alınıyor.
  Ekranda her elin bileğinin yanında **SOL / SAĞ** yazısı var, böylece etiketin doğruluğu her an gözle kontrol edilebiliyor.
  Bu, hazır bir modelin çıktısına körü körüne güvenmeyip **test ederek doğrulamanın** iyi bir örneği; sunumda anlatılabilir.
- MediaPipe bazen iki ele de aynı etiketi verebiliyor. Bu durumda ellerin x konumuna bakıyoruz:
  ayna görüntüsünde sol el ekranın solunda kalır.
- Bir el görünmüyorsa (ör. tek elli harfler) o elin yerine **sıfır** yazılır ve `sol_var` / `sag_var` sütunu 0 olur.

- **Tek elli harfler (C, I, L, O, P, U, V):** Sadece **baskın el** (varsayılan sağ) kaydedilir. Diğer el kadrajda görünse
  bile yok sayılır. Böylece tek elli harflerin hepsinde el hep aynı sütunlarda durur ve model tutarlı veri görür.
- **İki elli harfler:** Hem sol hem sağ elin ayrı ayrı görünmesi gerekir.

💬 **"Bir el görünmezse ne oluyor?"**
→ O elin 63 değeri sıfır yazılıyor ve "var" bayrağı 0 oluyor. Model bu bayrağa bakarak elin olmadığını öğrenebiliyor.
İki elli bir harfte bir el görünmüyorsa o kare hiç kaydedilmiyor, çünkü eksik veri modeli yanıltır.

### ⭐ ÖNEMLİ 5 – Neden ham koordinat kaydediyoruz?
- CSV'ye MediaPipe'ın verdiği **ham** koordinatları yazıyoruz; normalizasyon gibi işlemleri bir sonraki aşamada yapacağız.
- Sebep: Özellik çıkarma yöntemini sonradan değiştirmek istersek **veriyi baştan toplamamız gerekmez**.
  Veri toplama zahmetli, işleme ise ucuz.

### ⭐ ÖNEMLİ 6 – Veri kalitesi için alınan önlemler
| Önlem | Neden |
|---|---|
| **Her 2 karede bir** örnek (`KARE_ATLAMA = 2`) | Ardışık kareler neredeyse aynıdır; hepsini almak veri setini gereksiz tekrarla doldurur |
| **Gereken el sayısı** görünmüyorsa kayıt yok | Eksik veri modeli yanıltır |
| **3 sn geri sayım** | Kullanıcının elini doğru pozisyona getirmesi için zaman |
| **Onay adımı** (S: kaydet / X: iptal) | Yanlış yapılan bir kayıt veri setine girmeden atılabilir |
| **Kayıt sırasında elin hafif hareket ettirilmesi** | Model tek bir pozu ezberlemez, farklı mesafe/açı/konumlara genelleşir |
| **Kişi adı** (`--kisi`) | Farklı kişilerden veri toplanabilir; test aşamasında "hiç görmediği kişide başarı" ölçülebilir |

### Durum makinesi (state machine)
Program dört durum arasında geçiş yapar:
```
BEKLE ──SPACE──► GERI_SAYIM ──3 sn──► KAYIT ──5 sn──► ONAY ──S/X──► BEKLE
```
Her karede programın hangi durumda olduğuna göre farklı davranır. Bu, kullanıcı arayüzlerinde sık kullanılan basit bir yöntemdir.

### Diğer teknik ayrıntılar
- **Türkçe karakterler:** OpenCV'nin `putText` fonksiyonu Ç, Ğ, İ, Ş gibi harfleri çizemiyor. Bu yüzden yazılar
  **Pillow** kütüphanesiyle çiziliyor (`yazi_yaz` fonksiyonu).
- **Türkçe dosya yolları:** `cv2.imwrite` Windows'ta Türkçe karakterli klasörlere (`images/Ş/`) yazamıyor.
  Görüntü önce `cv2.imencode` ile bellekte JPEG'e çevrilip sonra `tofile` ile yazılıyor.
- **El görüntüsünün kırpılması:** Ellerin tüm noktalarını kapsayan dikdörtgen bulunur, %30 pay eklenip kare yapılır
  ve 224×224'e küçültülür. 224×224, MobileNet gibi hazır CNN modellerinin standart giriş boyutudur.
- **Kamera kaynağı:** `--kamera 0` bilgisayara bağlı kamerayı, `--kamera http://...` bir video adresini açar.
  Windows'ta `CAP_DSHOW` (DirectShow) kamerayı daha hızlı açtığı için kullanılıyor.

### CSV dosyasının yapısı (`data/alphabet/landmarks.csv`)
| Sütun | Açıklama |
|---|---|
| `ornek_id` | Benzersiz kimlik (kişi + tarih-saat). Aynı isimli görüntü dosyasıyla eşleşir. |
| `kisi` | Kaydı yapan kişi |
| `harf` | Etiket (A, B, C, Ç, ...) |
| `el_sayisi` | Görünen el sayısı (1 veya 2) |
| `sol_var` | Sol el görünüyor mu (0/1) |
| `sol_0_x` … `sol_20_z` | Sol elin 21 noktasının x, y, z değerleri (63 sütun) |
| `sag_var`, `sag_0_x` … `sag_20_z` | Aynısı sağ el için (64 sütun) |

Toplam **132 sütun**.

### Dikkat edilecek harf çiftleri (ilk tahmin)
EGO alfabe görselinde bazı harfler birbirine çok benziyor: **C–Ç, G–Ğ, S–Ş, O–Ö, U–Ü, I–İ**.
Bunlar genelde temel harfe küçük bir ek ya da hareket eklenerek yapılıyor. Modelin en çok karıştıracağı harfler
büyük ihtimalle bunlar olacak; confusion matrix'te (karışıklık matrisi) özellikle bunlara bakacağız ve raporda tartışacağız.

---

## Bölüm 2 – Özellik Çıkarma (`src/features.py`)

Yöntemlerin ve kütüphanelerin genel özeti: `docs/YONTEMLER.md`

### Ne işe yarıyor?
MediaPipe'ın verdiği ham koordinatları modelin kullanacağı **131 sayılık özellik vektörüne** çevirir.
Aynı fonksiyon hem eğitimde (CSV'den) hem de ileride canlı tanımada (kameradan) kullanılacak.

### ⭐ ÖNEMLİ 7 – Normalizasyon: neden ham koordinatları doğrudan kullanmıyoruz?
Ham x, y değerleri elin **ekrandaki yerine** ve **kameraya uzaklığına** göre değişir. Aynı A harfini ekranın solunda
ya da sağında, yakında ya da uzakta yapınca bambaşka sayılar çıkar. Model "harfi" değil "elin nerede durduğunu" öğrenirdi.

Çözüm, `el_ozelligi` fonksiyonu:
1. **Öteleme:** `goreli = noktalar - noktalar[0]` → bilek (0. nokta) orijine taşınır. Artık elin konumu önemsiz.
2. **Ölçekleme:** `goreli / el_boyutu(noktalar)` → bilek ile orta parmak kökü (9. nokta) arası mesafeye bölünür.
   Artık kameraya uzaklık önemsiz.

💬 **"Neden ölçek olarak bilek–orta parmak kökü mesafesini seçtiniz?"**
→ Bu iki nokta avucun içinde, el şekli değişse de (yumruk, açık el) aralarındaki mesafe neredeyse sabit kalır.
Parmak uçlarını kullansaydık, parmak bükülünce ölçek de değişirdi.

### ⭐ ÖNEMLİ 8 – Özellik vektörünün yapısı (131 sayı)
| Parça | Boyut | Açıklama |
|---|---|---|
| Sol el şekli | 63 | 21 nokta × (x, y, z), normalize |
| Sağ el şekli | 63 | aynı, sağ el için |
| El var mı | 2 | sol, sağ (1/0) — tek elli harflerde sol el 0 |
| Eller arası | 3 | sağ bileğin sol bileğe göre konumu (iki elin ortalama boyutuna bölünmüş) |

"Eller arası" bilgisi olmasaydı model sadece iki elin **şeklini** bilirdi, birbirine göre **nasıl durduklarını** bilmezdi.

---

## Bölüm 3 – Model Eğitimi (`src/train_alphabet.py`)

### Ne işe yarıyor?
Toplanan verilerle iki model eğitir (MLP ve Random Forest), test eder, sonuçları ve grafikleri kaydeder.

### ⭐ ÖNEMLİ 9 – MLP mi CNN mi? (Bu soru kesin gelir)
- Kullandığımız model **MLP (Multi-Layer Perceptron / çok katmanlı algılayıcı)**, yani klasik bir **yapay sinir ağı (ANN)**.
- **CNN kullanmadık**, çünkü CNN görüntü gibi **ızgara (piksel) yapısındaki** veriler için tasarlanmıştır; evrişim (convolution)
  filtreleri komşu pikseller arasındaki desenleri yakalar. Bizim modelimize giden veri bir görüntü değil, **131 sayılık bir vektör**.
- Görüntüyle ilgili zor işi (eli bulmak, noktaları çıkarmak) zaten **MediaPipe** yapıyor; MediaPipe'ın içinde CNN tabanlı modeller var.
  Yani sistemin tamamında CNN var, ama **bizim eğittiğimiz** sınıflandırıcı MLP.
- İleride kırpılmış el görüntüleriyle bir **CNN** eğitip iki yaklaşımı karşılaştıracağız (Aşama 16).

💬 **"Neden CNN kullanmadınız?"**
→ "Girdimiz görüntü değil, MediaPipe'ın çıkardığı 21 noktalık el iskeleti. Vektör şeklindeki veri için MLP uygun. İskelet tabanlı
yaklaşım arka plandan ve ışıktan daha az etkileniyor, az veriyle eğitilebiliyor ve gerçek zamanlı çalışıyor.
Görüntü tabanlı CNN ile karşılaştırmayı ayrıca deney olarak yapacağız."

### ⭐ ÖNEMLİ 10 – MLP'nin yapısı
```
131 giriş → [Linear 256 → BatchNorm → ReLU → Dropout %30] → [Linear 128 → BatchNorm → ReLU → Dropout %30] → Linear 28
```
| Bileşen | Görevi |
|---|---|
| **Linear (tam bağlantılı katman)** | Girdilerin ağırlıklı toplamını hesaplar (öğrenilen kısım) |
| **ReLU** | Doğrusal olmayan aktivasyon: negatifleri 0 yapar. Olmasa ağ ne kadar derin olursa olsun doğrusal bir model olurdu |
| **BatchNorm** | Katman çıktılarını normalize eder → daha hızlı ve kararlı eğitim |
| **Dropout** | Eğitimde nöronların %30'unu rastgele kapatır → ağ tek bir nörona bağımlı kalmaz, ezberlemez (overfitting önlenir) |
| **Çıkış (28)** | Her harf için bir skor; en yüksek skorlu harf tahmin edilir |
| **Cross-Entropy kaybı** | Doğru harfe verilen olasılık ne kadar düşükse kayıp o kadar büyük |
| **Adam** | Ağırlıkları güncelleyen optimizasyon algoritması (gradyan inişinin uyarlanabilir öğrenme oranlı hâli) |

### ⭐ ÖNEMLİ 11 – Kayıt bazlı bölme (veri sızıntısını önleme)
- Veriyi **eğitim / doğrulama / test** olarak üçe ayırıyoruz:
  - **Eğitim:** Model bununla öğrenir.
  - **Doğrulama:** Eğitim sırasında en iyi modeli seçmek için (early stopping).
  - **Test:** Sadece en sonda, bir kez; modelin hiç görmediği veride gerçek başarısı.
- Bölmeyi **örnek bazında değil kayıt bazında** yaptık: Her harfin 6 kaydından 1'i tamamen test, 1'i tamamen doğrulama.
- **Neden?** Bir kayıttaki 50 kare birbirinin neredeyse aynısı. Örnek bazında rastgele bölseydik test setindeki karelerin
  neredeyse aynısı eğitimde olurdu; model "ezberlediği" kareleri test ediyor olurdu ve başarı yapay olarak yüksek çıkardı.
  Buna **veri sızıntısı (data leakage)** denir.

💬 **"Test başarınız gerçekçi mi?"**
→ "Test verisi eğitimde hiç kullanılmayan ayrı kayıtlardan oluşuyor. Ama tüm veri tek kişiden ve benzer ortamlardan toplandı;
başka kişilerde başarı muhtemelen daha düşük olur. Bunu ölçmek için başka kişilerin verisiyle test planlıyoruz."
(Bu dürüst cevap, hocanın gözünde çok değerli olur.)

### ⭐ ÖNEMLİ 12 – Ezberlemeyi (overfitting) önlemek için alınan önlemler
1. **Dropout** (%30)
2. **Weight decay** (ağırlıkların büyümesini cezalandırma, L2 düzenlileştirme)
3. **Veri artırma:** Her epoch'ta örnekler ±10° döndürülür ve küçük gürültü eklenir (kamera eğikliği, MediaPipe titremesi)
4. **Early stopping:** Doğrulama başarısı 15 epoch iyileşmezse durdur, en iyi ağırlıkları kullan

### Random Forest neden var?
Karşılaştırma için. Raporda "derin öğrenme (MLP) klasik makine öğrenmesine (Random Forest) göre ne kazandırıyor?" sorusunu cevaplar.
Random Forest, çok sayıda karar ağacının **oylamasıyla** karar verir.

### İlk sonuçlar (19.10.2026)
| Model | Test başarısı | Eğitim süresi |
|---|---|---|
| **MLP** | **%99,62** | 8,3 sn (GPU) |
| Random Forest | %99,62 | 1,5 sn |

- 28 harf (Ğ henüz yok), 9.370 örnek: eğitim 6.232 / doğrulama 1.568 / test 1.570.
- 28 harften 26'sı %100. Tek hata: **U'nun %11'i O olarak tahmin edildi** (6 örnek). İkisi de tek elli ve el şekilleri benziyor.
- Beklenenin aksine G–S ve S–Ş karışmadı.
- **İki modelin aynı sonucu vermesi** şunu gösteriyor: işin zor kısmını iyi seçilmiş özellikler (normalizasyon) çözüyor;
  bu veri için sınıflandırıcının türü çok fark yaratmıyor.

💬 **"%99,6 çok yüksek değil mi, nasıl bu kadar iyi?"**
→ "Üç sebebi var: (1) MediaPipe gürültüyü (arka plan, ışık) eliyor ve elimize temiz noktalar kalıyor, (2) normalizasyon konum ve
mesafe farklarını ortadan kaldırıyor, (3) tüm veri tek kişiden. Üçüncüsü bir sınırlılık: başka kişilerde başarı düşebilir,
bunu ayrıca test edeceğiz."
