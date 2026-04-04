# CigerTool Durum

## Güncel Aşama

Bu turda iki ana konu düzeltildi:

- uygulama yerel Windows pencere davranışına geri döndürüldü
- yedekleme ve imaj modülünde gerçek akıllı imaj alma akışı açıldı

## Bu Turda Yapılanlar

- özel başlık çubuğu yaklaşımı bırakıldı
- standart Windows küçültme, büyütme, kapatma ve sürükleme davranışı geri getirildi
- pencere kenarındaki siyah çerçeve ve uyumsuz kabuk davranışına yol açan yaklaşım kaldırıldı
- yedekleme ekranı son kullanıcı diliyle yeniden düzenlendi
- bozuk dosya filtresi nedeniyle oluşan ham yedekleme hatası kapatıldı
- sistem dışı sürücüler için akıllı `.ctimg` imaj alma açıldı
- akıllı imaj geri yükleme akışı sistem dışı hedeflerde korunarak sürdürüldü
- doğrulama, yürütme, ilerleme, iptal ve rapor kaydetme akışı korundu

## Yayın Çıktıları

- [artifacts/app/CigerTool.exe](C:/Users/Radius%20Admin/Desktop/codex/CigerTool/artifacts/app/CigerTool.exe)
- [artifacts/winpe/CigerTool.WinPE.exe](C:/Users/Radius%20Admin/Desktop/codex/CigerTool/artifacts/winpe/CigerTool.WinPE.exe)

## Davranış Notları

- her iki yayın çıktısı da açılış için zorunlu yan dosya gerektirmez
- masaüstü yapısı yazılabilir verileri `%LocalAppData%\CigerTool` altında tutar
- WinPE odaklı yapı yazılabilir verileri `%TEMP%\CigerTool` altında tutar
- uygulama klasörü içine günlük veya veri klasörü açma önceliği yoktur

## Doğrulama

Başarıyla çalıştırılan komutlar:

- `dotnet build CigerTool.sln -c Release`
- `dotnet test CigerTool.sln -c Release --no-build`
- `powershell -ExecutionPolicy Bypass -File build/scripts/Publish-CigerTool.ps1`

Kısa açılış denemesi:

- standart yapı açıldı ve ilk birkaç saniyede çökmedi
- WinPE yapısı açıldı ve ilk birkaç saniyede çökmedi

## Bilinen Kalan Riskler

- ham klon ve ham imaj iş akışları sürücü düzeyinde çalışır; tam disk bölüm tablosu yeniden kurmaz
- akıllı kopya ve akıllı imaj NTFS odaklı, dosya temelli yaklaşımdır
- masaüstünde çalışan sistem sürücüsüne ham yazma bilerek engellenir
- gelişmiş SMART ve üretici telemetrisi hâlâ sınırlıdır

## Bilinçli Ürün Sınırı

Bu depo:

- WinPE üretmez
- ADK kurmaz
- işletim sistemi imajı oluşturmaz

Bu depo yalnızca:

- uygulamayı
- yayın kaynağı modelini
- USB oluşturma akışını
- WinPE içine yerleştirme sözleşmesini

taşır.
