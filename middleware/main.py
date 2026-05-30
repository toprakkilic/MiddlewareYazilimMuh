import socket
import re
import json
import os
import time
from datetime import datetime
from abc import ABC, abstractmethod


class LogFormatterStrategy(ABC):
    @abstractmethod
    def format_log(self, log_entry: dict) -> str:
        pass

class JSONFormatter(LogFormatterStrategy):
    """Web Developer Rolü için çıktı stratejisi"""
    def format_log(self, log_entry: dict) -> str:
        log_entry["enrichment"]["role_tag"] = "[DEV_INFO]"
        return json.dumps(log_entry, ensure_ascii=False) + "\n"

class CSVFormatter(LogFormatterStrategy):
    """Cyber Security Rolü için çıktı stratejisi"""
    def format_log(self, log_entry: dict) -> str:
        enrich = log_entry["enrichment"]
        role_tag = "[SECURITY_ALERT]" if log_entry["level"] == "CRITICAL" else "[SECURITY_AUDIT]"
        return f"{log_entry['timestamp']},{role_tag},{log_entry['level']},{log_entry['module']},{log_entry['message']},{enrich['transaction_no']}\n"

class HTMLFormatter(LogFormatterStrategy):
    """System Admin Rolü için çıktı stratejisi (Önem Derecesine Göre Vurgulama)"""
    def format_log(self, log_entry: dict) -> str:
        bg_color = "#ffffff" 
        text_color = "#000000"
        
        if log_entry["level"] == "CRITICAL":
            bg_color = "#ffcccc"
            text_color = "#990000"
        elif log_entry["level"] == "ERROR":
            bg_color = "#fff0b3" 
            text_color = "#b38600"

        enrich = log_entry["enrichment"]
        return f"<tr style='background-color: {bg_color}; color: {text_color}; font-family: monospace;'>" \
               f"<td>[{log_entry['timestamp']}]</td><td><b>[{log_entry['level']}]</b></td>" \
               f"<td>({log_entry['module']})</td><td>TX:{enrich['transaction_no']}</td>" \
               f"<td>-> {log_entry['message']}</td></tr>\n"


class LogPipeline:
    def __init__(self, config_path="mask_config.json"):
        self.tx_counter = 0
        self.config_path = config_path
        self.mask_config = self.load_mask_config()
        
        self.perf_test_enabled = os.getenv("PERFORMANCE_TEST", "false").lower() == "true"
        
        self.total_received = 0
        self.total_processed = 0
        self.start_time = time.time()

        self.date_str = datetime.now().strftime("%Y-%m-%d")

        os.makedirs("output_logs", exist_ok=True)
        self.init_files()

        self.strategies = {
            "webdev": (JSONFormatter(), f"output_logs/webdev_{self.date_str}.json"),
            "cybersec": (CSVFormatter(), f"output_logs/cybersec_{self.date_str}.csv"),
            "sysadmin": (HTMLFormatter(), f"output_logs/sysadmin_{self.date_str}.html")
        }

    def load_mask_config(self):
        with open(self.config_path, "r") as f:
            return json.load(f)

    def init_files(self):
        html_file = f"output_logs/sysadmin_{self.date_str}.html"
        if not os.path.exists(html_file):
            with open(html_file, "w") as f:
                f.write(f"<html><head><title>System Admin Logs - {self.date_str}</title></head><body><h2>System Admin Log Dashboard ({self.date_str})</h2><table border='1' cellpadding='5' cellspacing='0'>")
        
        csv_file = f"output_logs/cybersec_{self.date_str}.csv"
        if not os.path.exists(csv_file):
            with open(csv_file, "w") as f:
                f.write("timestamp,role_tag,level,module,message,transaction_no\n")

        dropped_file = f"output_logs/dropped_system_{self.date_str}.log"
        if not os.path.exists(dropped_file):
            with open(dropped_file, "w") as f:
                f.write("")

    def anonymize_text(self, text, rule):
        """Metin içerisindeki hassas verileri akıllıca karakter karakter yıldızlar."""
        if rule.get("is_email", False):
            def email_replacer(match):
                username, domain = match.groups()
                masked_user = username[0] + (rule["mask_char"] * (len(username) - 1))
                return f"{masked_user}@{domain}"
            return re.sub(rule["regex_pattern"], email_replacer, text)

        if rule.get("is_name", False):
            def name_replacer(match):
                name, surname = match.groups()
                masked_name = name[0] + (rule["mask_char"] * (len(name) - 1))
                masked_surname = surname[0] + (rule["mask_char"] * (len(surname) - 1))
                return f"Müşteri: {masked_name} {masked_surname}"
            return re.sub(rule["regex_pattern"], name_replacer, text)

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
        if self.perf_test_enabled:
            self.total_received += 1
            current_time = time.time()
            if current_time - self.start_time >= 1.0:
                throughput = self.total_received / (current_time - self.start_time)
                print(f"[PERFORMANS ÖLÇÜMÜ] Gelen Toplam Log: {self.total_received} | İşlenen (Önemli): {self.total_processed} | Saniye Başına İşlem (Throughput): {throughput:.2f} log/sn")
                self.total_received = 0
                self.total_processed = 0
                self.start_time = current_time

        pattern = r"\[(.*?)\]\s+\[(.*?)\]\s+\[(.*?)\]\s+->\s+(.*)"
        match = re.match(pattern, raw_log.strip())
        if not match:
            return

        timestamp, level, module, message = match.groups()

        current_date = datetime.now().strftime("%Y-%m-%d")
        if current_date != self.date_str:
            self.date_str = current_date
            self.init_files()
            self.strategies = {
                "webdev": (JSONFormatter(), f"output_logs/webdev_{self.date_str}.json"),
                "cybersec": (CSVFormatter(), f"output_logs/cybersec_{self.date_str}.csv"),
                "sysadmin": (HTMLFormatter(), f"output_logs/sysadmin_{self.date_str}.html")
            }

        if level in ["INFO", "WARNING"] or module in ["ACCESS_LOG", "DOCKER_INTERNAL"]:
            dropped_file = f"output_logs/dropped_system_{self.date_str}.log"
            with open(dropped_file, "a") as f:
                f.write(raw_log.strip() + "\n")
            return

        if self.perf_test_enabled:
            self.total_processed += 1
            
        self.tx_counter += 1

        clean_message = message
        if self.mask_config.get("masking_enabled", True):
            for rule in self.mask_config.get("rules", []):
                clean_message = self.anonymize_text(clean_message, rule)

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