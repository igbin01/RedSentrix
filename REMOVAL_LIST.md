# Components to Remove

## Directories to Remove:
1. `nebula_core/` - Duplicate core functionality
2. `redsentrix_backend/` - FastAPI backend (not needed)
3. `redsentrix_frontend/` - React frontend (not needed)
4. `redsentrix-frontend/` - Duplicate frontend
5. `mesh/` - Mesh networking (not needed)
6. `log/` - Old logging system
7. `logs/` - Old logs (keep structure, remove old files)
8. `test space/` - Test directory
9. `stealth_core/` - Empty/duplicate
10. `stealth_plugins/` - Empty/duplicate
11. `stealth_tests/` - Test files
12. `stealth_utils/` - Will be integrated into C layer

## Files to Remove:
1. `redsentrrix_gui.py` - GUI not needed (typo in name too)
2. `redsentrix_launcher.py` - GUI launcher
3. `redsentrix_modular_setup.py` - Setup script
4. `cpu_test.py` - Test file
5. `inject_test.py` - Test file
6. `dummy_*.py` - Test files
7. `dummy_*.sh` - Test files
8. `dummy_*.bin` - Test files
9. `malicious_payload.bin` - Test payload
10. `test_*.py` - All test files
11. `test_*.yar` - Test YARA rules
12. `*.log` - Old log files
13. `*.enc` - Old encrypted logs
14. `*.redlog` - Old log format
15. `session_log*.txt` - Old session logs
16. `RedSentrixLogs_*.txt` - Old log files
17. `encoded_result.txt` - Test output
18. `creds.txt` - Should not be in repo
19. `auto_yara.yar` - Move to config if needed

## Modules to Remove/Consolidate:
1. `modules/recon_sysinfo.py` - Keep advanced version
2. `modules/reon_network_advanced.py` - Typo, remove
3. `modules/stealth_mem_scanner.py` - Consolidate with stealth_memory_scanner.py
4. `modules/memory_scanner.py` - Redundant
5. `modules/demo.py` - Demo file
6. `modules/test_module.py` - Test file
7. `modules/sleep_timer.py` - Not needed
8. `modules/persistence_checker.py` - Will be in C layer
9. `modules/rootkit_detector.py` - Not needed for malware
10. `modules/kernel_exploit_enumerator.py` - Not core functionality

## Keep but Refactor:
- `redsentrix_core/` → Refactor into new `core/`
- `modules/` → Reorganize into new structure
- `core/` → Merge with redsentrix_core
- `config/` → Keep and enhance
- `requirements.txt` → Update for new dependencies

