# modules/anti_sandbox_probe.py
import time
import os
import random

def timing_check():
    start = time.time()
    time.sleep(2)
    delta = time.time() - start
    return delta < 1.5  # Too fast = suspicious

def cpu_core_check():
    try:
        cores = os.cpu_count()
        return cores <= 2  # Sandboxes often emulate 1-2 cores
    except:
        return False

def file_path_check():
    known_paths = ['/usr/bin/qemu-ga', '/usr/sbin/vboxadd', '/sys/class/dmi/id/product_name']
    return any(os.path.exists(path) for path in known_paths)

def run():
    flags = []
    if timing_check(): flags.append("Timing anomaly")
    if cpu_core_check(): flags.append("Low CPU cores")
    if file_path_check(): flags.append("VM artifacts found")

    if flags:
        return f"[AntiSandbox] Suspicious environment detected: {', '.join(flags)}"
    else:
        return "[AntiSandbox] Environment appears clean."
