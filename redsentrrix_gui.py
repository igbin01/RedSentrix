import sys
import os
import datetime
import psutil
import yara
import base64
import threading
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextBrowser, QLineEdit, QFileDialog, QListWidget,
    QStackedWidget, QCheckBox, QMessageBox, QTextEdit, QFormLayout,
    QComboBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPalette, QColor

# --- Scanner Thread ---
class ScannerThread(QThread):
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(str)

    def __init__(self, pid, yara_path, log_path, hex_output):
        super().__init__()
        self.pid = pid
        self.yara_path = yara_path
        self.log_path = log_path
        self.hex_output = hex_output

    def run(self):
        def log(msg):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_signal.emit(f"{timestamp} [INFO] {msg}")

        try:
            rules = yara.compile(filepath=self.yara_path)
            log(f"YARA rules compiled from: {self.yara_path}")
        except Exception as e:
            self.log_signal.emit(f"[ERROR] Failed to compile YARA rules: {e}")
            return

        try:
            with open(f"/proc/{self.pid}/maps", 'r') as maps:
                regions = [line.split()[0] for line in maps if 'rw' in line.split()[1]]

            with open(f"/proc/{self.pid}/mem", 'rb', 0) as mem:
                for region in regions:
                    try:
                        start, end = [int(x, 16) for x in region.split('-')]
                        mem.seek(start)
                        chunk = mem.read(end - start)
                        matches = rules.match(data=chunk)
                        for match in matches:
                            msg = f"YARA match '{match.rule}' at region {hex(start)}-{hex(end)}"
                            log(msg)
                            encoded = base64.b64encode(msg.encode()).decode()
                            if self.hex_output:
                                hexdump = ' '.join(f"{b:02x}" for b in msg.encode())
                                self.result_signal.emit(hexdump)
                            else:
                                self.result_signal.emit(msg)
                            with open(self.log_path, 'a') as f:
                                f.write(encoded + "\n")
                    except (OSError, ValueError):
                        continue
        except Exception as e:
            self.log_signal.emit(f"[ERROR] Failed during scanning: {e}")

