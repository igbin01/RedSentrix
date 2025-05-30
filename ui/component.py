from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QAction, QMenuBar, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from ui.themes import apply_dark_theme, apply_light_theme
from core.memory_scanner import MemoryScannerWidget
from core.process_monitor import ProcessMonitorWidget
from core.behavior_engine import BehaviorEngineWidget
from core.persistence_engine import PersistenceEngineWidget
from core.logger import LogViewerWidget
from core.plugin_engine import PluginLoaderWidget
from core.threat_feed import ThreatFeedStatusWidget


class RedSentrixMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RedSentrix - Unified ThreatOps Console")
        self.setGeometry(200, 100, 1200, 800)
        self.setWindowIcon(QIcon("assets/icon.png"))

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)

        self.setCentralWidget(self.tabs)
        self._create_tabs()
        self._create_menubar()

        self.current_theme = "dark"
        apply_dark_theme(self)

    def _create_tabs(self):
        self.tabs.addTab(MemoryScannerWidget(), "Memory Scanner")
        self.tabs.addTab(ProcessMonitorWidget(), "Live Monitoring")
        self.tabs.addTab(BehaviorEngineWidget(), "Malware Behavior")
        self.tabs.addTab(PersistenceEngineWidget(), "Persistence")
        self.tabs.addTab(LogViewerWidget(), "Session Logs")
        self.tabs.addTab(ThreatFeedStatusWidget(), "Threat Feed")
        self.tabs.addTab(PluginLoaderWidget(), "Add-on Modules")

    def _create_menubar(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        view_menu = menubar.addMenu("View")
        theme_toggle = QAction("Toggle Theme", self)
        theme_toggle.triggered.connect(self._toggle_theme)
        view_menu.addAction(theme_toggle)

        help_menu = menubar.addMenu("Help")
        about_action = QAction("About RedSentrix", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _toggle_theme(self):
        if self.current_theme == "dark":
            apply_light_theme(self)
            self.current_theme = "light"
        else:
            apply_dark_theme(self)
            self.current_theme = "dark"

    def _show_about(self):
        QMessageBox.information(
            self,
            "About RedSentrix",
            "RedSentrix Unified Threat Console\nPhase 1–4 MVP (Excludes AI/ML).\nBuilt for advanced offensive & defensive threat ops."
        )
