# CigerTool Yürütme Motoru Durumu

## Açılan Gerçek Motorlar

### Klonlama

- ham kopya yürütmesi
- akıllı kopya yürütmesi
- ilerleme raporlama
- iptal isteği
- sonuç raporu dışa aktarma

### İmaj İşlemleri

- sürücüden `.img` alma
- sürücüden `.ctimg` alma
- `.img` geri yükleme
- `.ctimg` geri yükleme
- `.img <-> .ctimg` dönüştürme
- ilerleme raporlama
- iptal isteği
- sonuç raporu dışa aktarma

## Kısmi Alanlar

- tam fiziksel disk düzeni yeniden kurma
- önyükleme onarımı
- BitLocker farkındalığı
- `Taşıma ve geçiş` bölümünde bağımsız yürütme

## Kullanılan İlk Teknik Yaklaşım

- ham işlemler: sürücü düzeyinde akış kopyalama
- akıllı kopya: dosya temelli hedef kökü eşleme
- imaj paketleme: ham içeriğin `.ctimg` kapsayıcısına alınması

## Sonraki Genişletme Alanları

- bölüm tablosu ve önyükleme bilgisi taşıma
- daha kapsamlı geri yükleme uyumluluk denetimi
- canlı sistem kopyasında daha iyi tutarlılık seçenekleri
