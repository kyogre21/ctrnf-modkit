"""Où trouver les paquets des mods et les fichiers livrés avec le kit (dépôt ou exe PyInstaller)."""
from pathlib import Path
import sys

FROZEN = getattr(sys, "frozen", False)
# dépôt : modkit/ctrnf_modkit/_paths.py -> racine du dépôt ; exe : dossier temporaire de PyInstaller
ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))


def setup():
    """Hors exe, rend importables ctrnf_rando (randomizer/) et ctrnf_stickers (autocollants/)."""
    if FROZEN:
        return
    for sub in ("randomizer", "autocollants"):
        path = str(ROOT / sub)
        if path not in sys.path:
            sys.path.insert(0, path)


def asl():
    """Le script LiveSplit livré avec le kit."""
    return ROOT / "autosplitter" / "CTRNF.asl"
