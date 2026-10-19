# Kelime Dağarcığı (Öneri – onay bekliyor)

Sistemin tanıyacağı TİD kelime işaretleri. Kelimeler belirli cümlelere göre değil, **günlük hayatta sık
kullanılma** ölçütüne göre seçildi. Dil katmanı (LLM) dilbilgisini tamamladığı için bu kelimeler serbestçe
birleştirilerek önceden görülmemiş cümleler kurulabilir. Listede olmayan kelimeler parmak alfabesiyle hecelenir.

**Toplam: 108 kelime + 1 "BOŞTA" sınıfı** (işaret yapılmayan / geçiş anları)

## Öncelik

- **Öncelik 1 (★):** İlk eğitilecek 30 kelime. Demo cümlelerinin tamamını karşılar.
- **Öncelik 2:** Kalan kelimeler, zaman kaldıkça eklenir.

## El dışı işaretler (vücut / yüz)

Bazı kelimelerde anlam sadece elle değil, **baş ve yüz hareketiyle** de verilir. Bunlar "el + vücut + yüz"
modelinin gerekliliğini göstermek için listeye bilerek eklendi (ablation deneyi, Aşama 10):
- **Olumsuzluk** (DEĞİL, YOK, HAYIR): baş sallama / geriye atma eşlik edebilir.
- **Soru kelimeleri** (NE, NEREDE, NEDEN...): kaş hareketi eşlik eder.
- **Duygu sıfatları** (MUTLU, ÜZGÜN, YORGUN): yüz ifadesi anlamın parçasıdır.

> Her kelimenin TİD'deki doğru yapılışı **Güncel TİD Sözlüğü**'nden (tidsozluk.aile.gov.tr) kontrol
> edilecek. TİD'de bazı Türkçe kelimelerin karşılığı aynı işaret olabilir (ör. YEMEK isim/fiil).

---

## 1. Kişiler ve zamirler (12)
| Kelime | Öncelik | Not |
|---|---|---|
| BEN | ★ | göstererek yapılır |
| SEN | ★ | |
| O | ★ | |
| BİZ | | |
| SİZ | | |
| ONLAR | | |
| ANNE | | |
| BABA | | |
| EŞ | ★ | |
| ARKADAŞ | ★ | |
| ÖĞRETMEN | | |
| ÖĞRENCİ | | |

## 2. Zaman (11)
| Kelime | Öncelik | Not |
|---|---|---|
| BUGÜN | ★ | cümlenin zaman kipini belirler |
| YARIN | ★ | gelecek zaman |
| DÜN | ★ | geçmiş zaman |
| ŞİMDİ | | |
| SONRA | | |
| ÖNCE | | |
| SABAH | | |
| AKŞAM | | |
| GECE | ★ | |
| HAFTA | | |
| SAAT | | |

## 3. Fiiller (25)
| Kelime | Öncelik | Not |
|---|---|---|
| GELMEK | ★ | hareket yönü önemli |
| GİTMEK | ★ | GELMEK'in ters yönü |
| YEMEK | ★ | isim ve fiil olarak |
| İÇMEK | | |
| UYUMAK | | |
| ÇALIŞMAK | | |
| OKUMAK | | |
| YAZMAK | | |
| GÖRMEK | | |
| BİLMEK | ★ | |
| ANLAMAK | ★ | |
| İSTEMEK | ★ | |
| SEVMEK | ★ | |
| YAPMAK | | |
| BEKLEMEK | | |
| YARDIM ETMEK | ★ | |
| KONUŞMAK | | |
| ALMAK | | |
| VERMEK | | |
| OTURMAK | | |
| BAŞLAMAK | | |
| BİTMEK | | |
| ÖĞRENMEK | | |
| DÜŞÜNMEK | | |
| OYNAMAK | | |

