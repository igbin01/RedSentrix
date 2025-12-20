# Add this to your RedSentrix GUI (e.g., in redsentrix_gui.py)

from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit, QWidget
import subprocess

class PersistenceTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Select payload to persist:")
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        self.select_button = QPushButton("Browse Payload")
        self.select_button.clicked.connect(self.browse_payload)

        self.run_button = QPushButton("Deploy Covert Persistence")
        self.run_button.clicked.connect(self.run_persistence)

        layout.addWidget(self.label)
        layout.addWidget(self.select_button)
        layout.addWidget(self.run_button)
        layout.addWidget(self.output)

        self.setLayout(layout)
        self.payload_path = ""

    def browse_payload(self):
        file_dialog = QFileDialog()
        path, _ = file_dialog.getOpenFileName(self, "Select Payload")
        if path:
            self.payload_path = path
            self.label.setText(f"Payload: {path}")

    def run_persistence(self):
        if not self.payload_path:
            self.output.append("[!] No payload selected.")
            return
        try:
            process = subprocess.Popen(["python3", "modules/covert_persistence_module.py", self.payload_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            self.output.append(stdout.decode())
            if stderr:
                self.output.append("[!] Error:\n" + stderr.decode())
        except Exception as e:
            self.output.append(f"[!] Exception: {e}")

# --- Add this snippet in your main RedSentrix GUI setup to add the tab ---
# from persistence_gui_integration import PersistenceTab  # make sure the import path matches
# persistence_tab = PersistenceTab()
# tabs.addTab(persistence_tab, "Persistence")
