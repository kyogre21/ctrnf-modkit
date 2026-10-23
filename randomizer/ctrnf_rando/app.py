"""Ce que fait le petit logiciel, sans la fenêtre : vérifier le dossier du port, fabriquer une graine, l'installer.
La fenêtre (gui.py) ne fait qu'appeler ces fonctions, que les tests peuvent donc vérifier."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from . import __version__
from .generator import generate, spoiler
from . import archives, comfort
from .i18n import tr
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
        problems.append(tr("ce n'est pas le dossier du port (bin/sacredfire.exe introuvable)"))
    if not (folder / "patches").is_dir():
        problems.append(tr("dossier « patches » introuvable"))
    eboot = folder / "out" / "eboot.elf"
    if not eboot.is_file():
        problems.append(tr("jeu pas encore préparé : lancez-le une fois avec le port (out/eboot.elf introuvable)"))
    else:
        data = eboot.read_bytes()
        wrong = [hex(a) for a, sig in signature_sites()
                 if data[EBOOT_CODE_OFFSET + a:EBOOT_CODE_OFFSET + a + len(sig)] != sig]
        if wrong:
            problems.append(tr("version du jeu inattendue (il faut CUSA13795 v1.21) : {n} endroit(s) différent(s)",
                                n=len(wrong)))
    version = folder / "bin" / "VERSION"
    found = version.read_text(encoding="utf-8", errors="replace").strip() if version.is_file() else tr("inconnue")
    if problems:
        return False, problems
    games = "" if archives.game_archives(folder) else tr(" (dossier du jeu introuvable dans launcher.ini : podiums "
                                                           "rapides et mini-carte des reliques indisponibles)")
    return True, [tr("port {version}, jeu CUSA13795 v1.21 vérifié", version=found) + games]


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


def wanted_archives(settings):
    """Nos archives à poser pour ces réglages (voir archives.py)."""
    return [s for s, on in ((archives.MINIMAP, settings.shuffle_rewards), (archives.PODIUM, settings.fast_podiums)) if on]


def install(seed, settings, port, rename=True):
    """Tire la graine, écrit le patch dans <port>/patches et la graine + le journal dans <port>/graines_randomizer, et
    pose (ou retire) nos archives dans le dossier du jeu. Rend (plan, empreinte, chemin du journal, messages).
    Lève ValueError / RuntimeError si la graine est impossible."""
    port = Path(port)
    target = port / "patches" / PATCH_NAME
    if target.is_file():
        head = target.read_text(encoding="utf-8", errors="replace")[:4000]
        if 'Name="Randomizer"' not in head or 'Author="kyogre21"' not in head:
            raise ValueError(tr("{file} existe et n'est pas un patch de ce randomizer : rien n'est écrit", file=target))
    plan = generate(seed, settings)
    rows = patch_rows(plan["rewards"]) if plan.get("rewards") else None
    separate = comfort.present(port)  # Confort.xml (onglet Confort du kit) s'occupe du confort
    xml = patch_xml(plan, rename=rename, rewards=rows, comfort=not separate)
    out = port / SEEDS_FOLDER
    out.mkdir(parents=True, exist_ok=True)
    (out / f"graine_{seed}.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    log = out / f"graine_{seed}_spoiler.txt"
    log.write_text(spoiler(plan), encoding="utf-8")
    target.write_text(xml, encoding="utf-8", newline="\n")
    notes = []
    folder = archives.game_archives(port)
    wanted = wanted_archives(settings)
    managed = archives.SCRIPTS
    if separate:
        managed = tuple(s for s in archives.SCRIPTS if s != archives.PODIUM)
        wanted = [s for s in wanted if s in managed]
        notes.append(tr("{file} présent : les options de confort viennent de l'onglet Confort du kit (celles de "
                        "cette graine ne sont pas posées).", file=comfort.NAME))
    if folder:
        notes += [tr("{file} {what} dans {folder}", file=name, what=tr(what), folder=folder)
                  for name, what in archives.install(folder, wanted, managed)]
    elif wanted:
        notes.append(tr("Dossier du jeu introuvable (launcher.ini du port, game_dir) : podiums rapides et mini-carte "
                        "des reliques non installés."))
    return plan, fingerprint(plan, rename), log, notes


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
