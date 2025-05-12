# nebula_core/loader.py
import importlib

def load_module(module_name):
    try:
        module = importlib.import_module(f"modules.{module_name}")
        return module
    except ImportError as e:
        print(f"Error loading module: {e}")
        return None
