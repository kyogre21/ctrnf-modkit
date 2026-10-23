"""Petit logiciel du randomizer : choisir le dossier du port, régler les options, générer et installer une graine.
Lancement : python -m ctrnf_rando.gui"""
import os
from pathlib import Path
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from . import __version__, app, share
from .i18n import tr
from .generator import ORIGINS, Settings

TITLE = f"CTR Nitro-Fueled Randomizer {__version__}"

# Aide affichée en bas de la fenêtre quand la souris passe sur une option.
HELP = {
    "port": "Le dossier du port CTR-NitroFueled-PC (celui qui contient bin, patches et out). Le logiciel vérifie que "
            "le jeu est bien la version 1.21 attendue par le patch.",
    "seed": "La graine décide de tout le tirage : la même graine avec les mêmes réglages donne la même partie. "
            "Laissez vide pour en tirer une au hasard.",
    "tracks": "Chaque portail de course du mode Aventure charge un circuit tiré au hasard. La récompense reste celle "
              "du portail.",
    "origins": "Où piocher les circuits : CTR (les 18 circuits de 1999), CNK (Crash Nitro Kart) et GP (circuits du "
               "Grand Prix). Il en faut au moins 18 sans les doublons.",
    "duplicates": "Autorise le même circuit derrière plusieurs portails.",
    "arenas": "Les 4 défis cristaux se jouent dans des arènes tirées au hasard (CTR et CNK).",
    "names": "Au hub, le bandeau et les menus de chaque portail affichent le nom du circuit qu'il charge.",
    "rewards": "Mélange les trophées, clés de boss, gemmes, jetons CTR et paliers de relique. Une logique garantit que "
               "la partie peut toujours être finie. Les objets qui tournent au-dessus d'un portail montrent ce qu'il "
               "donne ; l'écran de fin de course montre l'objet reçu.",
    "cups": "Coupes de gemmes de Gem Stone Valley. D'origine : rien ne change. Coupe au hasard : chaque portail joue une "
            "coupe tirée parmi les 16 du jeu. Circuits au hasard : chaque coupe est faite de 4 circuits tirés. Il y a "
            "toujours 5 coupes à jouer. En « circuits au hasard », les 20 courses sont tirées parmi 38 circuits (tous sauf "
            "Turbo Track et Retro Stadium, qui ne sont dans aucune coupe du jeu), sans circuit en double.",
    "pads": "Ce qu'il faut pour ouvrir la course de chaque portail, Slide Coliseum, Turbo Track, les arènes et les "
            "coupes. Nombres au hasard : le même type que le jeu, en nombre tiré. Tout au hasard : trophées, clés, "
            "reliques, gemmes ou jetons d'une couleur. Toujours atteignable ; deux portails de la plage restent "
            "ouverts au départ. Les garages de boss gardent 4, 8, 12 et 16 trophées.",
    "challenges": "Défi CTR et course aux reliques d'un portail, une fois son trophée gagné. D'origine : il faut des "
                  "clés. Ouverts : jouables tout de suite. Au hasard : il faut un nombre tiré de trophées, de "
                  "clés, de reliques, de gemmes ou de jetons d'une couleur (toujours atteignable).",
    "hints": "Les indices d'Aku Aku sont marqués comme déjà vus : ils ne coupent plus la partie. Les cinématiques "
             "d'ouverture des portes déjà ouvertes par vos clés sont aussi passées (le jeu les gardait pour le retour "
             "d'un boss).",
    "reserve": "Hors dérapage, la barre de dérapage (style classique, celle de CTR) montre votre réserve de boost : elle "
               "se remplit quand vous enchaînez les turbos et se vide quand la réserve s'épuise (pleine = 5 s ou plus).",
    "relics": "En course aux reliques, la cible affichée sous le chrono commence au temps platine ; quand votre "
              "chrono le dépasse, elle passe au temps or, puis au temps saphir (avec l'icône et la couleur du palier). "
              "Les récompenses ne changent pas.",
    "podiums": "Au podium, l'écran « appuyez pour passer » s'ouvre dès le début au lieu d'attendre la fin de "
               "l'animation (posé dans le dossier du jeu : archives/update_hub3.pak). Si vous ne passez pas, le "
               "podium garde sa dernière pose.",
    "retry": "À la fin d'une course relique, gagnée ou perdue, le menu propose Recommencer (en haut) et Continuer (en "
             "dessous) pour retenter un meilleur palier sans repasser par le hub. Sélectionné : Continuer si une relique "
             "vient d'être gagnée, sinon Recommencer. Continuer sans nouvelle relique ramène au hub sans podium (posé "
             "dans le dossier du jeu : archives/update5.pak).",
    "locations": "Les portails changent de place entre eux : une bataille peut se trouver là où était Crash Cove, une "
                 "coupe sur la plage, etc. Le décor reste en place, mais ce qui s'y lance, ses objets et sa condition "
                 "suivent le portail. Les garages de boss ne bougent pas. Toujours finissable : les conditions "
                 "s'adaptent au monde où chaque portail arrive.",
    "code": "Le code de partage contient la graine et tous les réglages (circuits, récompenses, conditions, confort…). "
            "Donnez-le à vos adversaires : en le collant ici puis « Utiliser », ils ont exactement la même partie "
            "(même empreinte). « Copier » donne le code de la graine et des réglages affichés.",
    "presets": "Règle d'un coup les options du tirage. Les options de confort ne changent pas.",
    "generate": "Tire la graine, pose le patch dans le dossier patches du port et enregistre la graine et son journal "
                "dans le dossier graines_randomizer du port. Commencez ensuite une nouvelle aventure.",
}


