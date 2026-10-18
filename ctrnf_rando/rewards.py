"""Récompenses mélangées : quels lieux du mode Aventure donnent quel objet, avec une logique qui garantit
qu'une graine peut toujours être finie.

Le jeu note chaque récompense gagnée par un bit dans la fiche d'un circuit (le « lieu »), et recalcule
les compteurs de la partie (trophées, clés, gemmes, jetons, reliques) d'après ces bits. Le patch garde les bits mais
change ce que chaque bit compte : c'est l'objet. Les portails, garages, portes et coupes ne regardent que
les compteurs, la logique ci-dessous fait donc de même (valeurs lues dans les données du hub, version 01.21).
"""
from collections import Counter
from dataclasses import dataclass, field

# Bits des récompenses dans la fiche d'un circuit (_collectiblesRewarded).
TROPHY, KEY, PLATINUM, SAPPHIRE, GOLD = 0x2, 0x4, 0x8, 0x10, 0x20
TOKEN_BITS = {"red": 0x40, "blue": 0x80, "purple": 0x100, "green": 0x200, "yellow": 0x400}
GEM_BITS = {"red": 0x1000, "blue": 0x2000, "purple": 0x4000, "green": 0x8000, "yellow": 0x10000}

# Objets = compteurs de la partie (position dans COctaneSaveSlotData).
COUNTERS = {
    "trophy": 0xC, "key": 0x10,
    "gem_red": 0x14, "gem_blue": 0x18, "gem_purple": 0x1C, "gem_green": 0x20, "gem_yellow": 0x24,
    "sapphire": 0x28, "gold": 0x2C, "platinum": 0x30,
    "token_red": 0x34, "token_blue": 0x38, "token_purple": 0x3C, "token_green": 0x40, "token_yellow": 0x44,
}
ITEM_NAMES = {
    "trophy": "Trophée", "key": "Clé de boss",
    "gem_red": "Gemme rouge", "gem_blue": "Gemme bleue", "gem_purple": "Gemme violette", "gem_green": "Gemme verte",
    "gem_yellow": "Gemme jaune",
    "sapphire": "Relique saphir", "gold": "Relique or", "platinum": "Relique platine",
    "token_red": "Jeton CTR rouge", "token_blue": "Jeton CTR bleu", "token_purple": "Jeton CTR violet",
    "token_green": "Jeton CTR vert", "token_yellow": "Jeton CTR jaune",
}
RELIC_ITEMS = {SAPPHIRE: "sapphire", GOLD: "gold", PLATINUM: "platinum"}

# Clés pour passer chaque porte (valeurs prudentes : en trop, une condition ne rend jamais une graine
# impossible). Plage : ouverte d'office.
AREA_KEYS = {"N. Sanity Beach": 0, "The Lost Ruins": 1, "Gemstone Valley": 2, "Glacier Park": 2,
             "Citadel City": 3}


@dataclass(frozen=True)
class RacePad:
    zone: str      # circuit d'origine du portail (la fiche qui reçoit les bits)
    hub: str
    trophies: int  # trophées pour ouvrir la course
    token: str     # couleur du jeton CTR de ce portail
    keys: int      # clés pour la relique et le défi CTR (une fois le trophée du portail gagné)


RACE_PADS = [
    RacePad("t111_crash_cove", "N. Sanity Beach", 0, "red", 1),
    RacePad("t112_roos_tubes", "N. Sanity Beach", 0, "green", 1),
    RacePad("t113_mystery_caves", "N. Sanity Beach", 1, "red", 1),
    RacePad("t114_sewer_speedway", "N. Sanity Beach", 3, "blue", 1),
    RacePad("t131_coco_park", "The Lost Ruins", 4, "green", 2),
    RacePad("t133_papus_pyramid", "The Lost Ruins", 6, "red", 2),
    RacePad("t134_dingo_canyon", "The Lost Ruins", 7, "yellow", 2),
    RacePad("t132_tiger_temple", "The Lost Ruins", 4, "blue", 2),
    RacePad("t141_blizzard_bluff", "Glacier Park", 8, "red", 3),
    RacePad("t142_dragon_mines", "Glacier Park", 9, "blue", 3),
    RacePad("t144_tiny_arena", "Glacier Park", 11, "yellow", 3),
    RacePad("t143_polar_pass", "Glacier Park", 10, "green", 3),
    RacePad("t151_ngin_labs", "Citadel City", 12, "blue", 4),
    RacePad("t152_cortex_castle", "Citadel City", 12, "green", 4),
    RacePad("t153_hot_air_skyway", "Citadel City", 14, "yellow", 4),
    RacePad("t154_oxide_station", "Citadel City", 15, "yellow", 4),
]

