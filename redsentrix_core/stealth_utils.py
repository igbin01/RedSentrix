import os
import importlib
import time
import base64
import subprocess
import platform
from redsentrix_core.logger import StealthLogger

logger = StealthLogger()
loaded_modules = set()

class StealthUtils:
    @staticmethod
    def random_sleep(min_ms=100, max_ms=300):
        import random
        time.sleep(random.randint(min_ms, max_ms) / 1000)

    @staticmethod
    def secure_print(msg):
        try:
            encoded = base64.b64encode(msg.encode()).decode()
            print(f"[REDACTED:{encoded}]")
        except Exception as e:
            print(f"[ERROR] secure_print failed: {e}")

    @staticmethod
    def get_real_cpu_info():
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        cpu_model = line.split(":", 1)[1].strip()
                        if cpu_model:
                            print(f"[DEBUG] CPU model from /proc/cpuinfo: {cpu_model}")
                            return cpu_model
        except Exception as e:
            print(f"[DEBUG] Error reading /proc/cpuinfo: {e}")

        try:
            output = subprocess.check_output("lscpu", shell=True, text=True)
            for line in output.splitlines():
                if "Model name" in line:
                    cpu_model = line.split(":", 1)[1].strip()
                    if cpu_model:
                        print(f"[DEBUG] CPU model from lscpu: {cpu_model}")
                        return cpu_model
        except Exception as e:
            print(f"[DEBUG] Error running lscpu: {e}")

        proc = platform.processor()
        if proc and proc.strip():
            print(f"[DEBUG] CPU model from platform.processor(): {proc.strip()}")
            return proc.strip()

        uname = platform.uname()
        if uname.processor:
            print(f"[DEBUG] CPU model from platform.uname(): {uname.processor}")
            return uname.processor

        print("[DEBUG] CPU model unknown")
        return "Unknown CPU"

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
                    StealthUtils.random_sleep(100, 300)
                else:
                    logger.log("main", f"⚠️ Module {module_name} has no run() function.")
            except Exception as e:
                logger.log("main", f"[!] Error loading {module_name}: {str(e)}")
                continue

def main():
    logger.log("main", "[+] Starting RedSentrix Framework...")

    cpu_info = StealthUtils.get_real_cpu_info()
    StealthUtils.secure_print(f"Processor: {cpu_info}")
    logger.log("main", f"Processor: {cpu_info}")

    load_modules()

    logger.log("main", "[✓] RedSentrix execution complete.")

if __name__ == "__main__":
    main()

