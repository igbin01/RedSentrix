import os
import time
import psutil
import ctypes
import random
from termcolor import colored

from redsentrix_core.stealth_utils import (
    throttle_activity,
    find_low_profile_targets,
    ptrace_attach,
    ptrace_detach,
    stealthy_mmap
)
from redsentrix_core.heuristics import analyze_memory
from redsentrix_core.logger import log


def read_process_memory(pid, mem_path="/proc/{}/mem", maps_path="/proc/{}/maps"):
    memory_data = []
    try:
        ptrace_attach(pid)
        with open(mem_path.format(pid), 'rb', 0) as mem_file, open(maps_path.format(pid), 'r') as maps_file:
            for line in maps_file:
                try:
                    if 'r' not in line.split(' ')[1]:
                        continue
                    start, end = [int(x, 16) for x in line.split(' ')[0].split('-')]
                    mem_file.seek(start)
                    data = mem_file.read(end - start)
                    memory_data.append((start, data))
                except Exception as e:
                    print(colored(f"[!] Error reading memory range {hex(start)}-{hex(end)}: {e}", 'red'))
                    continue
    except Exception as e:
        print(colored(f"[!] Failed to attach to PID {pid}: {e}", 'red'))
    finally:
        ptrace_detach(pid)
    return memory_data


def scan_memory(stealth: bool = False):
    # Removed is_debugger_present import and check as it's not defined

    if not stealth:
        print(colored("[+] Starting ultra-covert memory scan...", 'green'))

    targets = find_low_profile_targets()
    results = []

    for pid in targets:
        if not stealth:
            print(colored(f"[•] Scanning PID {pid}...", 'blue'))

        try:
            mem_chunks = read_process_memory(pid)
            for addr, chunk in mem_chunks:
                analysis = analyze_memory(chunk)
                if analysis.get("anomalies"):
                    results.append({
                        "pid": pid,
                        "address": hex(addr),
                        "flags": analysis["anomalies"],
                        "summary": analysis["summary"]
                    })
        except Exception as e:
            if not stealth:
                print(colored(f"[!] Scan failed on PID {pid}: {e}", 'red'))

        throttle_activity()

    if not stealth:
        if results:
            print(colored(f"[✓] Scan complete. {len(results)} suspicious findings.", 'green'))
            for result in results:
                print(colored(f"  ↳ PID {result['pid']} @ {result['address']}: {result['summary']} [{result['flags']}]", 'yellow'))
        else:
            print(colored("[✓] Scan complete. No suspicious findings.", 'green'))

    return results


def run_scan():
    print("[DEBUG] run_scan() started")
    log("SCAN", "Initiating scan from scanner module")
    scan_memory(stealth=False)


if __name__ == "__main__":
    run_scan()

