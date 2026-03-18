import tkinter as tk


class GUI:

    def __init__(self, plugin_manager):
        self.plugins = plugin_manager.plugins
        self.root = tk.Tk()
        self.root.title("Chessium")
        self._vars = {}

        tk.Label(self.root, text="Chessium Plugins", font=("Arial", 14)).pack(pady=5)

        for plugin in self.plugins:
            var = tk.BooleanVar(value=plugin.enabled)
            self._vars[plugin.name] = var

            tk.Checkbutton(
                self.root,
                text=plugin.name,
                variable=var,
                command=lambda p=plugin, v=var: self._toggle(p, v)
            ).pack(anchor="w", padx=10)

    def _toggle(self, plugin, var):
        plugin.enabled = var.get()
        print(f"[GUI] {plugin.name} -> {'on' if plugin.enabled else 'off'}")

    def run(self):
        print("[GUI] Starting")
        self.root.mainloop()