# --- Stealth Memory Scanner Tab ---
class StealthMemoryScannerTab(QWidget):
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.thread = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Process PID or Name:"))
        self.pid_input = QLineEdit()
        self.pid_input.setPlaceholderText("Enter PID or process name")
        layout.addWidget(self.pid_input)

        layout.addWidget(QLabel("YARA Rule File:"))
        h_rule = QHBoxLayout()
        self.rule_path = QLineEdit()
        self.rule_btn = QPushButton("Browse")
        self.rule_btn.clicked.connect(self.select_rule)
        h_rule.addWidget(self.rule_path)
        h_rule.addWidget(self.rule_btn)
        layout.addLayout(h_rule)

        layout.addWidget(QLabel("Log Output Path:"))
        h_log = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_btn = QPushButton("Browse")
        self.output_btn.clicked.connect(self.select_output)
        h_log.addWidget(self.output_path)
        h_log.addWidget(self.output_btn)
        layout.addLayout(h_log)

        self.hex_checkbox = QCheckBox("Hex-Dump Style Output")
        layout.addWidget(self.hex_checkbox)

        self.scan_btn = QPushButton("Start Scan")
        self.scan_btn.clicked.connect(self.start_scan)
        layout.addWidget(self.scan_btn)

        layout.addWidget(QLabel("Scan Output:"))
        self.output_box = QTextBrowser()
        self.output_box.setStyleSheet("background-color: #1e1e1e; color: #cfcfcf; font-family: Consolas, monospace;")
        self.output_box.setMinimumHeight(200)
        layout.addWidget(self.output_box)

        self.setLayout(layout)

    def select_rule(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select YARA Rule File", "", "YARA Files (*.yar *.yara)")
        if file:
            self.rule_path.setText(file)

    def select_output(self):
        file, _ = QFileDialog.getSaveFileName(self, "Select Output Log File", "encoded_result.txt", "Text Files (*.txt)")
        if file:
            self.output_path.setText(file)

    def start_scan(self):
        pid_or_name = self.pid_input.text().strip()
        pid = None

        if pid_or_name.isdigit():
            pid = int(pid_or_name)
        else:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == pid_or_name:
                    pid = proc.info['pid']
                    break

        if not pid:
            QMessageBox.critical(self, "Error", "Could not resolve process PID.")
            return

        rule_path = self.rule_path.text().strip()
        log_path = self.output_path.text().strip()

        if not os.path.exists(rule_path):
            QMessageBox.critical(self, "Error", "Invalid YARA rule path.")
            return

        if not log_path:
            QMessageBox.critical(self, "Error", "Please specify a log output path.")
            return

        self.output_box.clear()

        self.thread = ScannerThread(
            pid=pid,
            yara_path=rule_path,
            log_path=log_path,
            hex_output=self.hex_checkbox.isChecked()
        )
        self.thread.log_signal.connect(self.log_output)
        self.thread.result_signal.connect(self.log_output)
        self.thread.start()

    def log_output(self, message):
        self.output_box.append(message)
        self.log_signal.emit(message)

# --- Malware Behavior Generator Tab ---
class MalwareBehaviorGeneratorTab(QWidget):
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Enter malware behavior description keywords:"))
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("e.g., persistence, keylogging, privilege escalation")
        layout.addWidget(self.input_text)

        self.generate_btn = QPushButton("Generate Behavior Write-up")
        self.generate_btn.clicked.connect(self.generate_behavior)
        layout.addWidget(self.generate_btn)

        layout.addWidget(QLabel("Generated Malware Behavior Write-up:"))
        self.output_box = QTextBrowser()
        self.output_box.setStyleSheet("background-color: #222; color: #eee; font-family: Consolas, monospace;")
        self.output_box.setMinimumHeight(200)
        layout.addWidget(self.output_box)

        self.setLayout(layout)

    def generate_behavior(self):
        keywords = self.input_text.toPlainText().strip().lower()
        if not keywords:
            QMessageBox.warning(self, "Input needed", "Please enter some keywords.")
            return

        # Dummy behavior generation logic (replace with AI later)
        behavior = (
            f"Malware exhibits the following behaviors based on keywords: {keywords}.\n"
            f"It maintains persistence by establishing scheduled tasks or registry keys.\n"
            f"Capabilities may include keylogging, privilege escalation, and data exfiltration.\n"
            f"Further analysis required for exact behavior profiling."
        )

        self.output_box.setPlainText(behavior)
        self.log_signal.emit(f"Malware Behavior Generated with keywords: {keywords}")

# --- Covert Persistence Module Tab ---
class CovertPersistenceTab(QWidget):
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QFormLayout()

        self.techniques_combo = QComboBox()
        self.techniques_combo.addItems([
            "Windows Registry Run Key",
            "Scheduled Task",
            "Linux Cron Job",
            "DLL Injection (Placeholder)",
        ])
        layout.addRow(QLabel("Persistence Technique:"), self.techniques_combo)

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Target executable/script path")
        layout.addRow(QLabel("Target Path:"), self.target_input)

        self.add_btn = QPushButton("Add Persistence")
        self.add_btn.clicked.connect(self.add_persistence)
        layout.addRow(self.add_btn)

        self.remove_btn = QPushButton("Remove Persistence")
        self.remove_btn.clicked.connect(self.remove_persistence)
        layout.addRow(self.remove_btn)

        self.output_box = QTextBrowser()
        self.output_box.setStyleSheet("background-color: #222; color: #eee; font-family: Consolas, monospace;")
        self.output_box.setMinimumHeight(200)
        layout.addRow(QLabel("Output Log:"), self.output_box)

        self.setLayout(layout)

    def add_persistence(self):
        technique = self.techniques_combo.currentText()
        target = self.target_input.text().strip()
        if not target:
            QMessageBox.warning(self, "Input Error", "Please specify the target path.")
            return

        # For demo purposes, simulate persistence actions
        self.output_box.append(f"[INFO] Adding persistence via {technique} for target: {target}")
        self.log_signal.emit(f"Added persistence via {technique} for {target}")

    def remove_persistence(self):
        technique = self.techniques_combo.currentText()
        target = self.target_input.text().strip()
        if not target:
            QMessageBox.warning(self, "Input Error", "Please specify the target path.")
            return
        self.output_box.append(f"[INFO] Removing persistence via {technique} for target: {target}")
        self.log_signal.emit(f"Removed persistence via {technique} for {target}")

# --- RedOps Automation Tab ---
class RedOpsAutomationTab(QWidget):
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.thread = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Select Target Host/IP:"))
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter IP address or hostname")
        layout.addWidget(self.target_input)

        layout.addWidget(QLabel("Choose Attack Type:"))
        self.attack_combo = QComboBox()
        self.attack_combo.addItems([
            "Port Scan",
            "Vulnerability Scan",
            "Exploit Attempt",
            "Phishing Simulation"
        ])
        layout.addWidget(self.attack_combo)

        self.start_btn = QPushButton("Start RedOps Automation")
        self.start_btn.clicked.connect(self.start_redops)
        layout.addWidget(self.start_btn)

        layout.addWidget(QLabel("RedOps Automation Log:"))
        self.log_output = QTextBrowser()
        self.log_output.setStyleSheet("background-color: #111; color: #0f0; font-family: Consolas, monospace;")
        self.log_output.setMinimumHeight(200)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def start_redops(self):
        target = self.target_input.text().strip()
        attack_type = self.attack_combo.currentText()

        if not target:
            QMessageBox.warning(self, "Input Required", "Please enter a target host/IP.")
            return

        self.log_output.clear()
        self.log_output.append(f"[INFO] Starting {attack_type} on {target}...")
        self.log_signal.emit(f"RedOps started: {attack_type} on {target}")

        # Start thread to simulate redops
        self.thread = threading.Thread(target=self.redops_simulation, args=(target, attack_type), daemon=True)
        self.thread.start()

    def redops_simulation(self, target, attack_type):
        # Simulate multi-step red team automation
        steps = {
            "Port Scan": ["Scanning ports 1-1024...", "Open ports found: 22, 80, 443", "Port scan complete."],
            "Vulnerability Scan": ["Running vulnerability scan...", "Found CVE-2023-1234", "Scan complete."],
            "Exploit Attempt": ["Attempting exploit...", "Exploit successful!", "Payload executed."],
            "Phishing Simulation": ["Sending phishing email...", "Email delivered.", "No response yet."]
        }

        for step in steps.get(attack_type, []):
            time.sleep(2)
            self.log_output.append(step)

# --- Main Application Window ---
class RedSentrixMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RedSentrix Unified Framework")
        self.resize(900, 700)
        self.initUI()
        self.apply_dark_mode()

    def initUI(self):
        main_layout = QHBoxLayout(self)

        # Sidebar Buttons
        self.sidebar = QVBoxLayout()
        self.btn_scanner = QPushButton("Stealth Memory Scanner")
        self.btn_behavior = QPushButton("Malware Behavior Generator")
        self.btn_persistence = QPushButton("Covert Persistence Module")
        self.btn_redops = QPushButton("RedOps Automation")

        for btn in [self.btn_scanner, self.btn_behavior, self.btn_persistence, self.btn_redops]:
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            self.sidebar.addWidget(btn)

        self.btn_scanner.setChecked(True)  # Default

        self.sidebar.addStretch()

        main_layout.addLayout(self.sidebar, 1)

        # Stacked Widget for tabs
        self.stack = QStackedWidget()
        self.tab_scanner = StealthMemoryScannerTab()
        self.tab_behavior = MalwareBehaviorGeneratorTab()
        self.tab_persistence = CovertPersistenceTab()
        self.tab_redops = RedOpsAutomationTab()

        self.stack.addWidget(self.tab_scanner)
        self.stack.addWidget(self.tab_behavior)
        self.stack.addWidget(self.tab_persistence)
        self.stack.addWidget(self.tab_redops)

        main_layout.addWidget(self.stack, 4)

        # Connect sidebar buttons
        self.btn_scanner.clicked.connect(lambda: self.switch_tab(0))
        self.btn_behavior.clicked.connect(lambda: self.switch_tab(1))
        self.btn_persistence.clicked.connect(lambda: self.switch_tab(2))
        self.btn_redops.clicked.connect(lambda: self.switch_tab(3))

        # Sync logging from all tabs
        for tab in [self.tab_scanner, self.tab_behavior, self.tab_persistence, self.tab_redops]:
            tab.log_signal.connect(self.log_global)

        # Global log box
        self.global_log = QTextBrowser()
        self.global_log.setStyleSheet("background-color: #000; color: #0f0; font-family: Consolas, monospace;")
        self.global_log.setMaximumHeight(150)
        main_layout.addWidget(self.global_log, 2)

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        # Update button checked states
        for i, btn in enumerate([self.btn_scanner, self.btn_behavior, self.btn_persistence, self.btn_redops]):
            btn.setChecked(i == index)

    def log_global(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.global_log.append(f"{timestamp} {message}")

    def apply_dark_mode(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(18, 18, 18))
        palette.setColor(QPalette.WindowText, QColor(200, 200, 200))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(200, 200, 200))
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, QColor(200, 200, 200))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(200, 200, 200))
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

def main():
    app = QApplication(sys.argv)
    window = RedSentrixMainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
