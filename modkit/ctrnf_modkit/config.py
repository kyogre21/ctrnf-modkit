"""Réglages du kit (~/.ctrnf_modkit.json), repris une fois des réglages des mods autonomes s'il n'existe pas.
Les fichiers des mods autonomes ne sont jamais modifiés."""
import json
import os
from pathlib import Path

FORMAT = 1
MODULES = ("randomizer", "stickers", "autosplitter")


def path():
    return Path.home() / ".ctrnf_modkit.json"


def defaults():
    return {"format": FORMAT, "port": "", "game_dir_override": None, "enabled": list(MODULES),
            "launch": {"mode": "launcher", "direct_arg": "--play", "launcher_exe": None},
            "modules": {m: {} for m in MODULES}}


def _read(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def migrate_legacy():
    """Réglages repris de ~/.ctrnf_randomizer.json et ~/.ctrnf_stickers.json."""
    data = defaults()
    rando = _read(Path.home() / ".ctrnf_randomizer.json")
    stickers = _read(Path.home() / ".ctrnf_stickers.json")
    if isinstance(rando, dict):
        data["port"] = str(rando.get("port") or "")
        data["modules"]["randomizer"] = {k: v for k, v in rando.items() if k not in ("port", "version")}
    if isinstance(stickers, dict):
        data["modules"]["stickers"] = {k: stickers[k] for k in ("cutout", "icon") if k in stickers}
        folder = str(stickers.get("folder") or "").strip()
        if folder and not data["port"] and (Path(folder) / "launcher.ini").is_file():
            data["port"] = folder
    return data


def merged(raw):
    """Réglages lus, ramenés aux types attendus : une valeur d'un mauvais type est remplacée par celle par défaut."""
    data = defaults()
    for key, value in raw.items():
        if key not in data or data[key] is None or isinstance(value, type(data[key])):
            if isinstance(data.get(key), dict):
                data[key].update({k: v for k, v in value.items() if not isinstance(data[key].get(k), dict)
                                  or isinstance(v, dict)})
            else:
                data[key] = value
    data["enabled"] = [m for m in data["enabled"] if m in MODULES]
    return data


class Config:
    """data : le dictionnaire des réglages ; save() l'écrit (sauf s'il vient d'une version plus récente du kit)."""

    def __init__(self, file=None):
        self.file = Path(file) if file else path()
        self.read_only = False
        self.warning = ""
        if not self.file.exists():
            self.data = migrate_legacy()
            self.save()
            return
        raw = _read(self.file)
        if not isinstance(raw, dict) or not isinstance(raw.get("format", 0), int):
            try:
                os.replace(self.file, self.file.with_suffix(".json.bak"))
                self.warning = f"Réglages illisibles : copiés dans {self.file.name}.bak, réglages par défaut."
            except OSError:
                self.read_only = True
            self.data = defaults()
            return
        if raw.get("format", 0) > FORMAT:
            self.read_only = True
            self.warning = "Réglages faits par une version plus récente du kit : ils ne seront pas modifiés."
        self.data = merged(raw)

    def module(self, name):
        return dict(self.data["modules"].get(name) or {})

    def set_module(self, name, values):
        # un autre kit ouvert a pu enregistrer d'autres mods entre-temps : on reprend les siens
        disk = _read(self.file)
        if isinstance(disk, dict) and isinstance(disk.get("modules"), dict):
            for other, conf in disk["modules"].items():
                if other != name and other in MODULES and isinstance(conf, dict):
                    self.data["modules"][other] = conf
        self.data["modules"][name] = {k: v for k, v in values.items() if k not in ("port", "folder", "version")}
        self.save()

    def save(self):
        if self.read_only:
            return
        tmp = self.file.with_suffix(".json.tmp")
        try:
            tmp.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp, self.file)
        except OSError:
            pass
