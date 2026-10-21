"""Petit logiciel du randomizer : choisir le dossier du port, régler les options, générer et installer une graine.
Lancement : python -m ctrnf_rando.gui"""
import os
from pathlib import Path
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from . import __version__, app
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
    "podiums": "Au podium, l'écran « appuyez pour passer » s'ouvre dès le début au lieu d'attendre la fin de "
               "l'animation (posé dans le dossier du jeu : archives/update_hub3.pak). Si vous ne passez pas, le "
               "podium garde sa dernière pose.",
    "locations": "Les portails changent de place entre eux : une bataille peut se trouver là où était Crash Cove, une "
                 "coupe sur la plage, etc. Le décor reste en place, mais ce qui s'y lance, ses objets et sa condition "
                 "suivent le portail. Les garages de boss ne bougent pas. Toujours finissable : les conditions "
                 "s'adaptent au monde où chaque portail arrive.",
    "generate": "Tire la graine, pose le patch dans le dossier patches du port et enregistre la graine et son journal "
                "dans le dossier graines_randomizer du port. Commencez ensuite une nouvelle aventure.",
}


class App(ttk.Frame):
    def __init__(self, root):
        super().__init__(root, padding=10)
        self.root = root
        root.title(TITLE)
        root.minsize(740, 600)
        self.grid(sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        conf = app.load_config()
        self.log_path = None

        self.port = tk.StringVar(value=conf.get("port", ""))
        self.seed = tk.StringVar()
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
        self.locations = tk.BooleanVar(value=conf.get("locations", False))

        self.build_game().grid(row=0, column=0, sticky="ew")
        self.build_options().grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        self.rowconfigure(1, weight=1)
        self.help = ttk.Label(self, text="Passez la souris sur une option pour voir son aide.", wraplength=700,
                              justify="left", foreground="#444")
        self.help.grid(row=2, column=0, sticky="ew", pady=6)
        self.build_bottom().grid(row=3, column=0, sticky="ew")
        self.messages = tk.Text(self, height=7, wrap="word", state="disabled")
        self.messages.grid(row=4, column=0, sticky="nsew", pady=(6, 0))
        self.port.trace_add("write", lambda *_: self.check_port())
        self.check_port()

    # --- construction --------------------------------------------------------------------------------------------
    def helped(self, widget, key):
        widget.bind("<Enter>", lambda _: self.help.configure(text=HELP[key]))
        return widget

    def build_game(self):
        box = ttk.LabelFrame(self, text="Jeu et graine", padding=8)
        box.columnconfigure(1, weight=1)
        self.helped(ttk.Label(box, text="Dossier du port :"), "port").grid(row=0, column=0, sticky="w")
        self.helped(ttk.Entry(box, textvariable=self.port), "port").grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(box, text="Parcourir…", command=self.browse).grid(row=0, column=2)
        self.status = ttk.Label(box, text="")
        self.status.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 6))
        self.helped(ttk.Label(box, text="Graine :"), "seed").grid(row=2, column=0, sticky="w")
        self.helped(ttk.Entry(box, textvariable=self.seed, width=16), "seed").grid(row=2, column=1, sticky="w", padx=6)
        ttk.Button(box, text="Au hasard", command=self.random_seed).grid(row=2, column=2)
        return box

    def page(self, tabs, title, intro):
        """Un onglet, avec en haut une courte explication de ce qu'il règle ; rend (onglet, première ligne libre)."""
        page = ttk.Frame(tabs, padding=10)
        page.columnconfigure(0, weight=1)
        ttk.Label(page, text=intro, wraplength=690, justify="left", foreground="#333").grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))
        tabs.add(page, text=title)
        return page

    def choices(self, page, row, variable, key, options):
        """Boutons radio (valeur, texte) l'un sous l'autre à partir de la ligne `row`."""
        for i, (value, text) in enumerate(options):
            self.helped(ttk.Radiobutton(page, text=text, value=value, variable=variable), key).grid(
                row=row + i, column=0, columnspan=4, sticky="w", padx=12)

    def build_options(self):
        tabs = ttk.Notebook(self)

        page = self.page(tabs, "Circuits", "Quel circuit (ou quelle arène) charge chaque portail du mode Aventure. La "
                                           "récompense reste celle du portail.")
        self.helped(ttk.Checkbutton(page, text="Mélanger les circuits derrière les portails", variable=self.tracks),
                    "tracks").grid(row=1, column=0, columnspan=4, sticky="w")
        row = ttk.Frame(page)
        row.grid(row=2, column=0, columnspan=4, sticky="w", padx=24, pady=2)
        self.helped(ttk.Label(row, text="Circuits tirés parmi :"), "origins").pack(side="left")
        for origin in ORIGINS:
            self.helped(ttk.Checkbutton(row, text=origin, variable=self.origins[origin]), "origins").pack(
                side="left", padx=4)
        self.helped(ttk.Checkbutton(page, text="Autoriser le même circuit derrière plusieurs portails",
                                    variable=self.duplicates), "duplicates").grid(row=3, column=0, columnspan=4,
                                                                                  sticky="w", padx=24)
        self.helped(ttk.Checkbutton(page, text="Mélanger les arènes des défis cristaux", variable=self.arenas),
                    "arenas").grid(row=4, column=0, columnspan=4, sticky="w", pady=(6, 0))
        self.helped(ttk.Checkbutton(page, text="Afficher au hub le nom du circuit joué", variable=self.names),
                    "names").grid(row=5, column=0, columnspan=4, sticky="w")

        page = self.page(tabs, "Récompenses", "Ce que donne chaque course gagnée : trophée, clé de boss, gemme, jeton CTR "
                                              "ou palier de relique. Mélangées, elles restent toujours atteignables.")
        self.helped(ttk.Checkbutton(page, text="Mélanger les récompenses", variable=self.rewards), "rewards").grid(
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
        self.helped(ttk.Label(page, text="Courses des portails, Slide Coliseum, Turbo Track, arènes et coupes :"),
                    "pads").grid(row=1, column=0, sticky="w")
        self.choices(page, 2, self.pads, "pads", (
            ("origine", "D'origine (trophées, clés, reliques, gemmes et jetons du jeu)"),
            ("nombres", "Nombres au hasard (même type que le jeu)"),
            ("hasard", "Tout au hasard (trophées, clés, reliques, gemmes ou jetons)")))
        self.helped(ttk.Label(page, text="Défi CTR et course aux reliques (une fois le trophée du portail gagné) :"),
                    "challenges").grid(row=5, column=0, sticky="w", pady=(8, 0))
        self.choices(page, 6, self.challenges, "challenges", (
            ("origine", "D'origine (1 à 4 clés selon le monde)"),
            ("ouverts", "Ouverts tout de suite"),
            ("hasard", "Condition au hasard (trophées, clés, reliques, gemmes ou jetons)")))
        ttk.Label(page, text="Les garages de boss gardent 4, 8, 12 et 16 trophées.", foreground="#555").grid(
            row=9, column=0, sticky="w", pady=(8, 0))

        page = self.page(tabs, "Portails", "Où se trouve chaque portail du hub (courses, arènes de bataille, coupes, "
                                           "Slide Coliseum, Turbo Track).")
        self.helped(ttk.Checkbutton(page, text="Mélanger les emplacements des portails", variable=self.locations),
                    "locations").grid(row=1, column=0, sticky="w")

        page = self.page(tabs, "Confort", "Pour jouer plus vite et mieux voir ce qui se passe.")
        self.helped(ttk.Checkbutton(page, text="Passer les indices d'Aku Aku et les cinématiques des portes",
                                    variable=self.hints), "hints").grid(row=1, column=0, sticky="w")
        self.helped(ttk.Checkbutton(page, text="Afficher la réserve de boost dans la barre de dérapage",
                                    variable=self.reserve), "reserve").grid(row=2, column=0, sticky="w")
        self.helped(ttk.Checkbutton(page, text="Pouvoir passer les podiums dès le début", variable=self.podiums),
                    "podiums").grid(row=3, column=0, sticky="w")
        return tabs

    def build_bottom(self):
        row = ttk.Frame(self)
        row.columnconfigure(1, weight=1)
        self.go = self.helped(ttk.Button(row, text="Générer et installer", command=self.generate), "generate")
        self.go.grid(row=0, column=0)
        self.print_label = ttk.Label(row, text="", font=("TkDefaultFont", 11, "bold"))
        self.print_label.grid(row=0, column=1, padx=10, sticky="w")
        self.log_button = ttk.Button(row, text="Ouvrir le journal", command=self.open_log_file, state="disabled")
        self.log_button.grid(row=0, column=2)
        return row

    # --- actions -------------------------------------------------------------------------------------------------
    def say(self, text):
        self.messages.configure(state="normal")
        self.messages.insert("end", text + "\n")
        self.messages.see("end")
        self.messages.configure(state="disabled")

    def browse(self):
        folder = filedialog.askdirectory(title="Dossier du port CTR-NitroFueled-PC", initialdir=self.port.get() or None)
        if folder:
            self.port.set(folder)

    def random_seed(self):
        self.seed.set(str(random.SystemRandom().randrange(1 << 32)))

    def check_port(self):
        if not self.port.get().strip():
            self.status.configure(text="Choisissez le dossier du port.", foreground="#a60")
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
                        boost_reserve=self.reserve.get(), fast_podiums=self.podiums.get())

    def values(self):
        return {"port": self.port.get().strip(), "tracks": self.tracks.get(),
                "origins": [o for o in ORIGINS if self.origins[o].get()], "duplicates": self.duplicates.get(),
                "arenas": self.arenas.get(), "names": self.names.get(), "rewards": self.rewards.get(),
                "cups": self.cups.get(), "pads": self.pads.get(), "challenges": self.challenges.get(),
                "hints": self.hints.get(), "locations": self.locations.get(), "reserve": self.reserve.get(),
                "podiums": self.podiums.get()}

    def generate(self):
        if not self.check_port():
            messagebox.showerror(TITLE, "Le dossier du port n'est pas bon : voir le message en haut de la fenêtre.")
            return
        text = self.seed.get().strip()
        if text and not text.isdigit():
            messagebox.showerror(TITLE, "La graine doit être un nombre (ou vide pour un tirage au hasard).")
            return
        if not text:
            self.random_seed()
        seed = int(self.seed.get())
        if app.game_running() and not messagebox.askokcancel(
                TITLE, "Le jeu est ouvert : le patch ne servira qu'au prochain lancement. Continuer ?"):
            return
        self.go.configure(state="disabled")
        self.root.config(cursor="watch")
        self.root.update_idletasks()
        try:
            plan, mark, log, notes = app.install(seed, self.settings(), self.port.get().strip(), rename=self.names.get())
        except (ValueError, RuntimeError) as error:
            messagebox.showerror(TITLE, f"Impossible de tirer cette graine : {error}")
            return
        except OSError as error:
            messagebox.showerror(TITLE, f"Impossible d'écrire les fichiers : {error}")
            return
        finally:
            self.go.configure(state="normal")
            self.root.config(cursor="")
        app.save_config(self.values())
        self.log_path = log
        self.log_button.configure(state="normal")
        self.print_label.configure(text=f"Empreinte : {mark}")
        self.say(f"Graine {seed} installée (empreinte {mark}).")
        self.say(f"Patch : {Path(self.port.get().strip()) / 'patches' / app.PATCH_NAME}")
        self.say(f"Journal : {log}")
        for note in notes:
            self.say(note)
        self.say("Lancez le jeu et commencez une nouvelle aventure (une ancienne partie ne correspond plus).")

    def open_log_file(self):
        if self.log_path and Path(self.log_path).is_file():
            os.startfile(self.log_path) if hasattr(os, "startfile") else messagebox.showinfo(TITLE, str(self.log_path))


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