# Circuits de Gem Stone Valley : course aux reliques seulement, ouverte par 10 reliques / 5 gemmes.
SPECIAL_PADS = {"t121_slide_coliseum": ("relics", 10), "t122_turbo_track": ("gems", 5)}


@dataclass(frozen=True)
class Boss:
    name: str
    zone: str      # la clé est rangée dans la fiche du circuit du boss
    hub: str
    trophies: int


BOSSES = [
    Boss("Ripper Roo", "t112_roos_tubes", "N. Sanity Beach", 4),
    Boss("Papu Papu", "t133_papus_pyramid", "The Lost Ruins", 8),
    Boss("Komodo Joe", "t142_dragon_mines", "Glacier Park", 12),
    Boss("Pinstripe", "t153_hot_air_skyway", "Citadel City", 16),
]

# Défis cristaux (jeton violet) : arène d'origine du portail, monde, clés.
ARENA_PADS = [
    ("a115_skull_rock", "N. Sanity Beach", 1),
    ("a135_rampage_ruins", "The Lost Ruins", 2),
    ("a145_rocky_road", "Glacier Park", 3),
    ("a155_nitro_court", "Citadel City", 4),
]

# Coupes de gemmes : 4 jetons de leur couleur, à Gem Stone Valley. La gemme est rangée dans la fiche du premier
# circuit de la coupe (celle que lit le portail de la coupe). Oxide : 4 clés.
CUP_TOKENS = 4
CUP_FIRST = {"red": "t111_crash_cove", "blue": "t132_tiger_temple", "purple": "t112_roos_tubes",
             "green": "t112_roos_tubes", "yellow": "t134_dingo_canyon"}
CUP_OF = {bits: color for color, bits in GEM_BITS.items()}
OXIDE_KEYS = 4


@dataclass(frozen=True)
class Location:
    zone: str
    bits: int
    vanilla: str = field(compare=False)   # objet d'origine
    label: str = field(compare=False)     # pour le journal


def locations():
    out = []
    for pad in RACE_PADS:
        out.append(Location(pad.zone, TROPHY, "trophy", f"{pad.zone} : trophée"))
        out.append(Location(pad.zone, TOKEN_BITS[pad.token], f"token_{pad.token}", f"{pad.zone} : défi CTR"))
    for zone in [pad.zone for pad in RACE_PADS] + list(SPECIAL_PADS):
        for bits, item in RELIC_ITEMS.items():
            out.append(Location(zone, bits, item, f"{zone} : relique {ITEM_NAMES[item].split()[-1]}"))
    for boss in BOSSES:
        out.append(Location(boss.zone, KEY, "key", f"{boss.name} : clé"))
    for zone, _, _ in ARENA_PADS:
        out.append(Location(zone, TOKEN_BITS["purple"], "token_purple", f"{zone} : défi cristaux"))
    for color, bits in GEM_BITS.items():
        name = ITEM_NAMES[f"gem_{color}"].split()[-1]
        out.append(Location(CUP_FIRST[color], bits, f"gem_{color}", f"Coupe {name} : gemme"))
    return out


LOCATIONS = locations()
PAD_OF = {pad.zone: pad for pad in RACE_PADS}


def _counts(items):
    c = Counter(items)
    c["relics"] = c["sapphire"] + c["gold"] + c["platinum"]
    c["gems"] = sum(c[f"gem_{color}"] for color in GEM_BITS)
    return c


