import os
import yara
import base64
import json
from core.logger import RedSentrixLogger

logger = RedSentrixLogger("logs/session_memory_scan.json")


class StealthMemoryScanner:
    def __init__(self, yara_rule_path="rules/malware_auto.yar"):
        self.yara_rule_path = yara_rule_path
        self.yara_rules = self.load_yara_rules()

    def load_yara_rules(self):
        if not os.path.exists(self.yara_rule_path):
            raise FileNotFoundError(f"YARA rule file not found: {self.yara_rule_path}")
        return yara.compile(filepath=self.yara_rule_path)

    def scan_process_memory(self, pid):
        mem_path = f"/proc/{pid}/mem"
        maps_path = f"/proc/{pid}/maps"
        results = []

        try:
            with open(maps_path, 'r') as maps_file:
                memory_regions = [line.split(' ')[0] for line in maps_file.readlines()]

            with open(mem_path, 'rb', 0) as mem_file:
                for region in memory_regions:
                    try:
                        start, end = [int(x, 16) for x in region.split('-')]
                        mem_file.seek(start)
                        chunk = mem_file.read(end - start)
                        matches = self.yara_rules.match(data=chunk)

                        for match in matches:
                            encoded_match = base64.b64encode(chunk[:100]).decode('utf-8')
                            result = {
                                "pid": pid,
                                "match": match.rule,
                                "meta": match.meta,
                                "sample": encoded_match
                            }
                            logger.log(result)
                            results.append(result)
                    except Exception:
                        continue  # Skips unreadable regions
        except Exception as e:
            logger.log({"error": str(e), "pid": pid})

        return results
