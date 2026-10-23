"""Fichiers IGZ v10 (moteur Alchemy du jeu) : lecture (sections, corrections, objets, pointeurs) et réécriture avec des
objets ajoutés en fin de données. Les listes de corrections (RVTB, ROFS, RNEX…) sont décodées puis réencodées ; sans
modification, un fichier ressort identique octet pour octet."""
import struct

LISTS = ("RVTB", "ROFS", "RSTT", "RNEX", "RHND", "RPID", "REXT", "RSTR", "RMHN")


def unpack_ints(data, count):
    """Entiers des corrections : demi-octets (3 bits + bit de suite), écarts multipliés par 4, demi-octet bas d'abord."""
    out, last, pos, half = [], 0, 0, False
    for _ in range(count):
        value = shift = 0
        while True:
            b = data[pos]
            n = b >> 4 if half else b & 0xF
            if half:
                pos += 1
            half = not half
            value |= (n & 7) << shift
            shift += 3
            if not n & 8:
                break
        last += value * 4
        out.append(last)
    return out


def pack_ints(offsets):
    nibbles, last = [], 0
    for off in offsets:
        delta = off - last
        if delta < 0 or delta % 4:
            raise ValueError(f"correction mal placée : {off:#x}")
        value = delta // 4
        while True:
            nibbles.append(value & 7 | (8 if value >> 3 else 0))
            value >>= 3
            if not value:
                break
        last = off
    if len(nibbles) % 2:
        nibbles.append(0)
    return bytes(nibbles[i] | nibbles[i + 1] << 4 for i in range(0, len(nibbles), 2))


def _strings(blob, count):
    out, pos = [], 0
    for _ in range(count):
        end = blob.index(b"\0", pos)
        out.append(blob[pos:end].decode("latin-1"))
        pos = end + 1 + (end + 1) % 2  # chaînes alignées sur 2
    return out


class Igz:
    """Un fichier IGZ : `data` (section des données, modifiable), corrections, objets {position: type}."""

    def __init__(self, raw):
        self.src = bytes(raw)
        magic, version = struct.unpack_from("<II", raw, 0)
        if magic != 0x49475A01 or version != 10:
            raise ValueError("pas un fichier IGZ v10")
        (_, off0, size0, _), (_, off1, size1, _) = (struct.unpack_from("<4I", raw, 0x14 + 16 * i) for i in range(2))
        if off0 != 0x800 or off1 != off0 + size0 or off1 + size1 != len(raw):
            raise ValueError("disposition IGZ inattendue")
        self.data = bytearray(raw[off1:])
        self.original = bytes(self.data)  # les copies se font d'après les octets d'origine
        self.blocks = []  # [étiquette, nombre, en-tête, contenu brut ou liste, longueur, position]
        p = off0
        while p < off1:
            tag = raw[p:p + 4].decode("latin-1")
            count, length, head = struct.unpack_from("<III", raw, p + 4)
            if not length:
                break
            body = raw[p + head:p + length]
            self.blocks.append([tag, count, head, unpack_ints(body, count) if tag in LISTS else body, length, p])
            p += length
        self.tail = raw[p:off1]
        self.dirty = set()
        self.types = _strings(self.block("TMET")[3], self.block("TMET")[1])
        self.sizes = struct.unpack_from(f"<{len(self.types)}I", self.block("MTSZ")[3])
        self.objects = {off: self.types[struct.unpack_from("<Q", self.data, off)[0]] for off in self.fixups("RVTB")}
        self.pointers = set(self.fixups("ROFS"))

    def block(self, tag):
        return next(b for b in self.blocks if b[0] == tag)

    def fixups(self, tag):
        return self.block(tag)[3]

    def add_fixup(self, tag, off):
        lst = self.fixups(tag)
        if off not in lst:
            lst.append(off)
            lst.sort()
            self.dirty.add(tag)
        if tag == "ROFS":
            self.pointers.add(off)

    def u32(self, off):
        return struct.unpack_from("<I", self.data, off)[0]

    def u64(self, off):
        return struct.unpack_from("<Q", self.data, off)[0]

    def set_u64(self, off, value):
        struct.pack_into("<Q", self.data, off, value)

    def ptr(self, off):
        """Position visée par le pointeur rangé en `off`, ou None."""
        return self.u64(off) & 0x7FFFFFF if off in self.pointers else None

    def set_ptr(self, off, target):
        self.set_u64(off, target)
        self.add_fixup("ROFS", off)

    def kind(self, off):
        return self.objects.get(off)

    def append(self, raw, align=8):
        """Ajoute des octets en fin de données ; rend leur position."""
        self.data += bytes(-len(self.data) % align)
        at = len(self.data)
        self.data += raw
        return at

    def copy(self, off, size, extra=0):
        """Copie d'un objet (ou d'octets) existant, ajoutée en fin de données ; rend sa position."""
        return self.append(self.original[off:off + size] + bytes(extra))

    def new_object(self, template, size, extra=0):
        at = self.copy(template, size, extra)
        self.add_fixup("RVTB", at)
        self.objects[at] = self.objects[template]
        return at

    def add_ref(self, obj):
        """Une référence de plus vers un objet existant (compteur en +8)."""
        struct.pack_into("<I", self.data, obj + 8, self.u32(obj + 8) + 1)

    def build(self):
        out = bytearray()
        for tag, count, head, body, length, pos in self.blocks:
            if tag in LISTS and tag in self.dirty:
                raw = pack_ints(body)
                length = head + (len(raw) + 3 & ~3)
                block = bytearray(length)
                block[:4] = tag.encode("latin-1")
                struct.pack_into("<III", block, 4, len(body), length, head)
                block[head:head + len(raw)] = raw
            else:  # inchangé : recopie exacte (bourrage compris)
                block = self.src[pos:pos + length]
            out += block
        out += self.tail
        head = bytearray(self.src[:0x800])
        struct.pack_into("<II", head, 0x14 + 4, 0x800, len(out))
        struct.pack_into("<II", head, 0x24 + 4, 0x800 + len(out), len(self.data))
        return bytes(head + out + self.data)
