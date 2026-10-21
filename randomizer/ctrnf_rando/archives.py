"""Petites archives à nous, que le jeu cherche au démarrage dans le dossier `archives` du jeu, à côté des siennes :
elles remplacent quelques scripts du jeu sans toucher à ses fichiers (supprimer l'archive remet le jeu d'origine).

- `update4.pak` (avec les récompenses mélangées) : la mini-carte du hub ne coche un portail de course que quand ses
  3 paliers de relique sont gagnés (chaque palier est un lieu à part ; le jeu cochait dès le premier).
- `update_hub3.pak` (confort « podiums ») : l'écran « appuyez pour passer » du podium s'ouvre dès le début, l'animation
  du podium garde sa vitesse (après elle, le podium garde sa dernière pose).

Chaque script est lu dans l'archive du jeu du joueur, vérifié (empreinte SHA-256) et modifié de quelques octets ; aucun
fichier du jeu n'est copié dans ce dépôt. `update3.pak` appartient à l'outil des autocollants (ctrnf-stickers) : on n'y
touche jamais.
"""
import hashlib
import lzma
from pathlib import Path
import struct

SECTOR = 0x800
CHUNK = 0x8000
FULL = "temporary/octane/data/ps4/output/"  # préfixe des noms complets dans les archives du jeu


class Script:
    def __init__(self, archive, source, name, sha256, changes):
        self.archive = archive    # notre archive
        self.source = source      # archive du jeu qui contient le script d'origine
        self.name = name
        self.sha256 = sha256      # empreinte du script d'origine (jeu v1.21)
        self.changes = changes    # [(position dans le fichier, octet d'origine, nouvel octet)]


# Mini-carte : dans le test des reliques (platine, puis or, puis saphir), « gagné » passe au palier suivant et « pas
# gagné » à « pas terminé » (listes de sorties des nœuds platine et or).
MINIMAP = Script("update4.pak", "juicedomain_hub.pak", "vsc/UI/Octane_Minimap_HUB/Octane_Minimap_HUB_Race_Pad_Icon.igz",
                 "64b901d3867b33c42e5b76b33958e341f1af3985d77367b3baeb11a9f72f63ac",
                 [(0x3130, 0x68, 0xf0), (0x3131, 0x0d, 0x10), (0x3138, 0xf0, 0x20), (0x3139, 0x10, 0x08),
                  (0x31d0, 0x68, 0xc8), (0x31d1, 0x0d, 0x0c), (0x31d8, 0xc8, 0x20), (0x31d9, 0x0c, 0x08)])
# Podium : au début du podium, le script enchaîne sur le nœud « animation puis ouverture de l'écran », qui joue
# l'animation du podium (au lieu de sa boucle) sans boucler.
PODIUM = Script("update_hub3.pak", "update_hub2.pak", "vsc/Octane/H100_Hub/Hub_Start_Event_Chain.igz",
                "ee4e89b606b2ab11a445a3ab9ac6951abe67643a74b5de020a2b145b625bf477",
                [(0x1add4, 0x40, 0xe0), (0x1add5, 0x50, 0x4d), (0x1aec2, 0x01, 0x00), (0x2ce9c, 0xb8, 0xc0),
                 (0x2ce9d, 0x4c, 0x4f)])
SCRIPTS = (MINIMAP, PODIUM)


def game_archives(port):
    """Dossier `archives` du jeu, lu dans `launcher.ini` du port (`game_dir`), ou None."""
    ini = Path(port) / "launcher.ini"
    if not ini.is_file():
        return None
    game = ""
    for line in ini.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        key, sep, value = line.strip().partition("=")
        if sep and key.strip() == "game_dir":
            game = value.strip().strip('"')  # clé en double : la dernière compte (comme le kit)
    folder = Path(game) / "archives" if game else None
    return folder if folder and folder.is_dir() else None


def read_archive(path):
    """[(nom court, position, taille, mode)] d'une archive IGA v13, et (secteur, tables des blocs)."""
    with open(path, "rb") as f:
        head = f.read(0x38)
        (magic, version, _, count, sector, _, _, n32, n16, n8, names_pos, names_size, _) = struct.unpack(
            "<4sIIIIIIIIIQII", head)
        if magic != b"IGA\x1a" or version != 13:
            raise ValueError(f"{Path(path).name} : archive inconnue")
        f.read(4 * count)
        entries = [struct.unpack("<IIII", f.read(16)) for _ in range(count)]
        tables = {32: struct.unpack(f"<{n32}I", f.read(4 * n32)), 16: struct.unpack(f"<{n16}H", f.read(2 * n16)),
                  8: struct.unpack(f"<{n8}B", f.read(n8))}
        f.seek(names_pos)
        names = f.read(names_size)
    offsets = struct.unpack_from(f"<{count}I", names)
    files = []
    for i, (low, high, size, mode) in enumerate(entries):
        end = names.index(b"\0", offsets[i])
        short_end = names.index(b"\0", end + 1)
        files.append((names[end + 1:short_end].decode(), low | (high & 0xFF) << 32, size, mode))
    return files, sector, tables


