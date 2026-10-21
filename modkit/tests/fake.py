"""Faux port et faux jeu dans un dossier temporaire (fichiers vides : aucun fichier du jeu)."""
from pathlib import Path

from ctrnf_modkit import port


def make_port(base, game=True, launcher=True, python=True, ini_extra=""):
    base = Path(base)
    folder, game_dir = base / "OCTR port", base / "CUSA13795-1.21"
    (folder / "bin").mkdir(parents=True)
    (folder / "bin" / "sacredfire.exe").write_bytes(b"MZ")
    (folder / "bin" / "VERSION").write_text("v0.5.3-windows\n", encoding="utf-8")
    (folder / "patches").mkdir()
    (folder / "run.py").write_text("# faux run.py\n", encoding="utf-8")
    if launcher:
        (folder / "CTR-NitroFueled-PC.exe").write_bytes(b"MZ..." + port.LAUNCHER_MARK + b"...")
    (folder / "autre.exe").write_bytes(b"MZ pas un launcher")
    if python:
        (folder / "python").mkdir()
        (folder / "python" / "python.exe").write_bytes(b"MZ")
    if game:
        (game_dir / "archives").mkdir(parents=True)
        for name in port.ARCHIVES:
            (game_dir / "archives" / name).write_bytes(b"")
    (folder / "launcher.ini").write_text(f"﻿# CTR-NitroFueled-PC launcher\n{ini_extra}game_dir=\"{game_dir}\"\n"
                                         "ui_language=en\n", encoding="utf-8")
    return folder, game_dir
