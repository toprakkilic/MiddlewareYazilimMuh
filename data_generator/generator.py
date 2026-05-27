import socket
import time
import random
from datetime import datetime

class SingletonLogGenerator:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SingletonLogGenerator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, host="middleware", port=5001):
        if self._initialized:
            return
        self.host = host
        self.port = port
        self.sock = None
        self._initialized = True

    def connect(self):
        """Ara katman (Server) ayağa kalkana kadar bağlanmayı dener."""
        print(f"[{datetime.now()}] Ara katmana bağlanılıyor: {self.host}:{self.port}...")
        while True:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
                print(f"[{datetime.now()}] Ara katmana başarıyla bağlanıldı!")
                break
            except socket.error:
                time.sleep(2)  # Sunucu henüz açılmadıysa 2 saniye bekle

    def generate_random_kvkk(self):
        """Simülasyon için sahte KVKK verileri üretir (50 İsim, 50 Soyisim içerir)."""
        names = [
            "Abdullah", "Toprak", "Ahmet", "Mehmet", "Can", "Elif", "Zeynep", "Ali", "Veli", "Ayşe",
            "Fatma", "Mustafa", "Murat", "Hüseyin", "Hasan", "İbrahim", "Ömer", "Osman", "Yusuf", "Eren",
            "Arda", "Burak", "Deniz", "Ege", "Kaan", "Mert", "Oğuz", "Volkan", "Serkan", "Gökhan",
            "Hakan", "Tolga", "Onur", "Cem", "Barış", "Umut", "Özgür", "Doruk", "Kerem", "Yavuz",
            "Selin", "Merve", "Aslı", "Büşra", "Gamze", "Gizem", "Ebru", "Seda", "Gözde", "Dilan"
        ]
        surnames = [
            "Kılıç", "Yılmaz", "Kaya", "Demir", "Öztürk", "Şahin", "Aydın", "Özdemir", "Arslan", "Doğan",
            "Kılıçarslan", "Çetin", "Güneş", "Yıldız", "Yıldırım", "Öztürk", "Acar", "Yavuz", "Polat", "Sarı",
            "Avcı", "Karaca", "Aksoy", "Şen", "Köse", "Taş", "Uzun", "Bulut", "Aslan", "Çakır",
            "Güler", "Yalçın", "Aktaş", "Koç", "Kurt", "Tekin", "Uçar", "Eser", "Kahraman", "Duran",
            "Özkan", "Kartal", "Sever", "Peker", "Alkan", "Gündüz", "Sönmez", "Şimşek", "Erdoğan", "Aslan"
        ]
        
        tc = "".join([str(random.randint(0, 9)) for _ in range(11)])
        email = f"user{random.randint(100, 999)}@borsatr.com"
        card = "-".join(["".join([str(random.randint(0, 9)) for _ in range(4)]) for _ in range(4)])
        customer = f"{random.choice(names)} {random.choice(surnames)}"
        return tc, email, card, customer

    def create_log_pool(self):
        """Hocanın istediği tüm varyasyonları içeren genişletilmiş 100 senaryoluk devasa log havuzu."""
        tc, email, card, customer = self.generate_random_kvkk()
        
        # 1. KATEGORİ: Ara Katmanın İŞLEMEYECEĞİ (Filtreleyip Ham Log Dosyasına Atacağı) Önemsiz Loglar (50 Adet)
        dropped_logs = [
            {"level": "INFO", "module": "AUTH", "msg": f"Müşteri: {customer} sisteme başarılı giriş yaptı. IP: 192.168.2.45"},
            {"level": "INFO", "module": "AUTH", "msg": f"Kullanıcı oturumunu sonlandırdı (Logout). E-posta: {email}"},
            {"level": "INFO", "module": "AUTH", "msg": f"Müşteri: {customer} şifre yenileme bağlantısı talep etti."},
            {"level": "INFO", "module": "AUTH", "msg": f"Kullanıcı iki aşamalı doğrulamayı (2FA) başarıyla geçti. Mail: {email}"},
            {"level": "INFO", "module": "AUTH", "msg": f"Müşteri: {customer} profil bilgilerini güncelledi."},
            {"level": "INFO", "module": "AUTH", "msg": f"Kullanıcı sözleşmesi onaylandı. Onaylayan: {email}"},
            {"level": "INFO", "module": "AUTH", "msg": f"Müşteri: {customer} yeni bir API anahtarı (API Key) oluşturdu."},
            {"level": "INFO", "module": "AUTH", "msg": f"Oturum zaman aşımı uyarısı gönderildi. Kullanıcı: {email}"},
            {"level": "INFO", "module": "AUTH", "msg": f"Müşteri: {customer} gizlilik politikasını inceledi."},
            {"level": "INFO", "module": "AUTH", "msg": f"Mobil uygulama üzerinden yeni session açıldı. Mail: {email}"},
            
            {"level": "INFO", "module": "ACCESS_LOG", "msg": "GET /api/v1/market/orderbook/BTC-USDT HTTP/1.1 200 OK"},
            {"level": "INFO", "module": "ACCESS_LOG", "msg": "POST /api/v1/user/profile-picture HTTP/1.1 201 Created"},
            {"level": "INFO", "module": "ACCESS_LOG", "msg": "GET /api/v1/market/ticker/ETH-TRY HTTP/1.1 200 OK"},
            {"level": "INFO", "module": "ACCESS_LOG", "msg": "GET /api/v1/wallet/balances HTTP/1.1 200 OK"},
            {"level": "INFO", "module": "ACCESS_LOG", "msg": "POST /api/v1/notification/register HTTP/1.1 200 OK"},
            {"level": "INFO", "module": "ACCESS_LOG", "msg": "GET /static/images/logo.png HTTP/1.1 304 Not Modified"},
            {"level": "INFO", "module": "ACCESS_LOG", "msg": "GET /api/v1/health-check HTTP/1.1 200 OK"},
            {"level": "INFO", "module": "ACCESS_LOG", "msg": "OPTIONS /api/v1/trade/order HTTP/1.1 204 No Content"},
            {"level": "INFO", "module": "ACCESS_LOG", "msg": "GET /api/v1/kyc/status HTTP/1.1 200 OK"},
            {"level": "INFO", "module": "ACCESS_LOG", "msg": "GET /favicon.ico HTTP/1.1 200 OK"},
            
            {"level": "INFO", "module": "MARKET_DATA", "msg": "THY (THYAO) hisse senedi fiyatı güncellendi: 312.50 TL"},
            {"level": "INFO", "module": "MARKET_DATA", "msg": "Bitcoin (BTC) anlık piyasa fiyatı: 68,450.20 USDT"},
            {"level": "INFO", "module": "MARKET_DATA", "msg": "Ethereum (ETH) gas ücretleri optimize edildi: 15 Gwei"},
            {"level": "INFO", "module": "MARKET_DATA", "msg": "Aselsan (ASELS) derinlik tablosu yenilendi."},
            {"level": "INFO", "module": "MARKET_DATA", "msg": "Garanti Bankası (GARAN) hacim alarmı tetiklendi."},
            {"level": "INFO", "module": "MARKET_DATA", "msg": "Koç Holding (KCHOL) blok emir girişi yapıldı."},
            {"level": "INFO", "module": "MARKET_DATA", "msg": "Dolar/TL kuru borsa kuru ile eşitlendi: 32.45 TRY"},
            {"level": "INFO", "module": "MARKET_DATA", "msg": "Ereğli Demir Çelik (EREGL) tahtası işleme açıldı."},
            {"level": "INFO", "module": "MARKET_DATA", "msg": "Solana (SOL) piyasa yapıcı (Market Maker) botu devreye girdi."},
            {"level": "INFO", "module": "MARKET_DATA", "msg": "Yıllık temettü takvimi sisteme yüklendi."},
            
            {"level": "WARNING", "module": "WALLET", "msg": f"Yetersiz bakiye denemesi. Müşteri: {customer}, Limit yetersiz."},
            {"level": "WARNING", "module": "WALLET", "msg": f"Para çekme limiti sınırına yaklaşıldı. Kullanıcı E-posta: {email}"},
            {"level": "WARNING", "module": "WALLET", "msg": f"Müşteri: {customer} geçersiz bir promosyon kodu girmeyi denedi."},
            {"level": "WARNING", "module": "WALLET", "msg": f"Kredi kartı son kullanma tarihi yaklaşmakta. Kullanıcı: {email}"},
            {"level": "WARNING", "module": "WALLET", "msg": f"Şüpheli mikro transfer denemesi engellendi. Sahibi: {customer}"},
            {"level": "WARNING", "module": "WALLET", "msg": f"Yabancı para biriminden dönüştürme makası yüksek. Mail: {email}"},
            {"level": "WARNING", "module": "WALLET", "msg": f"Müşteri: {customer} günlük maksimum takas sınırını zorluyor."},
            {"level": "WARNING", "module": "WALLET", "msg": f"Bekleyen emir süresi dolmak üzere. Kullanıcı: {email}"},
            {"level": "WARNING", "module": "WALLET", "msg": f"Banka entegrasyonunda hafif gecikme (Delay). Müşteri: {customer}"},
            {"level": "WARNING", "module": "WALLET", "msg": f"Kripto cüzdan adresi doğrulama uyarısı. Hedef: {email}"},
            
            {"level": "WARNING", "module": "DOCKER_INTERNAL", "msg": "Container borsa_generator memory usage reached 68%"},
            {"level": "WARNING", "module": "DOCKER_INTERNAL", "msg": "Nginx container proxy connection cache is high (82%)"},
            {"level": "WARNING", "module": "DOCKER_INTERNAL", "msg": "Redis cache eviction rate is increasing."},
            {"level": "WARNING", "module": "DOCKER_INTERNAL", "msg": "Logrotate process took longer than expected."},
            {"level": "WARNING", "module": "DOCKER_INTERNAL", "msg": "Prometheus metrics endpoint scrap timeout warning."},
            {"level": "WARNING", "module": "NETWORK", "msg": "Gecikme süresi (Latency) yükseldi: 120ms. Lokasyon: Istanbul"},
            {"level": "WARNING", "module": "NETWORK", "msg": "TCP Paket kaybı (Packet Loss) oranı limit sınırında: %1.2"},
            {"level": "WARNING", "module": "NETWORK", "msg": "Yedek DNS sunucusuna geçiş yapıldı."},
            {"level": "WARNING", "module": "NETWORK", "msg": "SSL/TLS el sıkışması (Handshake) yavaş gerçekleşiyor."},
            {"level": "WARNING", "module": "NETWORK", "msg": "Yük dengeleyici (Load Balancer) seans aktarımı yaptı."}
        ]
        
        # 2. KATEGORİ: Ara Katmanın KESİNLİKLE İŞLEYECEĞİ (Maskeleyip, Zenginleştirip, Formatlayacağı) Önemli Loglar (50 Adet)
        processed_logs = [
            {"level": "ERROR", "module": "TRANSACTION", "msg": f"Kripto alım emri başarısız. Müşteri: {customer}, TC: {tc}, Hata: Likidite Sağlanamadı"},
            {"level": "ERROR", "module": "TRANSACTION", "msg": f"Para transferi (EFT) banka tarafından reddedildi. Alıcı Kart No: {card}"},
            {"level": "ERROR", "module": "TRANSACTION", "msg": f"Hisse senedi satım emri zaman aşımı. Satıcı Müşteri: {customer}"},
            {"level": "ERROR", "module": "TRANSACTION", "msg": f"Arbitraj işlemi iptal edildi. Kullanıcı TC: {tc}, Mail: {email}"},
            {"level": "ERROR", "module": "TRANSACTION", "msg": f"Marjin hesabı tasfiye (Liquidation) tetiklendi. Borçlu: {customer}"},
            {"level": "ERROR", "module": "TRANSACTION", "msg": f"Vadeli işlemler (Futures) pozisyonu kapatılamadı. Kart: {card}"},
            {"level": "ERROR", "module": "TRANSACTION", "msg": f"Müşteri: {customer} para yatırma dekont doğrulaması başarısız."},
            {"level": "ERROR", "module": "TRANSACTION", "msg": f"Otomatik stop-loss emri başarısız oldu. Kullanıcı TC: {tc}"},
            {"level": "ERROR", "module": "TRANSACTION", "msg": f"Swift kodu geçersiz transfer askıya alındı. Mail: {email}"},
            {"level": "ERROR", "module": "TRANSACTION", "msg": f"Komisyon hesaplama hatası oluştu. Hesap sahibi: {customer}"},
            
            {"level": "ERROR", "module": "DATABASE", "msg": f"Veritabanı kilitlenme (Deadlock) hatası algılandı. Sorgulayan TC: {tc}"},
            {"level": "ERROR", "module": "DATABASE", "msg": f"SQL Bağlantı havuzu tükendi (Connection Pool Exhausted). İstek Sahibi: {email}"},
            {"level": "ERROR", "module": "DATABASE", "msg": f"Birincil (Primary) DB disk alanı kritik seviyede (%94). Kullanıcı: {customer}"},
            {"level": "ERROR", "module": "DATABASE", "msg": f"Replikasyon senkronizasyon hatası (Lag: 45sn). Etkilenen TC: {tc}"},
            {"level": "ERROR", "module": "DATABASE", "msg": f"Bozuk index algılandı (Index Corruption). Tablo sahibi: {email}"},
            {"level": "ERROR", "module": "DATABASE", "msg": f"Migration betiği yarıda kaldı. Geri dönülüyor (Rollback). İstek: {customer}"},
            {"level": "ERROR", "module": "DATABASE", "msg": f"Büyük veri sorgusu (Slow Query) zaman aşımına uğradı. TC: {tc}"},
            {"level": "ERROR", "module": "DATABASE", "msg": f"Veritabanı şeması doğrulanamadı. Sorumlu Hesap: {email}"},
            {"level": "ERROR", "module": "DATABASE", "msg": f"NoSQL önbellek sunucusu veri yazma hatası. Kart sahibi: {customer}"},
            {"level": "ERROR", "module": "DATABASE", "msg": f"Yedekleme verisi bütünlük (MD5) kontrolü başarısız. TC: {tc}"},
            
            {"level": "ERROR", "module": "API_GATEWAY", "msg": f"Akbank Ödeme API entegrasyonu zaman aşımına uğradı. Sorumlu: {customer}"},
            {"level": "ERROR", "module": "API_GATEWAY", "msg": f"MKK (Merkezi Kayıt Kuruluşu) API 502 Bad Gateway hatası verdi. TC: {tc}"},
            {"level": "ERROR", "module": "API_GATEWAY", "msg": f"Binance WebSocket API bağlantısı koptu. Teknik İletişim: {email}"},
            {"level": "ERROR", "module": "API_GATEWAY", "msg": f"SMS Doğrulama (OTP) sağlayıcı servisi yanıt vermiyor. Alıcı: {customer}"},
            {"level": "ERROR", "module": "API_GATEWAY", "msg": f"Takasbank entegrasyon mutabakatı başarısız. Yetkili TC: {tc}"},
            {"level": "ERROR", "module": "API_GATEWAY", "msg": f"E-Devlet ikametgah doğrulama servisi çöktü. Kullanıcı: {email}"},
            {"level": "ERROR", "module": "API_GATEWAY", "msg": f"Para Garanti API geçersiz token hatası verdi. Müşteri: {customer}"},
            {"level": "ERROR", "module": "API_GATEWAY", "msg": f"TradingView sinyal entegrasyonu ayrıştırma hatası. Hesap: {email}"},
            {"level": "ERROR", "module": "API_GATEWAY", "msg": f"Push bildirim (Firebase) servisi kimlik doğrulama hatası. Kart: {card}"},
            {"level": "ERROR", "module": "API_GATEWAY", "msg": f"Kullanıcı KYC kimlik tarama API'si fotoğrafı okuyamadı. TC: {tc}"},
            
            {"level": "CRITICAL", "module": "SECURITY", "msg": f"Farklı IP'lerden aynı anda çoklu oturum açma denemesi! E-posta: {email}, Kart No: {card}"},
            {"level": "CRITICAL", "module": "SECURITY", "msg": f"SQL Injection şüphesi taşıyan istek engellendi! İstek Atan Müşteri: {customer}, TC: {tc}"},
            {"level": "CRITICAL", "module": "SECURITY", "msg": f"Kaba kuvvet (Brute Force) saldırısı algılandı. Hedef Hesap: {email}"},
            {"level": "CRITICAL", "module": "SECURITY", "msg": f"XSS (Cross-Site Scripting) payload içeren istek reddedildi. Müşteri: {customer}"},
            {"level": "CRITICAL", "module": "SECURITY", "msg": f"Kara listedeki (Blacklisted) bir IP adresinden API erişim denemesi. TC: {tc}"},
            {"level": "CRITICAL", "module": "SECURITY", "msg": f"Yönetici paneline (Admin) yetkisiz erişim teşebbüsü! Şüpheli: {customer}"},
            {"level": "CRITICAL", "module": "SECURITY", "msg": f"Kullanıcı şifresi sızıntı (Data Breach) havuzunda bulundu. Zorunlu reset: {email}"},
            {"level": "CRITICAL", "module": "SECURITY", "msg": f"Şüpheli API istek paterni (DDoS Şüphesi). İstek Sahibi TC: {tc}"},
            {"level": "CRITICAL", "module": "SECURITY", "msg": f"Cüzdan private key imza doğrulama hatası! Güvenlik ihlali şüphesi. Kart: {card}"},
            {"level": "CRITICAL", "module": "SECURITY", "msg": f"Çalıntı kart bildirimi olan hesaptan işlem denemesi! Kart: {card}, Müşteri: {customer}"},
            
            {"level": "CRITICAL", "module": "CORE_ENGINE", "msg": f"Emir eşleştirme motoru (Matching Engine) çöktü! Etkilenen Hesap: {email}"},
            {"level": "CRITICAL", "module": "CORE_ENGINE", "msg": f"Kritik bakiye mutabakat hatası (Balance Mismatch)! Müşteri: {customer}, Kart No: {card}"},
            {"level": "CRITICAL", "module": "CORE_ENGINE", "msg": "Emir defteri (Orderbook) bellek taşması (Memory Overflow) hatası!"},
            {"level": "CRITICAL", "module": "CORE_ENGINE", "msg": f"İşlem kuyruğu (Message Queue) yanıt vermeyi kesti. Kritik TC: {tc}"},
            {"level": "CRITICAL", "module": "CORE_ENGINE", "msg": f"Fiyat besleme (Price Feed) manipülasyonu algılandı! Şüpheli Hesap: {email}"},
            {"level": "CRITICAL", "module": "BACKUP_SYSTEM", "msg": f"Günlük borsa yedekleme (Backup) işlemi başarısız! Sistem yöneticisi TC: {tc}"},
            {"level": "CRITICAL", "module": "BACKUP_SYSTEM", "msg": "Felaket kurtarma (Disaster Recovery) sunucusu bağlantısı kesildi!"},
            {"level": "CRITICAL", "module": "BACKUP_SYSTEM", "msg": "Şifrelenmiş anahtar deposu (Vault) kilitlendi! Sistem geneli durma."},
            {"level": "CRITICAL", "module": "BACKUP_SYSTEM", "msg": f"Yedekleme diski salt okunur (Read-Only) moduna geçti. Etkilenen: {customer}"},
            {"level": "CRITICAL", "module": "BACKUP_SYSTEM", "msg": f"Ransomware şüphesi: Dosya sisteminde anormal değişim hızı! Sorumlu TC: {tc}"}
        ]
        
        all_logs = dropped_logs + processed_logs
        return random.choice(all_logs)

    def start_streaming(self):
        """Sürekli ve yüksek hızda log üreterek soketten gönderir (Stress Testi)."""
        if not self.sock:
            self.connect()

        print("Log akışı başlatıldı. Stres testi aktif...")
        try:
            while True:
                log_data = self.create_log_pool()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                
                log_string = f"[{timestamp}] [{log_data['level']}] [{log_data['module']}] -> {log_data['msg']}\n"
                self.sock.sendall(log_string.encode('utf-8'))
                time.sleep(0.001) 
                
        except (socket.error, BrokenPipeError):
            print("Ara katman bağlantısı koptu. Yeniden bağlanılıyor...")
            self.connect()
            self.start_streaming()

if __name__ == "__main__":
    generator = SingletonLogGenerator(host="middleware", port=5001)
    generator.start_streaming()