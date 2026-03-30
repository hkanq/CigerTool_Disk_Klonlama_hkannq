# CigerTool V2

CigerTool, Disk klonlama ve teknik usb yazılımlarının zorluklarından dolayı hkannq tarafından tamamen AI ile yazılmış olup, WinPE tabanlı çalışan grafik arayüzlü bir disk klonlama, kurtarma ve bakım platformudur. Ana hedefi, özellikle büyük bir HDD'deki Windows kurulumunu daha küçük bir SSD'ye güvenli, yönlendirmeli ve anlaşılır bir akışla taşımaktır.

Uygulama yalnızca klon alma mantığıyla sınırlı değildir. Aynı zamanda önyükleme onarımı, disk sağlığı görüntüleme, araç kutusu kullanımı, dosya yönetimi ve USB üzerinde genişletilebilir ISO kütüphanesi mantığı da sunar.

## Ne İşe Yarar?

- Büyük diskten küçük SSD'ye Windows taşıma planı çıkarır.
- Kaynak ve hedef diski analiz ederek uygun klon yöntemini önerir.
- `SMART CLONE`, `RAW CLONE` ve `SYSTEM CLONE` olmak üzere 3 farklı klon modu sunar.
- EFI ve MBR tabanlı açılış sorunları için önyükleme onarım planı hazırlar.
- Disk sağlığı, sıcaklık ve temel sistem bilgilerini görüntüler.
- Harici araçları ve taşınabilir yazılımları `tools/` klasöründen çalıştırabilir.
- `isos/windows`, `isos/linux`, `isos/tools` ve `iso-library` altındaki ISO dosyalarını tarar.
- UEFI odaklı önyükleme öncesi menü ile ISO kütüphanesi mantığı sunar.
- WinPE açıldığında uygulamayı doğrudan kabuk olarak başlatır; masaüstü beklemeden arayüz açılır.

## Son Kullanıcı İçin Öne Çıkan Özellikler

### 1. Disk Tarama

Uygulama takılı diskleri otomatik tarar ve şunları gösterir:

- Disk numarası
- Toplam kapasite
- Bağlantı tipi (`SATA`, `NVMe`, `USB`)
- Model ve seri bilgisi
- Kullanılan alan

Bu ekran, hangi diskin kaynak hangisinin hedef olacağını karıştırmamak için ilk adımdır.

### 2. Klonlama Sihirbazı

Kullanıcının en çok kullanacağı bölüm burasıdır. Burada:

- Kaynak disk seçilir
- Hedef disk seçilir
- Klon modu seçilir
- `Analiz Et` ile uyumluluk kontrolü yapılır
- `Dry-run / Simülasyon` seçeneği ile işlem gerçek yazma yapmadan test edilir
- Son onaydan sonra gerçek klon başlatılır

### 3. Önyükleme Onarımı

Klon sonrası veya mevcut bir sistemde açılış sorunu varsa önyükleme onarım planı üretir.

- UEFI sistemlerde EFI ve BCD onarımı planlar
- MBR sistemlerde etkin bölüm ve önyükleme kaydı onarımı planlar

### 4. Disk Sağlığı

Disk sağlığı ve sistem bilgisi ekranı temel olarak şunları gösterebilir:

- Disk sağlık durumu
- Çalışma durumu
- Medya tipi
- Sıcaklık
- Çalışma saati
- Okuma / yazma hata sayaçları

### 5. Hız Testi

Eğer uygun hız testi aracı `tools/` altında varsa:

- Disk hız testi aracı açılabilir
- Kullanıcı disk performansını gözlemleyebilir

### 6. Dosya Yöneticisi

Yerleşik dosya yöneticisi ile:

- Diskler gezilebilir
- USB içeriği incelenebilir
- Metin tabanlı dosyalar önizlenebilir

### 7. ISO Yönetimi

Uygulama şu klasörleri tarar:

- `isos/windows`
- `isos/linux`
- `isos/tools`
- `iso-library`

Bulduğu ISO'lar için şunları gösterir:

- ISO adı
- Destek durumu
- Kategori
- Profil
- Önyükleme stratejisi
- Boyut
- Dosya yolu

### 8. Araç Kutusu

Uygulama çekirdek araçlara ek olarak `tools/` içindeki taşınabilir `.exe` araçlarını da görebilir ve başlatabilir.

Örnek kullanım alanları:

- Tarayıcı
- Hız testi aracı
- Donanım tanılama aracı
- Ağ araçları
- Bölümleme araçları

### 9. Ayarlar ve Loglar

- WinPE ortamında mı normal Windows ortamında mı çalıştığını gösterir
- ADK durumunu özetler
- Araç kök dizinlerini ve ISO kök dizinlerini gösterir
- Uygulama loglarını inceleme imkanı verir

## Klon Modları

### SMART CLONE

En önemli ve en pratik moddur. Özellikle büyük diskten küçük SSD'ye geçiş için tasarlanmıştır.

Mantığı:

- Tüm sektörleri birebir kopyalamaz
- Kullanılan veriyi baz alır
- Hedef diske sığacak yeni bölüm düzeni oluşturur
- Gerekli EFI / Windows / veri / kurtarma düzenini planlar
- Kopyalama sonrası önyükleme kaydını yeniler

Ne zaman kullanılır?

- Büyük HDD -> küçük SSD geçişinde
- Kaynak disk hedef diskten büyük ama kullanılan veri daha küçükse
- En mantıklı günlük kullanım senaryosunda

### RAW CLONE

Birebir sektör kopyasıdır.

Mantığı:

- Kaynağın tamamını hedefe ham olarak kopyalar
- Hedef disk en az kaynak disk kadar büyük olmalıdır
- En riskli ve en az esnek yöntemdir

Ne zaman kullanılır?

- Birebir kopya isteniyorsa
- Hedef disk kaynakla aynı ya da daha büyükse
- Gelişmiş kullanıcı kontrollü senaryolarda

### SYSTEM CLONE

Yalnızca Windows'un açılması için gerekli bölümlere odaklanır.

Mantığı:

- Büyük veri bölümlerini taşımayabilir
- EFI + Windows + gerekli sistem bileşenleri öncelik alır
- Hedef çok küçük olduğunda tam veri taşınamasa bile sistemi ayağa kaldırmayı amaçlar

Ne zaman kullanılır?

- Tüm veriyi taşımak mümkün değilse
- Amaç sadece sistemi açılır halde yeni diske taşımaksa

## Normal Kullanıcı Nasıl Kullanır?

### 1. Uygulamayı Başlat

USB veya WinPE ortamından açıldığında CigerTool doğrudan arayüzle başlar.

İlk yapman gereken:

- `Disk Tara` ekranına bakmak
- Kaynak ve hedef diski doğru tanımak

### 2. Klonlama Yap

Önerilen akış:

1. `Klonla` ekranına gir
2. Kaynak diski seç
3. Hedef diski seç
4. Uygun modu seç
5. Önce `Dry-run / Simülasyon` açık halde bırak
6. `Analiz Et` butonuna bas
7. Çıkan özet, uyarılar ve önerilen yöntemi oku
8. Her şey doğruysa gerçek işlemi başlat

En güvenli yaklaşım:

- Önce analiz
- Sonra simülasyon
- En son gerçek klon

### 3. Açılış Sorunu Varsa

Klon sonrası sistem açılmazsa:

1. `Boot Repair` ekranına gir
2. İlgili disk seç
3. `Boot Fix Hazırla` ile planı oluştur
4. Planlanan onarım adımlarını uygula

### 4. Disk Sağlığını Kontrol Et

`Disk Sağlığı` ekranında:

- Sorunlu diskleri önceden fark edebilirsin
- Sıcaklık ve hata sayaçlarını görebilirsin
- Klonlama öncesi diskin genel durumunu kontrol edebilirsin

### 5. Araç ve ISO Ekle

#### Harici araç eklemek için

- Taşınabilir `.exe` araçlarını `tools/` klasörüne koy
- Uygulama bunları `Araç Kutusu` ekranında göstermeye çalışır

#### ISO eklemek için

- Windows ISO'larını `isos/windows` içine koy
- Linux ISO'larını `isos/linux` içine koy
- Kurtarma / yardımcı araç ISO'larını `isos/tools` içine koy
- Eski yapı kullanıyorsan `iso-library` desteği de sürer

## Desteklenen ISO Mantığı

Uygulama ISO'ları otomatik olarak profillendirir:

- Windows ISO: `WIMBOOT` tercih edilir, uygun değilse EFI yedek açılış yöntemi denenir
- Ubuntu / Debian türevleri: kernel + initrd loopback akışı kullanılır
- Arch tabanlı dağıtımlar: archiso mantığıyla ele alınır
- Araç ISO'ları: EFI zincirleme başlatma mantığıyla denenir
- Tanınmayan ISO'lar: desteklenmiyor veya test edilmedi olarak işaretlenebilir

İleri kullanım için:

- ISO ile aynı klasöre özel `.grub.cfg` koyarak özel açılış davranışı tanımlayabilirsin
- `.cigertool.json` ile profil ve önyükleme stratejisi üzerine yazılabilir

## USB Belleğe Nasıl Yazdırılır?

Bu proje için en pratik ve önerilen yöntem, üretilen `CigerTool-by-hkannq.iso` dosyasını Windows üzerinde `Rufus` ile USB belleğe yazdırmaktır.

### Gerekli Olanlar

- En az 8 GB, tercihen 16 GB veya üzeri bir USB bellek
- `CigerTool-by-hkannq.iso`
- Yazdırma için `Rufus`

### Önerilen Yazdırma Yöntemi

