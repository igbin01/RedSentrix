import os
import importlib.util

PLUGIN_DIR = "plugins/"
LOADED_PLUGINS = {}

def discover_plugins():
    """Scans the plugin directory and returns valid plugin filenames."""
    plugins = []
    if not os.path.exists(PLUGIN_DIR):
        os.makedirs(PLUGIN_DIR)

    for filename in os.listdir(PLUGIN_DIR):
        if filename.endswith(".py") or filename.endswith(".rsplugin"):
            plugins.append(filename)
    return plugins

def load_plugin(filepath):
    """Dynamically load a RedSentrix-compatible plugin."""
    plugin_name = os.path.splitext(filepath)[0]
    full_path = os.path.join(PLUGIN_DIR, filepath)

    spec = importlib.util.spec_from_file_location(plugin_name, full_path)
    if not spec:
        return None

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        if hasattr(module, "initialize_plugin"):
            LOADED_PLUGINS[plugin_name] = module
            return module
        else:
            print(f"⚠️ Plugin {plugin_name} missing 'initialize_plugin' entry point.")
    except Exception as e:
        print(f"❌ Error loading plugin {plugin_name}: {e}")
    return None

def load_all_plugins():
    plugins = discover_plugins()
    for plugin_file in plugins:
        load_plugin(plugin_file)

def get_loaded_plugins():
    return LOADED_PLUGINS
