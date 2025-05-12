# modules/recon_sysinfo.py
import platform

def run():
    print("Running system information module...")
    system_info = platform.uname()
    print(f"System Info: {system_info}")
import platform
import os

def run():
    """ Collect system info as a test action """
    sys_info = {
        "OS": platform.system(),
        "Platform": platform.version(),
        "Architecture": platform.architecture(),
    }
    return f"System Info: {sys_info}"
import importlib

class NebulaCore:
    def __init__(self):
        self.modules = {}  # Dictionary to store loaded modules
        self.log = self.setup_logger()

    def setup_logger(self):
        """ Set up the stealth logger. """
        logger = logging.getLogger('NebulaCoreLogger')
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()  # Can change to FileHandler for file logs
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

    def load_module(self, module_name):
        """ Dynamically load a module """
        try:
            # Dynamically import the module from the 'modules' directory
            module = importlib.import_module(f"modules.{module_name}")
            self.modules[module_name] = module
            self.log.info(f"Module '{module_name}' loaded successfully.")
        except ModuleNotFoundError as e:
            self.log.error(f"Module '{module_name}' not found. Error: {e}")
        except Exception as e:
            self.log.error(f"An error occurred while loading module '{module_name}': {e}")
            raise

    def execute_module(self, module_name):
        """ Execute a loaded module """
        if module_name in self.modules:
            module = self.modules[module_name]
            result = module.run()
            self.log_action(module_name, result)
        else:
            self.log.error(f"Module '{module_name}' is not loaded.")
    
    def log_action(self, module_name, result):
        """ Log module action with timestamp and result """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log.info(f"Action [{module_name}] at {timestamp}: {result}")
