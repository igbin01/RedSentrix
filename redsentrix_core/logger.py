import os
from datetime import datetime

class StealthLogger:
    def __init__(self, log_dir='log', log_file='nebula.log'):
        self.log_path = os.path.join(log_dir, log_file)
        os.makedirs(log_dir, exist_ok=True)

    def log(self, module_name, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {module_name}: {message}\n"

        try:
            with open(self.log_path, 'a') as log_file:
                log_file.write(log_entry)
        except Exception:
            pass  # Silently fail — stealthy

def setup():
    global logger
    logger = StealthLogger()

