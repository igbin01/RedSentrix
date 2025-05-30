import os
import time
import psutil
import threading
from modules.yara_autoloader import YARAAutoLoader
from modules.log_manager import log_threat

class MemoryMonitor:
    def __init__(self, interval=10):
        self.interval = interval  # seconds between scans
        self.monitoring = False
        self.yara_loader = YARAAutoLoader()
        self.rules = self.yara_loader.get_rules()
        self.monitor_thread = None

    def scan_process_memory(self, pid):
        try:
            with open(f"/proc/{pid}/mem", 'rb', 0) as mem:
                mem_data = mem.read()
                matches = self.rules.match(data=mem_data)
                return matches
        except Exception:
            return []

    def monitor_once(self):
        for proc in psutil.process_iter(['pid', 'name']):
            pid = proc.info['pid']
            pname = proc.info['name']
            matches = self.scan_process_memory(pid)
            if matches:
                for match in matches:
                    log_threat(
                        source="MemoryMonitor",
                        description=f"YARA match in process {pname} ({pid})",
                        details=match.rule,
                        severity="high"
                    )
                    print(f"[!] Match found: {match.rule} in PID {pid} ({pname})")

    def _monitor_loop(self):
        while self.monitoring:
            print("[*] Monitoring memory...")
            self.monitor_once()
            time.sleep(self.interval)

    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("[+] Memory monitoring started.")

    def stop_monitoring(self):
        if self.monitoring:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join()
            print("[+] Memory monitoring stopped.")

# Example usage
if __name__ == "__main__":
    monitor = MemoryMonitor(interval=15)
    monitor.start_monitoring()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop_monitoring()
