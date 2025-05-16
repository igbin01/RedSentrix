import ctypes
import mmap
import os
import time

malicious_string = b"malicious_pattern"

# Allocate a memory page using mmap, which is visible in /proc/<pid>/maps
mem = mmap.mmap(-1, 4096, prot=mmap.PROT_READ | mmap.PROT_WRITE)
mem.write(malicious_string)
mem.seek(0)

# Hold the address of the mmap buffer (for manual validation if needed)
addr = ctypes.addressof(ctypes.c_char.from_buffer(mem))

print(f"Dummy process running with malicious string in mmap memory.")
print(f"[DEBUG] PID: {os.getpid()}, mmap address: {hex(addr)}")

try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("\nExiting dummy process.")

