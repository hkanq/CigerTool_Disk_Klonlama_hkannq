# CigerTool Özellik Kapsamı

## Gerçekten Uygulananlar

### Klonlama

- ham kopya denetimi
- ham kopya yürütmesi
- akıllı kopya denetimi
- akıllı kopya yürütmesi
- canlı ilerleme görünümü
- iptal isteği
- denetim raporu kaydetme
- sonuç raporu kaydetme

### Yedekleme ve İmaj

- sürücüden ham `.img` alma
- sürücüden ham `.ctimg` alma
- sistem dışı sürücüden akıllı `.ctimg` alma
- `.img` dosyasını sürücüye geri yükleme
- ham `.ctimg` dosyasını sürücüye geri yükleme
- akıllı `.ctimg` dosyasını sistem dışı sürücüye geri yükleme
- `.img -> ham .ctimg` dönüştürme
- `ham .ctimg -> .img` dönüştürme
- doğrulama, yürütme, ilerleme ve sonuç raporu

### Diskler ve Sağlık

- bağlı sürücü listesi
- kapasite görünümü
- kullanım oranı
- model, bağlantı ve medya tipi görünümü
- sistem sürücüsü işareti
- düşük boş alan uyarısı
- Windows durum bilgisine göre temel sağlık özeti

### USB Ortamı Oluştur

- çevrimiçi manifest kaynağı
- yerel geçersiz kılma desteği
- elle dosya seçimi
- imaj indirme
- SHA-256 doğrulaması
- USB aygıt algılama
- güvenli aygıt engelleme kuralları
- USB yazma
- yazma sonrası doğrulama

## Kısmi Ama Dürüstçe Sunulanlar

- `Taşıma ve geçiş` bölümü:
  karar desteği ve yönlendirme sunar, bağımsız yürütme motoru henüz açık değildir
- masaüstünde çalışan sistem sürücüsü için ham klon ve ham imaj:
  bilinçli olarak engellenir, CigerTool OS önerilir
- akıllı kopya:
  NTFS odaklıdır ve dosya temelli eşleme yapar
- akıllı imaj:
  şu an sistem dışı sürücülerle ve `.ctimg` biçimiyle sınırlıdır

## Henüz Açılmayanlar

- tam fiziksel disk bölüm tablosu yeniden kurma
- önyükleme onarımı
- BitLocker iş akışları
- gelişmiş SMART ve üretici telemetrisi
- bağımsız `Taşıma ve geçiş` yürütme motoru

## Dürüstlük Kuralı

Ekranda görünen her alan şu üç durumdan birine açıkça oturmalıdır:

- uygulanmış
- kısmi veya sınırlı
- planlı

Yürütülemeyen bir işlev kullanıcıya tamamlanmış gibi sunulmaz.
