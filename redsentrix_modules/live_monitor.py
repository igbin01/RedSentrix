import os
import time
import psutil
import hashlib
from threading import Thread
from modules.session_logger import secure_log

class LiveMonitor:
    def __init__(self, interval=5):
        self.interval = interval
        self.prev_snapshot = {}
        self.running = False

    def _get_proc_snapshot(self):
        snapshot = {}
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'memory_info']):
            try:
                pid = proc.info['pid']
                name = proc.info['name']
                mem = proc.info['memory_info'].rss
                cmdline = " ".join(proc.info['cmdline']) if proc.info['cmdline'] else ""
                exe_path = proc.info['exe'] or ""
                sig = self._hash_proc(exe_path)
                snapshot[pid] = {
                    "name": name,
                    "cmdline": cmdline,
                    "rss": mem,
                    "exe_hash": sig
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return snapshot

    def _hash_proc(self, exe_path):
        if not exe_path or not os.path.isfile(exe_path):
            return None
        try:
            with open(exe_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return None

    def _detect_anomalies(self, old, new):
        added = set(new.keys()) - set(old.keys())
        removed = set(old.keys()) - set(new.keys())
        changed = []

        for pid in set(old.keys()).intersection(set(new.keys())):
            if old[pid]["exe_hash"] != new[pid]["exe_hash"]:
                changed.append(pid)

        return added, removed, changed

    def start_monitoring(self):
        if self.running:
            return
        self.running = True

        def monitor_loop():
            self.prev_snapshot = self._get_proc_snapshot()
            while self.running:
                time.sleep(self.interval)
                current = self._get_proc_snapshot()
                added, removed, changed = self._detect_anomalies(self.prev_snapshot, current)

                for pid in added:
                    secure_log(f"New process detected: {current[pid]['name']} [{pid}]")

                for pid in removed:
                    secure_log(f"Process terminated: PID {pid}")

                for pid in changed:
                    secure_log(f"Executable changed in memory: PID {pid}, New hash: {current[pid]['exe_hash']}")

                self.prev_snapshot = current

        Thread(target=monitor_loop, daemon=True).start()

    def stop_monitoring(self):
        self.running = False