# Conditions d'ouverture (forme JSON de la graine). Une condition = [type, nombre], le type étant ce que le jeu sait
# compter (COND_KINDS). Portails de course {zone: [la course, le défi CTR et la relique]} (la 2e une fois le trophée
# du portail gagné), Slide Coliseum et Turbo Track {zone: condition}, garages de boss {zone du boss: trophées},
# arènes {zone: condition}, coupes de gemmes {couleur: condition}.
COND_KINDS = ("trophy", "key", "relics", "gems") + tuple(f"token_{color}" for color in TOKEN_BITS)
COND_NAMES = {"trophy": "trophée", "key": "clé", "relics": "relique", "gems": "gemme", "token_red": "jeton rouge",
              "token_blue": "jeton bleu", "token_purple": "jeton violet", "token_green": "jeton vert",
              "token_yellow": "jeton jaune"}
# Bornes des nombres tirés, par monde : plage, ruines, glacier et Gem Stone Valley, citadelle.
TIER = {"N. Sanity Beach": 0, "The Lost Ruins": 1, "Gemstone Valley": 2, "Glacier Park": 2, "Citadel City": 3}
RANGES = {"trophy": ((0, 3), (2, 8), (5, 12), (8, 15)), "key": ((0, 1), (1, 2), (1, 3), (2, 4)),
          "relics": ((1, 3), (1, 6), (2, 10), (3, 15)), "gems": ((1, 1), (1, 2), (1, 3), (2, 5)),
          "token": ((1, 1), (1, 2), (1, 3), (2, 4))}
KIND_WEIGHTS = {"trophy": 4, "key": 2, "relics": 2, "gems": 1, "token": 2}  # type tiré (jeton : couleur au hasard)


# Emplacements des portails (option « emplacements ») : portails déplaçables (courses, Slide, Turbo, arènes, coupes
# « cup_<couleur> ») et monde de leur emplacement d'origine. conds["locations"] = {portail: emplacement} : un portail
# est alors dans le monde de son emplacement (portes, bornes des conditions).
SPOT_HUB = {**{pad.zone: pad.hub for pad in RACE_PADS}, **{zone: "Gemstone Valley" for zone in SPECIAL_PADS},
            **{zone: hub for zone, hub, _ in ARENA_PADS}, **{f"cup_{color}": "Gemstone Valley" for color in CUP_FIRST}}


def hub_of(conds, key):
    """Monde où se trouve le portail `key` (clé de SPOT_HUB)."""
    spot = ((conds or {}).get("locations") or {}).get(key, key)
    return SPOT_HUB[spot]


def cond_text(cond):
    kind, count = cond
    if count <= 0:
        return "ouvert"
    words = COND_NAMES[kind].split()
    return f"{count} " + " ".join(w + "s" for w in words) if count > 1 else f"{count} {COND_NAMES[kind]}"


def vanilla_conditions():
    return {"pads": {pad.zone: [["trophy", pad.trophies], ["key", pad.keys]] for pad in RACE_PADS},
            "special": {zone: list(cond) for zone, cond in SPECIAL_PADS.items()},
            "bosses": {boss.zone: boss.trophies for boss in BOSSES},
            "arenas": {zone: ["key", keys] for zone, _, keys in ARENA_PADS},
            "cups": {color: [f"token_{color}", CUP_TOKENS] for color in CUP_FIRST}}


VANILLA_CONDITIONS = vanilla_conditions()


def _group(kind):
    return "token" if kind.startswith("token_") else kind


def _count(rng, hub, kind):
    return rng.randint(*RANGES[_group(kind)][TIER[hub]])


def _any(rng, hub):
    """Une condition de n'importe quel type pour un portail de ce monde."""
    group = rng.choices(list(KIND_WEIGHTS), weights=list(KIND_WEIGHTS.values()))[0]
    kind = f"token_{rng.choice(list(TOKEN_BITS))}" if group == "token" else group
    return [kind, _count(rng, hub, kind)]


