## MÜHENDİSLİK FAKÜLTESİ
### BİLGİSAYAR MÜHENDİSLİĞİ BÖLÜMÜ

# DAĞITIK MİMARİDE TASARIM KALIPLARI İLE KVKK UYUMLU GÜVENLİ LOG YÖNETİMİ ARA KATMAN YAZILIMI

<br><br><br>

**Hazırlayan**  
Abdullah Toprak KILIÇ

**Öğrenci No:** 23253071

**Ders:**  
CENG302 – Yazılım Mühendisliği

<br><br>

---

# 1. ÖZET

Bu projede, finansal sistemlerin kritik gereksinimlerinden biri olan güvenli, ölçeklenebilir ve rol tabanlı log analizi ve denetimi problemi ele alınmıştır.

Proje kapsamında, harici bir kaynaktan gelen veri akışını soket mimarisi üzerinden dinleyen bir ara katman (Middleware) yazılımı geliştirilmiştir. Geliştirilen yazılım, gelen verileri performans süzgecine tabi tutmakta, KVKK kurallarına göre dinamik olarak maskelemekte ve kurumsal rollere göre farklı formatlarda eş zamanlı raporlamaktadır.

Projenin mimari tasarım, kalıp entegrasyonu, akıllı kodlama altyapısı ve kod optimizasyon süreçlerinde **aktif bir Yapay Zeka Ajanı (AI Agent)** ortak geliştirici ve mimar olarak rol almıştır. Proje, modern yazılım mühendisliği prensiplerine uygun olarak mikroservis felsefesiyle Docker konteynerleri üzerinde izole edilmiştir.

---

# 2. KULLANILAN YAZILIM MİMARİ STRATEJİLERİ 

Projenin omurgası, kurumsal distributed sistemlerde sıklıkla tercih edilen iki büyük mimari paternin hibrit mimaride birleştirilmesiyle oluşturulmuştur.

---

## 2.1. Dağıtık İstemci-Sunucu Mimarisi

Sistem, birbirinin iç çalışma mekanizmalarından tamamen bağımsız (decoupled) çalışan iki ayrı Docker konteynerine bölünmüştür.

- **İstemci (Data Generator):** Sürekli borsa verisi ve kullanıcı hareketleri simüle eden bir uç birimdir.

- **Sunucu (Middleware):** Belirlenen port üzerinden (Port 5001) TCP Soket katmanında bağlantıyı kabul eden ve tüm iş mantığını (business logic) üstlenen merkezî yapıdır.

Bu strateji sayesinde, veri üreten modül çökse dahi sunucu ayakta kalmaya devam eder, ya da sunucu kapansa bile istemci verileri kaybetmeden yeniden bağlanma (Auto-Reconnect) mekanizmasıyla sunucunun ayağa kalkmasını bekler.

---

## 2.2. Boru Hattı ve Filtre Mimarisi

Ara katman sunucusuna gelen ham string verilerin işlenmesi, ardışık ve bağımsız filtre bloklarından oluşan bir boru hattı (pipeline) yapısına devredilmiştir.

Her filtre, kendinden önceki filtrenin çıktısını girdi olarak alır.

1. **Performans Filtresi (Filter 1):** Önemsiz log seviyelerini (`INFO`, `WARNING`) ayırır.

2. **Güvenlik / KVKK Filtresi (Filter 2):** Hassas kişisel verileri regex kurallarına göre anonimleştirir.

3. **Zenginleştirme Filtresi (Filter 3):** Ham veriye işlem takip numarası ekler.

4. **Format Dağıtım Filtresi (Filter 4):** Veriyi tasarım kalıbına aktarır.

---

# 3. UYGULANAN TASARIM KALIPLARI

Projede nesne yönelimli programlama (OOP) kalitesini artırmak, kod tekrarını önlemek ve SOLID prensiplerine sadık kalmak amacıyla tam olarak **2 adet GOF (Gang of Four)** tasarım kalıbı uygulanmıştır.

---

## 3.1. Singleton Tasarım Kalıbı

### Uygulanan Birim
`data_generator/generator.py` içindeki `SingletonLogGenerator` sınıfı.

### Mühendislik Amacı

Dağıtık sistemlerde aynı anda birden fazla veri akış kanalının açılması ağ fırtınalarına (network storms) ve mükerrer soket kilitlenmelerine yol açar.

Python dilinin `__new__` metodu ezilerek (override edilerek), uygulamanın çalışma zamanında bellekte sadece tek bir nesne örneğinin barındırılması ve tek bir soket hattının yönetilmesi garanti altına alınmıştır.

---

## 3.2. Strategy Tasarım Kalıbı

### Uygulanan Birim

`middleware/main.py` içindeki `LogFormatterStrategy` soyut sınıfı ve ondan türeyen:

- `JSONFormatter`
- `CSVFormatter`
- `HTMLFormatter`

sınıfları.

### Mühendislik Amacı

Sistemde tanımlı olan kurumsal rollerin (Geliştirici, Siber Güvenlik Uzmanı, Sistem Yöneticisi) her birinin çıktı beklentisi farklıdır.

Bu biçimlendirme lojistiğini tek bir `if-else` bloğuna yığmak SOLID'in **Open/Closed Principle** prensibini doğrudan ihlal ederdi.

Strategy kalıbı sayesinde her rolün formatlama algoritması kendi sınıfında izole edilmiştir.

Sisteme yeni bir rol ve format (Örn: `XMLFormatter`) eklenmesi gerektiğinde, çalışan mevcut kod tabanına dokunulmadan sadece yeni bir strateji sınıfı eklenmesi yeterli kılınmıştır.

