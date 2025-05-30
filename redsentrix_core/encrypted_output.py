# redsentrix_core/encrypted_output.py

import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class EncryptedOutput:
    def __init__(self, key: bytes):
        self.key = key[:32]  # AES-256 key

    def encrypt_data(self, data: dict) -> str:
        raw = json.dumps(data).encode()
        iv = get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(raw, AES.block_size))
        return base64.b64encode(iv + ciphertext).decode()

    def decrypt_data(self, encrypted_b64: str) -> dict:
        decoded = base64.b64decode(encrypted_b64.encode())
        iv, ciphertext = decoded[:16], decoded[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        raw = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return json.loads(raw.decode())

    def secure_log(self, message: str, module_name="core"):
        encrypted = self.encrypt_data({"module": module_name, "msg": message})
        with open("logs/encrypted_output.log", "a") as f:
            f.write(encrypted + "\n")
