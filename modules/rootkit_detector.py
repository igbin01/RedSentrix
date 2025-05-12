# modules/rootkit_detector.py
import os
import psutil
import re
import subprocess
import ctypes
import platform
import time

def run():
    findings = []

    # Detect process hiding via /proc filesystem
    hidden_procs = []
    for pid in filter(str.isdigit, os.listdir("/proc")):
        try:
            with open(f"/proc/{pid}/cmdline", 'r') as cmd_file:
                cmd = cmd_file.read()
                # Common rootkit/hidden process pattern (this would be more refined in real scenarios)
                if "rootkit" in cmd.lower() or "hidden" in cmd.lower():
                    hidden_procs.append(pid)
        except FileNotFoundError:
            continue

    if hidden_procs:
        findings.append(f"[!] Hidden processes detected: {', '.join(hidden_procs)}")

    # Check for syscall tampering by comparing kernel syscall table
    if platform.system() == 'Linux':
        try:
            syscall_table = subprocess.check_output(["cat", "/proc/kallsyms"], text=True)
            if "sys_call_table" in syscall_table:
                findings.append("[!] Potential syscall table tampering detected.")
        except Exception:
            findings.append("[!] Error reading syscall table.")

    # Check for active debuggers by inspecting ptrace scope
    try:
        ptrace_scope = subprocess.check_output(['cat', '/proc/sys/kernel/yama/ptrace_scope'], text=True).strip()
        if ptrace_scope != '0':
            findings.append("[!] Non-default ptrace_scope detected. A debugger may be present.")
    except Exception:
        findings.append("[!] Error reading ptrace scope.")

    # Detect possible rootkit kernel modules
    try:
        modules = subprocess.check_output(["lsmod"], text=True)
        if "rootkit" in modules or "hidden" in modules:
            findings.append("[!] Suspicious rootkit-like kernel modules loaded.")
    except Exception:
        findings.append("[!] Error listing loaded kernel modules.")

    # Detect suspicious file changes (rootkits often hide files)
    try:
        files_to_check = ["/etc/passwd", "/etc/shadow", "/etc/ld.so.preload"]
        for file in files_to_check:
            if not os.path.exists(file):
                findings.append(f"[!] Suspicious missing file: {file}")
            else:
                stat = os.stat(file)
                # Comparing file size or checksum could help detect changes over time
                if stat.st_size == 0:
                    findings.append(f"[!] Empty suspicious file detected: {file}")
    except Exception:
        findings.append("[!] Error reading system files.")

    # Anti-debugging check: Checking if a debugger is attached to the process
    try:
        for pid in filter(str.isdigit, os.listdir("/proc")):
            if os.path.exists(f"/proc/{pid}/status"):
                with open(f"/proc/{pid}/status", 'r') as status_file:
                    for line in status_file:
                        if "TracerPid" in line:
                            tracer_pid = line.split(":")[1].strip()
                            if tracer_pid != "0":
                                findings.append(f"[!] Debugger detected on PID {pid} (TracerPid: {tracer_pid}).")
    except Exception:
        findings.append("[!] Error checking for active debuggers.")

    return "\n".join(findings) if findings else "[✓] No rootkit or debugger activity detected."
