"""Les mods du kit. Chacun déclare les fichiers qu'il pose (aucun chevauchement), dit ce qui est installé, sait se
désinstaller sans jamais toucher un fichier qui n'est pas à lui, et construit son onglet. Les paquets des mods sont
importés au dernier moment : un mod désactivé ne charge rien (numpy et Pillow pour les autocollants)."""
from dataclasses import dataclass
import hashlib
import json
import importlib
from pathlib import Path
import shutil

from . import _paths

PRESENT, ABSENT, FOREIGN = "posé par le mod", "absent", "étranger (non touché)"
PUBLISHED_ASL = {  # SHA-256 des versions publiées de CTRNF.asl (à compléter à chaque publication)
    "452f824fc9c4103ca9cfab909695249d88a871f516e70db90aa56633d3ac9423",  # 0.1.1-alpha (Mod Kit 0.1.0)
}


def backup_folder():
    """Copies de sécurité faites avant de retirer un fichier qui contient le travail du joueur (autocollants)."""
    return Path.home() / "CTRNF Mod Kit - sauvegardes"


@dataclass
class FileState:
    path: Path
    module: str
    what: str
    state: str

    @property
    def size(self):
        return self.path.stat().st_size if self.state != ABSENT and self.path.is_file() else 0


class ModuleError(Exception):
    pass


class Module:
    id = name = description = package = ""
    stage = ""  # « alpha » : tout début de développement (affiché partout)

    def version(self):
        try:
            return importlib.import_module(self.package).__version__
        except (ImportError, AttributeError):
            return "?"

    def available(self):
        return True, ""

    def owned(self, ctx):
        """[(chemin, description)] des fichiers que ce mod peut poser, même absents."""
        return []

    def is_ours(self, path):
        return True

    def files(self, ctx):
        out = []
        for path, what in self.owned(ctx):
            state = ABSENT if not path.exists() else PRESENT if self.is_ours(path) else FOREIGN
            out.append(FileState(path, self.name, what, state))
        return out

    def status(self, ctx):
        present = [f for f in self.files(ctx) if f.state == PRESENT]
        return f"{len(present)} fichier(s) posé(s)" if present else "rien d'installé"

    def uninstall(self, ctx):
        """Retire nos fichiers. Rend [messages]."""
        return []

    def warnings(self, ctx):
        """Avertissements avant de lancer le jeu."""
        return []

    def build_tab(self, parent, ctx):
        raise NotImplementedError


class Randomizer(Module):
    id, name, package = "randomizer", "Randomizer", "ctrnf_rando"
    description = "Mélange le mode Aventure (circuits, récompenses, coupes, conditions, portails), toujours finissable."

    def owned(self, ctx):
        out = []
        if ctx.port.folder:
            out.append((ctx.port.folder / "patches" / "Randomizer.xml", "patch de la graine"))
        if ctx.port.archives:
            out += [(ctx.port.archives / "update4.pak", "mini-carte des reliques"),
                    (ctx.port.archives / "update_hub3.pak", "podiums rapides")]
        return out

    def is_ours(self, path):
        from ctrnf_rando import archives
        if path.suffix == ".xml":
            head = path.read_text(encoding="utf-8", errors="replace")[:4000]
            return 'Name="Randomizer"' in head and 'Author="kyogre21"' in head
        script = {s.archive: s for s in archives.SCRIPTS}.get(path.name)
        return bool(script) and archives.ours(path, script)

    def status(self, ctx):
        xml = ctx.port.folder / "patches" / "Randomizer.xml" if ctx.port.folder else None
        if not xml or not xml.is_file():
            return "aucune graine installée"
        import re
        seed = re.search(r"graine (\d+)", xml.read_text(encoding="utf-8", errors="replace")[:2000])
        return f"graine {seed.group(1)} installée" if seed else "graine installée"

    def uninstall(self, ctx):
        from ctrnf_rando import archives
        done = []
        for f in self.files(ctx):
            if f.state == PRESENT and f.path.suffix == ".xml":
                f.path.unlink()
                done.append(f"{f.path.name} retiré")
        if ctx.port.archives:
            done += [f"{name} {what}" for name, what in archives.install(ctx.port.archives, [])]
        return done

    def warnings(self, ctx):
        out = []
        files = {f.path.name: f for f in self.files(ctx)}
        xml = files.get("Randomizer.xml")
        orphans = [n for n in ("update4.pak", "update_hub3.pak") if n in files and files[n].state == PRESENT]
        if xml and xml.state == ABSENT and orphans:
            out.append(f"Archives du randomizer sans graine installée ({', '.join(orphans)}) : faites « Tout "
                       "désinstaller » ou générez une graine.")
        patches_json = ctx.port.folder / "patches.json" if ctx.port.folder else None
        if xml and xml.state == PRESENT and patches_json and patches_json.is_file():
            try:
                disabled = json.loads(patches_json.read_text(encoding="utf-8")).get("disabled", [])
            except (OSError, ValueError, AttributeError):
                disabled = []
            if "Randomizer.xml/Randomizer" in disabled:
                out.append("Le patch « Randomizer » est désactivé dans l'onglet des patchs du launcher : la graine "
                           "ne sera pas appliquée.")
        return out

    def build_tab(self, parent, ctx):
        from ctrnf_rando import gui
        return gui.App(parent, context=ctx.for_module(self.id))


