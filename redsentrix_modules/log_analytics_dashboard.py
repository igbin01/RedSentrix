import os
import json
import csv
import re
from datetime import datetime
from cryptography.fernet import Fernet

LOG_PATH = "logs/redsentrix.log"
EXPORT_DIR = "exports"
SECRET_KEY_PATH = "configs/logkey.secret"

# Ensure export directory exists
os.makedirs(EXPORT_DIR, exist_ok=True)

# Load or create encryption key
def load_encryption_key():
    if not os.path.exists(SECRET_KEY_PATH):
        key = Fernet.generate_key()
        with open(SECRET_KEY_PATH, 'wb') as f:
            f.write(key)
    else:
        with open(SECRET_KEY_PATH, 'rb') as f:
            key = f.read()
    return Fernet(key)

fernet = load_encryption_key()

def read_logs():
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def filter_logs(keyword=None, date=None, module=None, severity=None):
    logs = read_logs()
    filtered = []

    for line in logs:
        if keyword and keyword.lower() not in line.lower():
            continue
        if date and date not in line:
            continue
        if module and module.lower() not in line.lower():
            continue
        if severity and severity.upper() not in line:
            continue
        filtered.append(line)

    return filtered

def export_logs(log_entries, format="json"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"redsentrix_logs_{timestamp}.{format}"
    path = os.path.join(EXPORT_DIR, filename)

    if format == "json":
        with open(path, "w") as f:
            json.dump(log_entries, f, indent=4)
    elif format == "csv":
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Log Entry"])
            for entry in log_entries:
                writer.writerow([entry])
    return path

def secure_export(log_entries):
    """Encrypts exported logs with Fernet"""
    data = json.dumps(log_entries, indent=2).encode()
    encrypted = fernet.encrypt(data)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(EXPORT_DIR, f"redsentrix_logs_encrypted_{timestamp}.bin")
    with open(path, "wb") as f:
        f.write(encrypted)
    return path

def decrypt_export(file_path):
    with open(file_path, "rb") as f:
        encrypted_data = f.read()
    decrypted = fernet.decrypt(encrypted_data)
    return json.loads(decrypted.decode())
