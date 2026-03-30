# ISO Library Planı

## Kaynak ve Runtime Ayrımı

Repo içindeki kaynak klasör:

- `iso-library/windows`
- `iso-library/linux`
- `iso-library/tools`

USB runtime dizinleri:

- `/isos/windows`
- `/isos/linux`
- `/isos/tools`

Build, kaynak kütüphaneyi runtime `/isos/*` düzenine taşır.

## Kullanıcı Deneyimi

Kullanıcı USB'yi bir kez yazar.
Sonrasında yeni ISO dosyalarını doğrudan USB üzerindeki `/isos/*` klasörlerine bırakır.
Açılış menüsü bu dizinleri her boot sırasında yeniden tarar.

## Profilleme

Windows:

- `wimboot` tercih edilir
- uygun değilse EFI chainload denenir

Linux:

- Ubuntu/Debian türevleri için `casper` tabanlı giriş
- Arch türevleri için archiso tabanlı giriş
- özel durumlar için `.grub.cfg` sidecar

Tools:

- varsayılan olarak EFI chainload
- özel durumlar için `.grub.cfg` sidecar

## Güvenli Fallback

ISO uygun şekilde boot edilemezse:

- ana menü bozulmaz
- kullanıcıya kısa hata mesajı gösterilir
- workspace ana yolu etkilenmez
