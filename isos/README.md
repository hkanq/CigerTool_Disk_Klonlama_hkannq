# isos

Bu klasor, `CigerTool Live` icin varsayilan ISO Library kok dizinidir.

Kullanici tarafinda eklenen ISO dosyalari burada tutulur ve iki yerde kullanilir:

- CigerTool icindeki `ISO Yonetimi` ekrani
- boot sirasinda olusan `ISO Library` menusu

## Beklenen klasor yapisi

- `isos/windows`
- `isos/linux`
- `isos/tools`

Her ISO ilgili kategori klasorune yerlestirilmelidir.

## Kategori davranisi

### `isos/windows`

- Windows kurulum, kurtarma ve WinPE turevi ISO'lar
- GRUB tarafinda `Windows ISO'lari` bolumune duser
- varsayilan strateji: `WIMBOOT`
- ikinci deneme olarak EFI boot fallback uygulanir

### `isos/linux`

- Ubuntu, Debian, Mint, Pop!_OS, Arch, Manjaro gibi Linux dagitimlari
- GRUB tarafinda `Linux ISO'lari` bolumune duser
- profil biliniyorsa loopback kernel + initrd akisi kullanilir
- profil bilinmiyorsa ISO guvenli fallback ile listelenir, kor blind boot denenmez

### `isos/tools`

- kurtarma, anti-virus, disk, rescue ve utility ISO'lari
- GRUB tarafinda `Arac ve Kurtarma ISO'lari` bolumune duser
- varsayilan strateji: EFI chainload
- EFI boot dosyasi bilinmiyorsa ISO sadece fallback olarak listelenir

## Yan dosya destegi

Her ISO dosyasinin yanina istege bagli olarak bir sidecar dosyasi konabilir:

- `ornek.iso` icin `ornek.cigertool.json`

Bu dosya ile su alanlar override edilebilir:

- `category`
- `profile`
- `boot_strategy`
- `kernel_path`
- `initrd_path`
- `efi_boot_path`
- `support_status`
- `failure_reason`
- `note`

Ornek dosya:

- `isos/_template/cigertool-iso.example.json`

## Guvenli fallback davranisi

Sistem desteklenmeyen veya tam profillenemeyen ISO'lari gizlemez; listelemeye devam eder.

Ancak bu ISO'lar icin:

- riskli otomatik boot denenmez
- boot menusu sadece neden bilgisini gosterir
- kullanici isterse sidecar veya ozel `.grub.cfg` ile davranisi genisletebilir

## Ozel GRUB config destegi

Bir ISO icin ozel boot mantigi gerekiyorsa ayni klasore su dosyalardan biri konabilir:

- `ornek.grub.cfg`
- `ornek.cfg`

Bu durumda ISO, `custom-config` olarak islenir ve boot menusu o config dosyasina yonlenir.

## Legacy yol

Eski `iso-library/` yapisi hala okunur ancak artik varsayilan kutuphane kok dizini degildir.

Yeni eklemeler icin her zaman once `isos/` kullanilmalidir.
