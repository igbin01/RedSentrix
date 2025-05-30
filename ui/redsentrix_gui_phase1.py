import os
import sys
import psutil
import threading
import time
import yara
import base64
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTextEdit, QTabWidget, QTableWidget, QTableWidgetItem, QComboBox,
                             QLineEdit, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from datetime import datetime

class SignalEmitter(QObject):
    memory_scan_output = pyqtSignal(str)
    malware_behavior_output = pyqtSignal(str)
    persistence_output = pyqtSignal(str)
    process_monitor_update = pyqtSignal(list)
    scan_complete = pyqtSignal()

class SessionLogger:
    def __init__(self, session_file='session.log'):
        self.session_file = session_file
        self.encryption_key = "my_secret_key"

    def encrypt(self, data):
        return base64.b64encode(data.encode()).decode()

    def decrypt(self, data):
        return base64.b64decode(data.encode()).decode()

    def log(self, message):
        with open(self.session_file, 'a') as f:
            f.write(self.encrypt(f"[{datetime.now()}] {message}\n"))

    def load(self):
        if not os.path.exists(self.session_file):
            return []
        with open(self.session_file, 'r') as f:
            lines = f.readlines()
            return [self.decrypt(line.strip()) for line in lines]

class MemoryScanner(threading.Thread):
    def __init__(self, pid, yara_rules, signals):
        super().__init__()
        self.pid = pid
        self.yara_rules = yara_rules
        self.signals = signals
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        try:
            with open(f"/proc/{self.pid}/mem", 'rb', 0) as mem_file:
                matches = []
                while not self._stop_event.is_set():
                    mem_file.seek(0)
                    chunk = mem_file.read(8192)
                    if not chunk:
                        break
                    result = self.yara_rules.match(data=chunk)
                    if result:
                        matches.extend(result)
                        break
            for match in matches:
                self.signals.memory_scan_output.emit(f"YARA Match: {match.rule}")
        except Exception as e:
            self.signals.memory_scan_output.emit(f"Scan error: {e}")
        self.signals.scan_complete.emit()

class LiveProcessMonitor(threading.Thread):
    def __init__(self, signals):
        super().__init__()
        self.signals = signals
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            try:
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    processes.append(proc.info)
                self.signals.process_monitor_update.emit(processes)
                time.sleep(2)
            except Exception:
                continue

    def stop(self):
        self._stop_event.set()

if __name__ == "__main__":
    from redsentrix_gui_main import RedSentrixGUI
    app = QApplication(sys.argv)
    main_win = RedSentrixGUI()
    main_win.show()
    sys.exit(app.exec_())