def draw_conditions(rng, pads="origine", challenges="origine", locations=None):
    """pads : "origine", "nombres" (même type que le jeu, nombre tiré) ou "hasard" (type et nombre tirés) pour la
    course de chaque portail, Slide Coliseum, Turbo Track, les arènes et les coupes (les garages de boss gardent 4 / 8
    / 12 / 16 trophées, à la demande de l'utilisateur) ; challenges : "origine", "ouverts" (défi CTR et relique
    ouverts dès le trophée du portail gagné) ou "hasard". Les nombres restent dans des bornes par monde ; le
    générateur vérifie ensuite que tout reste atteignable. locations : emplacements des portails (ou None)."""
    conds = vanilla_conditions()
    if locations:
        conds["locations"] = dict(locations)
    where = lambda key: hub_of(conds, key)  # noqa: E731
    if pads != "origine":
        def pick(hub, cond):
            return [cond[0], _count(rng, hub, cond[0])] if pads == "nombres" else _any(rng, hub)
        for pad in RACE_PADS:
            conds["pads"][pad.zone][0] = pick(where(pad.zone), conds["pads"][pad.zone][0])
        # deux portails de la plage restent ouverts dès le départ (des courses d'abord)
        beach = [g for g in _gates(pads, "origine", conds) if g[3] == "N. Sanity Beach"]
        races = [g for g in beach if g[0] == "pads"]
        others = [g for g in beach if g[0] != "pads"]
        chosen = rng.sample(races, 2) if len(races) >= 2 else races + rng.sample(others, min(2 - len(races), len(others)))
        for zone in SPECIAL_PADS:
            conds["special"][zone] = pick(where(zone), conds["special"][zone])
        for zone, _, _ in ARENA_PADS:
            conds["arenas"][zone] = pick(where(zone), conds["arenas"][zone])
        for color in CUP_FIRST:
            conds["cups"][color] = pick(where(f"cup_{color}"), conds["cups"][color])
        for part, key, i, _ in chosen:
            if i is None:
                conds[part][key] = ["trophy", 0]
            else:
                conds[part][key][i] = ["trophy", 0]
    if challenges == "ouverts":
        for pad in RACE_PADS:
            conds["pads"][pad.zone][1] = ["key", 0]
    elif challenges == "hasard":
        for pad in RACE_PADS:
            conds["pads"][pad.zone][1] = _any(rng, where(pad.zone))
    return conds


def _gates(pads, challenges, conds=None):
    """Les conditions que les réglages laissent tirer : (partie, clé, place dans la paire ou None, monde)."""
    out = []
    if pads != "origine":
        out += [("pads", pad.zone, 0, hub_of(conds, pad.zone)) for pad in RACE_PADS]
        out += [("special", zone, None, hub_of(conds, zone)) for zone in SPECIAL_PADS]
        out += [("arenas", zone, None, hub_of(conds, zone)) for zone, _, _ in ARENA_PADS]
        out += [("cups", color, None, hub_of(conds, f"cup_{color}")) for color in CUP_FIRST]
    if challenges == "hasard":
        out += [("pads", pad.zone, 1, hub_of(conds, pad.zone)) for pad in RACE_PADS]
    return out


def repair_conditions(rng, conds, placement, pads="origine", challenges="origine"):
    """Tant que la graine ne peut pas être finie avec ce placement, une condition qui bloque (portail dans un monde
    ouvert) est retirée parmi ce que le joueur possède à ce moment-là. Rend les conditions, ou None si aucune
    condition tirable ne bloque."""
    gates = _gates(pads, challenges, conds)
    while not beatable(placement, conds):
        got = reachable(placement, conds=conds)
        c = _counts(placement[loc] for loc in got if loc in placement)
        areas = {hub for hub, need in AREA_KEYS.items() if c["key"] >= need}
        blocked = []
        for part, key, i, hub in gates:
            cond = conds[part][key] if i is None else conds[part][key][i]
            if hub not in areas or c[cond[0]] >= cond[1]:
                continue
            if i == 1 and Location(key, TROPHY, "", "") not in got:
                continue  # le défi attend d'abord le trophée du portail
            blocked.append((part, key, i, hub, cond))
        if not blocked:
            return None
        part, key, i, hub, cond = rng.choice(blocked)
        same = part != "pads" or i == 0
        new = _fit(rng, hub, cond[0] if same and pads == "nombres" else None, c)
        if i is None:
            conds[part][key] = new
        else:
            conds[part][key][i] = new
    return conds


def _fit(rng, hub, kind, have):
    """Une condition déjà remplie avec `have` : type `kind` (ou tiré), nombre dans les bornes du monde si possible."""
    tier = TIER[hub]
    kinds = [kind] if kind else list(COND_KINDS)
    ok = [k for k in kinds if have[k] >= RANGES[_group(k)][tier][0]]
    if not ok:
        k = kind or "trophy"
        return [k, have[k]]
    k = rng.choices(ok, weights=[KIND_WEIGHTS[_group(k)] / (len(TOKEN_BITS) if _group(k) == "token" else 1)
                                 for k in ok])[0]
    lo, hi = RANGES[_group(k)][tier]
    return [k, rng.randint(lo, min(hi, have[k]))]


