# modules/process_inspector.py

import psutil

def inspect_processes():
    print("🧠 Process Inspection & Anomaly Detection")
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            print(f"[+] PID: {proc.info['pid']}, Name: {proc.info['name']}, User: {proc.info['username']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return "[+] Process inspection complete."

def run():
    return inspect_processes()