def extract(path, name):
    """Contenu d'un fichier d'une archive IGA (morceaux de 0x8000 octets, LZMA ou non)."""
    files, sector, tables = read_archive(path)
    entry = next((e for e in files if e[0] == name), None)
    if entry is None:
        raise ValueError(f"{name} absent de {Path(path).name}")
    _, pos, size, mode = entry
    with open(path, "rb") as f:
        if mode >> 28 != 2:
            f.seek(pos)
            return f.read(size)
        chunks = -(-size // CHUNK)
        sectors = -(-size // sector) + chunks
        width = 8 if sectors < 0x80 else 16 if sectors < 0x8000 else 32
        flag = 1 << (width - 1)
        blocks = tables[width][mode & 0xFFFFFF:(mode & 0xFFFFFF) + chunks + 1]
        out = bytearray()
        for i in range(chunks):
            f.seek(pos + (blocks[i] & (flag - 1)) * sector)
            want = min(CHUNK, size - i * CHUNK)
            if blocks[i] & flag:
                packed = struct.unpack("<I", f.read(4))[0]
                props = f.read(5)
                lc, rest = props[0] % 9, props[0] // 9
                dec = lzma.LZMADecompressor(lzma.FORMAT_RAW, filters=[{
                    "id": lzma.FILTER_LZMA1, "dict_size": struct.unpack("<I", props[1:])[0],
                    "lc": lc, "lp": rest % 5, "pb": rest // 5}])
                out += dec.decompress(f.read(packed), max_length=want)
            else:
                out += f.read(want)
    return bytes(out)


def fnv1a(text):
    h = 0x811c9dc5
    for c in text.lower().encode():
        h = ((h ^ c) * 0x01000193) & 0xffffffff
    return h


def pak_bytes(files):
    """{nom court: contenu} -> archive IGA v13, fichiers non compressés."""
    names = sorted(files, key=fnv1a)
    count = len(names)
    hashes = [fnv1a(n) for n in names]
    if len(set(hashes)) != count:
        raise ValueError("deux noms de même empreinte")
    div = 0xffffffff // count
    slop = max(abs(i - h // div) for i, h in enumerate(hashes))
    start = -(-(0x38 + 20 * count) // SECTOR) * SECTOR  # après l'en-tête (plus d'un secteur dès 100 fichiers)
    pos, places = start, []
    for n in names:
        places.append(pos)
        pos += -(-len(files[n]) // SECTOR) * SECTOR
    names_at = pos
    offsets, blob = [], b""
    for n in names:
        offsets.append(4 * count + len(blob))
        blob += (FULL + n).encode() + b"\0" + n.encode() + b"\0"
    name_block = struct.pack(f"<{count}I", *offsets) + blob + bytes(4)
    entries = b""
    for i, n in enumerate(names):
        nxt = i + 1 if i + 1 < count else 0xffffff
        entries += struct.pack("<IIII", places[i] & 0xffffffff, nxt << 8 | places[i] >> 32, len(files[n]), 0xffffffff)
    head = struct.pack("<4sIIIIIIIIIQII", b"IGA\x1a", 13, 20 * count, count, SECTOR, div, slop, 0, 0, 0, names_at,
                       len(name_block), 1)
    data = bytearray(head + struct.pack(f"<{count}I", *hashes) + entries).ljust(start, b"\0")
    for i, n in enumerate(names):
        data = data.ljust(places[i], b"\0") + files[n]
    return bytes(data.ljust(names_at, b"\0") + name_block)


def patched(script, data):
    if hashlib.sha256(data).hexdigest() != script.sha256:
        raise ValueError(f"{script.name} : version du jeu inattendue (il faut CUSA13795 v1.21)")
    out = bytearray(data)
    for at, old, new in script.changes:
        out[at] = new
    return bytes(out)


def ours(path, script):
    """L'archive en `path` est-elle la nôtre (rien d'autre que le script de `script`) ?"""
    try:
        return [e[0] for e in read_archive(path)[0]] == [script.name]
    except (OSError, ValueError, struct.error):
        return False


def install(folder, wanted):
    """Écrit (ou retire) nos archives dans le dossier `archives` du jeu. wanted : scripts voulus.
    Rend [(archive, « posée » | « retirée »)]. Une archive du même nom qui n'est pas la nôtre n'est jamais touchée."""
    folder = Path(folder)
    done = []
    for script in SCRIPTS:
        target = folder / script.archive
        if target.exists() and not ours(target, script):
            if script in wanted:
                raise ValueError(f"{target} existe déjà et n'est pas une archive du randomizer : rien n'est écrit")
            continue
        if script in wanted:
            data = patched(script, extract(folder / script.source, script.name))
            tmp = target.with_suffix(".tmp")  # jamais d'archive à moitié écrite, même si le jeu tourne
            tmp.write_bytes(pak_bytes({script.name: data}))
            tmp.replace(target)
            done.append((script.archive, "posée"))
        elif target.exists():
            target.unlink()
            done.append((script.archive, "retirée"))
    return done
