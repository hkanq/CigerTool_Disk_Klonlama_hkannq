# CigerTool Disk Sağlık Modeli

## Bu Sürümde Sunulanlar

Diskler ve Sağlık bölümü artık şu alanları bir araya getirir:

- sürücü adı ve harfi
- model bilgisi
- bağlantı türü
- medya tipi
- toplam / kullanılan / boş alan
- kullanım oranı
- sistem sürücüsü işareti
- temel uyarı özeti

## Uyarı Özeti Nasıl Üretilir

Bu sürümde uyarı özeti şu sinyallerden oluşur:

- Windows durum bilgisi `OK` dışında ise dikkat gerekir
- boş alan yüzde 10 altına düşerse düşük boş alan uyarısı verilir
- çalışan sistem sürücüsü ayrıca işaretlenir

## Bilinçli Sınır

Bu bölüm şu an:

- üreticiye özel derin SMART verisi sunmaz
- ömür tahmini yapmaz
- sektör hatası veya sıcaklık telemetrisi toplamaz

Ama yine de kullanıcıya seçim öncesi şu temel soruları yanıtlar:

- bu sürücü hangisi
- ne kadar dolu
- nasıl bağlı
- şu anda dikkat gerektiren bir durum var mı
