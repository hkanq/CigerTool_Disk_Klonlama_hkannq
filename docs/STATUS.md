# Status

## Durum

- Tarih: 2026-03-31
- Asama: Final repository cleanup
- Sonuc: kok yapi final mimariye gore sadeleştirildi, legacy yollar cikarildi, tek build girisi birakildi

## Tamamlananlar

- `workspace-os/` icerigi `workspace/` altinda toplandi
- `payload/` icerigi `workspace/payload/` altinda toplandi
- `isos/` kaynak yapisi `iso-library/` altina tasindi
- boot asset'leri `boot/assets/` altina tasindi
- tek resmi build girisi birakildi:
  - `build/build_cigertool_release.ps1`
- build yardimcilari `build/internal/` altinda toplandi
- operasyon scriptleri `cigertool/scripts/` altina tasindi
- `liveos/`, `winpe/`, legacy build scriptleri ve eski workflow'lar kaldirildi
- uygulama ici runtime, ayarlar ve ISO tarama dili final workspace modeline gore temizlendi
- dokumanlar final mimariye gore yeniden yazildi
- GitHub Actions release workflow'u iki modlu hale getirildi:
  - `push` -> `PlanOnly`
  - `workflow_dispatch` + WIM kaynagi -> gercek ISO build

## Ana Build Girisi

- `build/build_cigertool_release.ps1`

Plan dogrulama:

- `build/build_cigertool_release.ps1 -PlanOnly`

## Kalan Riskler

- Gercek full build hala yonetici hakli Windows host ister
- Gercek USB/VM boot smoke testi ayrica yapilmalidir
- ISO profilleme bazi medya ailelerinde hala heuristic temellidir
- GitHub Actions uzerinde gercek release icin runner'in erisebildigi bir `install.wim` kaynagi gerekir
