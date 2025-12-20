"""
Configuration management for RedSentrix
"""

import yaml
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Configuration manager"""
    
    def __init__(self, config_path: str = "config/phishing.yaml"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load()
    
    def load(self):
        """Load configuration from file"""
        if not self.config_path.exists():
            self._create_default_config()
            return
        
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def save(self):
        """Save configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def _create_default_config(self):
        """Create default configuration"""
        self.config = {
            "phishing": {
                "port": 8080,
                "target_url": "https://example.com",
                "cert_path": "build/phishing/cert.pem",
                "key_path": "build/phishing/key.pem",
                "domains": ["example.com"]
            },
            "c2": {
                "enabled": False,
                "url": "https://c2.example.com",
                "key": "",
                "interval": 60
            },
            "payload": {
                "stage": 1,
                "obfuscate": True,
                "encrypt": True,
                "method": "shellcode"
            },
            "modules": [
                "phishing.embedder",
                "dropper.dropper"
            ],
            "stealth": {
                "evasion": True,
                "injection_method": 2,
                "persistence": True
            }
        }
        self.save()

