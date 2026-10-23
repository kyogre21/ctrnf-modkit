"""Noms des textures d'autocollants et d'icônes, et reconnaissance de notre archive, sans numpy ni Pillow (le Mod Kit
s'en sert pour son état des fichiers sans charger la partie images)."""
from pathlib import Path
import struct

from . import iga

OURS = 'update3.pak'
ARCHIVES = ('stickers.pak', 'update.pak', 'update2.pak')  # de la plus ancienne à la plus récente
STICKER = ('textures/ColorMap,textures@!actors!Octane!Vehicles!Stickers!', '`tga,111.igz')
ICON = ('textures/GuiStandard_diffuse,textures@!ui!Octane!Customization!Icons!octane_ui_custo_ico_kart_sticker_',
        '`tga,101.igz')
ICON_TAG = 'ico_'  # nom court des icônes du menu : ico_<n> (ex. ico_133 = drapeau France)
# Le jeu lit update3.pak, update4.pak… et s'arrête au premier absent : quand update3.pak manque alors qu'une archive
# du Mod Kit est plus loin, le kit pose à sa place un « bouche-trou » (ce fichier du jeu, recopié à l'identique).
FILLER = ('update2.pak', 'models/LevelAssets/Basic/box.hkx')


def short(name):
    """Nom court d'une texture d'autocollant ou d'icône, ou None."""
    for (start, end), tag in ((STICKER, ''), (ICON, ICON_TAG)):
        if name.startswith(start) and name.endswith(end):
            return tag + name[len(start):-len(end)]
    return None


def is_filler(path):
    """L'archive en `path` est-elle un bouche-trou du Mod Kit (remplaçable par nos autocollants) ?"""
    try:
        with iga.Archive(Path(path)) as a:
            return list(a.names) == [FILLER[1]]
    except (OSError, ValueError, IndexError, struct.error):
        return False


def is_ours(path):
    """L'archive en `path` est-elle la nôtre (rien que des autocollants et des icônes) ?"""
    try:
        with iga.Archive(Path(path)) as a:
            return bool(a.names) and all(short(n) for n in a.names)
    except (OSError, ValueError, IndexError, struct.error):
        return False
