# Workspace OS Planı

## Kaynak

- `inputs/workspace/install.wim`

Bu dosya hazırlanmış Windows workspace kaynağıdır. Raw installer ISO veya Setup akışı değildir.

## Runtime Paketleme

Seçilen runtime modeli:

- build kaynağı: `install.wim`
- çalışma zamanı: `workspace/CigerToolWorkspace.vhdx`

Bu VHDX native boot için hazırlanır ve boot katmanına bağlanır.

## Offline Özelleştirme

Build sırasında şu adımlar uygulanır:

- `DISM /Apply-Image`
- Türkçe locale ve Türkiye saat dilimi
- autologon kullanıcısı: `CigerTool`
- boş parola
- OOBE ve first-run bastırma
- `CigerTool` uygulaması ve startup scriptleri
- payload merge

## Çalışma Dizinleri

Build staging alanları:

- `build-output/workspace/workspace-stage`
- `build-output/workspace/workspace`
- `build-output/workspace/usb-layout`
- `build-output/workspace/manifests`
