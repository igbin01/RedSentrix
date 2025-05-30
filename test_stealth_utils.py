# test_stealth_utils.py

from redsentrix_core.stealth_utils import StealthUtils

def test_secure_print():
    print("Testing secure_print:")
    StealthUtils.secure_print("This is a secure print message.")

def test_debugger_detection():
    print("Testing debugger detection:")
    if StealthUtils.is_debugger_present():
        print("Debugger detected!")
    else:
        print("No debugger detected.")

def test_sandbox_check():
    print("Testing sandbox check:")
    if StealthUtils.sandbox_check():
        print("Sandbox environment detected!")
    else:
        print("No sandbox detected.")

if __name__ == "__main__":
    test_secure_print()
    test_debugger_detection()
    test_sandbox_check()
