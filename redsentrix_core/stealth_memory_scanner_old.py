import argparse
import psutil
import os
import base64
import ctypes
import re
from ctypes import wintypes

# Constants and Windows API setup
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
PAGE_READWRITE = 0x04
MEM_COMMIT = 0x1000

kernel32 = ctypes.windll.kernel32
OpenProcess = kernel32.OpenProcess
ReadProcessMemory = kernel32.ReadProcessMemory
VirtualQueryEx = kernel32.VirtualQueryEx
CloseHandle = kernel32.CloseHandle

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('BaseAddress', ctypes.c_void_p),
        ('AllocationBase', ctypes.c_void_p),
        ('AllocationProtect', wintypes.DWORD),
        ('RegionSize', ctypes.c_size_t),
        ('State', wintypes.DWORD),
        ('Protect', wintypes.DWORD),
        ('Type', wintypes.DWORD),
    ]

# ----------------------------------
# Covert Encoding Utilities
# ----------------------------------

def encode_base64(data):
    return base64.b64encode(data.encode()).decode()

def encode_xor(data, key='secret'):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))

def covert_output(data, method):
    if method == 'xor':
        return encode_xor(data)
    return encode_base64(data)

# ----------------------------------
# Core Memory Scanner Logic
# ----------------------------------

def get_pid_by_name(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() == process_name.lower():
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def scan_memory(pid, pattern, encode_method=None):
    matches = []
    try:
        process_handle = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
        if not process_handle:
            return []

        address = 0
        mbi = MEMORY_BASIC_INFORMATION()
        regex = re.compile(pattern.encode(), re.IGNORECASE)

        while VirtualQueryEx(process_handle, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            if mbi.State == MEM_COMMIT and mbi.Protect == PAGE_READWRITE:
                buffer = ctypes.create_string_buffer(mbi.RegionSize)
                bytesRead = ctypes.c_size_t(0)

                if ReadProcessMemory(process_handle, ctypes.c_void_p(address), buffer, mbi.RegionSize, ctypes.byref(bytesRead)):
                    found = regex.findall(buffer.raw[:bytesRead.value])
                    if found:
                        for f in found:
                            encoded = covert_output(f.decode(errors='ignore'), encode_method) if encode_method else f.decode(errors='ignore')
                            matches.append(encoded)

            address += mbi.RegionSize

    finally:
        if process_handle:
            CloseHandle(process_handle)

    return matches

# ----------------------------------
# Argument Parser
# ----------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description="Ultra-Covert Memory Scanner")
    parser.add_argument('--process', type=str, required=True, help='Target process name')
    parser.add_argument('--pattern', type=str, required=True, help='Regex pattern to search for')
    parser.add_argument('--covert', nargs='?', const='base64', choices=['base64', 'xor'], help='Enable covert encoding (default: base64)')
    return parser.parse_args()

# ----------------------------------
# Entry Point
# ----------------------------------

def main():
    args = parse_args()
    pid = get_pid_by_name(args.process)
    if pid is None:
        return  # Silent fail for stealth

    matches = scan_memory(pid, args.pattern, args.covert)

    for m in matches:
        print(m)  # Optional: redirect to covert logger or IPC mechanism instead

if __name__ == "__main__":
    main()

