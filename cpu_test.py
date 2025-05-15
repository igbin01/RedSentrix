import platform
import subprocess

def get_real_cpu_info():
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if "model name" in line:
                    cpu_model = line.strip().split(":")[1].strip()
                    print(f"[DEBUG] CPU from /proc/cpuinfo: {cpu_model}")
                    return cpu_model
    except Exception as e:
        print(f"[DEBUG] Failed to read /proc/cpuinfo: {e}")

    try:
        output = subprocess.check_output("lscpu", shell=True, text=True)
        for line in output.splitlines():
            if "Model name" in line:
                cpu_model = line.split(":")[1].strip()
                print(f"[DEBUG] CPU from lscpu: {cpu_model}")
                return cpu_model
    except Exception as e:
        print(f"[DEBUG] Failed to run lscpu: {e}")

    print("[DEBUG] Falling back to platform.processor()")
    proc = platform.processor()
    print(f"[DEBUG] platform.processor() returns: {proc}")
    return proc or "Unknown"

print("Detected CPU:", get_real_cpu_info())
