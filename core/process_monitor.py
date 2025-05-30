import psutil
import time
import json

class LiveProcessMonitor:
    def __init__(self):
        self.prev_snapshot = {}

    def get_process_snapshot(self):
        snapshot = {}
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                snapshot[proc.info['pid']] = {
                    "name": proc.info['name'],
                    "memory": proc.info['memory_info'].rss
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return snapshot

    def diff_snapshot(self, old, new):
        changes = []
        for pid, data in new.items():
            if pid not in old:
                changes.append({"event": "NEW", "pid": pid, "info": data})
            elif old[pid] != data:
                changes.append({"event": "CHANGED", "pid": pid, "info": data})
        for pid in old:
            if pid not in new:
                changes.append({"event": "TERMINATED", "pid": pid, "info": old[pid]})
        return changes

    def monitor_loop(self, interval=2):
        while True:
            current = self.get_process_snapshot()
            changes = self.diff_snapshot(self.prev_snapshot, current)
            if changes:
                print(json.dumps(changes, indent=2))
            self.prev_snapshot = current
            time.sleep(interval)
