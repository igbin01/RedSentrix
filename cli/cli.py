import argparse
import importlib
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["list", "run", "all"])
    parser.add_argument("module", nargs="?")

    args, unknown = parser.parse_known_args()

    if args.action == "run" and args.module:
        try:
            print(f"Attempting to load: {args.module}")
            module = importlib.import_module(f"modules.{args.module}")

            # Universal module argument parser
            module_parser = argparse.ArgumentParser()
            module_parser.add_argument("--process", help="Target process name")
            module_parser.add_argument("--pattern", help="Pattern to search")
            module_parser.add_argument("--pid", type=int, help="Target PID")
            module_parser.add_argument("--covert", help="Encoding type (e.g., xor, base64)")
            module_parser.add_argument("--key", help="Encoding key")
            module_parser.add_argument("--entropy", action="store_true", help="Enable entropy scan mode")

            module_args = module_parser.parse_args(unknown)

            if hasattr(module, "main"):
                module.main(module_args)
            else:
                print(f"Module {args.module} has no main(args) method.")
        except Exception as e:
            print(f"Error loading module {args.module}: {e}")

if __name__ == "__main__":
    main()