class Stickers(Module):
    id, name, package = "stickers", "Autocollants", "ctrnf_stickers"
    description = "Remplace les autocollants des karts (et leurs icônes du menu) par vos propres images."

    def available(self):
        try:
            import numpy  # noqa: F401
            import PIL  # noqa: F401
        except ImportError as error:
            return False, f"{error.name} manquant : pip install -r autocollants/requirements.txt"
        return True, ""

    def owned(self, ctx):
        return [(ctx.port.archives / "update3.pak", "autocollants remplacés")] if ctx.port.archives else []

    def is_ours(self, path):
        from ctrnf_stickers import names
        return names.is_ours(path)

    def status(self, ctx):
        from ctrnf_stickers import iga, names
        files = [f for f in self.files(ctx) if f.state == PRESENT]
        if not files:
            return "aucun autocollant remplacé"
        with iga.Archive(files[0].path) as a:
            count = sum(1 for n in a.names if (names.short(n) or names.ICON_TAG)[:4] != names.ICON_TAG)
        return f"{count} autocollant(s) remplacé(s)"

    def uninstall(self, ctx):
        import datetime
        done = []
        for f in self.files(ctx):
            if f.state == PRESENT:
                backup = backup_folder()
                backup.mkdir(parents=True, exist_ok=True)
                copy = backup / f"update3_{datetime.datetime.now():%Y-%m-%d_%H%M%S}.pak"
                shutil.copyfile(f.path, copy)  # les images choisies ne vivent que là : on les garde
                f.path.unlink()
                done.append(f"{f.path.name} retiré (copie : {copy})")
        return done

    def build_tab(self, parent, ctx):
        from ctrnf_stickers import gui
        return gui.App(parent, context=ctx.for_module(self.id))


class Autosplitter(Module):
    id, name, stage = "autosplitter", "Autosplitter", "alpha"
    description = "Script LiveSplit : chrono coupé tout seul pendant le mode Aventure (lecture seule du jeu)."

    def version(self):
        try:
            for line in _paths.asl().read_text(encoding="utf-8").splitlines()[:15]:
                if line.startswith("// Version"):
                    return line.split(":", 1)[1].strip()
        except OSError:
            pass
        return "?"

    def dest(self, ctx):
        folder = ctx.config.module(self.id).get("dest")
        return Path(folder) / "CTRNF.asl" if folder else None

    def owned(self, ctx):
        dest = self.dest(ctx)
        return [(dest, "script LiveSplit")] if dest else []

    HEADER = b"// Autosplitter LiveSplit pour Crash Team Racing Nitro-Fueled"

    def is_ours(self, path):
        """Identique à un script livré : un script retouché par le joueur n'est plus « à nous » (jamais écrasé)."""
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return digest == hashlib.sha256(_paths.asl().read_bytes()).hexdigest() or digest in PUBLISHED_ASL

    def modified(self, path):
        return path.is_file() and path.read_bytes().startswith(self.HEADER) and not self.is_ours(path)

    def up_to_date(self, ctx):
        dest = self.dest(ctx)
        if not dest or not dest.is_file():
            return None
        digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
        return digest(dest) == digest(_paths.asl())

    def status(self, ctx):
        state = self.up_to_date(ctx)
        return {None: "pas encore copié", True: "CTRNF.asl copié, à jour",
                False: "CTRNF.asl copié, version différente"}[state]

    def install(self, ctx, folder, overwrite_modified=False):
        target = Path(folder) / "CTRNF.asl"
        if target.exists() and not self.is_ours(target) and not (overwrite_modified and self.modified(target)):
            if self.modified(target):
                raise ModuleError(f"{target} est notre script retouché à la main : rien n'est écrit")
            raise ModuleError(f"{target} existe et n'est pas notre script : rien n'est écrit")
        shutil.copyfile(_paths.asl(), target)
        ctx.config.set_module(self.id, {"dest": str(Path(folder))})
        return target

    def uninstall(self, ctx):
        done = []
        for f in self.files(ctx):
            if f.state == PRESENT:
                f.path.unlink()
                done.append(f"{f.path.name} retiré de {f.path.parent}")
        return done

    def build_tab(self, parent, ctx):
        from .tab_autosplitter import AutosplitterTab
        return AutosplitterTab(parent, ctx, self)


REGISTRY = (Randomizer(), Stickers(), Autosplitter())