1. USB belleği tak.
2. İçindeki önemli verileri yedekle.
3. `Rufus` programını aç.
4. `Aygıt` bölümünden USB belleğini seç.
5. `Önyükleme seçimi` bölümünde `CigerTool-by-hkannq.iso` dosyasını seç.
6. Bölüm düzeni olarak mümkünse `GPT` seç.
7. Hedef sistem olarak `UEFI` tercih et.
8. Dosya sistemi için Rufus'un önerdiği ayarı kullan.
9. Eğer Rufus sana yazdırma modu sorarsa `ISO Image mode` seçeneğini seç.
10. Yazdırma tamamlandıktan sonra USB'yi çıkarıp yeniden tak.

### Neden `ISO Image mode` Öneriliyor?

Çünkü CigerTool'un USB yapısı yalnızca önyükleme için değil, sonradan içerik eklemek için de tasarlanmıştır.

Bu sayede yazdırma işleminden sonra genellikle şu klasörleri görebilir ve düzenleyebilirsin:

- `tools`
- `isos/windows`
- `isos/linux`
- `isos/tools`
- `iso-library`

Bu klasör mantığı sayesinde:

- Yeni ISO ekleyebilirsin
- Yeni taşınabilir araç ekleyebilirsin
- USB'yi yeniden baştan üretmeden içeriği genişletebilirsin

### Dosya Sistemi Konusunda Önemli Not

- En geniş UEFI uyumluluğu için FAT32 genelde daha güvenlidir.
- Ancak FAT32'de 4 GB üstü tek dosya sınırı vardır.
- Çok büyük Windows ISO dosyalarını aynı belleğe sonradan eklemek istiyorsan bu sınırı dikkate almalısın.

Pratik öneri:

- Sadece CigerTool'u çalıştırmak için yazdırıyorsan Rufus'un önerdiği ayarla devam et.
- Sonradan çok büyük ISO arşivi taşımayı planlıyorsan USB yapını buna göre önceden düşün.

### MBR / BIOS Hakkında

CigerTool ISO içinde BIOS önyükleme bileşenleri de bulunur. Ancak önyükleme öncesi ISO menüsü UEFI odaklı tasarlanmıştır.

Bu nedenle:

- Yeni sistemlerde `GPT + UEFI` önerilir
- Eski sistemlerde gerekirse BIOS / MBR denenebilir

### USB Yazdırıldıktan Sonra Ne Yapılır?

Yazdırma bittikten sonra önerilen düzen:

1. USB içindeki CigerTool yapısını kontrol et
2. Gerekirse `tools/` içine taşınabilir araçlarını ekle
3. Gerekirse `isos/windows`, `isos/linux`, `isos/tools` klasörlerine ISO dosyalarını koy
4. Bilgisayarı USB'den başlat
5. WinPE açıldığında CigerTool arayüzü otomatik gelsin
6. Disk tarama ve klonlama işlemlerine başla

## USB Klasör Yapısı

Yazdırma sonrası önemli klasörler:

- `tools/`
  - Taşınabilir araçlar
- `isos/windows/`
  - Windows kurulum veya kurtarma ISO'ları
- `isos/linux/`
  - Linux canlı sistem veya bakım ISO'ları
- `isos/tools/`
  - Kurtarma, antivirüs, bölümleme ve yardımcı araç ISO'ları
- `iso-library/`
  - Geriye dönük uyumluluk yapısı

## Güvenlik ve Dikkat Edilmesi Gerekenler

- Kaynak ve hedef disk aynı olamaz.
- Hedef diskteki veri silinebilir.
- Gerçek klon işlemlerinde yönetici yetkisi gerekir.
- `Dry-run / Simülasyon` açıkken yıkıcı işlem yapılmaz.
- `SMART CLONE` ve `SYSTEM CLONE` kapasite analizi olmadan kullanılmamalıdır.
- Gerçek klon işleminden önce önemli verileri yedeklemek her zaman en güvenli yaklaşımdır.

## Proje Yapısı

- `cigertool/`
  - Ana Python uygulaması
- `build/scripts/`
  - Derleme, ADK kurulumu, klonlama ve ISO üretim betikleri
- `winpe/files/`
  - WinPE içine kopyalanan başlangıç dosyaları
- `tools/`
  - Harici araç klasörü
- `isos/`
  - Yeni ISO kütüphane yapısı
- `iso-library/`
  - Eski kütüphane uyumluluğu
- `.github/workflows/`
  - GitHub Actions ile ISO üretim hattı

## Derleme Çıktısı

Ana çıktı dosyası:

- `CigerTool-by-hkannq.iso`

GitHub Actions ayrıca şunları da üretebilir:

- `CigerTool-by-hkannq.iso.sha256`
- `CigerTool-by-hkannq.iso.json`

## Yerel Derleme

Geliştirici tarafında yerel üretim için temel akış:

1. `python -m pip install -r requirements.txt`
2. `powershell -ExecutionPolicy Bypass -File build\scripts\build_app.ps1`
3. `powershell -ExecutionPolicy Bypass -File build\scripts\build_winpe_iso.ps1`

## Ek Belgeler

- `docs/KULLANIM.md`
- `docs/MIMARI.md`
- `docs/WINPE_BUILD.md`
