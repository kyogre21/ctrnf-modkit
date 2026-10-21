"""Lancer le jeu. Toujours par le launcher du port ou par son run.py, jamais bin/sacredfire.exe directement : c'est
run.py qui compile patches/*.xml (dont Randomizer.xml) à chaque lancement."""
from dataclasses import dataclass
import os
from pathlib import Path
import re
import subprocess
import sys

MODES = {"launcher": "Ouvrir le launcher (recommandé)", "direct": "Démarrer directement (launcher sans fenêtre)",
         "secours": "Démarrage de secours (run.py, sans les réglages du launcher)"}
SHOWN = ("launcher", "secours")  # « direct » (--play) caché tant qu'il n'est pas validé en jeu
# variables posées par l'exe PyInstaller du kit, à ne pas transmettre au jeu
FROZEN_ENV = ("_MEIPASS2", "TCL_LIBRARY", "TK_LIBRARY", "PYTHONHOME", "PYTHONPATH")


@dataclass
class Plan:
    argv: list
    cwd: Path
    env: dict
    description: str
    shell: bool = False  # True : os.startfile (exe du launcher) ; False : subprocess


def clean_env(env):
    return {k: v for k, v in env.items() if k not in FROZEN_ENV and not k.startswith("_PYI")}


def plan(info, mode="launcher", direct_arg="--play", env=None):
    """Plan de lancement pour le PortInfo `info`, ou ValueError avec le message à montrer."""
    env = clean_env(dict(os.environ if env is None else env))
    if not info.ok:
        raise ValueError("Le dossier du port n'est pas bon : voir l'accueil.")
    if mode in ("launcher", "direct") and info.launcher:
        args = [direct_arg] if mode == "direct" and direct_arg else []
        return Plan([str(info.launcher)] + args, info.folder, env, f"{MODES[mode]} : {info.launcher.name}", True)
    if mode in ("launcher", "direct") and not info.launcher:
        mode = "secours"
    if not info.game_dir:
        raise ValueError("Dossier du jeu non renseigné (launcher.ini, game_dir) : ouvrez une fois le launcher du port "
                         "et choisissez le jeu.")
    env["BB_GAME_DIR"] = str(info.game_dir)  # run.py et le .bat chercheraient sinon le jeu dans le dossier du port
    if info.python and (info.folder / "run.py").is_file():
        return Plan([str(info.python), "-X", "utf8", "run.py"], info.folder, env,
                    f"{MODES['secours']} : python\\python.exe run.py")
    bat = next(iter(sorted(info.folder.glob("*sin launcher*.bat"))), None)
    if bat:
        return Plan(["cmd", "/c", str(bat)], info.folder, env, f"{MODES['secours']} : {bat.name}")
    raise ValueError(f"Launcher du port introuvable dans {info.folder}, et pas de démarrage de secours possible "
                     "(python\\python.exe ou run.py manquant).")


def start(p):
    """Démarre le plan. Rend le processus (secours) ou None (launcher). OSError si Windows refuse."""
    if getattr(sys, "frozen", False) and sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.SetDllDirectoryW(None)  # ne pas prêter les DLL de l'exe au jeu
        for key in list(os.environ):
            if key in FROZEN_ENV or key.startswith("_PYI"):
                del os.environ[key]
    if p.shell:
        os.startfile(p.argv[0], arguments=" ".join(p.argv[1:]), cwd=str(p.cwd))
        return None
    flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
    return subprocess.Popen(p.argv, cwd=str(p.cwd), env=p.env, creationflags=flags)


def last_run_summary(folder):
    """Résumé du dernier journal du port (last_run*.log) : archives chargées et patch du randomizer."""
    logs = sorted(Path(folder).glob("last_run*.log"), key=lambda p: p.stat().st_mtime) if folder else []
    if not logs:
        return ""
    text = logs[-1].read_text(encoding="utf-8", errors="replace")
    start = text.rfind("--- SacredFire launch")
    text = text[start:] if start >= 0 else text
    when = re.search(r"--- SacredFire launch (\S+ \S+)", text)
    ours = ("update3.pak", "update4.pak", "update5.pak", "update_hub3.pak", "update_hub4.pak")  # pas celles du jeu
    loaded = [a for a in ours if f"Loading app:/archives/{a}." in text]
    rando = re.search(r"Randomizer\.xml/Randomizer \((\d+) writes\)", text)
    parts = [f"dernier lancement {when.group(1)}" if when else "dernier lancement"]
    parts.append("archives chargées : " + (", ".join(loaded) if loaded else "aucune des nôtres"))
    parts.append(f"randomizer appliqué ({rando.group(1)} écritures)" if rando else "randomizer non appliqué")
    return " ; ".join(parts)


# Codes de fin du jeu (dernière ligne du journal : « --- the game ended with code N ») et leur sens.
EXIT_CODES = {
    0: "fin normale",
    1: "run.py a refusé de démarrer (pseudo, réglages ou fichiers manquants : voir les dernières lignes)",
    2: "vérification du jeu échouée (dossier du jeu absent ou mauvaise version)",
    3: "erreur du port au démarrage (souvent libwinpthread-1.dll : il faut OCTR v0.5.1 ou plus récent)",
    130: "interrompu (Ctrl+C)",
    0xC000013A: "fermé par Ctrl+C ou par la fermeture de sa console",
    139: "plantage mémoire (segmentation fault)",
    0xC0000005: "plantage mémoire : violation d'accès (le jeu a lu ou écrit une adresse interdite)",
    0xC00000FD: "plantage : dépassement de pile",
    0xC0000409: "plantage : erreur fatale détectée par le programme (0xC0000409)",
    0xC000001D: "plantage : instruction illégale (processeur ou GPU non pris en charge ?)",
    0xC0000374: "plantage mémoire : tas corrompu (0xC0000374)",
}


def code_text(code):
    if code is None:
        return "pas de code de fin (le jeu tourne encore, ou il a été tué)"
    meaning = EXIT_CODES.get(code, "erreur inconnue")
    return f"code {code} ({code:#x}) : {meaning}" if code > 0xFFFF else f"code {code} : {meaning}"


def last_run_report(folder, lines=40):
    """Ce que dit le dernier journal du port : {log, started, code, meaning, crashed, patches, tail} ou None."""
    logs = sorted(Path(folder).glob("last_run*.log"), key=lambda p: p.stat().st_mtime) if folder else []
    if not logs:
        return None
    text = logs[-1].read_text(encoding="utf-8", errors="replace")
    start = text.rfind("--- SacredFire launch")
    text = text[start:] if start >= 0 else text
    when = re.search(r"--- SacredFire launch (\S+ \S+)", text)
    end = re.findall(r"--- the game ended with code (-?\d+)", text)
    code = int(end[-1]) & 0xFFFFFFFF if end else None
    tail = [line for line in text.splitlines() if line.strip()][-lines:]
    return {"log": logs[-1], "started": when.group(1) if when else "?", "code": code, "meaning": code_text(code),
            "crashed": code not in (None, 0, 130, 0xC000013A), "patches": re.findall(r"Patches: external (.+?) \((\d+) writes\)", text),
            "tail": tail}
