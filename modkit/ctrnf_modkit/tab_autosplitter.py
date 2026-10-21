"""Onglet Autosplitter : copier CTRNF.asl où LiveSplit le trouvera, et expliquer comment le charger."""
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser

from . import _paths, theme

STEPS = ("1. Installer LiveSplit (livesplit.org), version 1.8 ou plus récente.",
         "2. Clic droit sur LiveSplit > « Edit Layout… » > « + » > « Control » > « Scriptable Auto Splitter ».",
         "3. Double-cliquer sur la ligne ajoutée, « Browse… », choisir CTRNF.asl (le dossier ci-dessus).",
         "4. Cocher ce qui doit couper le chrono, puis OK et enregistrer le layout.",
         "5. Préparer ses splits (clic droit > « Edit Splits… ») : un segment par split attendu, dans l'ordre.")
SETTINGS = ("Départ auto : une partie neuve (rien gagné, aucune cinématique vue) arrive en jeu.",
            "Splits au choix : trophée, clé de boss, Oxide battu, vraie fin (cochés) ; relique, gemme, jeton CTR.",
            "Charger une autre sauvegarde ne coupe pas le chrono.")
LIMITS = ("Pas encore de retrait des temps de chargement : le chrono compte le temps réel.",
          "La fin contre Oxide coupe à la cinématique ; le split à la ligne d'arrivée est en préparation.")


class AutosplitterTab(ttk.Frame):
    def __init__(self, parent, ctx, module):
        super().__init__(parent, padding=10)
        self.ctx, self.module = ctx, module
        self.columnconfigure(1, weight=1)
        conf = ctx.config.module(module.id)
        self.dest = tk.StringVar(master=self, value=conf.get("dest") or "")
        theme.alpha_banner(self, "Version alpha : tout début de développement. Le départ et les splits trophée / clé "
                                 "sont à valider en jeu, la fin contre Oxide coupe encore à la cinématique, et il n'y a "
                                 "pas de retrait des chargements. Vos retours sont les bienvenus !").grid(
            row=0, column=0, columnspan=4, sticky="ew", pady=(0, 10))
        ttk.Label(self, text="Le script LiveSplit lit la partie en cours (sans rien changer au jeu) et coupe le chrono "
                             "tout seul pendant le mode Aventure, avec ou sans randomizer.",
                  wraplength=860, justify="left").grid(row=0, column=0, columnspan=4, sticky="w", pady=(60, 0))
        ttk.Label(self, text="Dossier où copier CTRNF.asl :").grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(self, textvariable=self.dest).grid(row=1, column=1, sticky="ew", padx=6, pady=(10, 0))
        ttk.Button(self, text="Parcourir…", command=self.browse).grid(row=1, column=2, pady=(10, 0))
        row = ttk.Frame(self)
        row.grid(row=2, column=0, columnspan=4, sticky="w", pady=(6, 0))
        ttk.Button(row, text="Copier CTRNF.asl", command=self.copy).pack(side="left")
        ttk.Button(row, text="Ouvrir le dossier", command=self.open_folder).pack(side="left", padx=6)
        ttk.Button(row, text="Télécharger LiveSplit", command=lambda: webbrowser.open("https://livesplit.org")).pack(
            side="left")
        self.state = ttk.Label(self, text="")
        self.state.grid(row=3, column=0, columnspan=4, sticky="w", pady=(6, 0))
        for r, (title, lines) in enumerate((("Dans LiveSplit", STEPS), ("Réglages du script", SETTINGS),
                                            ("Limites de cette version", LIMITS)), start=4):
            box = ttk.LabelFrame(self, text=title, padding=8)
            box.grid(row=r, column=0, columnspan=4, sticky="ew", pady=(10, 0))
            for line in lines:
                ttk.Label(box, text=line, wraplength=840, justify="left").pack(anchor="w")
        self.update_state()

    def browse(self):
        folder = filedialog.askdirectory(title="Dossier pour CTRNF.asl", initialdir=self.dest.get() or None)
        if folder:
            self.dest.set(folder)

    def copy(self):
        folder = self.dest.get().strip()
        if not folder or not Path(folder).is_dir():
            messagebox.showerror("CTRNF Mod Kit", "Choisissez d'abord un dossier existant (par exemple celui de "
                                                  "LiveSplit).")
            return
        target = Path(folder) / "CTRNF.asl"
        overwrite = self.module.modified(target) and messagebox.askyesno(
            "CTRNF Mod Kit", f"{target} est le script du kit retouché à la main. Le remplacer par la version du kit "
                             "(vos changements seront perdus) ?")
        try:
            target = self.module.install(self.ctx, folder, overwrite_modified=overwrite)
        except Exception as error:  # ModuleError ou OSError : on montre le message
            messagebox.showerror("CTRNF Mod Kit", f"Copie impossible : {error}")
            return
        self.ctx.say(f"CTRNF.asl copié : {target}")
        self.update_state()

    def open_folder(self):
        folder = self.dest.get().strip()
        if folder and Path(folder).is_dir() and hasattr(os, "startfile"):
            os.startfile(folder)

    def update_state(self):
        if not _paths.asl().is_file():
            self.state.configure(text="✗ CTRNF.asl introuvable dans le kit.", foreground=theme.BAD)
            return
        self.state.configure(text=f"Version du script : {self.module.version()} ; "
                                  f"{self.module.status(self.ctx)}.", foreground=theme.MUTED)
