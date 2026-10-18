"""Ce que fait le petit logiciel, sans la fenêtre : vérifier le dossier du port, fabriquer une graine, l'installer.
La fenêtre (gui.py) ne fait qu'appeler ces fonctions, que les tests peuvent donc vérifier."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from . import __version__
from .generator import generate, spoiler
from .patch import patch_xml, signature_sites
from .rewards import patch_rows

PATCH_NAME = "Randomizer.xml"
SEEDS_FOLDER = "graines_randomizer"  # dans le dossier du port
EBOOT_CODE_OFFSET = 0x4000  # out/eboot.elf : le code du jeu commence à cette position du fichier (adresse 0)
CONFIG = Path.home() / ".ctrnf_randomizer.json"  # derniers réglages de la fenêtre


def check_port(folder):
    """(bon, [messages]) : le dossier est-il celui du port CTR-NitroFueled-PC, avec le jeu en version 1.21 ?"""
    folder = Path(folder)
    problems = []
    if not (folder / "bin" / "sacredfire.exe").is_file() and not (folder / "bin" / "VERSION").is_file():
        problems.append("ce n'est pas le dossier du port (bin/sacredfire.exe introuvable)")
    if not (folder / "patches").is_dir():
        problems.append("dossier « patches » introuvable")
    eboot = folder / "out" / "eboot.elf"
    if not eboot.is_file():
        problems.append("jeu pas encore préparé : lancez-le une fois avec le port (out/eboot.elf introuvable)")
    else:
        data = eboot.read_bytes()
        wrong = [hex(a) for a, sig in signature_sites()
                 if data[EBOOT_CODE_OFFSET + a:EBOOT_CODE_OFFSET + a + len(sig)] != sig]
        if wrong:
            problems.append(f"version du jeu inattendue (il faut CUSA13795 v1.21) : {len(wrong)} endroit(s) différent(s)")
    version = folder / "bin" / "VERSION"
    found = version.read_text(encoding="utf-8", errors="replace").strip() if version.is_file() else "inconnue"
    if problems:
        return False, problems
    return True, [f"port {found}, jeu CUSA13795 v1.21 vérifié"]


def game_running():
    """Le jeu (sacredfire.exe) tourne-t-il ? (Windows seulement ; ailleurs : on ne sait pas, donc non)"""
    if sys.platform != "win32":
        return False
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq sacredfire.exe", "/NH"], capture_output=True,
                             text=True, timeout=10, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    return "sacredfire.exe" in out.lower()


def fingerprint(plan, rename):
    """Empreinte courte de la graine et de ses réglages (deux joueurs comparent ce code pour être sûrs d'avoir la même
    partie)."""
    text = json.dumps({"plan": plan, "noms": rename}, sort_keys=True)
    digest = hashlib.sha256(text.encode()).hexdigest().upper()
    return f"{digest[:4]}-{digest[4:8]}"


def install(seed, settings, port, rename=True):
    """Tire la graine, écrit le patch dans <port>/patches et la graine + le journal dans <port>/graines_randomizer.
    Rend (plan, empreinte, chemin du journal). Lève ValueError / RuntimeError si la graine est impossible."""
    port = Path(port)
    plan = generate(seed, settings)
    rows = patch_rows(plan["rewards"]) if plan.get("rewards") else None
    xml = patch_xml(plan, rename=rename, rewards=rows)
    out = port / SEEDS_FOLDER
    out.mkdir(parents=True, exist_ok=True)
    (out / f"graine_{seed}.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    log = out / f"graine_{seed}_spoiler.txt"
    log.write_text(spoiler(plan), encoding="utf-8")
    (port / "patches" / PATCH_NAME).write_text(xml, encoding="utf-8", newline="\n")
    return plan, fingerprint(plan, rename), log


def load_config():
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_config(values):
    try:
        CONFIG.write_text(json.dumps({**values, "version": __version__}, indent=2), encoding="utf-8")
    except OSError:
        pass
