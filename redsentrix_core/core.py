from redsentrix_core.logger import StealthLogger
import os
import importlib
import logging
import sys
from datetime import datetime
from .loader import load_module
from .evasion import check_environment

class NebulaCore:
    def __init__(self):
        self.modules = {}  # Dictionary to store loaded modules
        self.logger = StealthLogger()

    def setup_logger(self):
        """Set up the stealth logger (optional override)."""
        logger = logging.getLogger('NebulaCoreLogger')
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()  # Change to FileHandler if needed
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

    def load_module(self, name):
        """Dynamically load a module from the 'modules' directory."""
        try:
            mod = importlib.import_module(f"modules.{name}")
            self.modules[name] = mod
            self.logger.log(name, "Module loaded successfully.")
        except ImportError as e:
            self.logger.log(name, f"Failed to load module. {e}")
            print(f"[!] Module '{name}' could not be loaded.")

    def execute_module(self, name):
        """Execute a previously loaded module."""
        if name in self.modules:
            try:
                self.modules[name].run()
                self.logger.log(name, "Module executed successfully.")
            except Exception as e:
                self.logger.log(name, f"Execution failed: {str(e)}")
        else:
            print(f"[!] Module '{name}' not loaded.")

    def check_evasion(self):
        """Perform anti-analysis/environmental checks."""
        print("Performing environment checks...")
        if check_environment():
            print("Environment is safe for execution.")
        else:
            print("Suspicious environment detected. Exiting.")
            sys.exit(1)

    def discover_modules(self, path='modules'):
        """Discover all Python modules in the specified directory."""
        discovered = []
        for file in os.listdir(path):
            if file.endswith('.py') and not file.startswith('__'):
                module_name = file[:-3]
                discovered.append(module_name)
        return discovered

    def load_modules(self, module_names):
        """Load a list of modules by name."""
        for module_name in module_names:
            self.load_module(module_name)
            print(f"Loaded module: {module_name}")

    def run(self):
        """Run all loaded modules."""
        print("RedSentrix is running...")
        for name, module in self.modules.items():
            try:
                module.run()
                self.logger.log(name, "Module executed in run().")
            except Exception as e:
                self.logger.log(name, f"Error during run(): {str(e)}")

    def initialize(self):
        """Initialize the core system, set up logging and check environment."""
        # Setup logger
        self.setup_logger()

        # Perform environment checks
        self.check_evasion()

        # Log initialization
        self.logger.log("Core", "System initialization complete.")
        print("[*] Core system initialized.")

