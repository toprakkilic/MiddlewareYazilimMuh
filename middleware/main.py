import socket
import re
import json
import os
import time
from abc import ABC, abstractmethod

# =====================================================================
# STRATEGY DESIGN PATTERN (Biçimlendirme & Rol Yönetimi)
# =====================================================================

class LogFormatterStrategy(ABC):
    @abstractmethod
    def format_log(self, log_entry: dict) -> str:
        pass

class JSONFormatter(LogFormatterStrategy):
    """Web Developer Rolü için çıktı stratejisi"""
    def format_log(self, log_entry: dict) -> str:
        # Geliştiriciler için ekstra debug/izlenebilirlik alanı ekleme
        log_entry["enrichment"]["role_tag"] = "[DEV_INFO]"
        return json.dumps(log_entry, ensure_ascii=False) + "\n"

class CSVFormatter(LogFormatterStrategy):
    """Cyber Security Rolü için çıktı stratejisi"""
    def format_log(self, log_entry: dict) -> str:
        # Güvenlikçiler için virgülle ayrılmış temiz alert formatı
        enrich = log_entry["enrichment"]
        role_tag = "[SECURITY_ALERT]" if log_entry["level"] == "CRITICAL" else "[SECURITY_AUDIT]"
        return f"{log_entry['timestamp']},{role_tag},{log_entry['level']},{log_entry['module']},{log_entry['message']},{enrich['transaction_no']}\n"

class HTMLFormatter(LogFormatterStrategy):
    """System Admin Rolü için çıktı stratejisi (Önem Derecesine Göre Vurgulama)"""
    def format_log(self, log_entry: dict) -> str:
        # Hocanın istediği 'vurgulama (highlighting)' mekanizması
        bg_color = "#ffffff"  # Varsayılan beyaz
        text_color = "#000000"
        
        if log_entry["level"] == "CRITICAL":
            bg_color = "#ffcccc"  # Açık Kırmızı Vurgu
            text_color = "#990000"
        elif log_entry["level"] == "ERROR":
            bg_color = "#fff0b3"  # Açık Sarı Vurgu
            text_color = "#b38600"

        enrich = log_entry["enrichment"]
        return f"<tr style='background-color: {bg_color}; color: {text_color}; font-family: monospace;'>" \
               f"<td>[{log_entry['timestamp']}]</td><td><b>[{log_entry['level']}]</b></td>" \
               f"<td>({log_entry['module']})</td><td>TX:{enrich['transaction_no']}</td>" \
               f"<td>-> {log_entry['message']}</td></tr>\n"


# =====================================================================
# PIPE AND FILTER ARCHITECTURE (Veri İşleme Hattı)
# =====================================================================

