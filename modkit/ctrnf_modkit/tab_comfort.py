"""Onglet Confort : les options de confort du randomizer sur le jeu d'origine (patches/Confort.xml et archive des
podiums rapides), sans tirer de graine."""
import tkinter as tk
from tkinter import messagebox, ttk

from . import theme
from .i18n import tr

# (option de ctrnf_rando.comfort.OPTIONS, texte de la case, clé de l'aide du randomizer)
BOXES = (("relic_targets", "Reliques : viser le platine, puis l'or, puis le saphir pendant la course", "relics"),
         ("boost_reserve", "Afficher la réserve de boost dans la barre de dérapage", "reserve"),
         ("fast_podiums", "Pouvoir passer les podiums dès le début", "podiums"),
         ("skip_hints", "Passer les indices d'Aku Aku et les cinématiques des portes", "hints"),
         ("relic_retry", "Fin des courses relique : Recommencer / Continuer, gagnée ou perdue", "retry"))


class ComfortTab(ttk.Frame):
    def __init__(self, parent, ctx, module):
        from ctrnf_rando import gui
        super().__init__(parent, padding=10)
        self.ctx, self.module = ctx, module
        self.columnconfigure(0, weight=1)
        conf = ctx.config.module(module.id)
        ttk.Label(self, text=tr("Ces options marchent sur le jeu d'origine, sans randomizer : votre partie et vos "
                                "sauvegardes ne changent pas. Avec une graine du randomizer installée, ce sont les "
                                "réglages de cet onglet qui comptent."), wraplength=860, justify="left").grid(
            row=0, column=0, sticky="w")
        box = ttk.LabelFrame(self, text=tr(" Options "), padding=10)
        box.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        self.vars = {}
        for r, (option, text, key) in enumerate(BOXES):
            self.vars[option] = tk.BooleanVar(master=self, value=conf.get(option, True))
            ttk.Checkbutton(box, text=tr(text), variable=self.vars[option]).grid(row=2 * r, column=0, sticky="w",
                                                                            pady=(0 if r == 0 else 6, 0))
            ttk.Label(box, text=gui.tr(gui.HELP[key]), style="Muted.TLabel", wraplength=820, justify="left").grid(
                row=2 * r + 1, column=0, sticky="w", padx=(24, 0))
        row = ttk.Frame(self)
        row.grid(row=2, column=0, sticky="w", pady=(10, 0))
        ttk.Button(row, text=tr("Installer le confort"), command=self.install).pack(side="left")
        ttk.Button(row, text=tr("Retirer"), command=self.remove).pack(side="left", padx=6)
        self.state = ttk.Label(self, text="", wraplength=860, justify="left")
        self.state.grid(row=3, column=0, sticky="w", pady=(8, 0))
        ttk.Label(self, text=tr("Le patch est lu au lancement du jeu : relancez-le s'il est ouvert."),
                  style="Muted.TLabel").grid(row=4, column=0, sticky="w", pady=(4, 0))
        ctx.on_port_change(self.update_state)
        self.load_installed()
        self.update_state()

    def values(self):
        return {option: var.get() for option, var in self.vars.items()}

    def load_installed(self):
        """Les cases reprennent ce qui est posé dans le port, s'il y a un Confort.xml."""
        from ctrnf_rando import comfort
        if self.ctx.port.folder:
            installed = comfort.read_settings(self.ctx.port.folder)
            for option, value in (installed or {}).items():
                if option in self.vars:
                    self.vars[option].set(value)

    def ready(self):
        if not (self.ctx.port.folder and self.ctx.port.ok):
            messagebox.showerror("CTRNF Mod Kit", tr("Choisissez d'abord le dossier du port dans l'onglet Accueil (il "
                                                     "doit être vérifié)."))
            return False
        return True

    def install(self):
        from ctrnf_rando import app, comfort
        if not self.ready():
            return
        if app.game_running() and not messagebox.askokcancel(
                "CTRNF Mod Kit", tr("Le jeu est ouvert : le confort ne servira qu'au prochain lancement. Continuer ?")):
            return
        try:
            notes = comfort.install(self.ctx.port.folder, self.values())
        except (ValueError, OSError) as error:
            messagebox.showerror("CTRNF Mod Kit", tr("Installation impossible : {error}", error=error))
            return
        self.ctx.config.set_module(self.module.id, self.values())
        for note in notes:
            self.ctx.say(note)
        self.update_state()

    def remove(self):
        if not self.ready():
            return
        try:
            notes = self.module.uninstall(self.ctx)
        except OSError as error:
            messagebox.showerror("CTRNF Mod Kit", tr("Impossible de retirer : {error}", error=error))
            return
        for note in notes or [tr("Rien à retirer.")]:
            self.ctx.say(note)
        self.update_state()

    def update_state(self):
        if not (self.ctx.port.folder and self.ctx.port.ok):
            self.state.configure(text=tr("Dossier du port pas encore choisi ou pas vérifié (onglet Accueil)."),
                                 foreground=theme.MUTED)
            return
        self.state.configure(text=tr("État : {state}.", state=self.module.status(self.ctx)), foreground=theme.MUTED)
