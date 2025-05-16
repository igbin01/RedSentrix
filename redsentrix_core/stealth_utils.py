import base64
import datetime
import math

def xor_encode(data: bytes, key: bytes) -> bytes:
    """XOR encode/decode data with the given key."""
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def base64_encode(data: bytes) -> str:
    """Base64 encode bytes data."""
    return base64.b64encode(data).decode('utf-8')

def entropy_check(data: bytes) -> float:
    """Calculate Shannon entropy of the given data."""
    if not data:
        return 0.0
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    entropy = 0.0
    length = len(data)
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy

def log_stealth(message: str, level: str = "info"):
    """Stealthy logging with timestamp and level prefix."""
    levels = {
        "info": "[*]",
        "warn": "[!]",
        "error": "[!!]"
    }
    prefix = levels.get(level.lower(), "[*]")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{prefix} [{timestamp}] {message}")

