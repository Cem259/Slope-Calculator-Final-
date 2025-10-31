# Slope Calculator V1

Slope Calculator

## Gereksinimler

Projeyi çalıştırmak için Python 3 ile birlikte aşağıdaki kütüphanelerin kurulu olması gerekir:

```bash
pip install PyQt6 matplotlib numpy
```

İsteğe bağlı olarak yeni bir sanal ortam oluşturup yukarıdaki komutu o ortamda da çalıştırabilirsiniz.

## Uygulamayı Çalıştırma

Projeyi klonladıktan veya ZIP dosyasını açtıktan sonra dizine girip aşağıdaki komutla uygulamayı başlatın:

```bash
python "Slope Calculator.py"
```

Komut, PyQt6 arayüzünü açar ve aşağıdaki işlevleri sunar:

- Yatay mesafe ile iki farklı noktanın yüksekliklerini girmenizi sağlar.
- "Calculate Slope" düğmesine bastığınızda eğimi yüzde cinsinden hesaplar.
- Hesaplama tamamlandığında matplotlib grafiği ile yatay mesafe, yükseklik farkı ve eğim çizgisini görselleştirir.
- Geçersiz veri girilmesi halinde kullanıcıyı bir uyarı penceresi ile bilgilendirir.
