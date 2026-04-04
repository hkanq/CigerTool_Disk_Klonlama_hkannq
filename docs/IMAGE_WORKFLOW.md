# CigerTool İmaj İş Akışları

## Desteklenen Biçimler

- `Ham imaj (.img)`
- `CigerTool imajı (.ctimg)`

`.ctimg` bu sürümde iki farklı içerik taşıyabilir:

- ham içerik
- akıllı içerik

## İmaj Oluşturma

Gerçekten çalışan kapsam:

- seçilen sürücüyü ham `.img` olarak alma
- seçilen sürücüyü ham `.ctimg` olarak alma
- sistem dışı sürücüyü akıllı `.ctimg` olarak alma

Akıllı imaj alma davranışı:

- yalnızca sistem dışı sürücülerde açıktır
- yalnızca kullanılan dosyaları paketler
- boş alanı ham olarak taşımaz
- şu an `CigerTool imajı (.ctimg)` biçimiyle sınırlıdır

Ham imaj alma davranışı:

- yönetici yetkisi ister
- aktif sistem sürücüsünde masaüstü modunda bilerek engellenir
- bu senaryo için CigerTool OS önerilir

## İmaj Geri Yükleme

Gerçekten çalışan kapsam:

- `.img` dosyasını hedef sürücüye ham olarak yazma
- ham `.ctimg` dosyasını hedef sürücüye ham olarak yazma
- akıllı `.ctimg` dosyasını sistem dışı hedefe dosya tabanlı geri yerleştirme

Akıllı geri yükleme davranışı:

- yalnızca sistem dışı hedeflerde açıktır
- hedef sürücüyü temizler
- dosyaları yeniden yerleştirir
- bölüm tablosunu yeniden kurmaz

Ham geri yükleme davranışı:

- yönetici yetkisi ister
- aktif sistem sürücüsüne masaüstünde bilerek kapalıdır
- bu senaryo için CigerTool OS önerilir

## Dönüştürme

Gerçekten çalışan dönüşümler:

- `.img -> ham .ctimg`
- `ham .ctimg -> .img`

Henüz açık olmayan dönüşüm:

- `akıllı .ctimg -> başka biçim`

## Henüz Desteklenmeyenler

- VHD/VHDX gibi ek biçimler
- bölüm seçerek geri yükleme
- tam fiziksel disk bölüm tablosu yeniden kurma
- önyükleme onarımı
- BitLocker farkındalığı
