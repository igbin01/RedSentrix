"""
Payload builder for RedSentrix
Generates multi-stage payloads with obfuscation and encryption
"""

import base64
import zlib
import random
import string
from typing import Optional

from .logger import Logger


class PayloadBuilder:
    """Builds and obfuscates payloads"""
    
    def __init__(self):
        self.logger = Logger()
    
    def build_payload(self, stage: int = 1, obfuscate: bool = True, 
                     encrypt: bool = True) -> str:
        """Build a payload"""
        # Generate stage-specific payload
        if stage == 1:
            payload = self._generate_stage1_payload()
        elif stage == 2:
            payload = self._generate_stage2_payload()
        else:
            payload = self._generate_final_payload()
        
        # Compress
        payload = zlib.compress(payload.encode())
        
        # Encrypt if requested
        if encrypt:
            payload = self._encrypt_payload(payload)
        
        # Encode
        encoded = base64.b64encode(payload).decode()
        
        # Obfuscate if requested
        if obfuscate:
            encoded = self._obfuscate_string(encoded)
        
        return encoded
    
    def _generate_stage1_payload(self) -> str:
        """Generate stage 1 (dropper) payload"""
        return """
        // Stage 1: Initial dropper
        // Downloads and executes stage 2
        """
    
    def _generate_stage2_payload(self) -> str:
        """Generate stage 2 (loader) payload"""
        return """
        // Stage 2: Loader
        // Loads final payload into memory
        """
    
    def _generate_final_payload(self) -> str:
        """Generate final payload"""
        return """
        // Final payload
        // Main malware functionality
        """
    
    def _encrypt_payload(self, payload: bytes) -> bytes:
        """Encrypt payload (XOR for simplicity)"""
        key = b"RedSentrixKey2024"
        return bytes([b ^ key[i % len(key)] for i, b in enumerate(payload)])
    
    def _obfuscate_string(self, s: str) -> str:
        """Obfuscate string"""
        # Simple obfuscation - add random characters
        obfuscated = ""
        for char in s:
            obfuscated += char
            if random.random() < 0.1:  # 10% chance
                obfuscated += random.choice(string.ascii_letters)
        return obfuscated

