"""Textures du jeu (IGZ v10, objet igImage2) : lecture en image et réécriture des pixels.

igImage2 : largeur / hauteur u16 en +0x18, niveaux u16 en +0x1e, taille des pixels u32 en +0x38 ; pixels = 3e section
du fichier, BC3 (DXT5), image retournée de haut en bas, chaque niveau en tuiles PS4 de 8 × 8 blocs (ordre de Morton dans
la tuile, tuiles complétées par des zéros).
"""
import io
import struct

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def _unpack_ints(data, count):
    """Entiers « compressés » des corrections R* : demi-octets (3 bits + bit de suite), écarts multipliés par 4."""
    out, last, half, pos = [], 0, False, 0
    for _ in range(count):
        value, shift = 0, 0
        while True:
            b = data[pos]
            if half:
                pos += 1
                n = b >> 4
            else:
                n = b & 0xF
            half = not half
            value |= (n & 7) << shift
            shift += 3
            if not n & 8:
                break
        last += value * 4
        out.append(last)
    return out


def _strings(blob, count):
    out, pos = [], 0
    for _ in range(count):
        end = blob.index(b'\0', pos)
        out.append(blob[pos:end].decode('latin-1'))
        pos = end + 1 + (end + 1) % 2  # chaînes alignées sur 2
    return out


def layout(data):
    """(largeur, hauteur, niveaux, position des pixels, taille des pixels) de l'igImage2 du fichier."""
    magic, version = struct.unpack_from('<II', data, 0)
    if magic != 0x49475a01 or version != 10:
        raise ValueError('pas une texture IGZ v10')
    sections, at = [], 0x14
    while True:
        _, offset, size, _ = struct.unpack_from('<4I', data, at)
        if not size:
            break
        sections.append((offset, size))
        at += 16
    fix, p, end = {}, sections[0][0], sum(sections[0])
    while p < end:
        tag = data[p:p + 4].decode('latin-1')
        count, length, head = struct.unpack_from('<III', data, p + 4)
        if not length:
            break
        fix[tag] = (count, data[p + head:p + length])
        p += length
    base = sections[1][0]
    types = _strings(fix['TMET'][1], fix['TMET'][0])
    for off in _unpack_ints(fix['RVTB'][1], fix['RVTB'][0]):
        if types[struct.unpack_from('<Q', data, base + off)[0]] == 'igImage2':
            break
    else:
        raise ValueError('pas d\'image dans ce fichier')
    w, h = struct.unpack_from('<HH', data, base + off + 0x18)
    levels = struct.unpack_from('<H', data, base + off + 0x1e)[0]
    size = struct.unpack_from('<I', data, base + off + 0x38)[0]
    at, length = sections[2]
    if length != size or at + size > len(data):
        raise ValueError('texture inattendue')
    return w, h, levels, at, size


def _level_sizes(w, h, levels):
    for level in range(levels):
        yield max(w >> level, 4), max(h >> level, 4)


