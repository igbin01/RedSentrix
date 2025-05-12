import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from RedSentrix.core import NebulaCore

from RedSentrix.core import NebulaCore
import sys

def main():
    print("\n🌀 Welcome to RedSentrix CLI 🌀")
    nebula = NebulaCore()

    if len(sys.argv) < 2:
        print("Usage: python cli.py [module_name | list | all]")
        return

    module_name = sys.argv[1]

    if module_name == 'list':
        print("\n📦 Available Modules:")
        for mod in nebula.discover_modules():
            print(f"  - {mod}")
        return

    if module_name == 'all':
        modules = nebula.discover_modules()
        for mod in modules:
            print(f"[+] Loading and executing: {mod}")
            nebula.load_module(mod)
            nebula.execute_module(mod)
        return

    # Load and execute a single module
    print(f"[+] Loading module: {module_name}")
    nebula.load_module(module_name)
    print(f"[+] Executing module: {module_name}")
    nebula.execute_module(module_name)

if __name__ == "__main__":
    main()

