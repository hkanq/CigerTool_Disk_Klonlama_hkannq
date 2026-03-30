# CigerTool by hkannq

CigerTool, tek bir USB ile iki işi yapan hazır çalışma alanı ürünüdür:

- `CigerTool Workspace`
  Hazır Windows çalışma alanını doğrudan masaüstüne açar ve `CigerTool` uygulamasını otomatik başlatır.
- `ISO Library`
  USB'ye sonradan bırakılan ISO dosyalarını açılış menüsünde gösterir.

Bu repo artık WinPE-first veya Windows Setup-first mantığı kullanmaz. Ana ürün davranışı, hazırlanmış workspace imajı üzerinden kurulur.

## Girdi

Zorunlu kaynak dosya:

- `inputs/workspace/install.wim`

Build bu WIM dosyasını kaynak workspace olarak kullanır. Dosya yoksa build açık hata verir.

## Nasıl Build Alınır

Tek resmi build girişi:

```powershell
powershell -ExecutionPolicy Bypass -File .\build\build_cigertool_release.ps1
```

Sadece plan ve staging doğrulaması için:

```powershell
powershell -ExecutionPolicy Bypass -File .\build\build_cigertool_release.ps1 -PlanOnly
```

Gerçek artifact üretimi için yönetici yetkisi gerekir. Bunun nedeni `diskpart`, `DISM` ve `bcdboot` ile VHDX hazırlama adımlarının yükseltilmiş hak istemesidir.

## Ana Çıktı

Birincil artifact:

- `artifacts/CigerTool-Workspace.iso`

İkincil artifact'ler:

- `artifacts/CigerTool-Workspace.iso.sha256`
- `artifacts/CigerTool-Workspace-debug.zip`
- `artifacts/CigerTool-Workspace.release.json`

## ISO Library Nasıl Çalışır

Repo içindeki kaynak klasör:

- `iso-library/windows`
- `iso-library/linux`
- `iso-library/tools`

Build sırasında bu içerik USB çalışma düzeninde şu köklere taşınır:

- `/isos/windows`
- `/isos/linux`
- `/isos/tools`

Son kullanıcı USB'yi yazdıktan sonra yeni ISO'ları doğrudan bu `/isos/*` dizinlerine bırakabilir. Açılış menüsü her boot sırasında bu dizinleri yeniden tarar.

## Klasör Özeti

- `build/`
  Final release build girişi ve iç yardımcı scriptler
- `boot/`
  GRUB tabanlı açılış katmanı ve boot asset'leri
- `workspace/`
  Hazır Windows workspace startup, unattend ve payload katmanı
- `cigertool/`
  Ana uygulama kodu ve runtime operasyon scriptleri
- `iso-library/`
  Build kaynak ISO kütüphanesi
- `tools/`
  USB'ye taşınacak portable araçlar
- `docs/`
  Mimari, boot, release ve durum belgeleri
- `inputs/`
  Build girdileri

## Ürün Davranışı

Açılış menüsünde varsayılan giriş:

- `CigerTool Workspace`

İkinci ana giriş:

- `ISO Library`

`CigerTool Workspace` hedef davranışı:

- Windows Setup yok
- OOBE yok
- parola yok
- doğrudan masaüstü
- `CigerTool` auto-start
