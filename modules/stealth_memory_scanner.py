import os
import psutil
import base64
import time
import random
import sys
import ctypes
import yara
from PyQt5.QtCore import QObject, pyqtSignal, QThread

from redsentrix_core.stealth_utils import StealthUtils, xor_encode, base64_encode, entropy_check, throttle_activity
from redsentrix_core.logger import Logger

logger = Logger()

class StealthMemoryScannerSignals(QObject):
    started = pyqtSignal(str)
    info = pyqtSignal(str)
    warning = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal()

class StealthMemoryScanner(QThread):
    def __init__(self, pattern=None, process_name=None, pid=None, encoding=None, key=None,
                 entropy_mode=False, yara_path=None, output_path=None, parent=None):
        super().__init__(parent)
        self.pattern = pattern
        self.process_name = process_name
        self.pid = pid
        self.encoding = encoding
        self.key = key.encode() if key else None
        self.entropy_mode = entropy_mode
        self.yara_path = yara_path
        self.output_path = output_path
        self.signals = StealthMemoryScannerSignals()
        self._is_running = True

    def find_process_pid(self, name):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == name:
                return proc.info['pid']
        return None

    def decode_pattern(self):
        try:
            raw_pattern = self.pattern.encode()
            if self.encoding == "xor":
                if not self.key:
                    raise ValueError("XOR encoding requires a key.")
                return xor_encode(raw_pattern, self.key)
            elif self.encoding == "base64":
                return base64.b64decode(self.pattern)
            return raw_pattern
        except Exception as e:
            self.signals.error.emit(f"Pattern decoding failed: {str(e)}")
            self._is_running = False

    def compile_yara(self):
        if not self.yara_path:
            return None
        try:
            return yara.compile(filepath=self.yara_path)
        except Exception as e:
            self.signals.error.emit(f"Failed to compile YARA rules: {e}")
            return None

    def scan_proc_mem(self, pid, pattern_bytes=None, yara_rules=None):
        mem_path = f"/proc/{pid}/mem"
        maps_path = f"/proc/{pid}/maps"

        if not os.path.exists(maps_path):
            self.signals.error.emit(f"Process {pid} does not exist or exited before scanning.")
            return

        try:
            with open(maps_path, 'r') as maps_file, open(mem_path, 'rb', 0) as mem_file:
                for line in maps_file:
                    if not self._is_running:
                        self.signals.info.emit("Stealth memory scan cancelled.")
                        break

                    parts = line.split()
                    if len(parts) < 2:
                        continue
                    address_range = parts[0]
                    perms = parts[1]

                    if 'r' not in perms or 'w' not in perms:
                        continue

                    start, end = [int(x, 16) for x in address_range.split('-')]

                    try:
                        mem_file.seek(start)
                        chunk = mem_file.read(end - start)

                        if self.entropy_mode:
                            ent = entropy_check(chunk)
                            if ent > 7.0:
                                self.signals.info.emit(f"High-entropy memory at 0x{start:x} (entropy={ent:.2f})")

                        # Pattern match
                        if pattern_bytes:
                            offset = chunk.find(pattern_bytes)
                            if offset != -1:
                                found_at = start + offset
                                encoded = base64.b64encode(chunk[offset:offset + len(pattern_bytes)]).decode()
                                msg = f"Pattern found at 0x{found_at:x} -> Encoded: {encoded}"
                                self.signals.info.emit(msg)
                                if self.output_path:
                                    with open(self.output_path, 'a') as f:
                                        f.write(msg + '\n')

                        # YARA match
                        if yara_rules:
                            matches = yara_rules.match(data=chunk)
                            for match in matches:
                                msg = f"YARA match '{match.rule}' at region 0x{start:x}-0x{end:x}"
                                self.signals.info.emit(msg)
                                if self.output_path:
                                    with open(self.output_path, 'a') as f:
                                        f.write(msg + '\n')

                        time.sleep(random.uniform(0.05, 0.1))
                    except Exception:
                        continue
        except FileNotFoundError:
            self.signals.error.emit(f"Process {pid} terminated during scanning.")
        except Exception as e:
            self.signals.error.emit(f"Failed reading memory: {e}")

    def spoof_name(self):
        try:
            libc = ctypes.cdll.LoadLibrary("libc.so.6")
            libc.prctl(15, b"[ksoftirqd/0]", 0, 0, 0)  # PR_SET_NAME
        except Exception:
            pass

    def run(self):
        self.spoof_name()
        self.signals.started.emit(f"Starting stealth memory scan for process '{self.process_name or self.pid}'...")

        if StealthUtils.is_debugger_present():
            self.signals.warning.emit("Debugger detected. Exiting for stealth.")
            return

        if StealthUtils.sandbox_check():
            self.signals.warning.emit("Sandbox environment detected. Exiting for stealth.")
            return

        throttle_activity()

        pid = self.pid or self.find_process_pid(self.process_name)
        if not pid:
            self.signals.error.emit("Target process not found.")
            return

        pattern_bytes = self.decode_pattern() if self.pattern else None
        if pattern_bytes is None and self.pattern:
            return  # Error emitted in decode_pattern

        yara_rules = self.compile_yara() if self.yara_path else None

        self.scan_proc_mem(pid, pattern_bytes, yara_rules)
        self.signals.finished.emit()

    def stop(self):
        self._is_running = False

# Entry point guard omitted for GUI integration
