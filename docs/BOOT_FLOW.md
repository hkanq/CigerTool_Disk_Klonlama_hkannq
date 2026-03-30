# Boot Flow

## Açılış Menüsü

USB açıldığında görünen ana girişler:

- `CigerTool Workspace`
- `ISO Library`

Varsayılan seçim:

- `CigerTool Workspace`

## Workspace Akışı

1. Firmware `EFI/BOOT/BOOTX64.EFI` dosyasını açar
2. GRUB menüsü gelir
3. `CigerTool Workspace` seçilir
4. `/EFI/Microsoft/Boot/bootmgfw.efi` chainload edilir
5. BCD store `/workspace/CigerToolWorkspace.vhdx` hedefini açar
6. Hazırlanmış Windows masaüstü gelir
7. `Start-CigerToolWorkspace.ps1` çalışır
8. `CigerTool` otomatik başlar

Bu yol:

- Windows Setup kullanmaz
- OOBE kullanmaz
- kullanıcı soruları göstermez

## ISO Library Akışı

GRUB her açılışta şu runtime dizinlerini tarar:

- `/isos/windows`
- `/isos/linux`
- `/isos/tools`

Windows ISO'lar için:

- önce `wimboot`
- sonra EFI fallback

Linux ISO'lar için:

- bilinen ailelerde loopback kernel/initrd
- gerekirse `.grub.cfg` sidecar

Tool ISO'lar için:

- EFI chainload
- gerekirse `.grub.cfg` sidecar

## Debug Noktaları

Build sırasında üretilen önemli dosyalar:

- `build-output/workspace/usb-layout/CigerTool.workspace.json`
- `build-output/workspace/usb-layout/EFI/CigerTool/grub.cfg`
- `build-output/workspace/usb-layout/EFI/CigerTool/boot-manifest.json`
