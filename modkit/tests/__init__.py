# Tests du CTRNF Mod Kit, sans le jeu. Lancer depuis le dossier modkit : python -m pytest -q tests
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for sub in ("modkit", "randomizer", "autocollants"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))
