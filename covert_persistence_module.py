import os
import sys
import time
import random
import psutil
import ctypes
from PyQt5.QtCore import QObject, pyqtSignal, QThread

from redsentrix_core.logger import Logger
from redsentrix_core.stealth_utils import StealthUtils, throttle_activity

logger = Logger()

class CovertPersistenceSignals(QObject):
    started = pyqtSignal(str)
    info = pyqtSignal(str)
    warning = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal()

class CovertPersistenceModule(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.signals = CovertPersistenceSignals()
        self._is_running = True

    def check_startup_tasks(self):
        # Dummy placeholder for actual startup persistence checks
        self.signals.info.emit("Checking startup tasks for persistence...")
        time.sleep(random.uniform(0.5, 1.0))

    def check_scheduled_jobs(self):
        self.signals.info.emit("Checking scheduled jobs (cron, at)...")
        time.sleep(random.uniform(0.5, 1.0))

    def check_dll_injection(self):
        self.signals.info.emit("Enumerating DLL injections for persistence...")
        time.sleep(random.uniform(0.5, 1.0))

    def check_registry(self):
        self.signals.info.emit("Checking Windows Registry persistence keys...")
        time.sleep(random.uniform(0.5, 1.0))

    def evade_detection(self):
        # Add anti-debugging, sandbox detection
        if StealthUtils.is_debugger_present():
            self.signals.warning.emit("Debugger detected during persistence scan. Aborting.")
            self._is_running = False

        if StealthUtils.sandbox_check():
            self.signals.warning.emit("Sandbox detected during persistence scan. Aborting.")
            self._is_running = False

    def run(self):
        self.signals.started.emit("Starting Covert Persistence Module scan...")

        self.evade_detection()
        if not self._is_running:
            self.signals.finished.emit()
            return

        throttle_activity()

        self.check_startup_tasks()
        if not self._is_running:
            self.signals.finished.emit()
            return

        self.check_scheduled_jobs()
        if not self._is_running:
            self.signals.finished.emit()
            return

        self.check_dll_injection()
        if not self._is_running:
            self.signals.finished.emit()
            return

        self.check_registry()

        self.signals.finished.emit()

    def stop(self):
        self._is_running = False
