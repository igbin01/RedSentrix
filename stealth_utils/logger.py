
# === stealth_utils/logger.py ===
import datetime

def log_stealth(message, level="info"):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = {"info": "[*]", "warn": "[!]", "err": "[!!]"}.get(level, "[*]")
    print(f"{prefix} [{now}] {message}")
