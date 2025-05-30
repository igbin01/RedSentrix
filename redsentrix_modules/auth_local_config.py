import os
import json
import getpass
from cryptography.fernet import Fernet

CONFIG_FILE = "configs/redsentrix_config.sec"
KEY_FILE = "configs/config.key"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as keyfile:
        keyfile.write(key)
    return Fernet(key)

def load_key():
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, 'rb') as keyfile:
        return Fernet(keyfile.read())

fernet = load_key()

def init_secure_config():
    """Initializes config file with a secure local password"""
    print("🔐 [Secure Config] First-time setup.")
    password = getpass.getpass("Set local RedSentrix password: ")
    config = {
        "auth_password": password,
        "autologin": False,
        "threat_feed_url": "https://malware.yara-rules.live/feeds/core.yar"
    }
    encrypted_data = fernet.encrypt(json.dumps(config).encode())
    with open(CONFIG_FILE, 'wb') as file:
        file.write(encrypted_data)
    print("✅ Secure config initialized.")

def load_secure_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, 'rb') as file:
        encrypted = file.read()
    try:
        decrypted = fernet.decrypt(encrypted)
        return json.loads(decrypted.decode())
    except Exception:
        return None

def validate_password():
    config = load_secure_config()
    if not config:
        print("❌ Config missing or corrupted.")
        return False

    attempt = getpass.getpass("🔐 Enter RedSentrix password: ")
    if attempt == config["auth_password"]:
        return True
    else:
        print("❌ Invalid password.")
        return False

def get_config_value(key):
    config = load_secure_config()
    return config.get(key) if config else None
