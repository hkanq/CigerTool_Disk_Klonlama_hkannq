# CigerTool UX Yeniden Tasarımı

## Amaç

Bu geçişin amacı, uygulamayı geliştirici aracı görünümünden çıkarıp gerçek son kullanıcı yüzeyine taşımaktır.

## Uygulanan Kararlar

### Pencere Davranışı

- Standart Windows pencere çerçevesi korunur.
- Sürükleme, küçültme, büyütme ve kapatma işletim sisteminin doğal davranışı ile çalışır.
- Uygulama ikonu artık boş bırakılmaz; uygulama dosyası için temiz bir `CigerTool.ico` atanır.

### Bilgi Mimarisi

Ana gezinme artık şu modüllere odaklanır:

- `Ana Sayfa`
- `Klonlama`
- `Yedekleme ve İmaj`
- `Diskler ve Sağlık`
- `USB Ortamı Oluştur`
- `Günlükler`
- `Ayarlar`

Önceki `Tools` yaklaşımı ana gezinmeden çıkarılmıştır. Yardımcı araçlar ürünün merkezinde değildir.

### Türkçe Standartlaştırma

- Görünür ana metinler Türkçeye çevrildi.
- Gerçek Türkçe karakterler kullanıldı: `ğ ş ü ö ç ı İ`
- Karışık İngilizce/Türkçe veya sahte Türkçe yazım kaldırıldı.

### Kullanıcı Dili

Ana yüzeyde:

- teknik profil dili azaltıldı
- iç sistem terimleri geri çekildi
- “hazırlık denetimi”, “sonraki adım”, “uyarılar”, “rapor kaydet” gibi eylem odaklı metinler öne çıkarıldı

Gelişmiş teknik ayrıntılar:

- `Ana Sayfa` içinde başlangıç denetimi ayrıntıları
- `Diskler ve Sağlık` içinde gelişmiş sistem bilgileri
- `USB Ortamı Oluştur` içinde kaynak ve bütünlük ayrıntıları
- `Ayarlar` içinde gelişmiş yollar ve yapılandırma

### Markalama

- Zayıf `CT` kutusu kaldırıldı.
- Uygulama içinde tam `CigerTool` kelime markası kullanıldı.
- Çalıştırılabilir dosya için özel ikon bağlandı.

## Akış Düzeltmeleri

### Klonlama

Artık görünür akış:

1. kaynak seç
2. hedef seç
3. hazırlık denetimini çalıştır
4. uyarıları gözden geçir
5. raporu kaydet

Yürütme motoru henüz açık değilse bu durum açıkça belirtilir; kullanıcı sahte bir “başlat” akışına sokulmaz.

### Yedekleme ve İmaj

Artık görünür akış:

1. işlem türünü seç
2. ilgili diski seç
3. hazırlık denetimini çalıştır
4. kapsam ve uyarıları oku
5. hazırlık raporunu kaydet

### USB Ortamı Oluştur

Artık görünür akış:

1. kaynağı yenile veya elle dosya seç
2. imajı indir
3. bütünlüğü doğrula
4. USB aygıtını seç
5. açık onay ver
6. yazma işlemini başlat

## Ürün Dili Kuralı

Ana yüzey yalnızca normal kullanıcıya karar vermede yardımcı olan bilgiyi gösterir. Çekirdek ilke:

- sade
- anlaşılır
- güven veren
- eylem odaklı
