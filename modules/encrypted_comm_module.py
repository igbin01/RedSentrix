from redsentrix_core.encrypted_output import EncryptedOutput
from redsentrix_core.encrypted_comm import EncryptedCommChannel, AITriggeredBehavior
import os

def run():
    key = b"RedSentrixSuperKey123"  # Must match the key used by EncryptedOutput
    channel = EncryptedCommChannel(key)
    ai = AITriggeredBehavior()

    print("[Module] Sending message...")
    channel.send_encrypted("execute payload please")

    print("[Module] Receiving message...")
    received = channel.receive_encrypted()
    print(f"[Module] Received: {received}")

    print("[Module] Running AI Trigger Check...")
    ai.trigger_action(received)
