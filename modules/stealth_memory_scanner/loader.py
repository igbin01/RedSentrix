# modules/stealth_memory_scanner/loader.py

from core.memory.scanner import MemoryScanner
from core.memory.heuristics import AnomalyDetector
from core.memory.stealth_utils import stealth_log
from config.memory_scanner_config import ScannerConfig

class StealthMemoryScannerModule:
    def __init__(self):
        self.config = ScannerConfig()
        self.scanner = MemoryScanner(self.config)
        self.detector = AnomalyDetector()

    def run(self):
        stealth_log("[🧠] Stealth Memory Scanner Initialized...")
        processes = self.scanner.list_target_processes()
        stealth_log(f"[+] Targeting {len(processes)} suspicious process(es)...")

        for proc in processes:
            try:
                memory_map = self.scanner.get_memory_regions(proc)
                suspicious_regions = self.detector.analyze_memory_regions(proc, memory_map)
                for region in suspicious_regions:
                    stealth_log(f"[!] Suspicious memory region: {region}")
            except Exception as e:
                stealth_log(f"[!] Skipping process {proc.pid}: {e}", level="debug")

        stealth_log("[✓] Scan complete. Results stored securely.")

def main():
    module = StealthMemoryScannerModule()
    module.run()

if __name__ == "__main__":
    main()
