import os
import time
import math

def calculate_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    occurrences = [0] * 256
    for byte in data:
        occurrences[byte] += 1
    entropy = 0
    for count in occurrences:
        if count:
            p = count / len(data)
            entropy -= p * math.log2(p)
    return entropy

def scan_memory(pid: int, stop_event, progress_callback, av_evasion_log_callback, output_callback):
    """
    Scans /proc/<pid>/mem regions for suspicious patterns or high entropy.
    Linux only.
    - stop_event: threading.Event to allow cancellation
    - progress_callback: function(progress: int) to update progress bar
    - av_evasion_log_callback: function(str) to log AV evasion alerts
    - output_callback: function(str) to output scan findings
    """
    try:
        mem_path = f"/proc/{pid}/mem"
        maps_path = f"/proc/{pid}/maps"

        if not os.path.exists(mem_path) or not os.path.exists(maps_path):
            output_callback(f"[Memory Scanner] Cannot access memory info for PID {pid}. Insufficient permissions or invalid PID.")
            return

        with open(maps_path, 'r') as maps_file, open(mem_path, 'rb', 0) as mem_file:
            lines = maps_file.readlines()
            total_lines = len(lines)

            for idx, line in enumerate(lines):
                if stop_event.is_set():
                    output_callback("[Memory Scanner] Scan stopped by user.")
                    break

                parts = line.split()
                if len(parts) < 2:
                    continue

                addr_range = parts[0]
                perms = parts[1]

                if 'r' not in perms:
                    continue

                start_str, end_str = addr_range.split('-')
                start = int(start_str, 16)
                end = int(end_str, 16)
                size = end - start

                try:
                    mem_file.seek(start)
                    chunk = mem_file.read(min(size, 4096))
                    entropy = calculate_entropy(chunk)
                    if b"malware" in chunk or b"persistence" in chunk or entropy > 7.5:
                        output_callback(f"[!] Suspicious pattern at {hex(start)} (Entropy: {entropy:.2f})")
                        av_evasion_log_callback(f"Suspicious pattern detected in PID {pid} at {hex(start)} (Entropy: {entropy:.2f})")
                except OSError as e:
                    # Ignore inaccessible regions
                    continue

                progress = int((idx + 1) / total_lines * 100)
                progress_callback(progress)
                time.sleep(0.01)
    except Exception as e:
        output_callback(f"[Memory Scanner Error] {e}")
    finally:
        progress_callback(0)
