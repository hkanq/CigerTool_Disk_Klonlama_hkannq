# CigerTool Clone Model

## Uygulanan Gerçek Kapsam

Klonlama bu sürümde iki yürütülebilir yol sunar:

### Ham Kopya

- sürücü düzeyinde gerçek bayt kopyası yapar
- kaynak sürücünün tüm içeriğini hedefe yazar
- hedef en az kaynak kadar büyük olmalıdır
- masaüstünde çalışan sistem sürücüsü kaynak olarak desteklenmez
- yönetici yetkisi gerekir

### Akıllı Kopya

- dosya temelli eşleme yapar
- hedef kökü temizlenir
- erişilebilen dosya ve klasörler hedefe kopyalanır
- NTFS kaynak odaklıdır
- kullanılan alan ve güvenlik tamponu ile uygunluk denetlenir

## Akış

Klonlama ekranı şu uçtan uca yolu tamamlar:

1. kaynak seç
2. hedef seç
3. denetimi çalıştır
4. uyarıları incele
5. üzerine yazma onayı ver
6. işlemi başlat
7. ilerlemeyi izle
8. sonucu kaydet

## Ham Kopya Sınırı

Ham kopya bu sürümde:

- bölüm tablosu yeniden yazma mantığını ayrı yönetmez
- önyükleme onarımı yapmaz
- BitLocker farkındalığı eklemez
- daha büyük hedefte kalan alanı büyütmez

## Akıllı Kopya Sınırı

Akıllı kopya bu sürümde:

- tam disk değil, sürücü / kök içerik eşler
- yeniden yönlendirme noktalarını atlar
- canlı sistemde kilitli dosyaları atlayabilir
- önyüklenebilirlik onarımı yapmaz

## Dürüstlük Notu

Bu yüzden:

- ham kopya gerçek ama hacim odaklıdır
- akıllı kopya gerçek ama dosya temelli ve NTFS odaklıdır
- tam fiziksel disk yeniden kurma gelecekteki genişletme alanıdır
