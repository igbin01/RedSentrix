# modules/stealth_memory_scanner.py
import psutil
import ctypes
import os

# Access to system-level memory scanning
libc = ctypes.CDLL("libc.so.6")

def run():
    findings = []

    # Checking for suspicious processes (i.e., hidden in memory)
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            # Let's filter out the known safe processes
            if "init" not in proc.info['name'].lower() and "systemd" not in proc.info['name'].lower():
                # Scan memory usage for abnormal patterns or high consumption which could be malicious
                memory_usage = proc.info['memory_info'].rss  # Resident Set Size (memory used)
                if memory_usage > 50 * 1024**2:  # Processes using >50MB of memory
                    findings.append(f"[!] High memory usage detected in process {proc.info['name']} (PID: {proc.info['pid']}).")

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Use more advanced scanning for anomalous code patterns
    try:
        with open("/proc/self/maps", 'r') as f:
            maps = f.readlines()
            for line in maps:
                if "rw-p" in line:  # Looking for readable/writable memory areas
                    findings.append(f"[!] Suspicious memory area detected: {line.strip()}")
    except Exception as e:
        findings.append(f"[!] Error scanning memory areas: {str(e)}")

    return "\n".join(findings) if findings else "[✓] No suspicious memory patterns detected."