---

# 4. DETAYLI FONKSİYONEL ANALİZ VE SİSTEM ÖZELLİKLERİ

---

## 4.1. Yapay Zeka Ajanı ile Ortak Geliştirme Metodolojisi

Bu projenin yaşam döngüsünde modern yazılım mühendisliği yaklaşımlarından olan **AI-Assisted Software Engineering** modeli benimsenmiştir. Proje mimarı olarak görev alan **Yapay Zeka Ajanı (AI Agent)**, geliştirme sürecinde şu kritik rolleri üstlenmiştir:
- **Mimarî Karar Mekanizması:** Boru hattındaki darboğazları engellemek adına Erken Filtreleme (Early Dropping) lojistiğinin kurgulanması.
- **Tasarım Kalıbı Orkestrasyonu:** Singleton ve Strategy pattern yapılarının Python çalışma zamanına (runtime) hata vermeyecek şekilde, eş zamanlı tarih damgalı dosya mimarisine (Log Rotation) entegre edilmesi.
- **Güvenli Kod Üretimi:** KVKK kapsamında regex tabanlı akıllı karakter maskeleme algoritmalarının asenkron yapıya uyumlu üretilmesi.

---

## 4.2. Performans Odaklı Erken Filtreleme

Sistem stres testi altındayken saniyede binlerce log üretmektedir.

Ağır metin işleme (Regex) ve disk I/O işlemleri sistem performansını düşüren en büyük darboğazlardır.

Yazılımda kurulan mimari sayesinde, `INFO` ve `WARNING` logları boru hattının en başında (`Filter 1`) tespit edilerek ağır KVKK ve formatlama süreçlerine sokulmadan, işlemciyi yormayacak şekilde doğrudan asenkron ham log dosyasına (`dropped_system.log`) yazılır.

Kurumsal borsa kaynakları sadece `ERROR` ve `CRITICAL` logların işlenmesi için harcanır.

---

## 4.3. Dinamik Konfigürasyon ve Akıllı KVKK Maskeleme

Kişisel verilerin maskelenmesi statik kod bloklarıyla değil, `mask_config.json` dosyası üzerinden harici olarak yönetilir.

Bu sayede sistem kapatılmadan dahi maskeleme kuralları esnekçe güncellenebilir.

Geliştirilen akıllı karakter yıldızlama algoritması verinin okunabilirliğini tamamen yok etmez:

- **E-posta:** `toprak@borsatr.com` → `t*****@borsatr.com`

- **İsim Soyisim:** `Abdullah Kılıç` → `A******* K****`

- **Kredi Kartı / TC No:** Baştan ve sondan belirli haneleri koruyarak aradaki haneleri dinamik olarak yıldızlar.

---

## 4.4. Önem Derecesine Göre Vurgulama

Sistem Yöneticisi (System Admin) için üretilen `sysadmin.html` raporu, görsel denetim kalitesini artırmak için dinamik CSS enjeksiyonuna sahiptir.

`HTMLFormatter` stratejisi, log nesnesinin içindeki veri seviyesini kontrol ederek:

- `CRITICAL` seviyesindeki log satırlarını açık kırmızı,
- `ERROR` seviyesindeki satırları ise açık sarı

arka plan rengiyle vurgulayarak operasyon ekiplerinin gözünden kaçmasını engeller.

---

# 5. STRES TESTİ VE PERFORMANS SONUÇLARI

Sistem, Docker altyapısı üzerinde `PERFORMANCE_TEST=true` konfigürasyonuyla stres testine tabi tutulmuştur.

## Test Parametreleri

- **İstemci Gönderim Hızı:** Her log arası `time.sleep(0.001)` (1 milisaniye) bekleme süresi set edilerek ara katmana yoğun bir veri bombardımanı simüle edilmiştir.

- **Throughput:** Yapılan testlerde tek çekirdek üzerinde çalışan Python ara katman sunucusunun, saniyede ortalama **800 - 950 adet logu** soketten okuyup, parse edip, elenenleri ayırıp, kalanları KVKK süzgecinden geçirerek 3 farklı dosyaya eş zamanlı yazabildiği ve kararlı bir şekilde çalıştığı gözlemlenmiştir.

---

# 6. SONUÇ VE DEĞERLENDİRME

Bu proje, teorik yazılım mühendisliği dersi kapsamında öğrenilen soyut tasarım kalıpları ve mimari paternlerin, gerçek dünya kurumsal problemlerine (KVKK uyumluluğu, distributed log yönetimi, stres altındaki sistem dayanıklılığı) nasıl kararlı çözümler üretebileceğini başarıyla ortaya koymuştur.

İnsan-AI iş birliğinin (**Human-AI Collaboration**) yazılım yaşam döngüsündeki hızlandırıcı ve optimize edici gücü, **AI Agent** entegrasyonu sayesinde bu projede somut olarak deneyimlenmiştir. Veritabanı katmanı kullanılmaksızın, tamamen Docker Volume ve dosya sistemi üzerinde kurulan bu yapı, düşük kaynak tüketimi ve yüksek genişletilebilirlik kapasitesi ile endüstriyel standartları yakalamıştır.

---

# 7. EKLER VE PROJE SUNUMU


🌐 **[CENG302 Proje Sunumu](https://drive.google.com/file/d/1s5bBbVRNL5tAfz5GdPfUHGcaXFd-DoAU/view?usp=sharing)**