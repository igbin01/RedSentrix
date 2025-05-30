import yara
import tempfile
import os

class YARAAutoLoader:
    def __init__(self):
        self.rules = None
        self.embedded_rules = {
            "Generic_Malware": '''
rule Generic_Malware
{
    meta:
        description = "Generic malware string detection"
        author = "RedSentrix"
        threat_level = 3

    strings:
        $a = "malicious"
        $b = "exploit"
        $c = "keylogger"

    condition:
        any of them
}
''',
            "Suspicious_API": '''
rule Suspicious_API
{
    meta:
        description = "Suspicious API usage"
        author = "RedSentrix"
        threat_level = 4

    strings:
        $a = "VirtualAllocEx"
        $b = "WriteProcessMemory"
        $c = "CreateRemoteThread"

    condition:
        any of them
}
'''
        }

    def compile_embedded_rules(self):
        rule_files = {}
        temp_files = []

        try:
            for name, content in self.embedded_rules.items():
                temp = tempfile.NamedTemporaryFile(delete=False, suffix=".yar")
                temp.write(content.encode())
                temp.close()
                temp_files.append(temp.name)
                rule_files[name] = temp.name

            self.rules = yara.compile(filepaths=rule_files)
        finally:
            for file_path in temp_files:
                os.unlink(file_path)

    def get_rules(self):
        if not self.rules:
            self.compile_embedded_rules()
        return self.rules

# Example usage
if __name__ == "__main__":
    y = YARAAutoLoader()
    compiled = y.get_rules()
    print("[+] Loaded rules:", compiled)
