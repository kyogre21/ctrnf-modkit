"""Les autres patchs que le port appliquera au jeu écrivent-ils aux mêmes adresses que les nôtres ?

Le 20/11/2026, le port OCTR v0.9.0 a intégré le « Pack Tacho », toujours actif, dont le code occupe une partie des
zones libres de l'exécutable où le randomizer pose le sien : deux écritures au même endroit, et le jeu plante. Une
prochaine mise à jour du port, ou un mod, peut refaire la même chose avec un nouveau fichier. Avant de poser une
graine (ou le confort), et à chaque ouverture du kit, on lit donc tous les patchs que le port appliquera :
patches/*.xml (sauf ceux désactivés dans patches.json), les paquets intégrés (scripts/*/patches/*.xml) et les mods
(mods/), pour le jeu USA (CUSA13795) ; un chevauchement est annoncé clairement au lieu d'un plantage."""
import json
from pathlib import Path
import re

TITLE = "CUSA13795"
OURS = {"Randomizer.xml": "Randomizer", "Confort.xml": "Confort"}
PATCH = re.compile(r"<Patch\b.*?</Patch>", re.S)
META = re.compile(r"<Metadata\b(.*?)>(.*?)</Metadata>", re.S)
LINE = re.compile(r"<Line\b[^>]*>")


def _attr(text, name):
    m = re.search(name + r'="([^"]*)"', text)
    return m.group(1) if m else None


def spans(xml):
    """[(début, fin)] des écritures d'un texte de patch (adresses telles qu'écrites dans le XML)."""
    out = []
    for m in LINE.finditer(xml):
        address, value = _attr(m.group(), "Address"), _attr(m.group(), "Value")
        if not address or value is None:
            continue
        try:
            start = int(address, 16)
        except ValueError:
            continue
        size = len(value) // 2 if _attr(m.group(), "Type") in (None, "bytes") else 8
        if size:
            out.append((start, start + size))
    return out


def _choices(port):
    """(activés, désactivés) à la main dans l'onglet des patchs du launcher (patches.json : « Fichier.xml/Nom »)."""
    try:
        data = json.loads((Path(port) / "patches.json").read_text(encoding="utf-8"))
        return set(data.get("enabled", [])), set(data.get("disabled", []))
    except (OSError, ValueError, AttributeError):
        return set(), set()


def _files(port):
    port = Path(port)
    yield from sorted((port / "patches").glob("*.xml"))
    scripts = port / "scripts"
    if scripts.is_dir():
        yield from sorted(p for p in scripts.glob("*/patches/*.xml"))
    mods = port / "mods"
    if mods.is_dir():
        yield from sorted(mods.rglob("*.xml"))


def other_patches(port):
    """[(fichier, nom du patch, [(début, fin)])] des patchs du jeu USA que le port appliquera, sauf les nôtres."""
    port = Path(port)
    enabled, disabled = _choices(port)
    out = []
    for path in _files(port):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for block in PATCH.findall(text) or [text]:
            if TITLE not in block:
                continue
            for attrs, body in META.findall(block):
                name = _attr(attrs, "Name") or path.stem
                key = f"{path.name}/{name}"
                if path.parent.name == "patches" and path.parent.parent == port:
                    if path.name in OURS and OURS[path.name] == name:
                        continue
                    # comme le launcher : actif s'il est coché dans patches.json, ou allumé dans son fichier sans
                    # avoir été décoché
                    on = key in enabled or (_attr(attrs, "isEnabled") != "false" and key not in disabled)
                    if not on:
                        continue
                elif _attr(attrs, "isEnabled") == "false":
                    continue   # un paquet ou un mod livré éteint
                found = spans(body)
                if found:
                    out.append((path, name, found))
    return out


def conflicts(port, xml):
    """[(fichier, nom du patch, première adresse commune)] : les patchs du port qui écrivent là où écrit `xml`."""
    ours = sorted(spans(xml))
    out = []
    for path, name, theirs in other_patches(port):
        hit = next((max(a, c) for a, b in ours for c, d in theirs if a < d and c < b), None)
        if hit is not None:
            out.append((path, name, hit))
    return out


def describe(port, found, limit=3):
    """"Barra de reservas" (scripts/tacho_pack/patches/BarraReservas.xml), … : pour un message."""
    port = Path(port)
    parts = []
    for path, name, _ in found[:limit]:
        try:
            where = path.parent.relative_to(port).as_posix()
        except ValueError:
            where = str(path.parent)
        parts.append(f"\"{name}\" ({where}/{path.name})")
    more = len(found) - limit
    return ", ".join(parts) + (f" +{more}" if more > 0 else "")
