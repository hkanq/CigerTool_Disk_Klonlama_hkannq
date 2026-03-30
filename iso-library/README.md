# ISO Library Kaynağı

Bu klasör, build sırasında USB içindeki `/isos/*` yapısına taşınan kaynak ISO kütüphanesidir.

Kaynak klasörler:

- `iso-library/windows`
- `iso-library/linux`
- `iso-library/tools`

Runtime karşılığı:

- `/isos/windows`
- `/isos/linux`
- `/isos/tools`

Son kullanıcı USB'yi yazdıktan sonra bu runtime dizinlerine yeni ISO bırakabilir. Açılış menüsü bu dizinleri her boot'ta yeniden tarar.
