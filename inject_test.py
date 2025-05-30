# save as inject_test.py
import time
import base64

data = b"secretpayload"
xor_key = 0x41
xor_encoded = bytes([b ^ xor_key for b in data])
base64_encoded = base64.b64encode(data)

# Store them in memory as-is
holder1 = xor_encoded
holder2 = base64_encoded

print(f"Injected XOR: {xor_encoded}")
print(f"Injected Base64: {base64_encoded}")
time.sleep(300)
