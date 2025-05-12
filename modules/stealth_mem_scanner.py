# modules/stealth_mem_scanner.py
import os
import re
import ctypes
import platform

def run():
    if platform.system() != 'Linux':
        return "[!] Unsupported OS for this module."

    suspicious_patterns = [b"\x90\x90", b"MZ", b"\xCC", b"\x00\x00\x00\x00\x00\x00\x00\x00"]
    results = []

    for pid in filter(str.isdigit, os.listdir("/proc")):
        try:
            maps_path = f"/proc/{pid}/maps"
            mem_path = f"/proc/{pid}/mem"
            with open(maps_path, 'r') as maps_file:
                for line in maps_file:
                    if 'rw' in line:
                        parts = line.split()
                        address = parts[0]
                        start, end = [int(x, 16) for x in address.split('-')]

                        try:
                            with open(mem_path, 'rb') as mem_file:
                                mem_file.seek(start)
                                chunk = mem_file.read(end - start)
                                for pattern in suspicious_patterns:
                                    if pattern in chunk:
                                        results.append(f"[!] Suspicious pattern in PID {pid} at {address}")
                        except Exception:
                            continue
        except Exception:
            continue

    if not results:
        return "[✓] No suspicious memory patterns detected."
    return "\n".join(results)
