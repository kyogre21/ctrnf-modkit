"""Options de confort sans randomizer : `patches/Confort.xml` (indices d'Aku Aku, réserve de boost, cible des
reliques) et l'archive des podiums rapides, posés par l'onglet Confort du kit. Le jeu reste celui d'origine.

Quand Confort.xml est là, le randomizer ne pose plus ses propres lignes de confort (voir app.install) ; à
l'installation, celles d'un Randomizer.xml déjà posé sont retirées, pour qu'aucune adresse ne soit écrite deux fois."""
from pathlib import Path
import re

from . import __version__, archives
from .i18n import tr
from .patch import COMFORT, comfort_addresses, comfort_xml

NAME = "Confort.xml"
RANDOMIZER = "Randomizer.xml"
OPTIONS = COMFORT + ("fast_podiums", "relic_retry")  # les deux derniers : des archives du jeu, pas des lignes du patch
ARCHIVES = {"fast_podiums": archives.PODIUM, "relic_retry": archives.RELIC}
LINE = re.compile(r'[ \t]*<Line Type="bytes" Address="(0x[0-9a-f]+)" Value="[0-9a-f]*"\s*Signature="[^"]*"/>\n')


def target(port):
    return Path(port) / "patches" / NAME


def _head(path):
    return path.read_text(encoding="utf-8", errors="replace")[:4000]


def is_ours(path):
    head = _head(path)
    return 'Name="Confort"' in head and 'Author="kyogre21"' in head


def _randomizer_ours(path):
    head = _head(path)
    return 'Name="Randomizer"' in head and 'Author="kyogre21"' in head


def present(port):
    path = target(port)
    return path.is_file() and is_ours(path)


def read_settings(port):
    """{option: bool} de ce qui est posé (Confort.xml et archive des podiums), ou None sans Confort.xml."""
    if not present(port):
        return None
    found = re.search(r"options:([^\n]*)", _head(target(port)))
    chosen = set(found.group(1).split()) if found else set()
    values = {k: k in chosen for k in COMFORT}
    folder = archives.game_archives(port)
    for option, script in ARCHIVES.items():
        path = folder / script.archive if folder else None
        values[option] = bool(path and path.is_file() and archives.ours(path, script))
    return values


def strip(text):
    """`text` (un patch) sans ses lignes de confort."""
    wanted = comfort_addresses()
    return LINE.sub(lambda m: "" if m.group(1) in wanted else m.group(0), text)


def _write(path, text):
    tmp = path.with_suffix(".tmp")  # jamais de fichier à moitié écrit
    tmp.write_text(text, encoding="utf-8", newline="\n")
    tmp.replace(path)


def install(port, settings):
    """Pose Confort.xml avec les options cochées de `settings` ({option: bool}, voir OPTIONS) et règle l'archive des
    podiums. Rend [messages]. Lève ValueError si un Confort.xml qui n'est pas le nôtre est en place."""
    port = Path(port)
    path = target(port)
    if not path.parent.is_dir():
        raise ValueError(tr("dossier « patches » introuvable dans {folder}", folder=port))
    if path.exists() and not is_ours(path):
        raise ValueError(tr("{file} existe et n'est pas un patch du kit : rien n'est écrit", file=path))
    notes = []
    _write(path, comfort_xml(settings, __version__))
    chosen = [k for k in COMFORT if settings.get(k)]
    notes.append(tr("{file} posé ({n} option(s) dans le patch)", file=NAME, n=len(chosen)))
    rando = path.parent / RANDOMIZER
    if rando.is_file() and _randomizer_ours(rando):
        text = rando.read_text(encoding="utf-8")
        cleaned = strip(text)
        if cleaned != text:
            _write(rando, cleaned)
            notes.append(tr("{file} : ses options de confort sont retirées (Confort.xml s'en charge)", file=RANDOMIZER))
    folder = archives.game_archives(port)
    wanted = [script for option, script in ARCHIVES.items() if settings.get(option)]
    if folder:
        notes += [tr("{file} {what} dans {folder}", file=name, what=tr(what), folder=folder)
                  for name, what in archives.install(folder, wanted, tuple(ARCHIVES.values()))]
    elif wanted:
        notes.append(tr("Dossier du jeu introuvable (launcher.ini du port, game_dir) : podiums rapides et "
                        "« Recommencer / Continuer » non installés."))
    return notes


def uninstall(port):
    """Retire Confort.xml et l'archive des podiums (seulement les nôtres). Rend [messages]."""
    port = Path(port)
    notes = []
    path = target(port)
    if path.is_file() and is_ours(path):
        path.unlink()
        notes.append(tr("{file} retiré", file=NAME))
        rando = path.parent / RANDOMIZER
        if rando.is_file() and _randomizer_ours(rando):
            notes.append(tr("{file} n'a plus d'options de confort : générez la graine à nouveau pour les remettre.",
                             file=RANDOMIZER))
    folder = archives.game_archives(port)
    if folder:
        notes += [f"{name} {tr(what)}" for name, what in archives.install(folder, [], tuple(ARCHIVES.values()))]
    return notes
