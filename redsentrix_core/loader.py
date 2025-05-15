import importlib
import time
from core.logger import Logger
from core.stealth_utils import StealthUtils

class ModuleLoader:
    def __init__(self):
        self.logger = Logger()

    def load_module(self, module_name):
        try:
            StealthUtils.secure_print(f"Attempting to load: {module_name}")
            module = importlib.import_module(f"modules.{module_name}")
            return module
        except ModuleNotFoundError:
            self.logger.log(f"Module not found: {module_name}")
        except Exception as e:
            self.logger.log(f"Error loading module {module_name}: {str(e)}")
        return None

    def run_module(self, module_name):
        if StealthUtils.is_debugger_present():
            self.logger.log("Debugger detected, aborting execution.")
            return
        if StealthUtils.sandbox_check():
            self.logger.log("Sandbox detected, aborting execution.")
            return
        
        module = self.load_module(module_name)
        if module and hasattr(module, "run"):
            StealthUtils.secure_print(f"Executing: {module_name}")
            try:
                module.run()
            except Exception as e:
                self.logger.log(f"Execution failed: {str(e)}")
        else:
            self.logger.log(f"Module {module_name} has no run() method.")

