# CigerTool

CigerTool, Windows için geliştirilen yerel bir disk işlemleri ürün ailesidir.

Ürün ailesi iki teslimattan oluşur:

- `CigerTool App`: Normal Windows 10/11 üzerinde çalışan masaüstü uygulaması
- `CigerTool OS`: Kullanıcının dışarıda hazırladığı Windows 10 PE tabanı içinde çalışan servis ortamı

## Sınır

Bu depo:

- WinPE üretmez
- Windows ADK kurmaz
- `boot.wim` oluşturmaz
- işletim sistemi imajı üretmez

Bu depo şunlardan sorumludur:

- CigerTool uygulaması
- USB ortamı oluşturma akışı
- yayın kaynağı ve manifest sistemi
- WinPE içine yerleştirme ve başlatma sözleşmesi

## Ana Modüller

- `Ana Sayfa`
- `Klonlama`
- `Yedekleme ve İmaj`
- `Diskler ve Sağlık`
- `USB Ortamı Oluştur`
- `Günlükler`
- `Ayarlar`

## Bugün Gerçekten Çalışan Çekirdek İşlemler

- ham kopya ile sürücüden sürücüye gerçek bayt kopyalama
- akıllı kopya ile dosya temelli sürücü eşleme
- sürücüden ham `.img` imaj alma
- sürücüden ham `.ctimg` imaj alma
- sistem dışı sürücülerden akıllı `.ctimg` imaj alma
- `.img`, ham `.ctimg` ve akıllı `.ctimg` için desteklenen geri yükleme akışları
- `.img` ile ham `.ctimg` arasında dönüştürme
- USB için imaj indirme, doğrulama ve yazma

## Bilinçli Kapsam Sınırı

Bu sürümde henüz tam kapsamlı olmayan alanlar:

- tam fiziksel disk bölüm tablosu yeniden kurma
- önyükleme onarımı
- BitLocker iş akışları
- gelişmiş SMART ve üretici telemetrisi
- `Taşıma ve geçiş` bölümünde bağımsız yürütme motoru

## Yayın Çıktıları

- standart masaüstü yapı: [CigerTool.exe](C:/Users/Radius%20Admin/Desktop/codex/CigerTool/artifacts/app/CigerTool.exe)
- WinPE odaklı yapı: [CigerTool.WinPE.exe](C:/Users/Radius%20Admin/Desktop/codex/CigerTool/artifacts/winpe/CigerTool.WinPE.exe)

Her iki çıktı da açılış için zorunlu yan dosya gerektirmez. Varsayılan ayarlar uygulamanın içinde taşınır.

Yazılabilir uygulama verileri işletim sistemi konumlarına gider:

- masaüstü yapı: `%LocalAppData%\CigerTool`
- WinPE odaklı yapı: `%TEMP%\CigerTool`

## Doğrulama

Bu turda doğrulananlar:

- `dotnet build CigerTool.sln -c Release`
- `dotnet test CigerTool.sln -c Release --no-build`
- `powershell -ExecutionPolicy Bypass -File build/scripts/Publish-CigerTool.ps1`
- iki yayın çıktısı için kısa açılış denemesi

## Ana Dokümanlar

- [docs/EXECUTION_ENGINE_STATUS.md](C:/Users/Radius%20Admin/Desktop/codex/CigerTool/docs/EXECUTION_ENGINE_STATUS.md)
- [docs/CLONE_MODEL.md](C:/Users/Radius%20Admin/Desktop/codex/CigerTool/docs/CLONE_MODEL.md)
- [docs/IMAGE_WORKFLOW.md](C:/Users/Radius%20Admin/Desktop/codex/CigerTool/docs/IMAGE_WORKFLOW.md)
- [docs/DISK_HEALTH_MODEL.md](C:/Users/Radius%20Admin/Desktop/codex/CigerTool/docs/DISK_HEALTH_MODEL.md)
- [docs/FEATURE_SCOPE.md](C:/Users/Radius%20Admin/Desktop/codex/CigerTool/docs/FEATURE_SCOPE.md)
- [docs/STATUS.md](C:/Users/Radius%20Admin/Desktop/codex/CigerTool/docs/STATUS.md)
