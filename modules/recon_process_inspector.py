# modules/recon_process_inspector.py
import psutil
import os
import time

def is_suspicious(proc):
    name = proc.name().lower()
    suspicious_keywords = ["hack", "meterpreter", "revshell", "exploit", "rat", "malware", "crypto", "miner"]
    return any(keyword in name for keyword in suspicious_keywords)

def run():
    print("\n🧠 Process Inspection & Anomaly Detection")
    result = []

    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            user = proc.info['username']
            cpu = proc.info['cpu_percent']
            mem = proc.info['memory_percent']

            line = f"PID: {pid} | Name: {name} | User: {user} | CPU: {cpu}% | MEM: {mem:.2f}%"

            if is_suspicious(proc):
                line += " <-- ⚠️ Suspicious"

            result.append(line)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return "\n".join(result)
