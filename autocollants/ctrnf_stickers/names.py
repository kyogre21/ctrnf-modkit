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


def short(name):
    """Nom court d'une texture d'autocollant ou d'icône, ou None."""
    for (start, end), tag in ((STICKER, ''), (ICON, ICON_TAG)):
        if name.startswith(start) and name.endswith(end):
            return tag + name[len(start):-len(end)]
    return None


def is_ours(path):
    """L'archive en `path` est-elle la nôtre (rien que des autocollants et des icônes) ?"""
    try:
        with iga.Archive(Path(path)) as a:
            return bool(a.names) and all(short(n) for n in a.names)
    except (OSError, ValueError, IndexError, struct.error):
        return False
