import requests
import yara
import threading
import time
import logging
from datetime import datetime

class ThreatFeedIntegration:
    def __init__(self, feed_urls, update_interval=3600, yara_rules_path="yara_rules_compiled.yar", logger=None):
        """
        :param feed_urls: list of URLs to download YARA rules from
        :param update_interval: seconds between update checks
        :param yara_rules_path: file path to save compiled YARA rules
        :param logger: optional logger instance
        """
        self.feed_urls = feed_urls
        self.update_interval = update_interval
        self.yara_rules_path = yara_rules_path
        self.logger = logger or self._setup_logger()
        self._stop_event = threading.Event()
        self.compiled_rules = None

    def _setup_logger(self):
        logger = logging.getLogger("ThreatFeedIntegration")
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler("threat_feed_integration.log")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger

    def download_rules(self):
        combined_rules = ""
        self.logger.info("Starting YARA rules download from feeds...")
        for url in self.feed_urls:
            try:
                self.logger.info(f"Fetching YARA rules from {url}")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                combined_rules += response.text + "\n"
                self.logger.info(f"Successfully fetched rules from {url}")
            except Exception as e:
                self.logger.error(f"Failed to fetch rules from {url}: {e}")
        return combined_rules

    def compile_and_save_rules(self, rules_text):
        try:
            compiled = yara.compile(source=rules_text)
            compiled.save(self.yara_rules_path)
            self.compiled_rules = compiled
            self.logger.info(f"Compiled and saved YARA rules to {self.yara_rules_path}")
            return True
        except yara.Error as e:
            self.logger.error(f"Failed to compile YARA rules: {e}")
            return False

    def load_compiled_rules(self):
        try:
            self.compiled_rules = yara.load(self.yara_rules_path)
            self.logger.info(f"Loaded compiled YARA rules from {self.yara_rules_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load compiled YARA rules: {e}")
            return False

    def update_loop(self):
        while not self._stop_event.is_set():
            self.logger.info("Running scheduled threat feed update...")
            rules_text = self.download_rules()
            if rules_text and self.compile_and_save_rules(rules_text):
                self.logger.info("YARA rules updated successfully.")
            else:
                self.logger.warning("YARA rules update failed or no rules downloaded.")
            time.sleep(self.update_interval)

    def start(self):
        self._stop_event.clear()
        thread = threading.Thread(target=self.update_loop, daemon=True)
        thread.start()
        self.logger.info("ThreatFeedIntegration update loop started.")

    def stop(self):
        self._stop_event.set()
        self.logger.info("ThreatFeedIntegration update loop stopped.")
