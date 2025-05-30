import os
import csv
import json
from datetime import datetime

LOG_FILE = "redsentrix_combined.log"

class LogAnalytics:
    def __init__(self, log_file=LOG_FILE):
        self.log_file = log_file

    def _parse_log_line(self, line):
        try:
            # Format: "2025-05-29 14:22:10,400 - INFO - Message"
            timestamp, level, message = line.strip().split(" - ", 2)
            return {
                "timestamp": timestamp,
                "level": level,
                "message": message
            }
        except Exception:
            return None

    def read_logs(self):
        if not os.path.exists(self.log_file):
            return []
        with open(self.log_file, "r") as f:
            lines = f.readlines()
        return [self._parse_log_line(line) for line in lines if self._parse_log_line(line)]

    def filter_logs(self, level=None, keyword=None, after=None, before=None):
        logs = self.read_logs()
        filtered = []
        for log in logs:
            if not log:
                continue
            if level and log["level"].lower() != level.lower():
                continue
            if keyword and keyword.lower() not in log["message"].lower():
                continue
            if after and datetime.strptime(log["timestamp"], "%Y-%m-%d %H:%M:%S,%f") < after:
                continue
            if before and datetime.strptime(log["timestamp"], "%Y-%m-%d %H:%M:%S,%f") > before:
                continue
            filtered.append(log)
        return filtered

    def export_logs_csv(self, output_path="exported_logs.csv", filtered_logs=None):
        logs = filtered_logs or self.read_logs()
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "level", "message"])
            writer.writeheader()
            for log in logs:
                writer.writerow(log)
        return output_path

    def export_logs_json(self, output_path="exported_logs.json", filtered_logs=None):
        logs = filtered_logs or self.read_logs()
        with open(output_path, "w") as f:
            json.dump(logs, f, indent=4)
        return output_path
