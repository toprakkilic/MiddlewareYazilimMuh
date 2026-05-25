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
        """Simülasyon için sahte KVKK verileri üretir."""
        tc = "".join([str(random.randint(0, 9)) for _ in range(11)])
        email = f"user{random.randint(100, 999)}@borsatr.com"
        card = "-".join(["".join([str(random.randint(0, 9)) for _ in range(4)]) for _ in range(4)])
        return tc, email, card

    def create_log_pool(self):
        """Hocanın istediği tüm varyasyonları içeren log havuzu."""
        tc, email, card = self.generate_random_kvkk()
        
        # Farklı modüller, seviyeler ve mesajlar
        logs = [
            # 1. Performans Filtresine Takılacak Önemsiz Loglar (INFO, WARNING, ACCESS)
            {"level": "INFO", "module": "AUTH", "msg": f"Kullanıcı sisteme istek gönderdi. IP: 192.168.1.10"},
            {"level": "WARNING", "module": "WALLET", "msg": f"Yetersiz bakiye denemesi. Kullanıcı E-posta: {email}"},
            {"level": "INFO", "module": "ACCESS_LOG", "msg": "GET /api/v1/market/status HTTP/1.1 200 OK"},
            {"level": "WARNING", "module": "DOCKER_INTERNAL", "msg": "Container CPU usage reached 75%"},
            
            # 2. Ara Katmanın Kesinlikle İşlemesi Gereken Önemli Loglar (ERROR, CRITICAL)
            {"level": "ERROR", "module": "TRANSACTION", "msg": f"Para çekme işlemi başarısız oldu. TC: {tc}, Miktar: 50000 TL"},
            {"level": "CRITICAL", "module": "SECURITY", "msg": f"Şüpheli üst üste hatalı işlem! Kart No: {card}, E-posta: {email}"},
            {"level": "ERROR", "module": "DATABASE", "msg": f"Bağlantı zaman aşımına uğradı. Sorgu sahibi TC: {tc}"},
            {"level": "CRITICAL", "module": "CORE_ENGINE", "msg": "Borsa eşleştirme motoru beklenmedik şekilde durdu! PANIC."},
            {"level": "ERROR", "module": "API_GATEWAY", "msg": f"Webhook entegrasyon hatası. Sağlayıcı maili: {email}"}
        ]
        return random.choice(logs)

    def start_streaming(self):
        """Sürekli ve yüksek hızda log üreterek soketten gönderir (Stress Testi)."""
        if not self.sock:
            self.connect()

        print("Log akışı başlatıldı. Stres testi aktif...")
        try:
            while True:
                log_data = self.create_log_pool()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                
                # Ham log string formatı (Bunu middleware ayrıştıracak)
                log_string = f"[{timestamp}] [{log_data['level']}] [{log_data['module']}] -> {log_data['msg']}\n"
                
                # Soket üzerinden gönderim
                self.sock.sendall(log_string.encode('utf-8'))
                
                # Stres testi için bekleme süresini çok küçük tutuyoruz (Saniyede binlerce log)
                time.sleep(0.001) 
                
        except (socket.error, BrokenPipeError):
            print("Ara katman bağlantısı koptu. Yeniden bağlanılıyor...")
            self.connect()
            self.start_streaming()

if __name__ == "__main__":
    # Singleton nesnesi oluşturuluyor ve süreç başlatılıyor
    generator = SingletonLogGenerator(host="middleware", port=5001)
    generator.start_streaming()
