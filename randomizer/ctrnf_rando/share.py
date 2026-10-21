"""Code de partage : la graine et tous les réglages en 12 caractères (ex. 3K7Q-M2XA-90BF), pour que deux joueurs
lancent exactement la même partie. Une lettre de contrôle repère les fautes de frappe. Préréglages de la fenêtre."""
from dataclasses import replace

from .generator import CHALLENGE_MODES, CUP_MODES, ORIGINS, PAD_MODES, Settings

FORMAT = 1                                      # change si le contenu du code change
ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"  # base 32 de Crockford : ni I, L, O ni U
LOOKALIKE = str.maketrans("ILO", "110")
# (champ de Settings, valeurs possibles) dans l'ordre du code ; un booléen prend 1 bit, un choix 2 bits
FLAGS = ("shuffle_tracks", "allow_duplicates", "shuffle_arenas", "shuffle_rewards", "skip_hints", "boost_reserve",
         "fast_podiums", "shuffle_locations")
CHOICES = (("shuffle_cups", CUP_MODES), ("pad_conditions", PAD_MODES), ("challenges", CHALLENGE_MODES))

# Préréglages : (nom, aide, réglages du tirage). Les options de confort ne sont pas touchées.
PRESETS = (
    ("Découverte", "Circuits et arènes mélangés, le reste comme dans le jeu : pour une première partie.",
     dict(shuffle_tracks=True, track_origins=ORIGINS, allow_duplicates=False, shuffle_arenas=True,
          shuffle_rewards=False, shuffle_cups="non", pad_conditions="origine", challenges="origine",
          shuffle_locations=False)),
    ("Classique", "Circuits, arènes et récompenses mélangés, coupes au hasard, conditions en nombres au hasard.",
     dict(shuffle_tracks=True, track_origins=ORIGINS, allow_duplicates=False, shuffle_arenas=True,
          shuffle_rewards=True, shuffle_cups="coupes", pad_conditions="nombres", challenges="origine",
          shuffle_locations=False)),
    ("Chaos", "Tout au hasard : récompenses, coupes circuit par circuit, conditions, défis et emplacements des "
              "portails.",
     dict(shuffle_tracks=True, track_origins=ORIGINS, allow_duplicates=False, shuffle_arenas=True,
          shuffle_rewards=True, shuffle_cups="circuits", pad_conditions="hasard", challenges="hasard",
          shuffle_locations=True)),
)


def _check(text):
    """Lettre de contrôle des 11 premiers caractères : somme pondérée par des poids impairs (1, 3, 5…), qui repère
    toute faute sur un seul caractère et presque toutes les inversions de deux voisins."""
    return ALPHABET[sum((2 * i + 1) * ALPHABET.index(c) for i, c in enumerate(text)) % 32]


def encode(seed, settings, rename):
    """Code de partage de la graine `seed` (0 à 2^32 - 1) avec ces réglages et l'option « noms »."""
    if not 0 <= seed < 1 << 32:
        raise ValueError("graine hors limites")
    number = 0
    for value in [rename] + [getattr(settings, f) for f in FLAGS] + [o in settings.track_origins for o in ORIGINS]:
        number = number << 1 | bool(value)
    for field, modes in CHOICES:
        number = number << 2 | modes.index(getattr(settings, field))
    number = (number << 32 | seed) << 4 | FORMAT  # 18 bits de réglages, 32 de graine, 4 de format : 54 bits
    chars = [ALPHABET[number >> 5 * i & 31] for i in reversed(range(11))]
    text = "".join(chars)
    text += _check(text)
    return f"{text[:4]}-{text[4:8]}-{text[8:]}"


def decode(code):
    """(graine, Settings, noms) d'un code de partage. Lève ValueError si le code est faux ou d'une autre version."""
    text = "".join(code.upper().translate(LOOKALIKE).split()).replace("-", "")
    if len(text) != 12 or any(c not in ALPHABET for c in text):
        raise ValueError("un code de partage a 12 caractères (lettres et chiffres)")
    if _check(text[:11]) != text[11]:
        raise ValueError("code mal recopié (la lettre de contrôle ne correspond pas)")
    number = 0
    for c in text[:11]:
        number = number << 5 | ALPHABET.index(c)
    if number & 15 != FORMAT:
        raise ValueError("code fait avec une autre version du randomizer")
    number >>= 4
    seed = number & 0xFFFFFFFF
    number >>= 32
    values = {}
    for field, modes in reversed(CHOICES):
        if number & 3 >= len(modes):
            raise ValueError("code mal recopié")
        values[field] = modes[number & 3]
        number >>= 2
    origins = []
    for origin in reversed(ORIGINS):
        if number & 1:
            origins.insert(0, origin)
        number >>= 1
    for field in reversed(FLAGS):
        values[field] = bool(number & 1)
        number >>= 1
    rename = bool(number & 1)
    if number >> 1:
        raise ValueError("code mal recopié")
    return seed, replace(Settings(), track_origins=tuple(origins), **values), rename
