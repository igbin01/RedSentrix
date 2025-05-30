import importlib
import argparse
import sys
import logging

# Use a local stealth_utils inside redsentrix_core
from redsentrix_core.stealth_utils import log_stealth

def load_and_run_module(module_name, args):
    module_paths = [f"redsentrix_core.{module_name}", f"modules.{module_name}"]

    for path in module_paths:
        try:
            module = importlib.import_module(path)
            if hasattr(module, "main"):
                sys.argv = [f"{module_name}.py"] + args
                log_stealth(f"Executing module: {path}", level="info")
                module.main()
                return
            else:
                log_stealth(f"Module '{path}' has no main() function.", level="warn")
        except ModuleNotFoundError:
            continue
        except Exception as e:
            log_stealth(f"Error in module '{path}': {e}", level="error")
            return

    log_stealth(f"Module '{module_name}' not found in known paths.", level="error")

def main():
    parser = argparse.ArgumentParser(description="RedSentrix Stealth Module Loader")
    parser.add_argument("--module", required=True, help="Module name to run (from redsentrix_core or modules)")
    args, unknown_args = parser.parse_known_args()

    load_and_run_module(args.module, unknown_args)

if __name__ == "__main__":
    main()

