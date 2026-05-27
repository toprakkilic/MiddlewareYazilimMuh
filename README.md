# 📊 Borsa Log Yönetimi ve Denetim Ara Katman Yazılımı

Bu proje, yüksek frekanslı bir borsa simülasyonundan gelen anlık log verilerini yakalayan, performans filtrelemesine tabi tutan, KVKK (Kişisel Verilerin Korunması Kanunu) kapsamında dinamik olarak maskeleyen ve farklı kurumsal rollere göre özelleştirilmiş formatlarda raporlayan distributed (dağıtık) bir **Log Management & Audit** yazılımıdır.

Proje, yazılım mühendisliği dersi (CENG) dönem sonu isterleri doğrultusunda; **2 Mimari Patern (Client-Server, Pipe & Filter)** ve **2 Tasarım Kalıbı (Singleton, Strategy)** kullanılarak tamamen izole Docker konteynerleri üzerinde kurgulanmıştır.

---

# 🏗️ Sistem Mimarisi ve Tasarım Kalıpları

Sistem, yazılım mimarisi standartlarına uygun olarak birbirine gevşek bağlı (loosely coupled) iki ana modülden oluşmaktadır:

1. **Data Generator Modülü (Client):** **Singleton Pattern** kullanılarak tasarlanmıştır. Sistemde tek bir veri üretici nesnesinin ve tek bir kararlı TCP soket bağlantısının olmasını garanti eder. Borsa işlemlerini simüle ederek saniyede binlerce karışık log üretir.

2. **Middleware Modülü (Server):** Gelen ham verileri **Pipe & Filter** mimarisiyle işler. Filtre hattından başarıyla geçen temiz verileri, **Strategy Pattern** kullanarak ilgili kurumsal rollere göre (`JSON`, `CSV`, `HTML`) biçimlendirip yerel dosya sistemine yazar.

## Veri İşleme Akış Hattı (Pipe & Filter)

Gelen her log satırı sırasıyla şu filtrelerden geçer:

- **Filter 1 (Performans Filtresi):** CPU ve I/O yükünü azaltmak için `INFO` ve `WARNING` seviyesindeki önemsiz logları boru hattının başında ayırır, işlemeksizin ham olarak yedek log dosyasına yazar.

- **Filter 2 (KVKK Maskeleme Filtresi):** `mask_config.json` dosyasındaki dinamik kurallara göre metin içindeki TC Kimlik, E-posta, İsim-Soyisim ve Kredi Kartı verilerini karakter bazlı akıllıca yıldızlar (`*`).

- **Filter 3 (Zenginleştirme / Enrichment):** Log nesnesine mikroservis takibi için benzersiz bir `Transaction_ID` (`TX-10000X`) ve metadata enjekte eder.

- **Filter 4 (Biçimlendirme / Strategy Dağıtımı):** Rol tabanlı stratejileri tetikleyerek eş zamanlı çıktı dosyalarını besler.

---

# 📂 Klasör Yapısı

```text
MiddlewareYazilimMuh/
│
├── data_generator/
│   ├── Dockerfile
│   └── generator.py        # Singleton Log Üretici (Client)
│
├── middleware/
│   ├── Dockerfile
│   ├── main.py             # Pipe & Filter / Strategy Server
│   └── mask_config.json    # Dinamik KVKK Kuralları
│
├── output_logs/            # Docker Volume ile bağlanan çıktı klasörü (Otomatik Oluşur)
│
└── docker-compose.yml      # Orkestrasyon ve Çevre Değişkenleri Ayarları
```

---

# ⚙️ Kurulum ve Çalıştırma Rehberi

## Gereksinimler

- Docker ve Docker Compose (Güncel Sürüm)

---

## 1. Sistemi Ayağa Kaldırma (Derleme ve Çalıştırma)

Projenin kök dizininde terminali açın ve sistemi arka planda izole ağ köprüleriyle başlatmak için şu komutu çalıştırın:

```bash
docker compose up --build
```

---

## 2. Çalışma Modu Seçimi (Feature Toggle)

Sistemin ekrana basacağı metrik yükü `docker-compose.yml` içindeki `PERFORMANCE_TEST` ortam değişkeninden dinamik olarak yönetilir:

### Production Modu (`PERFORMANCE_TEST=false`)

Sistem sessizce, maksimum I/O hızında çalışır. Disk ve CPU tamamen log işleme işine odaklanır.

### Sunum / Stres Testi Modu (`PERFORMANCE_TEST=true`)

Ara katman sunucusu saniyede kaç log işlediğini (Throughput) canlı olarak terminale basar.

---

# 📊 Üretilen Rapor Çıktıları

Sistem çalışmaya başladığı an, kök dizinde `output_logs/` adında bir klasör oluşur.

Bu klasörün altında her gün için ayrı tarih damgalı (Log Rotation) şu dosyalar üretilir:

- `webdev_YYYY-MM-DD.json`  
  Web geliştiricileri için izlenebilirlik metadatalarını içeren saf JSON nesneleri.

- `cybersec_YYYY-MM-DD.csv`  
  Siber güvenlik ekiplerinin SIEM araçlarına besleyebileceği, başında güvenlik etiketleri barındıran temiz denetim (audit) logları.

- `sysadmin_YYYY-MM-DD.html`  
  Sistem yöneticilerinin tarayıcıda izleyebileceği, `CRITICAL` logları kırmızı, `ERROR` logları sarı renk tonlarıyla görselleştiren (Highlighting) dinamik HTML Dashboard.

- `dropped_system_YYYY-MM-DD.log`  
  Performans filtresi tarafından elenmiş, CPU harcanmadan doğrudan diske bırakılmış ham sistem yedek logları.

---

# 🛑 Sistemi Kapatma

Konteynerleri güvenli bir şekilde kapatmak ve Docker sanal ağ köprülerini bilgisayardan temizlemek için yeni bir terminal sekmesinde şu komutu çalıştırın:

```bash
docker compose down
```

> Not: Bu komut `output_logs/` klasöründeki üretilmiş raporlarınıza asla zarar vermez.