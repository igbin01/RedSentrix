# redsentrix_core/core.py

import os
from .loader import ModuleLoader
from .logger import Logger

class NebulaCore:
    def __init__(self):
        self.logger = Logger()
        self.loader = ModuleLoader()

    def list_modules(self):
        self.logger.log("Listing modules...")
        modules_dir = os.path.join(os.path.dirname(__file__), '..', 'modules')
        modules = []
        try:
            for filename in os.listdir(modules_dir):
                if filename.endswith(".py") and not filename.startswith("__"):
                    modules.append(filename[:-3])
        except Exception as e:
            self.logger.log(f"Error listing modules: {str(e)}")
        return sorted(modules)

    def run_module(self, module_name):
        self.logger.log(f"Running module: {module_name}")
        self.loader.run_module(module_name)

