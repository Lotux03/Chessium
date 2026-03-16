import os
import importlib
import logging


class PluginManager:

    def __init__(self):

        self.plugins = []

    def trigger(self, event, *args, **kwargs):

        for plugin in self.plugins:   # <-- iterate the list

            if not getattr(plugin, "enabled", True):
                continue

            func = getattr(plugin, event, None)

            if not callable(func):
                continue

            try:
                func(*args, **kwargs)

            except Exception as e:
                print(f"[PLUGIN ERROR] {plugin.name} -> {event}")
                print(e)

    def register(self, plugin):

        logging.info(f"Loaded plugin: {plugin.name}")

        self.plugins.append(plugin)

    def load_plugins(self):

        folder = "plugins"

        for file in os.listdir(folder):

            if file.endswith(".py") and file != "base.py":

                name = file[:-3]

                try:

                    module = importlib.import_module(
                        f"plugins.{name}"
                    )

                    plugin = module.Plugin()

                    self.register(plugin)

                except Exception as e:

                    logging.error(f"Plugin failed: {file}")
                    logging.error(e)