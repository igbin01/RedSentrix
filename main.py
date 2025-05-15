import os
import importlib
import subprocess
import platform
from redsentrix_core.logger import StealthLogger
from redsentrix_core import stealth_utils
from redsentrix_core.stealth_utils import StealthUtils

logger = StealthLogger()
loaded_modules = set()

# --- FIXED get_real_cpu_info method added directly ---
def get_real_cpu_info():
    """Robust CPU info extraction, confirmed to work via /proc/cpuinfo"""
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.lower().startswith("model name"):
                    cpu_model = line.split(":", 1)[1].strip()
                    return cpu_model
    except Exception as e:
        StealthUtils.secure_print(f"[!] /proc/cpuinfo failed: {e}")

    try:
        output = subprocess.check_output("lscpu", shell=True, text=True)
        for line in output.splitlines():
            if "Model name" in line:
                return line.split(":", 1)[1].strip()
    except Exception as e:
        StealthUtils.secure_print(f"[!] lscpu failed: {e}")

    try:
        proc = platform.processor()
        if proc:
            return proc
    except Exception as e:
        StealthUtils.secure_print(f"[!] platform.processor failed: {e}")

    return "Unknown"

# --- Module loader ---
def load_modules():
    logger.log("main", "🔍 Scanning for modules...")
    modules_path = "modules"

    for file in os.listdir(modules_path):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = file[:-3]

            if module_name in loaded_modules:
                continue

            try:
                mod_path = f"{modules_path}.{module_name}"
                module = importlib.import_module(mod_path)
                if hasattr(module, "run"):
                    logger.log("main", f"✅ Loaded module: {module_name}")
                    module.run()
                    loaded_modules.add(module_name)
                    stealth_utils.random_sleep(100, 300)
                else:
                    logger.log("main", f"⚠️ Module {module_name} has no run() function.")
            except Exception as e:
                logger.log("main", f"[!] Error loading {module_name}: {str(e)}")
                continue

# --- Main function ---
def main():
    logger.log("main", "[+] Starting RedSentrix Framework...")

    cpu_info = get_real_cpu_info()
    logger.log("main", f"Processor: {cpu_info}")

    load_modules()
    logger.log("main", "[✓] RedSentrix execution complete.")

if __name__ == "__main__":
    main()

