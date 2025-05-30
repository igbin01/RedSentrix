import os
import json
from datetime import datetime
from cryptography.fernet import Fernet

class SessionLogger:
    def __init__(self, log_dir="logs", key_file="core/log_key.key"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.key_file = key_file
        self.key = self.load_or_create_key()
        self.cipher = Fernet(self.key)

    def load_or_create_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
            with open(self.key_file, "wb") as f:
                f.write(key)
            return key

    def log(self, module, data):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.log_dir, f"{module}_{timestamp}.log.enc")
        log_data = {
            "timestamp": timestamp,
            "module": module,
            "data": data
        }
        encrypted = self.cipher.encrypt(json.dumps(log_data, indent=2).encode())
        with open(filename, "wb") as f:
            f.write(encrypted)
        return filename

    def read_logs(self, filter_module=None, search_term=None):
        logs = []
        for file in os.listdir(self.log_dir):
            if not file.endswith(".enc"):
                continue
            path = os.path.join(self.log_dir, file)
            with open(path, "rb") as f:
                try:
                    decrypted = self.cipher.decrypt(f.read()).decode()
                    data = json.loads(decrypted)
                    if filter_module and data["module"] != filter_module:
                        continue
                    if search_term and search_term.lower() not in decrypted.lower():
                        continue
                    logs.append(data)
                except Exception:
                    continue
        return logs
