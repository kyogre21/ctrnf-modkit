"""Le dossier du port CTR-NitroFueled-PC / OCTR : vérification, dossier du jeu (launcher.ini), launcher, processus.
Seule source de vérité du kit ; les mods autonomes gardent leurs propres fonctions."""
from dataclasses import dataclass, field
from pathlib import Path
import subprocess
import sys

ARCHIVES = ("stickers.pak", "update.pak", "update2.pak")  # présentes dans tout dossier archives du jeu
LAUNCHER_NAMES = ("CTR-NitroFueled-PC.exe", "Crash™ Team Racing Nitro-Fueled.exe")
LAUNCHER_MARK = b"ctr.nitrofueled.pc.launcher"  # nom du manifeste de l'exe du launcher
GAME_PROCESS = "sacredfire.exe"


@dataclass
class PortInfo:
    folder: Path = None
    ok: bool = False
    messages: list = field(default_factory=list)
    version: str = ""
    game_dir: Path = None    # dossier du jeu (launcher.ini, game_dir)
    archives: Path = None    # game_dir/archives, s'il contient les archives du jeu
    launcher: Path = None    # exe du launcher officiel
    python: Path = None      # python du port (démarrage de secours)


def read_ini(path):
    """{clé: valeur} d'un fichier clé=valeur (launcher.ini) : lignes # ignorées, BOM et guillemets enlevés, la
    dernière valeur d'une clé en double."""
    values = {}
    try:
        text = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return values
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", ";", "[")):
            continue
        key, sep, value = line.partition("=")
        if sep:
            values[key.strip()] = value.strip().strip('"')  # clé en double : la dernière compte
    return values


def is_launcher(path, limit=64 << 20):
    """L'exe porte-t-il le manifeste du launcher ? (lu par morceaux ; les gros fichiers sont ignorés)"""
    try:
        path = Path(path)
        if path.stat().st_size > limit:
            return False
        with open(path, "rb") as f:
            tail = b""
            while chunk := f.read(1 << 20):
                if LAUNCHER_MARK in tail + chunk:
                    return True
                tail = chunk[-len(LAUNCHER_MARK):]
    except OSError:
        pass
    return False


def find_launcher(folder, forced=None):
    """Exe du launcher : celui forcé, sinon parmi les noms connus puis tous les .exe de la racine du port, ceux qui
    portent le manifeste du launcher, le plus récent. None si aucun."""
    if forced and Path(forced).is_file():
        return Path(forced)
    folder = Path(folder)
    named = [folder / n for n in LAUNCHER_NAMES]
    others = sorted(p for p in folder.glob("*.exe") if p not in named)
    found = [p for p in named + others if p.is_file() and is_launcher(p)]
    return max(found, key=lambda p: p.stat().st_mtime) if found else None


def resolve(folder, game_dir_override=None, launcher_override=None):
    """PortInfo du dossier choisi (rien n'est écrit)."""
    info = PortInfo()
    if not str(folder or "").strip():
        info.messages = ["Choisissez le dossier du port."]
        return info
    folder = info.folder = Path(str(folder).strip())
    if not (folder / "bin" / GAME_PROCESS).is_file():
        info.messages.append("ce n'est pas le dossier du port (bin/sacredfire.exe introuvable)")
    if not (folder / "patches").is_dir():
        info.messages.append("dossier « patches » introuvable")
    version = folder / "bin" / "VERSION"
    info.version = version.read_text(encoding="utf-8", errors="replace").strip() if version.is_file() else ""
    game = game_dir_override or read_ini(folder / "launcher.ini").get("game_dir", "")
    if game:
        info.game_dir = Path(game)
        if all((info.game_dir / "archives" / n).is_file() for n in ARCHIVES):
            info.archives = info.game_dir / "archives"
    is_port = (folder / "bin" / GAME_PROCESS).is_file()
    info.launcher = find_launcher(folder, launcher_override) if is_port else None
    python = folder / "python" / "python.exe"
    info.python = python if python.is_file() else None
    info.ok = not info.messages
    if info.ok:
        info.messages.append(f"port {info.version or 'version inconnue'}")
        if not info.game_dir:
            info.messages.append("dossier du jeu non renseigné (launcher.ini, game_dir) : ouvrez une fois le "
                                 "launcher du port et choisissez le jeu")
        elif not info.archives:
            info.messages.append(f"archives du jeu introuvables dans {info.game_dir}")
        if not info.launcher:
            info.messages.append("launcher du port introuvable (démarrage de secours seulement)")
    return info


def running(*names):
    """Noms (en minuscules) des processus de `names` qui tournent (Windows seulement)."""
    if sys.platform != "win32":
        return set()
    try:
        out = subprocess.run(["tasklist", "/NH", "/FO", "CSV"], capture_output=True, text=True, timeout=10,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout.lower()
    except (OSError, subprocess.SubprocessError):
        return set()
    return {n.lower() for n in names if f'"{n.lower()}"' in out}


def game_running():
    return bool(running(GAME_PROCESS))
