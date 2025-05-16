# === redsentrix_modular_setup.py ===
# This script will help modularize RedSentrix architecture for flexibility, stealth, and maintainability.

# --- [1] Create Git Initialization Script ---
import os

def initialize_git_repo():
    if not os.path.exists(".git"):
        os.system("git init")
        os.system("echo '__pycache__/\n*.log\n*.pyc\n' > .gitignore")
        print("[+] Git repo initialized with .gitignore")
    else:
        print("[!] Git already initialized.")

# --- [2] Folder Structure Setup ---
def create_module_structure():
    folders = [
        "stealth_core",       # Core modules like scanners, enumerators
        "stealth_utils",      # Encoders, loggers, entropy, covert tools
        "stealth_plugins",    # Optional plug-ins (dynamic loaders)
        "stealth_tests"       # Sandbox test scripts
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    print("[+] Modular folder structure created.")

# --- [3] Sample Helper Modules ---
utils_code = '''
# === stealth_utils/logger.py ===
import datetime

def log_stealth(message, level="info"):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = {"info": "[*]", "warn": "[!]", "err": "[!!]"}.get(level, "[*]")
    print(f"{prefix} [{now}] {message}")
'''

def create_sample_utils():
    os.makedirs("stealth_utils", exist_ok=True)
    with open("stealth_utils/logger.py", "w") as f:
        f.write(utils_code)
    print("[+] Sample logger utility created.")

# --- [4] Git Commit Starter ---
def first_commit():
    os.system("git add .")
    os.system("git commit -m 'Initial RedSentrix modular setup'")
    print("[+] First commit made.")

# --- [5] Main Runner ---
if __name__ == "__main__":
    initialize_git_repo()
    create_module_structure()
    create_sample_utils()
    first_commit()

