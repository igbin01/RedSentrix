# nebula_core/evasion.py
import platform

def check_environment():
    system_info = platform.system().lower()
    
    if "linux" in system_info and "vmware" in platform.machine().lower():
        return False  # Suspected VM
    if "windows" in system_info and "hyperv" in platform.machine().lower():
        return False  # Suspected VM
    
    return True  # Environment appears safe

