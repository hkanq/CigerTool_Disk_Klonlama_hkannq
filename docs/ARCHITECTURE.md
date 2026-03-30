# Architecture

## Final Katmanlar

- `build/`
  Tek resmi build girişi ve iç build yardımcıları
- `boot/`
  GRUB tabanlı pre-boot menü ve boot asset'leri
- `workspace/`
  Hazır Windows workspace startup, unattend ve payload modeli
- `cigertool/`
  Ana uygulama kodu ve runtime operasyon scriptleri
- `iso-library/`
  Build kaynak ISO kütüphanesi
- `tools/`
  USB'ye taşınacak portable araçlar
- `docs/`
  Ürün ve release belgeleri
- `inputs/`
  Build girdileri

## Ana Build Stratejisi

Seçilen model:

- kaynak format: hazırlanmış WIM
- runtime format: native boot VHDX
- boot modeli: GRUB -> Microsoft Boot Manager -> native VHDX boot

Neden bu model seçildi:

- Windows Setup akışını ana yoldan çıkarır
- OOBE olmayan hazır masaüstü deneyimini destekler
- `CigerTool` ve payload merge işlemlerini build zamanında sabitler
- yazılabilir bir workspace runtime verir

## Build Akışı

1. `inputs/workspace/install.wim` doğrulanır
2. `CigerTool` uygulaması paketlenir
3. workspace staging hazırlanır
4. WIM, `CigerToolWorkspace.vhdx` içine uygulanır
5. unattend, locale, autologon ve startup sözleşmesi işlenir
6. `iso-library/*` içeriği USB layout içinde `/isos/*` dizinine taşınır
7. boot katmanı oluşturulur
8. final deliverable olarak `CigerTool-Workspace.iso` üretilir

## Final Kaynak Scriptler

Tek dış build girişi:

- `build/build_cigertool_release.ps1`

İç build yardımcıları:

- `build/internal/package_cigertool_app.ps1`
- `build/internal/prepare_workspace_runtime.ps1`
- `build/internal/stage_release_layout.ps1`
- `build/internal/build_boot_layer.ps1`
- `build/internal/render_boot_menu.py`

Runtime operasyon scriptleri:

- `cigertool/scripts/invoke_smart_clone.ps1`
- `cigertool/scripts/invoke_raw_clone.ps1`
- `cigertool/scripts/invoke_boot_fix.ps1`

## Çıkarılan Legacy Alanlar

Repo artık şunları ana mimarinin parçası saymaz:

- WinPE-first build akışları
- Windows Setup tabanlı workspace boot yolu
- `liveos/`
- `winpe/`
- `build/scripts/legacy/`
- eski EFI image ve `xorriso` / `mformat` deneyleri
