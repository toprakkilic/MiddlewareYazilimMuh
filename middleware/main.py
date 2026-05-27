import socket
import re
import json
import os
import time
from datetime import datetime
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
        # Geliştiriciler için ekstra izlenebilirlik alanı ekleme
        log_entry["enrichment"]["role_tag"] = "[DEV_INFO]"
        return json.dumps(log_entry, ensure_ascii=False) + "\n"

class CSVFormatter(LogFormatterStrategy):
    """Cyber Security Rolü için çıktı stratejisi"""
    def format_log(self, log_entry: dict) -> str:
        # Güvenlikçiler için virgülle ayrılmış temiz denetim formatı
        enrich = log_entry["enrichment"]
        role_tag = "[SECURITY_ALERT]" if log_entry["level"] == "CRITICAL" else "[SECURITY_AUDIT]"
        return f"{log_entry['timestamp']},{role_tag},{log_entry['level']},{log_entry['module']},{log_entry['message']},{enrich['transaction_no']}\n"

class HTMLFormatter(LogFormatterStrategy):
    """System Admin Rolü için çıktı stratejisi (Önem Derecesine Göre Vurgulama)"""
    def format_log(self, log_entry: dict) -> str:
        # Önem derecesine göre satır bazlı renklendirme (Highlighting)
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
        
        # İşletim sisteminden (Docker ortam değişkeninden) çalışma modunu okuyoruz
        # Eğer compose dosyasında "true" verilirse performans ölçüm ekranı aktifleşir
        self.perf_test_enabled = os.getenv("PERFORMANCE_TEST", "false").lower() == "true"
        
        # Stres testi performans ölçüm metrikleri
        self.total_received = 0
        self.total_processed = 0
        self.start_time = time.time()

        # Raporların üretildiği günün tarih damgası (Format: YYYY-MM-DD)
        self.date_str = datetime.now().strftime("%Y-%m-%d")

        # Çıktı klasörünü güvenli bir şekilde oluştur
        os.makedirs("output_logs", exist_ok=True)
        self.init_files()

        # Dinamik Tarihli Strateji Dosya Yapılandırması
        self.strategies = {
            "webdev": (JSONFormatter(), f"output_logs/webdev_{self.date_str}.json"),
            "cybersec": (CSVFormatter(), f"output_logs/cybersec_{self.date_str}.csv"),
            "sysadmin": (HTMLFormatter(), f"output_logs/sysadmin_{self.date_str}.html")
        }

    def load_mask_config(self):
        with open(self.config_path, "r") as f:
            return json.load(f)

    def init_files(self):
        # 1. HTML Başlığı (Eğer dosya yoksa sıfırdan tablo şablonuyla yazar)
        html_file = f"output_logs/sysadmin_{self.date_str}.html"
        if not os.path.exists(html_file):
            with open(html_file, "w") as f:
                f.write(f"<html><head><title>System Admin Logs - {self.date_str}</title></head><body><h2>System Admin Log Dashboard ({self.date_str})</h2><table border='1' cellpadding='5' cellspacing='0'>")
        
        # 2. CSV Başlığı (Eğer dosya yoksa kolon adlarını yazar)
        csv_file = f"output_logs/cybersec_{self.date_str}.csv"
        if not os.path.exists(csv_file):
            with open(csv_file, "w") as f:
                f.write("timestamp,role_tag,level,module,message,transaction_no\n")

        # 3. Elenen Ham Sistem Logları Dosyası
        dropped_file = f"output_logs/dropped_system_{self.date_str}.log"
        if not os.path.exists(dropped_file):
            with open(dropped_file, "w") as f:
                f.write("")

    def anonymize_text(self, text, rule):
        """Metin içerisindeki hassas verileri akıllıca karakter karakter yıldızlar."""
        # 1. E-posta Maskeleme Lojistiği (Örn: toprak@borsatr.com -> t*****@borsatr.com)
        if rule.get("is_email", False):
            def email_replacer(match):
                username, domain = match.groups()
                masked_user = username[0] + (rule["mask_char"] * (len(username) - 1))
                return f"{masked_user}@{domain}"
            return re.sub(rule["regex_pattern"], email_replacer, text)

        # 2. İsim Soyisim Maskeleme Lojistiği (Örn: Abdullah Kılıç -> A******* K****)
        if rule.get("is_name", False):
            def name_replacer(match):
                name, surname = match.groups()
                masked_name = name[0] + (rule["mask_char"] * (len(name) - 1))
                masked_surname = surname[0] + (rule["mask_char"] * (len(surname) - 1))
                return f"Müşteri: {masked_name} {masked_surname}"
            return re.sub(rule["regex_pattern"], name_replacer, text)

        # 3. Genel Kural/TC/Kredi Kartı Maskeleme (Başı ve sonu korur, araları yıldızlar)
        keep = rule.get("keep_fields", {"start": 0, "end": 0})
        def generic_replacer(match):
            val = match.group(0)
            if len(val) <= (keep["start"] + keep["end"]):
                return rule["mask_char"] * len(val)
            
            start_chars = val[:keep["start"]]
            end_chars = val[-keep["end"]:] if keep["end"] > 0 else ""
            middle_masked = rule["mask_char"] * (len(val) - keep["start"] - keep["end"])
            return f"{start_chars}{middle_masked}{end_chars}"
            
        return re.sub(rule["regex_pattern"], generic_replacer, text)

    def process_raw_string(self, raw_log: str):
        # Eğer performans testi modu (Feature Toggle) açıksa sayaçları artır ve saniyede bir ekrana bas
        if self.perf_test_enabled:
            self.total_received += 1
            current_time = time.time()
            if current_time - self.start_time >= 1.0:
                throughput = self.total_received / (current_time - self.start_time)
                print(f"[PERFORMANS ÖLÇÜMÜ] Gelen Toplam Log: {self.total_received} | İşlenen (Önemli): {self.total_processed} | Saniye Başına İşlem (Throughput): {throughput:.2f} log/sn")
                self.total_received = 0
                self.total_processed = 0
                self.start_time = current_time

        # Regex ile ham log satırını ayrıştırma
        pattern = r"\[(.*?)\]\s+\[(.*?)\]\s+\[(.*?)\]\s+->\s+(.*)"
        match = re.match(pattern, raw_log.strip())
        if not match:
            return

        timestamp, level, module, message = match.groups()

        # Gün döngüsü kontrolü (Gece 00:00'ı geçince otomatik yeni tarihli dosyalara bağlanır)
        current_date = datetime.now().strftime("%Y-%m-%d")
        if current_date != self.date_str:
            self.date_str = current_date
            self.init_files()
            self.strategies = {
                "webdev": (JSONFormatter(), f"output_logs/webdev_{self.date_str}.json"),
                "cybersec": (CSVFormatter(), f"output_logs/cybersec_{self.date_str}.csv"),
                "sysadmin": (HTMLFormatter(), f"output_logs/sysadmin_{self.date_str}.html")
            }

        # -------------------------------------------------------------
        # FILTER 1: Performans Filtresi (Önemsiz logları ayırır ve ham olarak kaydeder)
        # -------------------------------------------------------------
        if level in ["INFO", "WARNING"] or module in ["ACCESS_LOG", "DOCKER_INTERNAL"]:
            dropped_file = f"output_logs/dropped_system_{self.date_str}.log"
            with open(dropped_file, "a") as f:
                f.write(raw_log.strip() + "\n")
            return

        # Sadece performans modu açıksa tam işleme tabi tutulan log sayacını güncelle
        if self.perf_test_enabled:
            self.total_processed += 1
            
        self.tx_counter += 1

        # -------------------------------------------------------------
        # FILTER 2: KVKK Filtresi (Akıllı Dinamik Karakter Yıldızlama)
        # -------------------------------------------------------------
        clean_message = message
        if self.mask_config.get("masking_enabled", True):
            for rule in self.mask_config.get("rules", []):
                clean_message = self.anonymize_text(clean_message, rule)

        # -------------------------------------------------------------
        # FILTER 3: Zenginleştirme (Microservices Enrichment)
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