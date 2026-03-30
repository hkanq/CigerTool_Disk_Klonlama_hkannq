# Workspace Katmanı

Bu klasör, `CigerTool Workspace` için gerekli hazır Windows çalışma alanı sözleşmesini taşır.

Kaynak girdi:

- `inputs/workspace/install.wim`

Build modeli:

1. `install.wim` kaynak workspace snapshot olarak alınır
2. build sırasında `CigerToolWorkspace.vhdx` oluşturulur
3. locale, autologon, startup ve payload offline uygulanır
4. EFI + BCD zinciri hazırlanır
5. final USB layout içine `workspace/CigerToolWorkspace.vhdx` yerleştirilir

Bu katmanın hedef davranışı:

- Windows Setup yok
- OOBE yok
- kullanıcı adı/parola sorusu yok
- Türkçe varsayılanlar hazır
- doğrudan masaüstü
- `CigerTool` otomatik başlar
