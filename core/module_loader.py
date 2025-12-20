"""
Module loader for RedSentrix
"""

import importlib
import os
from pathlib import Path
from typing import Optional

from .logger import Logger


class ModuleLoader:
    """Dynamic module loader"""
    
    def __init__(self):
        self.logger = Logger()
        self.modules_path = Path("modules")
        self.loaded_modules = {}
    
    def load_and_execute(self, module_name: str, *args, **kwargs) -> Optional[object]:
        """Load and execute a module"""
        try:
            # Try loading from modules directory
            module_path = f"modules.{module_name}"
            module = importlib.import_module(module_path)
            
            # Check if module has run function
            if hasattr(module, "run"):
                self.logger.log(f"Executing module: {module_name}", "info")
                result = module.run(*args, **kwargs)
                self.loaded_modules[module_name] = module
                return result
            else:
                self.logger.log(f"Module {module_name} has no run() function", "warning")
                return None
                
        except ImportError as e:
            self.logger.log(f"Failed to import module {module_name}: {e}", "error")
            return None
        except Exception as e:
            self.logger.log(f"Error executing module {module_name}: {e}", "error")
            return None
    
    def list_modules(self) -> list:
        """List available modules"""
        modules = []
        if self.modules_path.exists():
            for file in self.modules_path.rglob("*.py"):
                if file.name != "__init__.py":
                    rel_path = file.relative_to(self.modules_path)
                    module_name = str(rel_path.with_suffix("")).replace("/", ".")
                    modules.append(module_name)
        return sorted(modules)
