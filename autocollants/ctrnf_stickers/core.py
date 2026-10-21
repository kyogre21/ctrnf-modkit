"""Ce que fait le logiciel, sans la fenêtre : trouver les archives du jeu, lister les autocollants, les lire, en
remplacer et remettre d'origine.

Les images remplacées vont dans une petite archive à nous, `archives/update3.pak`, que le jeu cherche au démarrage et
charge après update.pak / update2.pak. Les archives du jeu ne sont jamais modifiées : supprimer update3.pak remet tout
d'origine.
"""
import json
from pathlib import Path
import subprocess
import sys

from . import iga, texture
from .icons import ICONS
from .names import ARCHIVES, ICON, ICON_TAG, OURS, STICKER, is_ours  # noqa: F401
from .names import short as _short

CONFIG = Path.home() / '.ctrnf_stickers.json'


def find_archives(folder):
    """Dossier choisi (dossier archives, dossier du jeu qui le contient, ou dossier du port avec son launcher.ini)
    -> dossier archives. ValueError si rien de bon."""
    folder = Path(folder)
    candidates = [folder, folder / 'archives']
    ini = folder / 'launcher.ini'
    if ini.is_file():
        game = ''
        for line in ini.read_text(encoding='utf-8-sig', errors='replace').splitlines():
            key, _, value = line.partition('=')
            if key.strip() == 'game_dir':
                game = value.strip().strip('"')  # clé en double : la dernière compte (comme le kit)
        if game:
            candidates.append(Path(game) / 'archives')
    for c in candidates:
        if all((c / name).is_file() for name in ARCHIVES):
            return c
    raise ValueError('archives du jeu introuvables (il faut le dossier qui contient stickers.pak, update.pak et '
                     'update2.pak, le dossier du jeu au-dessus, ou le dossier du port)')


class Game:
    """Les autocollants d'un jeu : `textures` = {nom court: (archive, nom du fichier)}, version la plus récente."""

    def __init__(self, archives):
        self.folder = Path(archives)
        self.textures = {}
        for pak in ARCHIVES:
            with iga.Archive(self.folder / pak) as a:
                for name in a.names:
                    short = _short(name)
                    if short:
                        self.textures[short] = (pak, name)

    def stickers(self):
        return sorted(s for s in self.textures if not s.startswith(ICON_TAG))

    def icons(self):
        return sorted((s for s in self.textures if s.startswith(ICON_TAG)), key=lambda s: int(s[len(ICON_TAG):]))

    def icon(self, short):
        """Nom court de l'icône du menu de cet autocollant, ou None s'il n'en a pas."""
        ico = ICONS.get(short)
        return ico if ico in self.textures else None

    def original(self, short):
        pak, name = self.textures[short]
        with iga.Archive(self.folder / pak) as a:
            return a.read(name)

    def _ours(self):
        """Contenu de update3.pak : {nom du fichier: contenu} (vide s'il n'existe pas)."""
        path = self.folder / OURS
        if not path.is_file():
            return {}
        with iga.Archive(path) as a:
            return {name: a.read(name) for name in a.names}

    def changed(self):
        """Noms courts des autocollants remplacés."""
        path = self.folder / OURS
        if not path.is_file():
            return set()
        with iga.Archive(path) as a:
            return {s for s in map(_short, a.names) if s in self.textures}

    def current(self, short):
        """Texture telle que le jeu la verra (la nôtre si elle est remplacée)."""
        name = self.textures[short][1]
        path = self.folder / OURS
        if path.is_file():
            with iga.Archive(path) as a:
                if name in a.names:
                    return a.read(name)
        return self.original(short)

    def replace(self, short, img, icon=True):
        """Remplace l'autocollant par l'image, et son icône du menu aussi (si `icon` et s'il en a une)."""
        files = self._ours()
        targets = [short] + ([self.icon(short)] if icon and self.icon(short) else [])
        for s in targets:
            files[self.textures[s][1]] = texture.replace(self.original(s), img)
        iga.write(files, self.folder / OURS)

    def restore(self, short):
        """Remet l'autocollant d'origine, avec son icône du menu."""
        files = self._ours()
        for s in (short, self.icon(short)):
            if s:
                files.pop(self.textures[s][1], None)
        if files:
            iga.write(files, self.folder / OURS)
        else:
            self.restore_all()

    def restore_all(self):
        """Supprime update3.pak, seulement s'il est à nous (ValueError sinon)."""
        path = self.folder / OURS
        if path.exists() and not is_ours(path):
            raise ValueError(f"{path} n'est pas une archive de cet outil : elle n'est pas supprimée")
        path.unlink(missing_ok=True)


def game_running():
    """Le jeu (sacredfire.exe) tourne-t-il ? (Windows seulement ; ailleurs : on ne sait pas, donc non)"""
    if sys.platform != 'win32':
        return False
    try:
        out = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq sacredfire.exe', '/NH'], capture_output=True,
                             text=True, timeout=10, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    return 'sacredfire.exe' in out.lower()


def load_config():
    try:
        return json.loads(CONFIG.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def save_config(values):
    try:
        CONFIG.write_text(json.dumps(values, indent=1), encoding='utf-8')
    except OSError:
        pass
