from redsentrix_core.encrypted_output import EncryptedOutput
import os
import random
import time

class EncryptedCommChannel:
    def __init__(self, key: bytes, comm_file: str = 'comm_channel.enc'):
        self.crypto = EncryptedOutput(key)
        self.comm_file = comm_file

    def send_encrypted(self, message: str):
        encrypted_data = self.crypto.encrypt(message)
        with open(self.comm_file, 'wb') as f:
            f.write(encrypted_data)

    def receive_encrypted(self, delete_after: bool = True) -> str:
        if not os.path.exists(self.comm_file):
            return ""
        with open(self.comm_file, 'rb') as f:
            encrypted_data = f.read()
        if delete_after:
            os.remove(self.comm_file)
        return self.crypto.decrypt(encrypted_data)

class AITriggeredBehavior:
    def __init__(self, trigger_keywords=None):
        self.trigger_keywords = trigger_keywords or ["execute", "start", "deploy"]

    def evaluate_input(self, input_text):
        detected = [word for word in self.trigger_keywords if word in input_text.lower()]
        return bool(detected), detected

    def trigger_action(self, input_text):
        triggered, words = self.evaluate_input(input_text)
        if triggered:
            print(f"AI Triggered by: {', '.join(words)}")
            self.perform_action()
        else:
            print("No trigger keywords found.")

    def perform_action(self):
        print("[AI Action] Simulating payload execution...")
        time.sleep(random.uniform(0.5, 1.5))
        print("[AI Action] Execution complete.")

