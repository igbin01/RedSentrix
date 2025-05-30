import sys
import os
from PyQt5.QtWidgets import QApplication
from ui.components import RedSentrixMainWindow
from core.threat_feed import auto_update_yara_rules

if __name__ == "__main__":
    # Ensure required directories exist
    os.makedirs("data/logs", exist_ok=True)

    # Auto-update YARA threat feeds
    auto_update_yara_rules()

    # Start the GUI
    app = QApplication(sys.argv)
    window = RedSentrixMainWindow()
    window.show()
    sys.exit(app.exec_())
