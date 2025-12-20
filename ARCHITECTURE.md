# RedSentrix 2.0 - Advanced Phishing + Stealth Malware Framework

## Architecture Overview

Multi-language framework combining Evilginx2-inspired phishing capabilities with advanced stealth malware techniques.

### Language Distribution

- **Go**: Phishing proxy, HTTP/HTTPS handling, session management, C2 communication
- **C**: Low-level stealth operations, memory injection, process manipulation, rootkit features
- **Python**: Orchestration layer, module system, high-level logic, integration glue

---

## Core Components

### 1. Phishing Proxy (Go) - `phishing/`
Inspired by Evilginx2, handles:
- Reverse proxy for credential harvesting
- SSL/TLS termination and certificate generation
- Session hijacking and cookie stealing
- Real-time credential extraction
- Template-based phishing pages
- Multi-site support

**Key Files:**
- `phishing/proxy/proxy.go` - Main proxy server
- `phishing/sessions/session.go` - Session management
- `phishing/certs/cert.go` - Certificate generation
- `phishing/templates/template.go` - Phishing page templates

### 2. Stealth Malware Core (C) - `stealth/`
Low-level operations for evasion:
- Process injection (DLL injection, shellcode injection)
- Memory manipulation (hiding payloads in memory)
- Anti-debugging techniques
- Sandbox evasion
- Rootkit-like process/file hiding
- Persistence mechanisms (registry, services, etc.)

**Key Files:**
- `stealth/inject/inject.c` - Process injection
- `stealth/memory/memory.c` - Memory manipulation
- `stealth/evasion/evasion.c` - Anti-debugging/sandbox
- `stealth/persistence/persistence.c` - Persistence mechanisms
- `stealth/hide/hide.c` - Process/file hiding

### 3. Orchestration Layer (Python) - `core/`
High-level coordination:
- Module loading and execution
- C2 communication
- Payload generation and embedding
- Configuration management
- Logging and encryption
- Integration between Go and C components

**Key Files:**
- `core/orchestrator.py` - Main orchestrator
- `core/module_loader.py` - Dynamic module loading
- `core/payload_builder.py` - Payload generation
- `core/c2_client.py` - C2 communication
- `core/config.py` - Configuration management

### 4. Embedded Payload System
- Payload embedded within phishing pages
- Multi-stage dropper system
- Encrypted payloads
- Polymorphic capabilities

---

## Directory Structure

```
RedSentrix/
├── phishing/              # Go-based phishing proxy
│   ├── proxy/
│   │   ├── proxy.go       # Main proxy server
│   │   ├── handler.go     # Request/response handlers
│   │   └── middleware.go  # Middleware for logging/injection
│   ├── sessions/
│   │   ├── session.go     # Session management
│   │   └── storage.go     # Session storage
│   ├── certs/
│   │   ├── cert.go        # Certificate generation
│   │   └── ca.go          # CA management
│   ├── templates/
│   │   └── template.go    # Template engine
│   └── go.mod
│
├── stealth/               # C-based stealth operations
│   ├── inject/
│   │   ├── inject.c       # Process injection
│   │   ├── dll_inject.c   # DLL injection
│   │   └── shellcode.c    # Shellcode injection
│   ├── memory/
│   │   ├── memory.c       # Memory operations
│   │   └── hide_mem.c     # Memory hiding
│   ├── evasion/
│   │   ├── anti_debug.c   # Anti-debugging
│   │   └── sandbox.c      # Sandbox evasion
│   ├── persistence/
│   │   ├── persistence.c  # Persistence mechanisms
│   │   └── registry.c     # Windows registry
│   ├── hide/
│   │   ├── hide_proc.c    # Process hiding
│   │   └── hide_file.c    # File hiding
│   └── Makefile
│
├── core/                  # Python orchestration
│   ├── orchestrator.py    # Main orchestrator
│   ├── module_loader.py   # Module system
│   ├── payload_builder.py # Payload generation
│   ├── c2_client.py       # C2 communication
│   ├── config.py          # Configuration
│   ├── logger.py          # Logging
│   └── crypto.py          # Encryption utilities
│
├── modules/               # Python modules
│   ├── phishing/
│   │   └── embedder.py    # Embed payload in phishing
│   ├── dropper/
│   │   └── dropper.py     # Multi-stage dropper
│   └── c2/
│       └── beacon.py      # C2 beacon
│
├── payloads/              # Payload storage
│   ├── stage1/            # Initial dropper
│   ├── stage2/            # Secondary payload
│   └── final/             # Final payload
│
├── config/                # Configuration files
│   ├── phishing.yaml      # Phishing config
│   ├── c2.yaml            # C2 config
│   └── modules.yaml       # Module config
│
├── build/                 # Build artifacts
│   ├── phishing/          # Compiled Go binaries
│   └── stealth/           # Compiled C libraries
│
└── main.py                # Entry point
```