def _tiled_size(w, h):
    return -(-w // 32) * -(-h // 32) * 64 * 16


def supported(data):
    """La texture est-elle en BC3 tuilé (le seul format que l'on sait réécrire) ?"""
    w, h, levels, _, size = layout(data)
    return size == sum(_tiled_size(lw, lh) for lw, lh in _level_sizes(w, h, levels))


def _morton(t):
    """n° dans une tuile de 8 × 8 blocs -> (x, y) : bits pairs = x, bits impairs = y."""
    return ((t & 1) | (t >> 1 & 2) | (t >> 2 & 4)), ((t >> 1 & 1) | (t >> 2 & 2) | (t >> 3 & 4))


def untile(data, w, h, bpb=16):
    """Blocs PS4 (tuiles de 8 × 8 blocs de 4 × 4 pixels) -> ordre linéaire."""
    wb, hb = w // 4, h // 4
    out, src = bytearray(wb * hb * bpb), 0
    for ty in range(0, hb, 8):
        for tx in range(0, wb, 8):
            for t in range(64):
                x, y = _morton(t)
                if tx + x < wb and ty + y < hb:
                    dst = ((ty + y) * wb + tx + x) * bpb
                    out[dst:dst + bpb] = data[src:src + bpb]
                src += bpb
    return bytes(out)


def tile(data, w, h, bpb=16):
    """L'inverse de untile."""
    wb, hb = w // 4, h // 4
    out = bytearray()
    for ty in range(0, hb, 8):
        for tx in range(0, wb, 8):
            for t in range(64):
                x, y = _morton(t)
                if tx + x < wb and ty + y < hb:
                    at = ((ty + y) * wb + tx + x) * bpb
                    out += data[at:at + bpb]
                else:
                    out += bytes(bpb)
    return bytes(out)


def _dds(w, h, blocks):
    head = struct.pack('<4sIIIIIII44sII4s20sI16s', b'DDS ', 124, 0x81007, h, w, len(blocks), 0, 1, bytes(44),
                       32, 4, b'DXT5', bytes(20), 0x1000, bytes(16))
    return head + blocks


def to_image(data):
    """Texture -> image PIL RGBA (niveau 0)."""
    if not supported(data):
        raise ValueError('format de texture non géré')
    w, h, _, at, size = layout(data)
    img = Image.open(io.BytesIO(_dds(w, h, untile(data[at:at + size], w, h))))
    return img.convert('RGBA').transpose(Image.Transpose.FLIP_TOP_BOTTOM)


def _bc3_blocks(rgba):
    """Image RGBA (numpy h × w × 4, côtés multiples de 4) -> blocs BC3 en ordre linéaire (couleurs et alpha extrêmes
    de chaque bloc)."""
    h, w, _ = rgba.shape
    px = rgba.reshape(h // 4, 4, w // 4, 4, 4).transpose(0, 2, 1, 3, 4).reshape(-1, 16, 4).astype(np.int32)
    # alpha : a0 = max, a1 = min, 8 niveaux
    a = px[:, :, 3]
    a0, a1 = a.max(1), a.min(1)
    levels = np.stack([a0, a1] + [((7 - k) * a0 + k * a1) // 7 for k in range(1, 7)], 1)
    aidx = np.abs(a[:, :, None] - levels[:, None, :]).argmin(2)
    aidx[a0 == a1] = 0
    abits = np.zeros(len(px), np.uint64)
    for i in range(16):
        abits |= aidx[:, i].astype(np.uint64) << np.uint64(3 * i)
    # couleur : extrémités de la boîte des couleurs (pixels visibles d'abord)
    rgb = px[:, :, :3]
    vis = (a > 8)[:, :, None]
    lo = np.where(vis.any(1), np.where(vis, rgb, 255).min(1), rgb.min(1))
    hi = np.where(vis.any(1), np.where(vis, rgb, 0).max(1), rgb.max(1))

    def to565(c):
        return ((c[:, 0] >> 3) << 11) | ((c[:, 1] >> 2) << 5) | (c[:, 2] >> 3)

    def from565(v):
        r, g, b = v >> 11 & 31, v >> 5 & 63, v & 31
        return np.stack([r << 3 | r >> 2, g << 2 | g >> 4, b << 3 | b >> 2], 1)

    c0, c1 = to565(hi), to565(lo)
    swap = c0 < c1
    c0, c1 = np.where(swap, c1, c0), np.where(swap, c0, c1)
    e0, e1 = from565(c0), from565(c1)
    pal = np.stack([e0, e1, (2 * e0 + e1) // 3, (e0 + 2 * e1) // 3], 1)
    cidx = ((rgb[:, :, None, :] - pal[:, None, :, :]) ** 2).sum(3).argmin(2)
    cidx[c0 == c1] = 0
    cbits = np.zeros(len(px), np.uint32)
    for i in range(16):
        cbits |= cidx[:, i].astype(np.uint32) << np.uint32(2 * i)
    out = bytearray()
    for k in range(len(px)):
        out += struct.pack('<BB', int(a0[k]), int(a1[k])) + int(abits[k]).to_bytes(6, 'little')
        out += struct.pack('<HHI', int(c0[k]), int(c1[k]), int(cbits[k]))
    return bytes(out)


def cut_out(img, tolerance=48):
    """Détoure une image : le fond uni qui touche les bords devient transparent (couleur du fond = médiane du
    pourtour, écart toléré en distance RGB), les bords du dessin sont adoucis, puis l'image est recadrée sur ce qui
    reste. Les zones de la couleur du fond enfermées dans le dessin sont gardées. Une image dont le pourtour est déjà
    transparent est seulement recadrée."""
    img = img.convert('RGBA')
    px = np.asarray(img).astype(np.int32)
    border = np.concatenate([px[0], px[-1], px[:, 0], px[:, -1]])
    opaque = border[border[:, 3] >= 128]
    if len(opaque) * 2 >= len(border):
        bg = np.median(opaque[:, :3], 0)
        dist = np.sqrt(((px[:, :, :3] - bg) ** 2).sum(2))
        near = (dist <= tolerance) | (px[:, :, 3] < 128)
        # remplissage depuis un cadre d'un pixel ajouté autour : touche tout le fond relié aux bords, d'un coup
        # (copy : l'image tirée de numpy partage sa mémoire en lecture seule, le remplissage n'y ferait rien)
        mask = Image.fromarray(np.pad(near, 1, constant_values=True).astype(np.uint8) * 255).copy()
        ImageDraw.floodfill(mask, (0, 0), 128)
        back = np.asarray(mask)[1:-1, 1:-1] == 128
        edge = np.asarray(Image.fromarray(back.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(3))) > 0
        alpha = px[:, :, 3].astype(np.float64)
        alpha = np.where(edge, np.minimum(alpha, np.clip((dist - tolerance) / tolerance * 255, 0, 255)), alpha)
        alpha[back] = 0
        img = Image.fromarray(np.dstack([px[:, :, :3], alpha]).astype(np.uint8), 'RGBA')
    box = img.getchannel('A').getbbox()
    return img.crop(box) if box else img


def fit(img, w, h):
    """Image quelconque -> image w × h : agrandie ou réduite sans déformer, centrée sur un fond transparent."""
    img = img.convert('RGBA')
    scale = min(w / img.width, h / img.height)
    img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.Resampling.LANCZOS)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out.paste(img, ((w - img.width) // 2, (h - img.height) // 2))
    return out


def replace(data, img):
    """Texture du jeu + image -> même texture avec l'image (ajustée à la taille de la texture, tous les niveaux)."""
    if not supported(data):
        raise ValueError('format de texture non géré')
    w, h, levels, at, size = layout(data)
    pixels = b''
    for lw, lh in _level_sizes(w, h, levels):  # chaque niveau tiré de l'image d'origine, pour la netteté
        mip = np.asarray(fit(img, lw, lh).transpose(Image.Transpose.FLIP_TOP_BOTTOM))
        pixels += tile(_bc3_blocks(mip), lw, lh)
    if len(pixels) != size:
        raise ValueError(f'taille des pixels : {len(pixels)} au lieu de {size}')
    return data[:at] + pixels + data[at + size:]
