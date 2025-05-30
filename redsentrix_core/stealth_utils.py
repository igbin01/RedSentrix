
import os
import sys
import platform
import subprocess
import time
import base64
import math
import logging

# Setup stealth-aware logging
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

def throttle_activity(seconds=1):
    """Pause execution for given seconds to throttle activity."""
    time.sleep(seconds)

def xor_encode(data: bytes, key: bytes) -> bytes:
    """XOR encode data with the given key."""
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def base64_encode(data: bytes) -> str:
    """Base64 encode byte data and return string."""
    return base64.b64encode(data).decode()

def entropy_check(data: bytes) -> float:
    """Calculate Shannon entropy of given data."""
    if not data:
        return 0.0

    byte_counts = [0] * 256
    for byte in data:
        byte_counts[byte] += 1

    entropy = 0.0
    for count in byte_counts:
        if count:
            p = count / len(data)
            entropy -= p * math.log2(p)
    return entropy

def log_stealth(message: str, level: str = "info"):
    """Custom stealth logging interface."""
    if level == "debug":
        logging.debug(message)
    elif level == "warn":
        logging.warning(message)
    elif level == "error":
        logging.error(message)
    else:
        logging.info(message)

def stealth_init():
    """Placeholder to initiate stealth mode (extend as needed)."""
    log_stealth("Stealth memory scanner initialized.", level="debug")

def update_scanner_regions():
    """Placeholder to simulate stealth updates to memory regions (extend as needed)."""
    log_stealth("Scanner regions updated.", level="debug")

class StealthUtils:
    @staticmethod
    def is_debugger_present():
        if sys.gettrace():
            return True

        if platform.system() == "Linux":
            try:
                with open("/proc/self/status") as f:
                    for line in f:
                        if "TracerPid" in line:
                            tracer_pid = int(line.split()[1])
                            if tracer_pid > 0:
                                return True
            except Exception:
                pass

        if platform.system() == "Windows":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                return kernel32.IsDebuggerPresent() != 0
            except Exception:
                pass

        return False

    @staticmethod
    def sandbox_check():
        if platform.system() == "Linux":
            vm_signs = [
                "/sys/class/dmi/id/product_name",
                "/sys/class/dmi/id/sys_vendor",
                "/proc/scsi/scsi",
            ]
            for path in vm_signs:
                try:
                    with open(path) as f:
                        content = f.read().lower()
                        if any(x in content for x in ["vmware", "virtualbox", "kvm", "qemu", "hyper-v"]):
                            return True
                except Exception:
                    continue

            for var in ["VBOX", "VMWARE", "KVM", "QEMU", "HYPERV"]:
                if os.getenv(var):
                    return True

        elif platform.system() == "Windows":
            suspicious_processes = [
                "vboxservice.exe", "vboxtray.exe", "vmtoolsd.exe",
                "vmwaretray.exe", "vmwareuser.exe", "vmsrvc.exe",
                "vmware.exe"
            ]
            try:
                output = subprocess.check_output("tasklist", shell=True).decode().lower()
                for proc in suspicious_processes:
                    if proc in output:
                        return True
            except Exception:
                pass

        return False

    @staticmethod
    def secure_print(message):
        """Secure print wrapper to avoid output leaks."""
        print(message)
