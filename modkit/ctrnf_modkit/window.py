"""Fenêtre du CTRNF Mod Kit : accueil (dossier du port, mods, fichiers posés), un onglet par mod, à propos, et le
bouton « Lancer le jeu »."""
import os
import platform
from pathlib import Path
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser

from . import AUTHOR, HOME, __version__, _paths, config, i18n, launch, port, report, theme
from .context import Context
from .i18n import tr
from .modules import ABSENT, FOREIGN, PRESENT, REGISTRY, backup_folder

NAME = "CTRNF Mod Kit"
POLL_MS = 5000


class KitWindow(ttk.Frame):
    def __init__(self, root, conf=None):
        super().__init__(root, padding=0)
        self.root = root
        self.config = conf or config.Config()
        i18n.set_language(self.config.data.get("language", "fr"))
        self.modern = theme.apply(root)
        root.title(tr("CTRNF Mod Kit {version} — par {author}", version=__version__, author=AUTHOR))
        root.minsize(980, 740)
        self.grid(sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.ctx = Context(root, self.config, say=self.say)
        self.tabs = {}      # id du mod -> cadre de l'onglet (construit à la première ouverture)
        self.built = set()
        self.running = False
        self.closed = False
        self.seen_names = None  # réponse du dernier tasklist (rempli par un thread, lu ici)
        self.process = None     # démarrage de secours en cours
        self.starting = None    # bouton « Lancer » bloqué juste après un lancement
        self.shown_crash = None
        root.report_callback_exception = self.on_error

        self.build_header().grid(row=0, column=0, sticky="ew")
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=12, pady=(10, 0))
        self.notebook.add(self.build_home(), text=tr("Accueil"))
        for m in REGISTRY:
            frame = ttk.Frame(self.notebook)
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)
            self.tabs[m.id] = frame
            self.notebook.add(frame, text=tr("{name} (alpha)", name=tr(m.name)) if m.stage else tr(m.name))
        self.notebook.add(self.build_about(), text=tr("À propos"))
        self.notebook.bind("<<NotebookTabChanged>>", lambda _: self.tab_changed())
        self.build_bottom().grid(row=2, column=0, sticky="ew", padx=12, pady=10)
        for m in REGISTRY:
            self.show_tab(m)
        self.ctx.on_port_change(self.refresh)
        self.refresh()
        if self.config.warning:
            self.say(tr(self.config.warning))
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.after(500, self.poll)

    # --- construction -------------------------------------------------------------------------------------------
    def build_header(self):
        bar = theme.header(self, NAME, tr("Mods pour Crash Team Racing Nitro-Fueled (PC)   ·   version {version}"
                                          "   ·   par {author}", version=__version__, author=AUTHOR),
                           HOME.replace("https://", ""), lambda: webbrowser.open(HOME))
        box = tk.Frame(bar, background=theme.DARK)
        box.pack(side="right", anchor="s", padx=(0, 18))
        tk.Label(box, text=tr("Langue :"), background=theme.DARK, foreground="#b8c0cc").pack(side="left")
        self.language = tk.StringVar(master=self.root, value=i18n.LANGUAGES[i18n.current])
        choice = ttk.Combobox(box, textvariable=self.language, values=list(i18n.LANGUAGES.values()),
                              state="readonly", width=10)
        choice.pack(side="left", padx=(6, 0))
        choice.bind("<<ComboboxSelected>>", lambda _: self.change_language())
        return bar

    def build_home(self):
        page = ttk.Frame(self.notebook, padding=14)
        page.columnconfigure(0, weight=1)
        page.rowconfigure(2, weight=1)

        box = ttk.LabelFrame(page, text=tr(" Jeu "), padding=12)
        box.grid(row=0, column=0, sticky="ew")
        box.columnconfigure(1, weight=1)
        ttk.Label(box, text=tr("Dossier du port :")).grid(row=0, column=0, sticky="w")
        ttk.Entry(box, textvariable=self.ctx.port_var).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(box, text=tr("Parcourir…"), command=self.browse).grid(row=0, column=2)
        self.port_label = ttk.Label(box, text="", wraplength=860, justify="left")
        self.port_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))
        self.game_label = ttk.Label(box, text="", style="Muted.TLabel", wraplength=860, justify="left")
        self.game_label.grid(row=2, column=0, columnspan=3, sticky="w")
        self.last_label = ttk.Label(box, text="", foreground="#555", wraplength=760, justify="left")
        self.last_label.grid(row=3, column=0, columnspan=2, sticky="w")
        self.report_button = ttk.Button(box, text=tr("Voir le rapport"), command=self.show_last_report)
        self.report_button.grid(row=3, column=2, sticky="e")
        self.report_button.grid_remove()

        box = ttk.LabelFrame(page, text=tr(" Mods "), padding=12)
        box.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        box.columnconfigure(1, weight=1)
        self.mod_status = {}
        for r, m in enumerate(REGISTRY):
            var = tk.BooleanVar(master=self.root, value=m.id in self.config.data["enabled"])
            pady = (0 if r == 0 else 10, 0)
            ttk.Checkbutton(box, variable=var, command=lambda m=m, v=var: self.toggle(m, v.get())).grid(
                row=2 * r, column=0, rowspan=2, sticky="w", pady=pady)
            title = ttk.Frame(box)
            title.grid(row=2 * r, column=1, sticky="w", pady=pady)
            ttk.Label(title, text=tr(m.name), style="Name.TLabel").pack(side="left")
            ttk.Label(title, text=f"  {m.version()}", style="Muted.TLabel").pack(side="left")
            if m.stage:
                ttk.Label(title, text=m.stage.upper(), style="Alpha.TLabel").pack(side="left", padx=(8, 0))
            ttk.Label(box, text=tr(m.description), style="Muted.TLabel").grid(row=2 * r + 1, column=1, sticky="w")
            self.mod_status[m.id] = ttk.Label(box, text="")
            self.mod_status[m.id].grid(row=2 * r, column=2, rowspan=2, sticky="e", padx=10, pady=pady)
            ttk.Button(box, text=tr("Ouvrir"), command=lambda m=m: self.open_tab(m)).grid(
                row=2 * r, column=3, rowspan=2, pady=pady)

        box = ttk.LabelFrame(page, text=tr(" Fichiers posés par les mods "), padding=12)
        box.grid(row=2, column=0, sticky="nsew", pady=(12, 0))
        box.columnconfigure(0, weight=1)
        box.rowconfigure(0, weight=1)
        columns = ("file", "folder", "mod", "state", "size")
        self.files = ttk.Treeview(box, columns=columns, show="headings", height=6)
        for col, text, width in zip(columns, (tr("Fichier"), tr("Dossier"), tr("Mod"), tr("État"), tr("Taille")),
                                    (150, 380, 110, 150, 80)):
            self.files.heading(col, text=text)
            self.files.column(col, width=width, anchor="w")
        self.files.grid(row=0, column=0, sticky="nsew")
        row = ttk.Frame(box)
        row.grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Button(row, text=tr("Actualiser"), command=self.refresh).pack(side="left")
        ttk.Button(row, text=tr("Ouvrir le dossier du jeu"), command=self.open_game_folder).pack(side="left", padx=6)
        ttk.Button(row, text=tr("Tout désinstaller…"), command=self.uninstall_all).pack(side="left")
        ttk.Label(box, text=tr("Aucun mod ne modifie les fichiers du jeu : chacun pose ses propres fichiers, et un "
                               "fichier qui n'est pas à lui n'est jamais touché."), style="Muted.TLabel").grid(
            row=2, column=0, sticky="w", pady=(6, 0))
        return page

    def build_about(self):
        page = ttk.Frame(self.notebook, padding=18)
        ttk.Label(page, text=f"{NAME} {__version__}", style="Section.TLabel").pack(anchor="w")
        ttk.Label(page, text=tr("Auteur : {author}", author=AUTHOR)).pack(anchor="w", pady=(6, 0))
        link = ttk.Label(page, text=HOME, foreground=theme.ACCENT, cursor="hand2")
        link.pack(anchor="w")
        link.bind("<Button-1>", lambda _: webbrowser.open(HOME))
        ttk.Label(page, text=tr("Licence MIT : utilisation, modification et partage autorisés, en gardant le nom "
                                "de l'auteur."), wraplength=860, justify="left").pack(anchor="w", pady=(6, 0))
        box = ttk.LabelFrame(page, text=tr(" Mods "), padding=12)
        box.pack(anchor="w", fill="x", pady=(12, 0))
        for m in REGISTRY:
            ttk.Label(box, text=f"{tr(m.name)} {m.version()}" + (f"  ({m.stage})" if m.stage else "")).pack(anchor="w")
        ttk.Label(page, text=tr("Crédits : idée du randomizer inspirée du CTR-Randomizer d'icebound777 (version PS1, "
                                "MIT). Le jeu tourne avec le port CTR-NitroFueled-PC / OCTR-NitroFueled-PC (GPL), que "
                                "le kit lance sans l'inclure. Sans affiliation avec Sony, Activision ou Beenox."),
                  wraplength=860, justify="left", style="Muted.TLabel").pack(anchor="w", pady=(12, 0))
        ttk.Button(page, text=tr("Copier les versions"), command=self.copy_versions).pack(anchor="w", pady=(10, 0))
        return page

    def build_bottom(self):
        row = ttk.Frame(self)
        row.columnconfigure(1, weight=1)
        self.game_state = ttk.Label(row, text=tr("Jeu fermé"), style="Muted.TLabel")
        self.game_state.grid(row=0, column=0, sticky="w")
        self.message = ttk.Label(row, text="")
        self.message.grid(row=0, column=1, sticky="w", padx=10)
        self.mode = tk.StringVar(master=self.root, value=tr(launch.MODES.get(self.config.data["launch"].get("mode"),
                                                                             launch.MODES["launcher"])))
        ttk.Combobox(row, textvariable=self.mode, values=[tr(launch.MODES[m]) for m in launch.SHOWN], state="readonly",
                     width=42).grid(row=0, column=2, padx=6)
        self.launch_button = ttk.Button(row, text=tr("Lancer le jeu"), command=self.launch,
                                        style=theme.launch_style(self.modern))
        self.launch_button.grid(row=0, column=3)
        return row

    # --- onglets des mods ---------------------------------------------------------------------------------------
    def show_tab(self, module):
        frame = self.tabs[module.id]
        if module.id in self.config.data["enabled"]:
            self.notebook.add(frame)
        else:
            self.notebook.hide(frame)

    def toggle(self, module, on):
        enabled = [m.id for m in REGISTRY if (m.id in self.config.data["enabled"] and m.id != module.id)
                   or (m.id == module.id and on)]
        self.config.data["enabled"] = enabled
        self.config.save()
        self.show_tab(module)
        present = [f for f in self.safe_files(module) if f.state == PRESENT]
        if not on and present:
            listing = "\n".join(f"  • {f.path.name} : {tr(f.what)}" for f in present)
            if port.game_running():
                messagebox.showinfo(NAME, tr("{name} est décoché : son onglet est caché, mais ses fichiers restent dans "
                                             "le jeu (le mod s'applique toujours) :\n{listing}\n\nLe jeu est ouvert : "
                                             "fermez-le, puis utilisez « Tout désinstaller » pour les supprimer.",
                                             name=tr(module.name), listing=listing))
            elif messagebox.askyesno(NAME, tr("{name} est décoché : son onglet est caché. Ses fichiers sont encore "
                                              "dans le jeu, donc le mod s'applique toujours :\n{listing}\n\n"
                                              "Oui : SUPPRIMER ces fichiers (le mod ne s'appliquera plus au jeu).\n"
                                              "Non : les garder (le mod reste actif, seul l'onglet est caché).",
                                              name=tr(module.name), listing=listing) + self.backup_note([module])):
                messagebox.showinfo(NAME, "\n".join(self.uninstall([module])) or tr("Rien à retirer."))
        self.refresh()

    def open_tab(self, module):
        if module.id not in self.config.data["enabled"]:
            self.say(tr("{name} est désactivé : cochez-le pour ouvrir son onglet.", name=tr(module.name)))
            return
        self.notebook.select(self.tabs[module.id])

    def tab_changed(self):
        if self.notebook.index("current") == 0:
            self.refresh()
        self.build_current()

    def build_current(self):
        current = self.notebook.select()
        for m in REGISTRY:
            frame = self.tabs[m.id]
            if str(frame) == current and m.id not in self.built:
                self.built.add(m.id)
                ok, why = m.available()
                if not ok:
                    ttk.Label(frame, text=tr("{name} indisponible : {why}", name=tr(m.name), why=why),
                              foreground="#b00").grid(padx=10, pady=10)
                    return
                self.root.config(cursor="watch")
                self.root.update_idletasks()
                try:
                    m.build_tab(frame, self.ctx).grid(row=0, column=0, sticky="nsew")
                except Exception as error:  # un onglet cassé ne doit pas fermer le kit
                    for child in frame.winfo_children():
                        child.destroy()
                    ttk.Label(frame, text=tr("{name} : erreur à l'ouverture ({error})", name=tr(m.name), error=error),
                              foreground="#b00").grid(padx=10, pady=10)
                finally:
                    self.root.config(cursor="")

    # --- état ---------------------------------------------------------------------------------------------------
    def safe_files(self, module):
        try:
            return module.files(self.ctx)
        except Exception:  # fichier illisible, etc. : l'accueil doit rester utilisable
            return []

    def refresh(self):
        info = self.ctx.port
        self.port_label.configure(text=("✓ " if info.ok else "✗ ") + " ; ".join(info.messages),
                                  foreground=theme.OK if info.ok else theme.BAD)
        game = tr("Dossier du jeu : {folder} (lu dans launcher.ini)", folder=info.game_dir) if info.game_dir else ""
        if info.game_dir:
            game += tr(". Les archives des mods y sont posées : elles servent aussi aux autres ports qui l'utilisent.")
        self.game_label.configure(text=game)
        try:
            summary = launch.last_run_summary(info.folder) if info.ok else ""
            rep = launch.last_run_report(info.folder) if info.ok else None
        except OSError:
            summary, rep = "", None
        if rep and rep["crashed"]:
            summary += "\n✗ " + tr("Le jeu s'est arrêté : {why}.", why=rep["meaning"])
            self.report_button.grid()
        else:
            self.report_button.grid_remove()
        self.last_label.configure(text=summary, foreground=theme.BAD if rep and rep["crashed"] else theme.MUTED)
        self.files.delete(*self.files.get_children())
        for m in REGISTRY:
            try:
                status = m.status(self.ctx) if info.ok or m.id == "autosplitter" else tr("port à choisir")
            except Exception as error:
                status = tr("état illisible ({error})", error=error)
            self.mod_status[m.id].configure(text=status)
            for f in self.safe_files(m):
                size = tr("{n} Ko", n=-(-f.size // 1024)) if f.state != ABSENT else ""
                self.files.insert("", "end", values=(f.path.name, str(f.path.parent), tr(f.module), tr(f.state), size))

    def poll(self):
        """Toutes les 5 s : tasklist dans un thread (il peut être lent), résultat repris ici, dans le thread de Tk."""
        if self.closed:
            return
        if self.seen_names is not None:
            names, self.seen_names = self.seen_names, None
            self.set_running(names)

        names = self.launcher_names()

        def work():
            self.seen_names = port.running(port.GAME_PROCESS, *names)

        threading.Thread(target=work, daemon=True).start()
        self.after(POLL_MS, self.poll)

    def set_running(self, names):
        game = port.GAME_PROCESS.lower() in names
        launcher = bool(set(names) - {port.GAME_PROCESS.lower()})
        if self.running and not game:  # le jeu vient de se fermer : planté ?
            self.after(1500, self.check_crash)
        self.running = game
        self.game_state.configure(text=tr("● Jeu en cours") if game else tr("● Launcher ouvert") if launcher
                                  else tr("Jeu fermé"),
                                  foreground=theme.OK if game or launcher else theme.MUTED)
        if game or not self.starting:
            self.launch_button.configure(state="disabled" if game else "normal",
                                         text=tr("Jeu en cours") if game else tr("Lancer le jeu"))

    def check_crash(self):
        """Après la fermeture du jeu : si le journal dit qu'il a planté, montrer le rapport (une fois par lancement)."""
        self.refresh()
        try:
            rep = launch.last_run_report(self.ctx.port.folder)
        except OSError:
            return
        if rep and rep["crashed"] and (rep["log"], rep["started"]) != self.shown_crash:
            self.shown_crash = (rep["log"], rep["started"])
            report.show_crash(self.root, self.ctx, rep)

    def show_last_report(self):
        try:
            rep = launch.last_run_report(self.ctx.port.folder)
        except OSError as error:
            messagebox.showerror(NAME, tr("Journal du port illisible : {error}", error=error))
            return
        if rep:
            report.show_crash(self.root, self.ctx, rep)

    def on_error(self, kind, value, tb):
        """Erreur dans un bouton ou un onglet : rapport lisible au lieu d'une erreur invisible (exe sans console)."""
        import traceback
        report.show_error(self.root, self.ctx, tr("fenêtre"), "".join(traceback.format_exception(kind, value, tb)))

    # --- actions ------------------------------------------------------------------------------------------------
    def say(self, text):
        self.message.configure(text=text)

    def browse(self):
        folder = filedialog.askdirectory(title=tr("Dossier du port CTR-NitroFueled-PC / OCTR"),
                                         initialdir=self.ctx.port_var.get() or None)
        if folder:
            self.ctx.port_var.set(folder)

    def open_game_folder(self):
        folder = self.ctx.port.archives or self.ctx.port.game_dir
        if folder and folder.is_dir() and hasattr(os, "startfile"):
            os.startfile(folder)

    def backup_note(self, modules):
        if any(m.id == "stickers" for m in modules):
            return "\n\n" + tr("Vos autocollants (update3.pak) sont d'abord copiés dans « {folder} ».",
                                 folder=backup_folder())
        return ""

    def uninstall(self, modules):
        report = []
        for m in modules:
            try:
                report += m.uninstall(self.ctx)
            except Exception as error:
                report.append(f"{tr(m.name)} : {error}")
        if self.ctx.port.archives:  # un autocollant retiré peut laisser un trou dans la chaîne update3/4/5
            from ctrnf_rando import archives
            try:
                report += [f"{name} {tr(what)}" for name, what in archives.fix_chain(self.ctx.port.archives)]
            except (OSError, ValueError) as error:
                report.append(str(error))
        foreign = [f"{f.path.name} ({tr(f.module)})" for m in modules for f in self.safe_files(m)
                   if f.state == FOREIGN]
        if foreign:
            report.append(tr("Non touchés (pas à nous) : ") + ", ".join(foreign))
        self.refresh()
        return report

    def uninstall_all(self):
        if port.game_running():
            messagebox.showerror(NAME, tr("Le jeu est ouvert : fermez-le avant de désinstaller."))
            return
        if not self.ctx.port.ok or not self.ctx.port.archives:
            messagebox.showerror(NAME, tr("Choisissez d'abord le bon dossier du port (avec le dossier du jeu "
                                          "trouvé) : sans lui, le kit ne peut pas savoir ce qui est posé."))
            return
        present = [f for m in REGISTRY for f in self.safe_files(m) if f.state == PRESENT]
        if not present:
            messagebox.showinfo(NAME, tr("Aucun fichier des mods n'est posé."))
            return
        listing = "\n".join(f"• {f.path}" for f in present)
        if not messagebox.askokcancel(NAME, tr("Retirer ces fichiers ? Le jeu redeviendra celui d'origine (vos "
                                               "graines et vos sauvegardes sont gardées).\n\n{listing}",
                                               listing=listing) + self.backup_note(REGISTRY)):
            return
        report = self.uninstall(list(REGISTRY))
        messagebox.showinfo(NAME, "\n".join(report) or tr("Rien à retirer."))

    def launch(self):
        info = self.ctx.port = self.ctx.resolve()
        mode = next((k for k, v in launch.MODES.items() if tr(v) == self.mode.get()), "launcher")
        self.config.data["launch"]["mode"] = mode
        self.config.save()
        if port.game_running():
            messagebox.showinfo(NAME, tr("Le jeu est déjà ouvert."))
            return
        try:
            p = launch.plan(info, mode, self.config.data["launch"].get("direct_arg") or "--play")
        except ValueError as error:
            messagebox.showerror(NAME, str(error))
            return
        warnings = [w for m in REGISTRY if m.id in self.config.data["enabled"] for w in self.safe_warnings(m)]
        if warnings and not messagebox.askokcancel(NAME, "\n\n".join(warnings) + "\n\n" + tr("Lancer quand même ?")):
            return
        if p.shell and port.running(*self.launcher_names()):
            messagebox.showinfo(NAME, tr("Le launcher est déjà ouvert : cliquez sur JOUER dans sa fenêtre."))
            return
        if self.starting or (self.process is not None and self.process.poll() is None):
            messagebox.showinfo(NAME, tr("Le jeu est déjà en train de démarrer."))
            return
        try:
            self.process = launch.start(p)
        except OSError as error:
            messagebox.showerror(NAME, tr("Impossible de démarrer : {error}", error=error))
            return
        self.say(p.description)
        # le jeu (ou le launcher) met quelques secondes à apparaître : pas de second lancement entre-temps
        self.launch_button.configure(state="disabled", text=tr("Démarrage…"))
        self.starting = self.after(15000, self.end_starting)

    def end_starting(self):
        self.starting = None
        if not self.running and not self.closed:
            self.launch_button.configure(state="normal", text=tr("Lancer le jeu"))

    def launcher_names(self):
        launcher = self.ctx.port.launcher
        return (*port.LAUNCHER_NAMES, launcher.name) if launcher else port.LAUNCHER_NAMES

    def safe_warnings(self, module):
        try:
            return module.warnings(self.ctx)
        except Exception:
            return []

    def copy_versions(self):
        lines = [f"{NAME} {__version__}"] + [f"{tr(m.name)} {m.version()}" for m in REGISTRY]
        lines.append(tr("Port : {version}", version=self.ctx.port.version or tr("inconnu")))
        lines.append(f"Windows : {platform.platform()}")
        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(lines))
        self.say(tr("Versions copiées."))

    def change_language(self):
        """Nouvelle langue : enregistrée, puis la fenêtre est refaite (onglets des mods compris)."""
        code = next((k for k, v in i18n.LANGUAGES.items() if v == self.language.get()), "fr")
        if code == i18n.current:
            return
        self.config.data["language"] = code
        self.config.save()
        if self.ctx._pending:  # dossier tapé il y a moins de 400 ms : l'enregistrer d'abord
            self.root.after_cancel(self.ctx._pending)
            self.ctx.refresh()
        if self.starting:
            self.after_cancel(self.starting)
        self.closed = True
        root, conf, previous = self.root, self.config, i18n.current
        self.destroy()
        try:
            KitWindow(root, conf)
        except Exception:  # jamais de fenêtre vide : retour à la langue d'avant, erreur gardée dans le journal
            import traceback
            trace = traceback.format_exc()
            report.log(f"Changement de langue ({code}) :\n{trace}")
            for child in root.winfo_children():
                child.destroy()
            conf.data["language"] = previous
            conf.save()
            KitWindow(root, conf)
            messagebox.showerror(NAME, tr("Changement de langue impossible :\n\n{trace}\n\n(gardé dans {log})",
                                          trace=trace, log=report.log_path()))

    def close(self):
        if self.ctx._pending:  # dossier tapé il y a moins de 400 ms : l'enregistrer quand même
            self.root.after_cancel(self.ctx._pending)
            self.ctx.refresh()
        self.closed = True
        self.root.destroy()


def selftest(out):
    """Vérifie que tout se charge (pour la recette de l'exe, qui n'a pas de console) : écrit le rapport dans `out`."""
    import importlib
    import traceback
    lines = []
    for name in ("ctrnf_rando.gui", "ctrnf_rando.share", "ctrnf_rando.relic_menu", "ctrnf_rando.igz",
                 "ctrnf_stickers.gui", "ctrnf_stickers.names", "ctrnf_modkit.lang_en", "ctrnf_rando.lang_en",
                 "ctrnf_stickers.lang_en", "numpy", "PIL"):
        try:
            importlib.import_module(name)
            lines.append(f"OK {name}")
        except Exception:
            lines.append(f"KO {name}\n{traceback.format_exc()}")
    lines.append(("OK " if _paths.asl().is_file() else "KO ") + f"asl {_paths.asl()}")
    lines += [f"version {m.name} {m.version()}" for m in REGISTRY]
    # ce que le jeu hériterait de l'exe du kit sans nettoyage (DLL et Python de l'exe : risque de plantage)
    risky = sorted(k for k in os.environ if k.startswith(("_PYI", "_MEI")) or k in launch.FROZEN_ENV)
    leaked = sorted(launch.clean_env(dict(os.environ)).keys() & set(risky))
    in_path = [p for p in os.environ.get("PATH", "").split(os.pathsep) if "_MEI" in p]
    lines.append(f"env exe : {risky} ; après nettoyage : {leaked} ; PATH avec _MEI : {in_path}")
    Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")


def selftest_ui(out):
    """Recette de l'exe : ouvre la fenêtre (avec une copie des réglages), ouvre chaque onglet comme le bouton
    « Ouvrir », note les erreurs, puis referme. Écrit le rapport dans `out`."""
    import shutil
    import tempfile
    import traceback
    lines, errors = [], []
    tmp = Path(tempfile.mkdtemp()) / "kit.json"
    if config.path().is_file():
        shutil.copyfile(config.path(), tmp)
    root = tk.Tk()
    try:
        win = KitWindow(root, config.Config(tmp))
        root.report_callback_exception = lambda kind, value, tb: errors.append(
            "".join(traceback.format_exception(kind, value, tb)))
        lines.append(f"port : {win.ctx.port.ok} {win.ctx.port.messages}")
        for m in REGISTRY:
            win.open_tab(m)
            for _ in range(40):
                root.update()
            children = [type(c).__name__ for c in win.tabs[m.id].winfo_children()]
            lines.append(f"onglet {m.id} : {children} ; fenêtre ouverte : {bool(root.winfo_exists())}")
        win.notebook.select(0)
        root.update()
        lines.append(f"thème moderne : {win.modern}")
    except Exception:
        lines.append("KO\n" + traceback.format_exc())
    lines += [f"erreur : {e}" for e in errors]
    try:
        root.destroy()
    except tk.TclError:
        pass
    Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    _paths.setup()
    if len(sys.argv) > 2 and sys.argv[1] == "--selftest":
        selftest(sys.argv[2])
        return
    if len(sys.argv) > 2 and sys.argv[1] == "--selftest-ui":
        selftest_ui(sys.argv[2])
        return
    root = tk.Tk()
    try:
        KitWindow(root)
    except Exception:  # pas de console dans l'exe : montrer l'erreur et la garder dans le journal du kit
        import traceback
        trace = traceback.format_exc()
        report.log(f"Erreur au démarrage :\n{trace}")
        messagebox.showerror(NAME, tr("Le kit n'a pas pu démarrer :\n\n{trace}\n\n(gardé dans {log})", trace=trace,
                                      log=report.log_path()))
        root.destroy()
        return
    root.mainloop()
