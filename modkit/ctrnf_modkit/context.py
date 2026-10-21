"""Ce que la fenêtre du kit partage avec les onglets : le dossier du port (une seule variable pour tous les mods), ce
qu'on en sait (port.PortInfo) et les réglages."""
import tkinter as tk

from . import port


class Context:
    def __init__(self, root, config, say=print):
        self.root = root
        self.config = config
        self.say = say
        self.listeners = []
        self.port_var = tk.StringVar(master=root, value=config.data.get("port", ""))
        self.port = self.resolve()
        self._pending = None
        self.port_var.trace_add("write", lambda *_: self._schedule())

    def resolve(self):
        return port.resolve(self.port_var.get(), self.config.data.get("game_dir_override"),
                            self.config.data["launch"].get("launcher_exe"))

    def _schedule(self):
        if self._pending:
            self.root.after_cancel(self._pending)
        self._pending = self.root.after(400, self.refresh)

    def refresh(self):
        """Relit le dossier du port, l'enregistre et prévient les onglets."""
        self._pending = None
        self.port = self.resolve()
        self.config.data["port"] = self.port_var.get().strip()
        self.config.save()
        for callback in list(self.listeners):
            callback()

    def on_port_change(self, callback):
        self.listeners.append(callback)

    def for_module(self, name):
        return ModuleContext(self, name)


class ModuleContext:
    """Ce que reçoit la fenêtre d'un mod (App(parent, context=...)) : le dossier commun et ses propres réglages."""

    def __init__(self, kit, name):
        self.kit = kit
        self.name = name
        self.port_var = kit.port_var
        self.root = kit.root

    def module_config(self):
        return self.kit.config.module(self.name)

    def save_module_config(self, values):
        self.kit.config.set_module(self.name, values)

    def archives(self):
        """Dossier archives du jeu déjà trouvé par le kit, ou None."""
        return self.kit.port.archives

    def on_port_change(self, callback):
        self.kit.on_port_change(callback)
