# modules/stealth_memory_scanner.py
import os
import struct
import ctypes
import base64
import logging
import threading

logger = logging.getLogger(__name__)

class StealthMemoryScanner:
    def __init__(self, target_pid: int, pattern: bytes):
        self.pid = target_pid
        self.pattern = pattern
        self.matches = []
        self._stop_event = threading.Event()

    def _read_mem(self, address, size):
        try:
            with open(f"/proc/{self.pid}/mem", 'rb', 0) as mem_file:
                mem_file.seek(address)
                return mem_file.read(size)
        except Exception as e:
            logger.debug(f"Memory read failed at {hex(address)}: {e}")
            return None

    def _get_memory_maps(self):
        maps = []
        try:
            with open(f"/proc/{self.pid}/maps", 'r') as maps_file:
                for line in maps_file:
                    parts = line.split()
                    addr_range = parts[0]
                    perms = parts[1]
                    if 'r' in perms:
                        start_str, end_str = addr_range.split('-')
                        start = int(start_str, 16)
                        end = int(end_str, 16)
                        maps.append((start, end))
        except Exception as e:
            logger.error(f"Error reading maps for pid {self.pid}: {e}")
        return maps

    def _scan_memory(self):
        maps = self._get_memory_maps()
        for start, end in maps:
            if self._stop_event.is_set():
                logger.info("Scan stopped by user")
                break
            size = end - start
            chunk = self._read_mem(start, size)
            if chunk is None:
                continue
            idx = chunk.find(self.pattern)
            while idx != -1:
                match_addr = start + idx
                self.matches.append(match_addr)
                idx = chunk.find(self.pattern, idx + 1)

    def scan(self):
        logger.info(f"Starting stealth scan on PID {self.pid} for pattern {self.pattern.hex()}")
        self.matches.clear()
        self._stop_event.clear()
        scan_thread = threading.Thread(target=self._scan_memory)
        scan_thread.start()
        scan_thread.join()
        logger.info(f"Scan complete. Matches found: {len(self.matches)}")
        return self._encode_results()

    def stop(self):
        self._stop_event.set()

    def _encode_results(self):
        encoded = []
        for addr in self.matches:
            encoded.append(base64.b64encode(struct.pack('<Q', addr)).decode())
        return encoded
