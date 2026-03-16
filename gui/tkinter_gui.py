import tkinter as tk


class GUI:

    def __init__(self, plugin_manager):

        self.plugins = plugin_manager.plugins
        self.root = tk.Tk()
        self.root.title("Chessium")

        # store variables so they don't get garbage collected
        self.vars = {}

        title = tk.Label(self.root, text="Chessium Plugins", font=("Arial", 14))
        title.pack(pady=5)

        for plugin in self.plugins:

            var = tk.BooleanVar(value=plugin.enabled)

            self.vars[plugin.name] = var

            cb = tk.Checkbutton(
                self.root,
                text=plugin.name,
                variable=var,
                command=lambda p=plugin, v=var: self.toggle(p, v)
            )

            cb.pack(anchor="w", padx=10)

            print(f"[GUI] Loaded plugin: {plugin.name}")

    def toggle(self, plugin, var):

        plugin.enabled = var.get()

        print(f"[PLUGIN TOGGLE] {plugin.name} -> {plugin.enabled}")

    def run(self):

        print("[GUI] Starting Tkinter loop")
        self.root.mainloop()
