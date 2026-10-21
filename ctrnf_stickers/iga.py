"""Archives IGA v13 (.pak) de CTR Nitro-Fueled : lecture (fichiers non compressés ou LZMA) et écriture (non compressé).

Format :
  en-tête 0x38 octets : magic "IGA\\x1a", version, taille_toc, nb_fichiers, taille_secteur (0x800),
    diviseur_hash, slop_hash, nb_blocs_u32, nb_blocs_u16, nb_blocs_u8, pos_noms (u64), taille_noms, drapeaux
  puis nb_fichiers empreintes (u32, FNV-1a 32 du nom court en minuscules, triées), puis nb_fichiers entrées de
  16 octets : u32 position basse | u24 n° du fichier suivant dans l'ordre des positions << 8 + u8 position haute |
  u32 taille | u32 mode (0xffffffff = non compressé, 0x2…… = LZMA + n° dans la table des blocs)
  puis les tables de blocs (u32, u16, u8) ; données à 0x800, alignées sur 0x800 ;
  noms à la fin : un décalage u32 par nom, puis "chemin complet\\0nom court\\0", 4 zéros.
"""
import lzma
from pathlib import Path
import struct

CHUNK = 0x8000
SECTOR = 0x800
FULL = 'temporary/octane/data/ps4/output/'


def fnv1a(text):
    h = 0x811c9dc5
    for c in text.lower().encode():
        h = ((h ^ c) * 0x01000193) & 0xffffffff
    return h


class Archive:
    """Archive ouverte en lecture : `names` = {nom court: (position, taille, mode)}."""

    def __init__(self, path):
        self.f = open(path, 'rb')
        head = self.f.read(0x38)
        (_, version, _, count, self.sector, _, _, n32, n16, n8, names_pos, names_size, _) = struct.unpack(
            '<4sIIIIIIIIIQII', head)
        if version != 13:
            raise ValueError(f'{Path(path).name} : archive version {version}, 13 attendue')
        self.f.read(4 * count)  # empreintes
        entries = [struct.unpack('<IIII', self.f.read(16)) for _ in range(count)]
        self.tables = {32: struct.unpack(f'<{n32}I', self.f.read(4 * n32)),
                       16: struct.unpack(f'<{n16}H', self.f.read(2 * n16)),
                       8: struct.unpack(f'<{n8}B', self.f.read(n8))}
        self.f.seek(names_pos)
        names = self.f.read(names_size)
        offsets = struct.unpack_from(f'<{count}I', names)
        self.names = {}
        for i, (low, high, size, mode) in enumerate(entries):
            end = names.index(b'\0', offsets[i])
            short = names[end + 1:names.index(b'\0', end + 1)].decode()
            self.names[short] = (low | (high & 0xFF) << 32, size, mode)

    def close(self):
        self.f.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def read(self, name):
        pos, size, mode = self.names[name]
        if mode >> 28 != 2:
            self.f.seek(pos)
            return self.f.read(size)
        chunks = -(-size // CHUNK)
        sectors = -(-size // self.sector) + chunks  # la largeur de la table dépend du nombre de secteurs
        width = 8 if sectors < 0x80 else 16 if sectors < 0x8000 else 32
        flag = 1 << (width - 1)
        blocks = self.tables[width][mode & 0xFFFFFF:(mode & 0xFFFFFF) + chunks + 1]
        out = bytearray()
        for i in range(chunks):
            self.f.seek(pos + (blocks[i] & (flag - 1)) * self.sector)
            want = min(CHUNK, size - i * CHUNK)
            if blocks[i] & flag:  # morceau compressé : u32 taille, 5 octets de propriétés LZMA, données
                packed = struct.unpack('<I', self.f.read(4))[0]
                props = self.f.read(5)
                lc, rest = props[0] % 9, props[0] // 9
                dec = lzma.LZMADecompressor(lzma.FORMAT_RAW, filters=[{
                    'id': lzma.FILTER_LZMA1, 'dict_size': struct.unpack('<I', props[1:])[0],
                    'lc': lc, 'lp': rest % 5, 'pb': rest // 5}])
                out += dec.decompress(self.f.read(packed), max_length=want)
            else:
                out += self.f.read(want)
        return bytes(out)


def write(files, out):
    """files : {nom court: contenu} -> archive IGA v13, fichiers non compressés."""
    names = sorted(files, key=fnv1a)
    count = len(names)
    hashes = [fnv1a(n) for n in names]
    if len(set(hashes)) != count:
        raise ValueError('deux noms de même empreinte')
    div = 0xffffffff // count
    slop = max(abs(i - h // div) for i, h in enumerate(hashes))
    pos, places = SECTOR, []
    for n in names:  # données dans l'ordre des noms, chacune alignée sur un secteur
        places.append(pos)
        pos += -(-len(files[n]) // SECTOR) * SECTOR
    names_at = pos
    offsets, blob = [], b''
    for n in names:
        offsets.append(4 * count + len(blob))
        blob += (FULL + n).encode() + b'\0' + n.encode() + b'\0'
    name_block = struct.pack(f'<{count}I', *offsets) + blob + bytes(4)
    entries = b''
    for i, n in enumerate(names):
        nxt = i + 1 if i + 1 < count else 0xffffff
        entries += struct.pack('<IIII', places[i] & 0xffffffff, nxt << 8 | places[i] >> 32, len(files[n]), 0xffffffff)
    head = struct.pack('<4sIIIIIIIIIQII', b'IGA\x1a', 13, 20 * count, count, SECTOR, div, slop, 0, 0, 0, names_at,
                       len(name_block), 1)
    data = bytearray(head + struct.pack(f'<{count}I', *hashes) + entries)
    data = data.ljust(SECTOR, b'\0')
    for i, n in enumerate(names):
        data = data.ljust(places[i], b'\0') + files[n]
    data = data.ljust(names_at, b'\0') + name_block
    tmp = Path(out).with_suffix('.tmp')
    tmp.write_bytes(data)
    tmp.replace(out)  # le fichier n'est jamais à moitié écrit
