"""Rapports d'erreur lisibles : plantage du jeu (lu dans le journal du port) ou erreur du kit. Le texte se copie d'un
clic pour être collé dans un message, au lieu d'une capture d'écran ; les erreurs du kit vont aussi dans un journal."""
import datetime
import os
from pathlib import Path
import platform
import re
import tkinter as tk
from tkinter import filedialog, ttk

from . import __version__, launch
from .modules import REGISTRY


def log_path():
    return Path.home() / ".ctrnf_modkit.log"


def log(text):
    """Ajoute au journal du kit (gardé petit : les 200 derniers Ko)."""
    path = log_path()
    try:
        old = path.read_text(encoding="utf-8", errors="replace")[-200_000:] if path.is_file() else ""
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        path.write_text(old + f"\n===== {stamp}\n{text}\n", encoding="utf-8")
    except OSError:
        pass


def context_lines(ctx):
    """Versions, port, mods activés, fichiers posés et graine : ce qu'il faut pour comprendre un problème."""
    info = ctx.port
    lines = [f"CTRNF Mod Kit {__version__} ; " + ", ".join(f"{m.name} {m.version()}" for m in REGISTRY),
             f"Windows : {platform.platform()}",
             f"Port : {info.folder} ({info.version or 'version inconnue'})",
             f"Dossier du jeu : {info.game_dir or 'inconnu'}",
             "Mods activés : " + ", ".join(ctx.config.data.get("enabled", []))]
    for m in REGISTRY:
        try:
            files = m.files(ctx)
        except Exception as error:  # le rapport doit sortir même si un mod est abîmé
            lines.append(f"{m.name} : fichiers illisibles ({error})")
            continue
        for f in files:
            lines.append(f"  {f.path.name} : {f.state}")
    xml = info.folder / "patches" / "Randomizer.xml" if info.folder else None
    if xml and xml.is_file():
        head = xml.read_text(encoding="utf-8", errors="replace")[:600]
        seed = re.search(r"graine (\d+)", head)
        lines.append(f"Graine du randomizer : {seed.group(1) if seed else '?'}")
    return lines


def crash_text(ctx, rep):
    lines = [f"Le jeu s'est arrêté : {rep['meaning']}", f"Lancé le {rep['started']}, journal : {rep['log']}", ""]
    lines += context_lines(ctx)
    lines += ["", "Patchs appliqués : " + (", ".join(f"{n} ({w})" for n, w in rep["patches"]) or "aucun"),
              "", f"Dernières lignes du journal ({len(rep['tail'])}) :"] + rep["tail"]
    return "\n".join(lines)


def hints(rep):
    """Pistes lisibles selon le code et le journal."""
    out = []
    code = rep["code"]
    if code == 0xC0000005 and any("AI controlled racer" in line for line in rep["tail"][-5:]):
        out.append("Plantage pendant la création des pilotes IA : défaut connu des anciennes versions du port, corrigé "
                   "dans OCTR v0.5.1 ou plus récent.")
    if code == 3:
        out.append("Code 3 au démarrage : mettre à jour le port (OCTR v0.5.1 ou plus récent).")
    if code in (0xC0000005, 0xC0000374) and any("Randomizer" in n for n, _ in rep["patches"]):
        out.append("Si le plantage revient au même endroit, refaites l'essai sans le randomizer (« Tout désinstaller » "
                   "ou décochez-le) pour savoir s'il en est la cause, et envoyez ce rapport.")
    return out


class ReportWindow(tk.Toplevel):
    def __init__(self, master, title, summary, text, log_file=None):
        super().__init__(master)
        self.title(title)
        self.minsize(720, 480)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        ttk.Label(self, text=summary, foreground="#b00", wraplength=700, justify="left",
                  font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 6))
        box = ttk.Frame(self)
        box.grid(row=1, column=0, sticky="nsew", padx=10)
        box.columnconfigure(0, weight=1)
        box.rowconfigure(0, weight=1)
        self.text = tk.Text(box, wrap="none", font=("Consolas", 9))
        self.text.insert("1.0", text)
        self.text.configure(state="disabled")  # lecture seule, mais sélectionnable
        self.text.grid(row=0, column=0, sticky="nsew")
        for orient, row, col in (("vertical", 0, 1), ("horizontal", 1, 0)):
            bar = ttk.Scrollbar(box, orient=orient,
                                command=self.text.yview if orient == "vertical" else self.text.xview)
            bar.grid(row=row, column=col, sticky="ns" if orient == "vertical" else "ew")
            self.text.configure(**{"yscrollcommand" if orient == "vertical" else "xscrollcommand": bar.set})
        buttons = ttk.Frame(self)
        buttons.grid(row=2, column=0, sticky="w", padx=10, pady=10)
        self.done = ttk.Label(buttons, text="")
        ttk.Button(buttons, text="Copier le rapport", command=lambda: self.copy(text)).pack(side="left")
        ttk.Button(buttons, text="Enregistrer…", command=lambda: self.save(text)).pack(side="left", padx=6)
        if log_file and Path(log_file).is_file() and hasattr(os, "startfile"):
            ttk.Button(buttons, text="Ouvrir le journal", command=lambda: os.startfile(log_file)).pack(side="left")
        ttk.Button(buttons, text="Fermer", command=self.destroy).pack(side="left", padx=6)
        self.done.pack(side="left", padx=6)

    def copy(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.done.configure(text="Copié : collez-le dans votre message.")

    def save(self, text):
        path = filedialog.asksaveasfilename(parent=self, title="Enregistrer le rapport", defaultextension=".txt",
                                            initialfile="rapport_ctrnf.txt", filetypes=[("Texte", "*.txt")])
        if path:
            Path(path).write_text(text, encoding="utf-8")
            self.done.configure(text=f"Enregistré : {path}")


def show_crash(master, ctx, rep):
    text = crash_text(ctx, rep)
    tips = hints(rep)
    summary = f"Le jeu s'est arrêté : {rep['meaning']}." + ("\n" + "\n".join(tips) if tips else "")
    return ReportWindow(master, "CTRNF Mod Kit — le jeu s'est arrêté", summary, text, rep["log"])


def show_error(master, ctx, where, trace):
    text = f"Erreur du kit ({where}) :\n{trace}\n"
    try:
        text += "\n" + "\n".join(context_lines(ctx))
    except Exception:
        pass
    log(text)
    return ReportWindow(master, "CTRNF Mod Kit — erreur", "Une erreur est survenue dans le kit. Copiez le rapport et "
                        f"envoyez-le (il est aussi gardé dans {log_path()}).", text, log_path())