def reachable(placement, assumed=(), conds=None):
    """Lieux atteignables en ramassant tout ce qui s'ouvre, avec en plus les objets `assumed`.
    placement : {Location: objet} (les lieux absents ne donnent rien) ; conds : conditions d'ouverture."""
    conds = conds or VANILLA_CONDITIONS
    where = {key: hub_of(conds, key) for key in SPOT_HUB}
    have = Counter(assumed)
    got = set()
    while True:
        c = _counts(have)
        keys, trophies = c["key"], c["trophy"]
        met = lambda cond: c[cond[0]] >= cond[1]  # noqa: E731
        areas = {hub for hub, need in AREA_KEYS.items() if keys >= need}
        open_spots = {key for key, hub in where.items() if hub in areas}
        new = []
        for loc in LOCATIONS:
            if loc in got:
                continue
            if loc.bits in CUP_OF:  # coupe de gemmes (avant les portails : la fiche est celle d'un circuit)
                ok = f"cup_{CUP_OF[loc.bits]}" in open_spots and met(conds["cups"][CUP_OF[loc.bits]])
            elif loc.zone in PAD_OF:
                pad = PAD_OF[loc.zone]
                first, second = conds["pads"][loc.zone]
                ok = pad.zone in open_spots and met(first)
                if ok and loc.bits != TROPHY:
                    ok = Location(pad.zone, TROPHY, "", "") in got and met(second)
                if loc.bits == KEY:  # la clé du boss est dans la fiche de son circuit
                    boss = next(b for b in BOSSES if b.zone == loc.zone)
                    ok = boss.hub in areas and trophies >= conds["bosses"][loc.zone]
            elif loc.zone in SPECIAL_PADS:
                ok = loc.zone in open_spots and met(conds["special"][loc.zone])
            else:
                ok = loc.zone in open_spots and met(conds["arenas"][loc.zone])
            if ok:
                new.append(loc)
        if not new:
            return got
        for loc in new:
            got.add(loc)
            if loc in placement:
                have[placement[loc]] += 1


def beatable(placement, conds=None):
    """Tous les lieux atteignables, et Oxide (4 clés, Gem Stone Valley) aussi."""
    got = reachable(placement, conds=conds)
    keys = sum(1 for loc in got if placement.get(loc) == "key")
    return len(got) == len(LOCATIONS) and keys >= max(OXIDE_KEYS, AREA_KEYS["Gemstone Valley"])


def possible(conds):
    """Avec tous les objets en poche, tout s'ouvre-t-il ? (sinon aucun placement ne peut convenir)"""
    return len(reachable({}, [loc.vanilla for loc in LOCATIONS], conds)) == len(LOCATIONS)


def shuffle(rng, tries=50, conds=None):
    """Remplissage « supposé » : chaque objet va dans un lieu atteignable en supposant tous les objets
    pas encore placés déjà en poche ; la graine reste donc toujours faisable."""
    for _ in range(tries):
        items = [loc.vanilla for loc in LOCATIONS]
        rng.shuffle(items)
        placement = {}
        while items:
            item = items.pop()
            got = reachable(placement, items, conds)
            # dans l'ordre de LOCATIONS : l'ordre d'un set change d'un lancement à l'autre (hachage des noms)
            free = [loc for loc in LOCATIONS if loc in got and loc not in placement]
            if not free:
                break
            placement[rng.choice(free)] = item
        if not items and len(placement) == len(LOCATIONS) and beatable(placement, conds):
            return placement
    raise RuntimeError("impossible de placer les récompenses (essais épuisés)")


def to_plan(placement):
    """Forme JSON : [[zone, bits, objet], ...] dans l'ordre des lieux."""
    return [[loc.zone, loc.bits, placement[loc]] for loc in LOCATIONS]


def patch_rows(rows):
    """[[zone, bits, objet]] -> [(zone, bits, position du compteur)] pour le patch."""
    return [(zone, bits, COUNTERS[item]) for zone, bits, item in rows]
