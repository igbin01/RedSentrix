import os
import re
import requests
import yara
import logging
from datetime import datetime
from modules.session_logger import secure_log

YARA_FEED_URLS = [
    "https://raw.githubusercontent.com/Yara-Rules/rules/master/malware/MALW_Loader.yar",
    "https://raw.githubusercontent.com/Yara-Rules/rules/master/malware/MALW_Infostealer.yar",
    "https://raw.githubusercontent.com/Yara-Rules/rules/master/malware/MALW_Generic.yar",
]

LOCAL_CACHE_PATH = "resources/yara_rules_auto.yar"

def fetch_yara_rules():
    compiled_rules = []
    all_rules = ""

    for url in YARA_FEED_URLS:
        try:
            secure_log(f"🌐 Fetching YARA rules from {url}")
            response = requests.get(url, timeout=8)
            if response.status_code == 200:
                rule_text = clean_yara(response.text)
                all_rules += rule_text + "\n"
            else:
                logging.warning(f"[YARA Fetch] Failed to fetch {url}")
        except Exception as e:
            logging.error(f"[YARA Fetch] {url} - {str(e)}")

    if all_rules.strip():
        with open(LOCAL_CACHE_PATH, "w") as f:
            f.write(all_rules)
        secure_log("✅ YARA rules updated and cached.")
    else:
        secure_log("⚠️ No YARA rules fetched. Using cached rules.")

    return compile_cached_yara()

def clean_yara(yara_text):
    """Removes comments and unnecessary lines to improve compilation reliability"""
    lines = yara_text.splitlines()
    cleaned = [line for line in lines if not line.strip().startswith('//')]
    return "\n".join(cleaned)

def compile_cached_yara():
    if not os.path.exists(LOCAL_CACHE_PATH):
        raise FileNotFoundError("No local YARA cache exists.")

    try:
        rules = yara.compile(filepath=LOCAL_CACHE_PATH)
        secure_log("🎯 YARA rules compiled successfully.")
        return rules
    except yara.SyntaxError as e:
        logging.error(f"[YARA Compilation] Syntax error: {e}")
        return None
