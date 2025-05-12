# modules/recon_sysinfo_advanced.py
import platform
import uuid
import socket
import os

def run():
    sysinfo = {
        "OS": platform.platform(),
        "Hostname": socket.gethostname(),
        "IP Address": socket.gethostbyname(socket.gethostname()),
        "MAC Address": hex(uuid.getnode()),
        "Processor": platform.processor(),
        "Architecture": platform.architecture(),
        "BIOS": os.popen('wmic bios get smbiosbiosversion').read().strip() if os.name == 'nt' else "N/A",
        "Virtualization Check": "KVM" if os.path.exists('/dev/kvm') else "Unknown"
    }

    for key, value in sysinfo.items():
        print(f"{key}: {value}")

    return "[Recon] Advanced system info collected."
