# Boot Katmanı

Bu klasör, ürünün açılış öncesi davranışını taşır.

Final hedef:

- varsayılan giriş `CigerTool Workspace`
- ikinci ana giriş `ISO Library`
- `CigerTool Workspace` seçildiğinde `bootmgfw.efi` üzerinden hazırlanmış VHDX workspace açılır
- `ISO Library` seçildiğinde `/isos/windows`, `/isos/linux`, `/isos/tools` dizinleri dinamik taranır

Ana dosyalar:

- `boot/assets/grub/`
  UEFI için vendored GRUB EFI dosyaları
- `boot/assets/preboot/grub.cfg`
  Dinamik menüye yönlendiren küçük bootstrap
- `build/internal/build_boot_layer.ps1`
  Boot katmanı staging scripti
- `build/internal/render_boot_menu.py`
  Dinamik GRUB menü üreticisi