class LogPipeline:
    def __init__(self, config_path="mask_config.json"):
        self.tx_counter = 0
        self.config_path = config_path
        self.mask_config = self.load_mask_config()
        
        # Stres testi performans ölçüm metrikleri
        self.total_received = 0
        self.total_processed = 0
        self.start_time = time.time()

        # Rol dosyalarını temiz olarak başlatalım
        os.makedirs("output_logs", exist_ok=True)
        self.init_files()

        # Stratejileri tanımlayalım
        self.strategies = {
            "webdev": (JSONFormatter(), "output_logs/webdev.json"),
            "cybersec": (CSVFormatter(), "output_logs/cybersec.csv"),
            "sysadmin": (HTMLFormatter(), "output_logs/sysadmin.html")
        }

    def load_mask_config(self):
        with open(self.config_path, "r") as f:
            return json.load(f)

    def init_files(self):
        # HTML dosyasının tablosunu açalım
        with open("output_logs/sysadmin.html", "w") as f:
            f.write("<html><head><title>System Admin Logs</title></head><body><h2>System Admin Log Dashboard</h2><table border='1' cellpadding='5' cellspacing='0'>")
        # CSV dosyasının başlıklarını yazalım
        with open("output_logs/cybersec.csv", "w") as f:
            f.write("timestamp,role_tag,level,module,message,transaction_no\n")
        # JSON dosyasını boşaltalım
        with open("output_logs/webdev.json", "w") as f:
            f.write("")

    def process_raw_string(self, raw_log: str):
        self.total_received += 1
        
        # Saniyede bir performans raporu basalım (Hocanın istediği Stres Testi ölçümü)
        current_time = time.time()
        if current_time - self.start_time >= 1.0:
            throughput = self.total_received / (current_time - self.start_time)
            print(f"[PERFORMANS ÖLÇÜMÜ] Gelen Toplam Log: {self.total_received} | İşlenen (Önemli): {self.total_processed} | Saniye Başına İşlem (Throughput): {throughput:.2f} log/sn")
            # Metrikleri sıfırla
            self.total_received = 0
            self.total_processed = 0
            self.start_time = current_time

        # Regex ile log satırını ayrıştırma
        # Örnek format: [2026-05-25 12:00:00.123] [INFO] [AUTH] -> Mesaj içeriği
        pattern = r"\[(.*?)\]\s+\[(.*?)\]\s+\[(.*?)\]\s+->\s+(.*)"
        match = re.match(pattern, raw_log.strip())
        if not match:
            return

        timestamp, level, module, message = match.groups()

        # -------------------------------------------------------------
        # FILTER 1: Performans Filtresi (Gereksiz logları eleme)
        # -------------------------------------------------------------
        if level in ["INFO", "WARNING"] or module in ["ACCESS_LOG", "DOCKER_INTERNAL"]:
            # Önemli olmayan logları doğrudan çöpe atıyoruz, kaynak tüketmiyoruz
            return

        self.total_processed += 1
        self.tx_counter += 1

        # -------------------------------------------------------------
        # FILTER 2: KVKK Filtresi (Dinamik Anonimleştirme)
        # -------------------------------------------------------------
        clean_message = message
        if self.mask_config.get("masking_enabled", True):
            for rule in self.mask_config.get("rules", []):
                regex_pat = rule["regex_pattern"]
                
                # Eşleşen KVKK verisini bulalım
                for found in re.finditer(regex_pat, clean_message):
                    full_match = found.group(0)
                    # Sadece yakalanmak istenen hassas kısmı maskeleyelim
                    # Karmaşık maskeleme lojistiği yerine basitçe [GİZLENDİ] formatına çekiyoruz
                    clean_message = clean_message.replace(full_match, f"{full_match[:10]}... [KVKK GİZLENDİ]")

        # -------------------------------------------------------------
        # FILTER 3: Zenginleştirme (Enrichment)
        # -------------------------------------------------------------
        log_obj = {
            "timestamp": timestamp,
            "level": level,
            "module": module,
            "message": clean_message,
            "enrichment": {
                "transaction_no": f"TX-{100000 + self.tx_counter}",
                "processed_by_middleware_version": "v1.2.0"
            }
        }

        # -------------------------------------------------------------
        # FILTER 4: Biçimlendirme & Dağıtım (Strategy Pattern)
        # -------------------------------------------------------------
        for role, (strategy, file_path) in self.strategies.items():
            formatted_output = strategy.format_log(log_obj)
            
            # Veritabanı yerine hocanın istediği gibi dosyaya yazıyoruz
            with open(file_path, "a") as f:
                f.write(formatted_output)


# =====================================================================
# TCP SOCKET SERVER (Mimarî Strateji: Client-Server)
# =====================================================================

def start_middleware_server():
    pipeline = LogPipeline()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", 5001))
    server_socket.listen(1)
    
    print("[MİMARİ] Ara Katman TCP Sunucusu 5001 portunda dinlemede...")
    
    while True:
        client_conn, client_addr = server_socket.accept()
        print(f"[BAĞLANTI] Data Generator bağlandı: {client_addr}")
        
        buffer = ""
        try:
            while True:
                data = client_conn.recv(4096).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line:
                        pipeline.process_raw_string(line)
        except ConnectionResetError:
            print("[UYARI] Data Generator bağlantısı kesildi.")
        finally:
            client_conn.close()

if __name__ == "__main__":
    start_middleware_server()
