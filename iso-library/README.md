# iso-library

Bu klasor, eski ISO Library yapisi icin geriye donuk uyumluluk yoludur.

Beklenen kullanim:

- Yeni kullanimda ISO dosyalarini `isos/windows`, `isos/linux` veya `isos/tools` altina kopyala
- `iso-library/` yalnizca eski USB duzenlerini kirmamak icin okunmaya devam eder

Prompt 6 itibariyla:

- `iso-library/` altindaki ISO'lar hala tespit edilir
- uygun olanlar boot menusune dahil edilir
- ama varsayilan ve onerilen yol artik `isos/` kokudur

Mumkun olan en temiz duzen:

- `isos/windows`
- `isos/linux`
- `isos/tools`