---

## Components to REMOVE

### Unnecessary/Redundant:
1. `nebula_core/` - Duplicate core functionality
2. `redsentrix_backend/` - FastAPI backend (not needed for malware)
3. `redsentrix_frontend/` - React frontend (not needed)
4. `redsentrix-frontend/` - Duplicate frontend
5. `mesh/` - Mesh networking (not needed)
6. `cli/` - CLI interface (keep minimal)
7. `tests/` - Test files (remove for production)
8. `log/` - Old logging system
9. `logs/` - Old logs directory
10. Multiple duplicate modules:
    - `recon_sysinfo.py` / `recon_sysinfo_advanced.py` (keep advanced)
    - `recon_network_advanced.py` / `reon_network_advanced.py` (typo, remove)
    - `stealth_mem_scanner.py` / `stealth_memory_scanner.py` (consolidate)
    - `memory_scanner.py` (redundant)

### Keep but Refactor:
- `redsentrix_core/` - Refactor into new `core/`
- `modules/` - Keep but reorganize
- Stealth utilities - Integrate into C layer

---

## Components to ADD

### New Go Components:
1. **Phishing Proxy** (`phishing/proxy/`)
   - HTTP/HTTPS reverse proxy
   - SSL certificate generation
   - Session management
   - Credential extraction

2. **Template Engine** (`phishing/templates/`)
   - Dynamic phishing page generation
   - Payload embedding
   - Multi-site support

### New C Components:
1. **Process Injection** (`stealth/inject/`)
   - DLL injection
   - Shellcode injection
   - Process hollowing
   - Reflective DLL loading

2. **Memory Operations** (`stealth/memory/`)
   - Memory allocation hiding
   - Encrypted memory regions
   - Memory scanning evasion

3. **Evasion Techniques** (`stealth/evasion/`)
   - Anti-debugging
   - Sandbox detection
   - VM detection
   - Timing checks

4. **Persistence** (`stealth/persistence/`)
   - Windows registry
   - Service installation
   - Scheduled tasks
   - Startup folder

5. **Hiding Mechanisms** (`stealth/hide/`)
   - Process hiding
   - File hiding
   - Network hiding

### New Python Components:
1. **Orchestrator** (`core/orchestrator.py`)
   - Coordinates Go and C components
   - Manages execution flow
   - Handles errors and recovery

2. **Payload Builder** (`core/payload_builder.py`)
   - Generates multi-stage payloads
   - Embeds payloads in phishing pages
   - Encrypts and obfuscates

3. **C2 Client** (`core/c2_client.py`)
   - HTTP/HTTPS C2 communication
   - Encrypted channels
   - Command execution

4. **Module System** (`core/module_loader.py`)
   - Dynamic module loading
   - Module dependencies
   - Execution sandboxing

---

## Integration Flow

```
1. User runs main.py
   ↓
2. Python orchestrator initializes
   ↓
3. Loads configuration (phishing targets, C2 server, etc.)
   ↓
4. Starts Go phishing proxy
   ↓
5. Generates phishing pages with embedded payloads
   ↓
6. When victim visits phishing page:
   - Go proxy intercepts request
   - Serves phishing page with embedded payload
   - Victim enters credentials
   - Credentials extracted and sent to C2
   - Payload executes on victim machine
   ↓
7. Payload execution:
   - C library handles process injection
   - Stealth mechanisms activate
   - Establishes persistence
   - Connects to C2 via Python client
   ↓
8. C2 communication:
   - Python C2 client maintains connection
   - Receives commands
   - Executes via C libraries
   - Returns results
```

---

## Build System

### Go Components:
```bash
cd phishing/
go mod init redsentrix-phishing
go build -o ../build/phishing/proxy ./proxy
```

### C Components:
```bash
cd stealth/
make all  # Compiles all C libraries
```

### Python:
```bash
pip install -r requirements.txt
python main.py
```

---

## Security Considerations

1. **Encryption**: All communications encrypted
2. **Obfuscation**: Payloads obfuscated and polymorphic
3. **Stealth**: Multiple evasion techniques
4. **Persistence**: Multiple persistence mechanisms
5. **Modularity**: Easy to add/remove components

---

## Next Steps

1. Create new directory structure
2. Implement Go phishing proxy
3. Implement C stealth libraries
4. Refactor Python core
5. Create integration layer
6. Build and test

