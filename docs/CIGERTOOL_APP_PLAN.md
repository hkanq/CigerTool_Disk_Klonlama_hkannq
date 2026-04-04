# CigerTool App Plan

## Amaç

Bu doküman, `CigerTool App` uygulamasının bugün ulaştığı gerçek durumu ve taşıdığı mimari yönü özetler.

Uygulama iki çalışma bağlamını hedefler:

- normal Windows 10/11 masaüstü kullanımı
- kullanıcı tarafından dışarıda hazırlanmış Windows 10 PE tabanı içinde çalışma

## Seçilen UI Yığını

- `.NET 8`
- `WPF`

Bu seçim hâlâ doğrudur çünkü CigerTool için:

- olgun masaüstü davranışı
- Windows 10/11 uyumu
- tek dosya publish yolu
- WinPE tarafına taşınırken daha öngörülebilir çalışma davranışı

sağlar.

## Güncel Milestone

Gerçek yürütme katmanının ilk kullanılabilir sürümü açılmış durumdadır.

Uygulama bugün:

- gerçek ham kopya yürütmesi
- gerçek akıllı kopya yürütmesi
- gerçek ham imaj alma
- gerçek imaj geri yükleme
- gerçek `.img <-> .ctimg` dönüştürme
- disk kimliği ve temel sağlık görünümü
- USB imaj indirme, doğrulama ve yazma
- kullanıcı görünür günlükler ve sonuç raporları

sunmaktadır.

## Katman Sorumlulukları

### `app/CigerTool.App`

- WPF kabuk ve gezinme
- sayfa view model ve view katmanı
- dosya seçimleri, komutlar, ilerleme ve sonuç bağları
- kullanıcı dostu hata raporlama

### `core/CigerTool.Domain`

- ürün enum ve domain kayıtları
- klonlama ve imaj durum modelleri
- disk, sistem, log gibi temel tipler

### `core/CigerTool.Application`

- servis sözleşmeleri
- UI çalışma alanı snapshot modelleri
- yürütme istek, ilerleme ve sonuç tipleri

### `core/CigerTool.Infrastructure`

- ayarlar ve yol çözümü
- başlangıç denetimi
- logging
- dashboard birleştirme
- disk envanteri ve sağlık özeti
- klonlama yürütmesi
- imaj alma / geri yükleme / dönüştürme yürütmesi

### `usb/CigerTool.Usb`

- release-source çözümü
- manifest ve override davranışı
- imaj indirme ve doğrulama
- USB aygıt algılama
- ham yazma ve yazma sonrası doğrulama

## Bilinçli Sınırlar

Bu sürüm henüz:

- tam fiziksel disk bölüm tablosu yeniden kurma
- önyükleme onarımı
- BitLocker iş akışları
- üreticiye özel derin sağlık telemetrisi
- bağımsız `Taşıma ve geçiş` yürütmesi

sunmaz.

## Doğrulama

Bu repo durumunda doğrulanan komutlar:

- `dotnet build CigerTool.sln -c Release`
- `dotnet test CigerTool.sln -c Release --no-build`
- `powershell -ExecutionPolicy Bypass -File build/scripts/Publish-CigerTool.ps1`
