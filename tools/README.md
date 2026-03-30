# Tools Layout

Bu klasor, `CigerTool Live` icinde kullanilacak tasinabilir araclarin ve kullanici tarafindan eklenecek `.exe` uygulamalarinin ana kokudur.

Amaç:

- bundled tools yapisini netlestirmek
- portable uygulamalarin ayni USB uzerinden calisabilmesini saglamak
- launcher tarafinin sabit bir klasor sozlesmesiyle calismasi

## Beklenen Klasor Yapisi

Onerilen yapi su sekildedir:

- `tools/browser/`
- `tools/diagnostics/`
- `tools/benchmark/`
- `tools/storage/`
- `tools/network/`
- `tools/user/`

Her arac tercihen kendi klasorunde tutulmalidir:

- `tools/browser/chrome-portable/ChromePortable.exe`
- `tools/diagnostics/cpu-z/cpuz_x64.exe`
- `tools/benchmark/disk-benchmark/benchmark.exe`
- `tools/storage/partition-tool/partition-tool.exe`
- `tools/network/network-tools/nettools.exe`
- `tools/user/my-portable-tool/MyTool.exe`

## Portable App Manifesti

Launcher, bir arac klasorunde `cigertool-tool.json` dosyasi bulursa onu tercih eder.

Ornek:

```json
{
  "name": "HWiNFO Portable",
  "category": "Diagnostics",
  "description": "Donanim ozeti ve sensor bilgileri.",
  "entry": "HWiNFO64.exe",
  "arguments": ["/portable"],
  "working_directory": ".",
  "layer": "USER"
}
```

Alanlar:

- `name`: Launcher'da gorunecek ad
- `category`: `Browser`, `Diagnostics`, `Benchmark`, `Storage`, `Network`, `User Tool`
- `description`: Arac aciklamasi
- `entry`: calistirilacak `.exe` dosyasi, manifest klasorune gore goreli yol
- `arguments`: istege bagli arguman listesi
- `working_directory`: istege bagli calisma dizini
- `layer`: genelde `USER`, onceden paketli araclar icin `PRELOADED`

## Manifest Yoksa Ne Olur?

Manifest yoksa launcher yine de `.exe` dosyalarini tarar:

- kategorili klasor altindaysa klasore gore kategorilendirir
- degilse dosya adina gore tahmini kategori verir

Bu fallback sayesinde kullanici sadece `.exe` kopyalayarak da arac ekleyebilir.

## Canli Ortam Davranisi

- `build/scripts/build_liveos_foundation.ps1` bu klasoru oldugu gibi `build-output/liveos/layout/tools` altina kopyalar
- transitional ISO build path de `tools/` icerigini runtime medyasina kopyalar
- live session sirasinda `CIGERTOOL_TOOLS_ROOT` ortam degiskeni set edilirse uygulama bunu tercih eder
- aksi halde uygulama runtime `tools/` kokunu ve repo `tools/` kokunu tarar

## Onerilen Kullanim

1. Araci uygun kategori klasorune koy
2. Gerekirse yanina `cigertool-tool.json` ekle
3. Live ortamda `Arac Kutusu` ekranini yenile
4. Araci launcher uzerinden ac

## Not

Bu klasor lisans nedenleriyle bos veya kismi gelebilir. Ucuncu parti portable uygulamalar repoya dogrudan eklenmek zorunda degildir; kullanici tarafinda sonradan yerlestirilebilir.
