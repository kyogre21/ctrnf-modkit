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
from .i18n import tr

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
        from ctrnf_rando import archives
        for path, what in self.owned(ctx):
            if not path.exists() or (path.name in archives.CHAIN and archives.is_filler(path)):
                state = ABSENT  # un bouche-trou du kit (voir archives.fix_chain) tient juste la place
            else:
                state = PRESENT if self.is_ours(path) else FOREIGN
            out.append(FileState(path, self.name, what, state))
        return out

    def status(self, ctx):
        present = [f for f in self.files(ctx) if f.state == PRESENT]
        return tr("{n} fichier(s) posé(s)", n=len(present)) if present else tr("rien d'installé")

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
            out.append((ctx.port.archives / "update4.pak", "mini-carte des reliques"))
            if not comfort_installed(ctx):  # sinon, les podiums rapides sont réglés par l'onglet Confort
                out.append((ctx.port.archives / "update_hub3.pak", "podiums rapides"))
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
            return tr("aucune graine installée")
        import re
        seed = re.search(r"graine (\d+)", xml.read_text(encoding="utf-8", errors="replace")[:2000])
        return tr("graine {seed} installée", seed=seed.group(1)) if seed else tr("graine installée")

    def uninstall(self, ctx):
        from ctrnf_rando import archives
        done = []
        for f in self.files(ctx):
            if f.state == PRESENT and f.path.suffix == ".xml":
                f.path.unlink()
                done.append(tr("{file} retiré", file=f.path.name))
        if ctx.port.archives:
            managed = (archives.MINIMAP,) if comfort_installed(ctx) else archives.SCRIPTS
            done += [f"{name} {tr(what)}" for name, what in archives.install(ctx.port.archives, [], managed)]
        return done

    def warnings(self, ctx):
        out = []
        files = {f.path.name: f for f in self.files(ctx)}
        xml = files.get("Randomizer.xml")
        orphans = [n for n in ("update4.pak", "update_hub3.pak") if n in files and files[n].state == PRESENT]
        if xml and xml.state == ABSENT and orphans:
            out.append(tr("Archives du randomizer sans graine installée ({files}) : faites « Tout désinstaller » "
                          "ou générez une graine.", files=", ".join(orphans)))
        patches_json = ctx.port.folder / "patches.json" if ctx.port.folder else None
        if xml and xml.state == PRESENT and "Randomizer.xml/Randomizer" in disabled_patches(ctx):
            out.append(tr("Le patch « Randomizer » est désactivé dans l'onglet des patchs du launcher : la graine "
                          "ne sera pas appliquée."))
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
            return False, tr("{name} manquant : pip install -r autocollants/requirements.txt", name=error.name)
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
            return tr("aucun autocollant remplacé")
        with iga.Archive(files[0].path) as a:
            count = sum(1 for n in a.names if (names.short(n) or names.ICON_TAG)[:4] != names.ICON_TAG)
        return tr("{n} autocollant(s) remplacé(s)", n=count)

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
                done.append(tr("{file} retiré (copie : {copy})", file=f.path.name, copy=copy))
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
        return tr({None: "pas encore copié", True: "CTRNF.asl copié, à jour",
                   False: "CTRNF.asl copié, version différente"}[state])

    def install(self, ctx, folder, overwrite_modified=False):
        target = Path(folder) / "CTRNF.asl"
        if target.exists() and not self.is_ours(target) and not (overwrite_modified and self.modified(target)):
            if self.modified(target):
                raise ModuleError(tr("{file} est notre script retouché à la main : rien n'est écrit", file=target))
            raise ModuleError(tr("{file} existe et n'est pas notre script : rien n'est écrit", file=target))
        shutil.copyfile(_paths.asl(), target)
        ctx.config.set_module(self.id, {"dest": str(Path(folder))})
        return target

    def uninstall(self, ctx):
        done = []
        for f in self.files(ctx):
            if f.state == PRESENT:
                f.path.unlink()
                done.append(tr("{file} retiré de {folder}", file=f.path.name, folder=f.path.parent))
        return done

    def build_tab(self, parent, ctx):
        from .tab_autosplitter import AutosplitterTab
        return AutosplitterTab(parent, ctx, self)


class Comfort(Module):
    id, name, package = "comfort", "Confort", "ctrnf_rando"
    description = "Options de confort sur le jeu d'origine, sans randomizer (reliques, réserve de boost, podiums…)."

    def owned(self, ctx):
        out = []
        if ctx.port.folder:
            out.append((ctx.port.folder / "patches" / "Confort.xml", "options de confort"))
        if ctx.port.archives and comfort_installed(ctx):  # sans Confort.xml : archive du randomizer
            out.append((ctx.port.archives / "update_hub3.pak", "podiums rapides"))
        if ctx.port.archives:
            out.append((ctx.port.archives / "update5.pak", "Recommencer / Continuer des reliques"))
        return out

    def is_ours(self, path):
        from ctrnf_rando import archives, comfort
        if path.suffix == ".xml":
            return comfort.is_ours(path)
        return archives.ours(path, archives.RELIC if path.name == archives.RELIC.archive else archives.PODIUM)

    def status(self, ctx):
        from ctrnf_rando import comfort
        values = comfort.read_settings(ctx.port.folder) if ctx.port.folder else None
        if values is None:
            return tr("rien d'installé")
        count = sum(values.values())
        return tr("{n} option(s) installée(s)", n=count) if count else tr("Confort.xml posé, aucune option")

    def uninstall(self, ctx):
        from ctrnf_rando import comfort
        return comfort.uninstall(ctx.port.folder) if ctx.port.folder else []

    def warnings(self, ctx):
        files = {f.path.name: f for f in self.files(ctx)}
        xml = files.get("Confort.xml")
        if xml and xml.state == PRESENT and "Confort.xml/Confort" in disabled_patches(ctx):
            return [tr("Le patch « Confort » est désactivé dans l'onglet des patchs du launcher : les options de "
                       "confort ne seront pas appliquées.")]
        return []

    def build_tab(self, parent, ctx):
        from .tab_comfort import ComfortTab
        return ComfortTab(parent, ctx, self)


def comfort_installed(ctx):
    """Confort.xml (à nous) est-il posé ? Alors l'archive des podiums rapides est à l'onglet Confort, sinon au
    randomizer : chaque fichier n'a qu'un seul mod propriétaire."""
    from ctrnf_rando import comfort
    return bool(ctx.port.folder) and comfort.present(ctx.port.folder)


def disabled_patches(ctx):
    """Patchs désactivés dans l'onglet des patchs du launcher (patches.json du port : « fichier/nom »)."""
    patches_json = ctx.port.folder / "patches.json" if ctx.port.folder else None
    if not patches_json or not patches_json.is_file():
        return []
    try:
        return json.loads(patches_json.read_text(encoding="utf-8")).get("disabled", [])
    except (OSError, ValueError, AttributeError):
        return []


REGISTRY = (Randomizer(), Stickers(), Autosplitter(), Comfort())
