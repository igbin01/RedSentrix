import re
import math
import hashlib
from typing import List
from .models import MemoryRegion, ScanResult

# Example pattern signatures for injected code (simple signatures, should be extended)
SUSPICIOUS_PATTERNS = [
    b"\x90\x90\x90\x90",  # NOP sled (common in shellcode)
    b"\x68",               # PUSH instruction in assembly (common in shellcode)
    b"\x89\xe5",           # MOV ESP, EBP (commonly used to manipulate stack)
    b"\x31\xc0",           # XOR EAX, EAX (often used for nulling registers)
    b"\x48\x31\xc0",       # XOR RAX, RAX (in modern x86_64)
    b"\x55\x48\x89\xe5",   # PUSH RBP, MOV RBP, RSP (prologue of injected code)
]

def compute_entropy(data: bytes) -> float:
    """ Compute entropy of a byte string (data) """
    byte_freq = {byte: 0 for byte in range(256)}
    for byte in data:
        byte_freq[byte] += 1

    data_length = len(data)
    entropy = 0
    for byte in byte_freq.values():
        if byte > 0:
            probability = byte / data_length
            entropy -= probability * math.log2(probability)

    return entropy


def detect_suspicious_patterns(memory: bytes) -> List[str]:
    """ Detect suspicious patterns in the memory dump """
    found_patterns = []
    for pattern in SUSPICIOUS_PATTERNS:   
        if pattern in memory:
            found_patterns.append(f"Pattern {pattern.hex()} detected")
    return found_patterns


def analyze_memory(memory_data: bytes) -> dict:
    """ Analyze memory and return structured results with summary """
    anomalies = []

    if b"\x90" * 10 in memory_data:
        anomalies.append("Suspicious NOP sled detected (possible shellcode)")

    if b"MZ" in memory_data and b"PE" in memory_data:
        anomalies.append("PE header found in memory (possible code injection)")

    if len(set(memory_data)) / len(memory_data) < 0.1:
        anomalies.append("Low entropy region detected (possible packed payload)")

    summary = "Anomalies found" if anomalies else "Clean"
    return {
        "summary": summary,
        "anomalies": anomalies
    }


def analyze_memory_region(region: MemoryRegion, memory_data: bytes) -> ScanResult:
    """ Analyze the memory region for anomalies like injected code """
    entropy_score = compute_entropy(memory_data)
    suspicious_patterns = detect_suspicious_patterns(memory_data)
    memory_anomalies = analyze_memory(memory_data)

    scan_result = ScanResult(
        region=region,
        suspicious_patterns=suspicious_patterns + memory_anomalies,
        entropy_score=entropy_score
    )

    return scan_result


def analyze_process_memory(pid: int, process_memory: List[MemoryRegion]) -> List[ScanResult]:
    """ Analyze memory of the given process (using its memory regions) """
    scan_results = []
    for region in process_memory:
        # Here, you would actually extract memory data from the system using `pid` and `region.start`/`region.end`
        # For now, we'll mock this with empty memory data for illustration purposes.
        memory_data = b"\x90" * 1000  # Placeholder for the actual memory read (NOP sled example)

        scan_result = analyze_memory_region(region, memory_data)
        scan_results.append(scan_result)

    return scan_results


def filter_results_by_entropy(scan_results: List[ScanResult], threshold: float = 7.0) -> List[ScanResult]:
    """ Filter scan results by entropy score to detect highly compressed/injected code """
    return [result for result in scan_results if result.entropy_score > threshold]

