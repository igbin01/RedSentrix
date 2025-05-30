import os
import yara

class YaraEngine:
    def __init__(self, rule_dir="rules"):
        self.rule_dir = rule_dir
        os.makedirs(rule_dir, exist_ok=True)
        self.rules = self.load_rules()

    def load_rules(self):
        rule_files = {
            filename: os.path.join(self.rule_dir, filename)
            for filename in os.listdir(self.rule_dir)
            if filename.endswith(".yar") or filename.endswith(".yara")
        }
        if not rule_files:
            print("[!] No YARA rules found in the 'rules' directory.")
            return None
        try:
            return yara.compile(filepaths=rule_files)
        except yara.SyntaxError as e:
            print(f"[!] YARA syntax error: {e}")
            return None

    def scan_buffer(self, data):
        if not self.rules:
            return []
        try:
            matches = self.rules.match(data=data)
            return [match.rule for match in matches]
        except Exception as e:
            print(f"[!] YARA scan error: {e}")
            return []

    def scan_file(self, file_path):
        if not self.rules:
            return []
        try:
            matches = self.rules.match(filepath=file_path)
            return [match.rule for match in matches]
        except Exception as e:
            print(f"[!] YARA file scan error: {e}")
            return []
