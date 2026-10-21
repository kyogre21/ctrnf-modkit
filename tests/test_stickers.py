"""Tests sans le jeu : archive écrite puis relue, texture remplacée puis relue."""
import struct
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from ctrnf_stickers import iga, texture


def fake_texture(w, h, levels):
    """Plus petit fichier IGZ v10 que texture.layout sait lire : TMET + RVTB, un igImage2, des pixels nuls."""
    size = sum(-(-max(w >> k, 4) // 32) * -(-max(h >> k, 4) // 32) * 1024 for k in range(levels))
    tmet = b'igImage2\0\0'
    rvtb = bytes([0])  # un objet, en position 0 des données
    fix = b''
    for tag, count, body in ((b'TMET', 1, tmet), (b'RVTB', 1, rvtb)):
        fix += tag + struct.pack('<III', count, 16 + len(body), 16) + body
    obj = bytearray(0x40)
    struct.pack_into('<HH', obj, 0x18, w, h)
    struct.pack_into('<H', obj, 0x1e, levels)
    struct.pack_into('<I', obj, 0x38, size)
    head = 0x14 + 16 * 4
    at_fix, at_obj = head, head + len(fix)
    at_pix = at_obj + len(obj)
    data = struct.pack('<4I', 0x49475a01, 10, 0, 0) + bytes(4)
    for off, length in ((at_fix, len(fix)), (at_obj, len(obj)), (at_pix, size)):
        data += struct.pack('<4I', 0, off, length, 0)
    data += bytes(16)
    return data + fix + bytes(obj) + bytes(size)


class Tests(unittest.TestCase):
    def test_archive(self):
        files = {'a/b`x.igz': b'abc' * 1000, 'c': b'', 'd': bytes(0x900)}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'update3.pak'
            iga.write(files, path)
            with iga.Archive(path) as a:
                self.assertEqual({n: a.read(n) for n in a.names}, files)

    def test_texture(self):
        data = fake_texture(128, 64, 6)
        self.assertTrue(texture.supported(data))
        img = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
        img.paste((255, 0, 0, 255), (0, 0, 100, 100))
        back = texture.to_image(texture.replace(data, img))
        self.assertEqual(back.size, (128, 64))
        self.assertEqual(back.getpixel((64, 32))[:4], (255, 0, 0, 255))  # carré rouge au centre
        self.assertEqual(back.getpixel((2, 32))[3], 0)  # bords transparents : pas déformé

    def test_cut_out(self):
        img = Image.new('RGB', (100, 60), (250, 250, 250))  # fond presque blanc
        img.paste((0, 0, 200), (30, 10, 70, 50))  # carré bleu
        img.paste((250, 250, 250), (45, 25, 55, 35))  # trou blanc enfermé : gardé
        out = texture.cut_out(img)
        self.assertEqual(out.size, (40, 40))  # recadrée sur le carré
        self.assertEqual(out.getpixel((20, 20)), (250, 250, 250, 255))
        self.assertEqual(out.getpixel((5, 5))[3], 255)
        again = texture.cut_out(Image.new('RGBA', (50, 50), (0, 0, 0, 0)))  # déjà transparente : inchangée
        self.assertEqual(again.size, (50, 50))


if __name__ == '__main__':
    unittest.main()