## 4. Sıfatlar ve durumlar (14)
| Kelime | Öncelik | Not |
|---|---|---|
| İYİ | ★ | |
| KÖTÜ | | |
| GÜZEL | ★ | |
| HASTA | ★ | |
| MUTLU | | yüz ifadesi |
| ÜZGÜN | | yüz ifadesi |
| YORGUN | | yüz ifadesi |
| AÇ | | |
| BÜYÜK | | |
| KÜÇÜK | | |
| ÇOK | | |
| AZ | | |
| SICAK | | |
| SOĞUK | | |

## 5. Yerler (10)
| Kelime | Öncelik | Not |
|---|---|---|
| EV | ★ | |
| OKUL | ★ | |
| DERS | ★ | |
| HASTANE | | |
| RESTORAN | ★ | |
| İŞ | | |
| MARKET | | |
| ŞEHİR | | |
| YOL | | |
| KÜTÜPHANE | | |

## 6. Nesneler ve kavramlar (10)
| Kelime | Öncelik | Not |
|---|---|---|
| SU | | |
| ÇAY | | |
| KİTAP | | |
| PARA | | |
| TELEFON | | |
| ARABA | | |
| İSİM | ★ | "adım ..." cümleleri için |
| DOKTOR | | |
| İLAÇ | | |
| ZAMAN | | |

## 7. Soru kelimeleri (7)
| Kelime | Öncelik | Not |
|---|---|---|
| NE | ★ | kaş hareketi |
| NEREDE | | kaş hareketi |
| NE ZAMAN | | kaş hareketi |
| NEDEN | | kaş hareketi |
| NASIL | | kaş hareketi |
| KİM | | kaş hareketi |
| KAÇ | | kaş hareketi |

## 8. Olumlu / olumsuz (6)
| Kelime | Öncelik | Not |
|---|---|---|
| DEĞİL | ★ | baş hareketi |
| YOK | | baş hareketi |
| VAR | | |
| EVET | | |
| HAYIR | | baş hareketi |
| TAMAM | | |

## 9. Sosyal ifadeler (9)
| Kelime | Öncelik | Not |
|---|---|---|
| MERHABA | ★ | |
| GÜNAYDIN | | |
| HOŞÇA KAL | | |
| TEŞEKKÜRLER | ★ | |
| LÜTFEN | | |
| ÖZÜR DİLERİM | | |
| GEÇMİŞ OLSUN | | |
| NASILSIN | | |
| TANIŞTIĞIMIZA MEMNUN OLDUM | | |

## 10. Bağlaç ve diğer (4)
| Kelime | Öncelik | Not |
|---|---|---|
| BERABER | ★ | |
| AMA | | |
| DAHA | | |
| HER | | |

---

## Örnek cümleler (bu dağarcıkla kurulabilenler)

| TİD gloss dizisi | Beklenen Türkçe cümle |
|---|---|
| BEN BUGÜN HASTA DERS GELMEK DEĞİL | Ben bugün hasta olduğum için derse gelmeyeceğim. |
| DÜN GECE GÜZEL RESTORAN EŞ BERABER YEMEK | Dün gece güzel bir restoranda eşimle beraber yemek yedim. |
| MERHABA BEN İSİM [M-E-R-V-A-N] | Merhaba, benim adım Mervan. |
| SEN YARIN OKUL GELMEK NE | Sen yarın okula gelecek misin? |
| BEN ANLAMAK DEĞİL YARDIM ETMEK | Anlamadım, yardım eder misin? |
| ARKADAŞ EV GİTMEK İSTEMEK | Arkadaşım eve gitmek istiyor. |
| TEŞEKKÜRLER SEN İYİ | Teşekkürler, sen iyisin. / Teşekkür ederim, çok iyisin. |

`[M-E-R-V-A-N]`: dağarcıkta olmayan kelime, parmak alfabesiyle hecelenir.

## Açık konular

- [ ] Listenin kullanıcı tarafından onaylanması
- [ ] Her kelimenin TİD Sözlüğü'nden kontrol edilmesi
- [ ] AUTSL veri setinde bu kelimelerden hangilerinin bulunduğunun kontrolü
