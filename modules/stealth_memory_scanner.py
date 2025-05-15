import psutil
import ctypes
import os
from termcolor import colored
from redsentrix_core.stealth_utils import throttle_activity, is_debugger_present
from redsentrix_core.logger import StealthLogger

logger = StealthLogger()

# Access to system-level memory scanning
libc = ctypes.CDLL("libc.so.6")

def check_process_memory(proc):
    findings = []
    
    try:
        # Filter out known safe processes like init and systemd
        name = proc.info['name'].lower()
        if "init" not in name and "systemd" not in name:
            memory_usage = proc.info['memory_info'].rss  # Resident Set Size
            if memory_usage > 50 * 1024**2:  # 50MB threshold
                findings.append(f"[!] High memory usage in {proc.info['name']} (PID: {proc.info['pid']})")
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
    
    return findings

def scan_memory():
    findings = []

    # Check processes for abnormal memory usage
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        findings.extend(check_process_memory(proc))

    # Check memory maps for suspicious writable areas
    try:
        with open("/proc/self/maps", 'r') as f:
            for line in f:
                if "rw-p" in line:
                    findings.append(f"[!] Suspicious memory area: {line.strip()}")
    except Exception as e:
        findings.append(f"[!] Error reading memory maps: {str(e)}")

    return findings

def run(stealth=False):
    """
    Executes the stealth memory scan.
    """
    if is_debugger_present():
        if not stealth:
            print(colored("[x] Exiting: Debugger detected.", 'red'))
        return []

    if not stealth:
        print(colored("[+] Starting stealth memory scan...", 'green'))
    else:
        logger.log("stealth_memory_scanner", "Initiating ultra-covert memory scan...")

    findings = scan_memory()

    if stealth:
        if findings:
            logger.log("stealth_memory_scanner", "\n".join(findings))
        else:
            logger.log("stealth_memory_scanner", "No suspicious findings detected.")
    else:
        if findings:
            print(colored(f"[✓] Scan complete. {len(findings)} suspicious findings.", 'green'))
            for finding in findings:
                print(colored(f"  ↳ {finding}", 'yellow'))
        else:
            print(colored("[✓] Scan complete. No suspicious findings.", 'green'))

    throttle_activity()

if __name__ == "__main__":
    run(stealth=False)

