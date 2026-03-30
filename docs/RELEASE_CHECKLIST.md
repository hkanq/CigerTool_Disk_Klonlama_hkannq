# Release Checklist

## Build Öncesi

- [ ] `inputs/workspace/install.wim` mevcut
- [ ] `build-output/app/dist/CigerTool/CigerTool.exe` mevcut veya build sırasında üretilebiliyor

## Build Sonrası

- [ ] `artifacts/CigerTool-Workspace.iso` oluştu
- [ ] `artifacts/CigerTool-Workspace.iso.sha256` oluştu
- [ ] `artifacts/CigerTool-Workspace-debug.zip` oluştu
- [ ] `build-output/workspace/usb-layout/EFI/CigerTool/grub.cfg` mevcut
- [ ] `build-output/workspace/usb-layout/EFI/CigerTool/boot-manifest.json` mevcut
- [ ] `build-output/workspace/usb-layout/EFI/Microsoft/Boot/bootmgfw.efi` mevcut
- [ ] `build-output/workspace/usb-layout/EFI/Microsoft/Boot/BCD` mevcut
- [ ] `build-output/workspace/usb-layout/workspace/CigerToolWorkspace.vhdx` mevcut
- [ ] `build-output/workspace/usb-layout/isos/windows` mevcut
- [ ] `build-output/workspace/usb-layout/isos/linux` mevcut
- [ ] `build-output/workspace/usb-layout/isos/tools` mevcut

## Manuel Test

- [ ] Açılış menüsünde `CigerTool Workspace` ve `ISO Library` görünüyor
- [ ] Varsayılan giriş `CigerTool Workspace`
- [ ] Windows Setup görünmüyor
- [ ] OOBE görünmüyor
- [ ] Doğrudan masaüstü açılıyor
- [ ] `CigerTool` otomatik başlıyor
- [ ] `workspace-startup.log` ve `workspace-status.json` oluşuyor
- [ ] Sonradan eklenen en az bir Windows ISO menüde görünüyor
- [ ] Sonradan eklenen en az bir Linux ISO menüde görünüyor
- [ ] Sonradan eklenen en az bir Tool ISO menüde görünüyor