def help_text(key):
    """Aide d'une option, dans la langue choisie (les préréglages listent ce que fait chacun)."""
    text = tr(HELP[key])
    if key == "presets":
        text += " " + " ".join(f"{tr(name)} : {tr(what)}" for name, what, _ in share.PRESETS)
    return text


class App(ttk.Frame):
    def __init__(self, root, context=None):
        """root : la fenêtre (logiciel autonome) ou, avec `context`, l'onglet du CTRNF Mod Kit qui la reçoit : le
        dossier du port et les réglages viennent alors du kit."""
        super().__init__(root, padding=10)
        self.root = root.winfo_toplevel()
        self.context = context
        if context is None:
            root.title(TITLE)
            root.minsize(740, 600)
            self.grid(sticky="nsew")
            root.columnconfigure(0, weight=1)
            root.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        conf = context.module_config() if context else app.load_config()
        self.log_path = None

        self.port = context.port_var if context else tk.StringVar(value=conf.get("port", ""))
        self.seed = tk.StringVar()
        self.code = tk.StringVar()
        self.tracks = tk.BooleanVar(value=conf.get("tracks", True))
        self.origins = {o: tk.BooleanVar(value=o in conf.get("origins", ORIGINS)) for o in ORIGINS}
        self.duplicates = tk.BooleanVar(value=conf.get("duplicates", False))
        self.arenas = tk.BooleanVar(value=conf.get("arenas", True))
        self.names = tk.BooleanVar(value=conf.get("names", True))
        self.rewards = tk.BooleanVar(value=conf.get("rewards", True))
        self.cups = tk.StringVar(value=conf.get("cups", "non"))
        self.pads = tk.StringVar(value=conf.get("pads", "origine"))
        self.challenges = tk.StringVar(value=conf.get("challenges", "origine"))
        self.hints = tk.BooleanVar(value=conf.get("hints", True))
        self.reserve = tk.BooleanVar(value=conf.get("reserve", True))
        self.podiums = tk.BooleanVar(value=conf.get("podiums", True))
        self.relics = tk.BooleanVar(value=conf.get("relics", True))
        self.locations = tk.BooleanVar(value=conf.get("locations", False))

        self.build_game().grid(row=0, column=0, sticky="ew")
        self.build_options().grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        self.rowconfigure(1, weight=1)
        self.help = ttk.Label(self, text=tr("Passez la souris sur une option pour voir son aide."), wraplength=700,
                              justify="left", foreground="#444")
        self.help.grid(row=2, column=0, sticky="ew", pady=6)
        self.build_bottom().grid(row=3, column=0, sticky="ew")
        self.messages = tk.Text(self, height=7, wrap="word", state="disabled")
        self.messages.grid(row=4, column=0, sticky="nsew", pady=(6, 0))
        self.port.trace_add("write", lambda *_: self.check_port())
        self.check_port()

    # --- construction --------------------------------------------------------------------------------------------
    def helped(self, widget, key):
        widget.bind("<Enter>", lambda _: self.help.configure(text=help_text(key)))
        return widget

    def build_game(self):
        box = ttk.LabelFrame(self, text=tr("Jeu et graine"), padding=8)
        box.columnconfigure(1, weight=1)
        self.helped(ttk.Label(box, text=tr("Dossier du port :")), "port").grid(row=0, column=0, sticky="w")
        self.helped(ttk.Entry(box, textvariable=self.port, state="readonly" if self.context else "normal"),
                    "port").grid(row=0, column=1, sticky="ew", padx=6)
        if self.context:
            ttk.Label(box, text=tr("(choisi dans l'Accueil)"), foreground="#555").grid(row=0, column=2)
        else:
            ttk.Button(box, text=tr("Parcourir…"), command=self.browse).grid(row=0, column=2)
        self.status = ttk.Label(box, text="")
        self.status.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 6))
        self.helped(ttk.Label(box, text=tr("Graine :")), "seed").grid(row=2, column=0, sticky="w")
        self.helped(ttk.Entry(box, textvariable=self.seed, width=16), "seed").grid(row=2, column=1, sticky="w", padx=6)
        ttk.Button(box, text=tr("Au hasard"), command=self.random_seed).grid(row=2, column=2)
        self.helped(ttk.Label(box, text=tr("Code de partage :")), "code").grid(row=3, column=0, sticky="w", pady=(4, 0))
        row = ttk.Frame(box)
        row.grid(row=3, column=1, columnspan=2, sticky="w", padx=6, pady=(4, 0))
        self.helped(ttk.Entry(row, textvariable=self.code, width=18), "code").pack(side="left")
        self.helped(ttk.Button(row, text=tr("Utiliser"), command=self.use_code), "code").pack(side="left", padx=(6, 0))
        self.helped(ttk.Button(row, text=tr("Copier"), command=self.copy_code), "code").pack(side="left", padx=(6, 0))
        self.helped(ttk.Label(box, text=tr("Préréglages :")), "presets").grid(row=4, column=0, sticky="w", pady=(4, 0))
        row = ttk.Frame(box)
        row.grid(row=4, column=1, columnspan=2, sticky="w", padx=6, pady=(4, 0))
        for name, _, values in share.PRESETS:
            self.helped(ttk.Button(row, text=tr(name), command=lambda v=values, n=name: self.preset(n, v)),
                        "presets").pack(side="left", padx=(0, 6))
        return box

    def page(self, tabs, title, intro):
        """Un onglet, avec en haut une courte explication de ce qu'il règle ; rend (onglet, première ligne libre)."""
        page = ttk.Frame(tabs, padding=10)
        page.columnconfigure(0, weight=1)
        ttk.Label(page, text=tr(intro), wraplength=690, justify="left", foreground="#333").grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))
        tabs.add(page, text=tr(title))
        return page

    def choices(self, page, row, variable, key, options):
        """Boutons radio (valeur, texte) l'un sous l'autre à partir de la ligne `row`."""
        for i, (value, text) in enumerate(options):
            self.helped(ttk.Radiobutton(page, text=tr(text), value=value, variable=variable), key).grid(
                row=row + i, column=0, columnspan=4, sticky="w", padx=12)

    def build_options(self):
        tabs = ttk.Notebook(self)

        page = self.page(tabs, "Circuits", "Quel circuit (ou quelle arène) charge chaque portail du mode Aventure. La "
                                           "récompense reste celle du portail.")
        self.helped(ttk.Checkbutton(page, text=tr("Mélanger les circuits derrière les portails"), variable=self.tracks),
                    "tracks").grid(row=1, column=0, columnspan=4, sticky="w")
        row = ttk.Frame(page)
        row.grid(row=2, column=0, columnspan=4, sticky="w", padx=24, pady=2)
        self.helped(ttk.Label(row, text=tr("Circuits tirés parmi :")), "origins").pack(side="left")
        for origin in ORIGINS:
            self.helped(ttk.Checkbutton(row, text=origin, variable=self.origins[origin]), "origins").pack(
                side="left", padx=4)
        self.helped(ttk.Checkbutton(page, text=tr("Autoriser le même circuit derrière plusieurs portails"),
                                    variable=self.duplicates), "duplicates").grid(row=3, column=0, columnspan=4,
                                                                                  sticky="w", padx=24)
        self.helped(ttk.Checkbutton(page, text=tr("Mélanger les arènes des défis cristaux"), variable=self.arenas),
                    "arenas").grid(row=4, column=0, columnspan=4, sticky="w", pady=(6, 0))
        self.helped(ttk.Checkbutton(page, text=tr("Afficher au hub le nom du circuit joué"), variable=self.names),
                    "names").grid(row=5, column=0, columnspan=4, sticky="w")

        page = self.page(tabs, "Récompenses", "Ce que donne chaque course gagnée : trophée, clé de boss, gemme, jeton CTR "
                                              "ou palier de relique. Mélangées, elles restent toujours atteignables.")
        self.helped(ttk.Checkbutton(page, text=tr("Mélanger les récompenses"), variable=self.rewards), "rewards").grid(
            row=1, column=0, sticky="w")

        page = self.page(tabs, "Coupes", "À Gem Stone Valley, 5 portails de coupe (rouge, bleue, verte, jaune, violette) "
                                         "font jouer 4 courses à la suite. Ce réglage choisit les circuits de ces coupes ; "
                                         "il y a toujours 5 coupes à jouer.")
        self.choices(page, 1, self.cups, "cups", (
            ("non", "D'origine : chaque portail garde ses 4 circuits"),
            ("coupes", "Coupe au hasard : chaque portail joue une des 16 coupes du jeu (Arcade, CNK, Grand Prix…)"),
            ("circuits", "Circuits au hasard : chaque coupe est faite de 4 circuits tirés, sans circuit en double")))

        page = self.page(tabs, "Conditions", "Ce qu'il faut pour ouvrir les portails. Les conditions tirées au hasard "
                                             "restent toujours atteignables.")
        self.helped(ttk.Label(page, text=tr("Courses des portails, Slide Coliseum, Turbo Track, arènes et coupes :")),
                    "pads").grid(row=1, column=0, sticky="w")
        self.choices(page, 2, self.pads, "pads", (
            ("origine", "D'origine (trophées, clés, reliques, gemmes et jetons du jeu)"),
            ("nombres", "Nombres au hasard (même type que le jeu)"),
            ("hasard", "Tout au hasard (trophées, clés, reliques, gemmes ou jetons)")))
        self.helped(ttk.Label(page, text=tr("Défi CTR et course aux reliques (une fois le trophée du portail gagné) :")),
                    "challenges").grid(row=5, column=0, sticky="w", pady=(8, 0))
        self.choices(page, 6, self.challenges, "challenges", (
            ("origine", "D'origine (1 à 4 clés selon le monde)"),
            ("ouverts", "Ouverts tout de suite"),
            ("hasard", "Condition au hasard (trophées, clés, reliques, gemmes ou jetons)")))
        ttk.Label(page, text=tr("Les garages de boss gardent 4, 8, 12 et 16 trophées."), foreground="#555").grid(
            row=9, column=0, sticky="w", pady=(8, 0))

        page = self.page(tabs, "Portails", "Où se trouve chaque portail du hub (courses, arènes de bataille, coupes, "
                                           "Slide Coliseum, Turbo Track).")
        self.helped(ttk.Checkbutton(page, text=tr("Mélanger les emplacements des portails"), variable=self.locations),
                    "locations").grid(row=1, column=0, sticky="w")

        page = self.page(tabs, "Confort", "Pour jouer plus vite et mieux voir ce qui se passe.")
        self.helped(ttk.Checkbutton(page, text=tr("Passer les indices d'Aku Aku et les cinématiques des portes"),
                                    variable=self.hints), "hints").grid(row=1, column=0, sticky="w")
        self.helped(ttk.Checkbutton(page, text=tr("Afficher la réserve de boost dans la barre de dérapage"),
                                    variable=self.reserve), "reserve").grid(row=2, column=0, sticky="w")
        self.helped(ttk.Checkbutton(page, text=tr("Pouvoir passer les podiums dès le début"), variable=self.podiums),
                    "podiums").grid(row=3, column=0, sticky="w")
        self.helped(ttk.Checkbutton(page, text=tr("Reliques : viser le platine, puis l'or, puis le saphir pendant la course"),
                                    variable=self.relics), "relics").grid(row=4, column=0, sticky="w")
        return tabs

    def build_bottom(self):
        row = ttk.Frame(self)
        row.columnconfigure(1, weight=1)
        self.go = self.helped(ttk.Button(row, text=tr("Générer et installer"), command=self.generate), "generate")
        self.go.grid(row=0, column=0)
        self.print_label = ttk.Label(row, text="", font=("TkDefaultFont", 11, "bold"))
        self.print_label.grid(row=0, column=1, padx=10, sticky="w")
        self.log_button = ttk.Button(row, text=tr("Ouvrir le journal"), command=self.open_log_file, state="disabled")
        self.log_button.grid(row=0, column=2)
        return row

    # --- actions -------------------------------------------------------------------------------------------------
    def say(self, text):
        self.messages.configure(state="normal")
        self.messages.insert("end", text + "\n")
        self.messages.see("end")
        self.messages.configure(state="disabled")

    def browse(self):
        if self.context:  # dans le kit, le dossier du port se change dans l'Accueil
            return
        folder = filedialog.askdirectory(title=tr("Dossier du port CTR-NitroFueled-PC"), initialdir=self.port.get() or None)
        if folder:
            self.port.set(folder)

    def random_seed(self):
        self.seed.set(str(random.SystemRandom().randrange(1 << 32)))

    def check_port(self):
        if not self.port.get().strip():
            self.status.configure(text=tr("Choisissez le dossier du port."), foreground="#a60")
            return False
        ok, messages = app.check_port(self.port.get().strip())
        self.status.configure(text=("✓ " if ok else "✗ ") + " ; ".join(messages),
                              foreground="#070" if ok else "#b00")
        return ok

    def settings(self):
        return Settings(shuffle_tracks=self.tracks.get(),
                        track_origins=tuple(o for o in ORIGINS if self.origins[o].get()),
                        shuffle_arenas=self.arenas.get(), allow_duplicates=self.duplicates.get(),
                        shuffle_rewards=self.rewards.get(), shuffle_cups=self.cups.get(),
                        pad_conditions=self.pads.get(), challenges=self.challenges.get(),
                        skip_hints=self.hints.get(), shuffle_locations=self.locations.get(),
                        boost_reserve=self.reserve.get(), fast_podiums=self.podiums.get(),
                        relic_targets=self.relics.get())

    def apply(self, settings):
        """Remet dans la fenêtre les réglages d'un Settings."""
        self.tracks.set(settings.shuffle_tracks)
        for origin in ORIGINS:
            self.origins[origin].set(origin in settings.track_origins)
        self.duplicates.set(settings.allow_duplicates)
        self.arenas.set(settings.shuffle_arenas)
        self.rewards.set(settings.shuffle_rewards)
        self.cups.set(settings.shuffle_cups)
        self.pads.set(settings.pad_conditions)
        self.challenges.set(settings.challenges)
        self.hints.set(settings.skip_hints)
        self.reserve.set(settings.boost_reserve)
        self.podiums.set(settings.fast_podiums)
        self.relics.set(settings.relic_targets)
        self.locations.set(settings.shuffle_locations)

    def preset(self, name, values):
        self.apply(Settings(**{**self.settings().__dict__, **values}))
        self.say(tr("Préréglage « {name} » appliqué (options de confort inchangées).", name=tr(name)))

    def use_code(self):
        try:
            seed, settings, rename = share.decode(self.code.get())
        except ValueError as error:
            messagebox.showerror(TITLE, tr("Code de partage refusé : {error}.", error=error))
            return
        self.seed.set(str(seed))
        self.apply(settings)
        self.names.set(rename)
        self.code.set(share.encode(seed, settings, rename))
        self.say(tr("Code {code} : graine {seed} et réglages chargés. Cliquez sur « Générer et installer ».",
                    code=self.code.get(), seed=seed))

    def copy_code(self):
        text = self.seed.get().strip()
        if not (text.isascii() and text.isdigit()) or int(text) >= 1 << 32:
            messagebox.showerror(TITLE, tr("Choisissez une graine (ou « Au hasard ») pour avoir son code de partage."))
            return
        self.code.set(share.encode(int(text), self.settings(), self.names.get()))
        self.root.clipboard_clear()
        self.root.clipboard_append(self.code.get())
        self.say(tr("Code de partage copié : {code}", code=self.code.get()))

    def values(self):
        return {"port": self.port.get().strip(), "tracks": self.tracks.get(),
                "origins": [o for o in ORIGINS if self.origins[o].get()], "duplicates": self.duplicates.get(),
                "arenas": self.arenas.get(), "names": self.names.get(), "rewards": self.rewards.get(),
                "cups": self.cups.get(), "pads": self.pads.get(), "challenges": self.challenges.get(),
                "hints": self.hints.get(), "locations": self.locations.get(), "reserve": self.reserve.get(),
                "podiums": self.podiums.get(), "relics": self.relics.get()}

    def generate(self):
        if not self.check_port():
            messagebox.showerror(TITLE, tr("Le dossier du port n'est pas bon : voir le message en haut de la fenêtre."))
            return
        text = self.seed.get().strip()
        if text and (not (text.isascii() and text.isdigit()) or int(text) >= 1 << 32):
            messagebox.showerror(TITLE, tr("La graine doit être un nombre de 0 à 4294967295 (ou vide pour un tirage au "
                                            "hasard)."))
            return
        if not text:
            self.random_seed()
        seed = int(self.seed.get())
        if app.game_running() and not messagebox.askokcancel(
                TITLE, tr("Le jeu est ouvert : le patch ne servira qu'au prochain lancement. Continuer ?")):
            return
        self.go.configure(state="disabled")
        self.root.config(cursor="watch")
        self.root.update_idletasks()
        try:
            plan, mark, log, notes = app.install(seed, self.settings(), self.port.get().strip(), rename=self.names.get())
        except (ValueError, RuntimeError) as error:
            messagebox.showerror(TITLE, tr("Impossible de tirer cette graine : {error}", error=error))
            return
        except OSError as error:
            messagebox.showerror(TITLE, tr("Impossible d'écrire les fichiers : {error}", error=error))
            return
        finally:
            self.go.configure(state="normal")
            self.root.config(cursor="")
        if self.context:
            self.context.save_module_config(self.values())
        else:
            app.save_config(self.values())
        self.log_path = log
        self.log_button.configure(state="normal")
        self.print_label.configure(text=tr("Empreinte : {mark}", mark=mark))
        self.say(tr("Graine {seed} installée (empreinte {mark}).", seed=seed, mark=mark))
        self.say(tr("Patch : {file}", file=Path(self.port.get().strip()) / "patches" / app.PATCH_NAME))
        self.say(tr("Journal : {file}", file=log))
        self.code.set(share.encode(seed, self.settings(), self.names.get()))
        self.say(tr("Code de partage : {code} (vos adversaires le collent pour avoir la même partie)",
                    code=self.code.get()))
        for note in notes:
            self.say(note)
        self.say(tr("Lancez le jeu et commencez une nouvelle aventure (une ancienne partie ne correspond plus)."))

    def open_log_file(self):
        if self.log_path and Path(self.log_path).is_file():
            os.startfile(self.log_path) if hasattr(os, "startfile") else messagebox.showinfo(TITLE, str(self.log_path))


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
