import os
import importlib
import logging


class PluginManager:

    def __init__(self):
        self.plugins = []

    def register(self, plugin):
        logging.info(f"Registered plugin: {plugin.name}")
        self.plugins.append(plugin)

    def load_plugins(self):
        folder = "plugins"

        for file in sorted(os.listdir(folder)):
            if not file.endswith(".py") or file == "base.py":
                continue

            module_name = file[:-3]

            try:
                module = importlib.import_module(f"plugins.{module_name}")
                plugin = module.Plugin()
                self.register(plugin)
            except Exception as e:
                logging.error(f"Failed to load plugin '{file}': {e}")

    def trigger(self, event, *args, **kwargs):
        for plugin in self.plugins:
            if not getattr(plugin, "enabled", True):
                continue

            func = getattr(plugin, event, None)
            if not callable(func):
                continue

            try:
                func(*args, **kwargs)
            except Exception as e:
                logging.error(f"[PLUGIN ERROR] {plugin.name} -> {event}: {e}")
