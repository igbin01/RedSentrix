import argparse
import base64
import ctypes
import os
import re
import struct
import sys
import time
from stealth_utils import xor_encode, base64_encode, log_stealth

def find_process_pid(process_name):
    """Find the PID of a process by name on Linux."""
    try:
        # Read from /proc to find process with matching name
        for pid in os.listdir("/proc"):
            if pid.isdigit():
                try:
                    with open(f"/proc/{pid}/comm", "r") as f:
                        comm = f.read().strip()
                        if comm == process_name:
                            return int(pid)
                except IOError:
                    continue
    except Exception as e:
        log_stealth(f"Error finding PID: {e}", level="error")
    return None

def read_process_memory(pid, pattern):
    """Read /proc/pid/mem and scan for pattern."""
    maps_path = f"/proc/{pid}/maps"
    mem_path = f"/proc/{pid}/mem"
    found_offsets = []

    try:
        with open(maps_path, 'r') as maps_file, open(mem_path, 'rb') as mem_file:
            for line in maps_file:
                m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) (\S+)', line)
                if not m:
                    continue
                start = int(m.group(1), 16)
                end = int(m.group(2), 16)
                perms = m.group(3)

                if 'r' not in perms:
                    continue  # Skip non-readable regions

                mem_file.seek(start)
                chunk = mem_file.read(end - start)

                # Search for pattern
                offsets = [m.start() for m in re.finditer(pattern.encode(), chunk)]
                for offset in offsets:
                    absolute_offset = start + offset
                    found_offsets.append(absolute_offset)
    except PermissionError:
        log_stealth("Permission denied reading process memory. Try running as root.", level="error")
        sys.exit(1)
    except Exception as e:
        log_stealth(f"Error reading memory: {e}", level="error")
        sys.exit(1)
    return found_offsets

def covert_encode(data: bytes, method: str) -> str:
    """Apply covert encoding based on method."""
    if method == "xor":
        key = 0x42
        encoded = xor_encode(data, key)
        return base64.b64encode(encoded).decode()
    elif method == "base64":
        return base64_encode(data)
    else:
        # No encoding
        return data.decode(errors='replace')

def main():
    parser = argparse.ArgumentParser(description="Stealth Memory Scanner")
    parser.add_argument("--process", required=True, help="Process name to scan")
    parser.add_argument("--pattern", required=True, help="Pattern to search for in memory")
    parser.add_argument("--covert", default="none", choices=["none", "xor", "base64"], help="Covert encoding method")

    args = parser.parse_args()

    log_stealth(f"Starting stealth memory scan for pattern '{args.pattern}' in process '{args.process}'...", level="info")

    pid = find_process_pid(args.process)
    if pid is None:
        log_stealth(f"Process '{args.process}' not found.", level="error")
        return

    log_stealth(f"Scanning process '{args.process}' (PID: {pid}) for pattern '{args.pattern}'...", level="info")

    offsets = read_process_memory(pid, args.pattern)

    if not offsets:
        log_stealth(f"Pattern '{args.pattern}' not found in process memory.", level="warn")
    else:
        for offset in offsets:
            # For demonstration, we just log the found offset with covert encoding of the pattern itself
            encoded_pattern = covert_encode(args.pattern.encode(), args.covert)
            log_stealth(f"Pattern found at memory offset 0x{offset:x}. Covert encoded pattern: {encoded_pattern}", level="info")

if __name__ == "__main__":
    main()

