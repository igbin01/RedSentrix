import time
import os

# This string will live in memory and be scannable
secret = "TOP_SECRET_PAYLOAD"

print(f"Dummy process running. PID: {os.getpid()}")
print(f"Holding secret in memory: {secret}")

# Keep the process alive for scanning
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Dummy process exiting.")
