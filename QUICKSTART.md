# RedSentrix 2.0 Quick Start Guide

## Prerequisites

- **Go** 1.21 or later
- **GCC** (for C compilation)
- **Python** 3.8 or later
- **Make** (for building C libraries)

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Build C stealth libraries:**
```bash
cd stealth
make
cd ..
```

3. **Build Go phishing proxy:**
```bash
cd phishing
go mod download
go build -o ../build/phishing/proxy ./proxy
cd ..
```

Or use the Python build command:
```bash
python main.py --build
```

## Configuration

1. **Create configuration file:**
```bash
mkdir -p config
python -c "from core.config import Config; Config('config/phishing.yaml')"
```

2. **Edit `config/phishing.yaml`:**
```yaml
phishing:
  port: 8080
  target_url: "https://example.com"
  cert_path: "build/phishing/cert.pem"
  key_path: "build/phishing/key.pem"
  domains: ["example.com"]

c2:
  enabled: false
  url: "https://c2.example.com"
  key: ""
  interval: 60

payload:
  stage: 1
  obfuscate: true
  encrypt: true
  method: "shellcode"

modules:
  - "phishing.embedder"
  - "dropper.dropper"

stealth:
  evasion: true
  injection_method: 2
  persistence: true
```

## Usage

### Generate SSL Certificate

```bash
cd phishing
go run proxy/main.go -gen-cert -domain example.com
cd ..
```

### Start Phishing Proxy

```bash
python main.py -m phishing
```

### Generate Payload Only

```bash
python main.py -m payload
```

### C2 Mode

```bash
python main.py -m c2
```

## Architecture Overview

- **Go Proxy**: Handles HTTP/HTTPS reverse proxy, credential harvesting
- **C Libraries**: Low-level stealth operations (injection, evasion, persistence)
- **Python Core**: Orchestration, module loading, payload generation

## Module Development

Create modules in `modules/` directory:

```python
# modules/my_module.py
from core.logger import Logger

def run():
    logger = Logger()
    logger.log("My module executed", "info")
```

Add to `config/phishing.yaml`:
```yaml
modules:
  - "my_module"
```

## Troubleshooting

### C Library Build Fails
- Ensure GCC is installed
- Check Makefile paths
- Verify C source files exist

### Go Build Fails
- Run `go mod download` in `phishing/` directory
- Check Go version: `go version`
- Verify all Go files compile

### Python Import Errors
- Ensure you're running from project root
- Check `core/__init__.py` exists
- Verify Python path includes project root

## Next Steps

1. Read `ARCHITECTURE.md` for detailed architecture
2. Review `REMOVAL_LIST.md` for cleanup
3. Check `REDESIGN_SUMMARY.md` for overview
4. Customize configuration for your needs
5. Develop custom modules

## Security Notice

This framework is designed for:
- Legitimate security research
- Authorized penetration testing
- Red team exercises
- Educational purposes

**Always ensure proper authorization before use.**

