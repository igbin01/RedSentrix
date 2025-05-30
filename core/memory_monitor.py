import os
import re
import time
import psutil
import threading
from core.yara_engine import YaraEngine

class MemoryMonitor:
    def __init__(self, interval=10, stealth=True):
        self.interval = interval
        self.yara_engine = YaraEngine()
        self.stealth = stealth
        self._stop_event = threading.Event()

    def _get_memory_segments(self, pid):
        try:
            with open(f"/proc/{pid}/maps", "r") as maps_file:
                return [line.split()[0] for line in maps_file if "r" in line.split()[1]]
        except Exception:
            return []

    def _read_memory_segment(self, pid, segment_range):
        try:
            start, end = [int(x, 16) for x in segment_range.split("-")]
            with open(f"/proc/{pid}/mem", "rb", 0) as mem_file:
                mem_file.seek(start)
                return mem_file.read(end - start)
        except Exception:
            return b""

    def _scan_process(self, proc):
        pid = proc.pid
        segments = self._get_memory_segments(pid)
        for segment in segments:
            data = self._read_memory_segment(pid, segment)
            if data:
                matches = self.yara_engine.scan_buffer(data)
                if matches:
                    print(f"[!] YARA match in PID {pid} ({proc.name()}): {matches}")

    def start_monitoring(self):
        print("[*] Memory monitor started (press Ctrl+C to stop)")
        def monitor_loop():
            while not self._stop_event.is_set():
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        self._scan_process(proc)
                    except Exception:
                        continue
                time.sleep(self.interval)
        threading.Thread(target=monitor_loop, daemon=True).start()

    def stop_monitoring(self):
        self._stop_event.set()
        print("[*] Memory monitor stopped.")
