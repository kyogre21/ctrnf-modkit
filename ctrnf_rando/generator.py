"""Tirage d'une graine : quel circuit / quelle arène derrière chaque portail de l'Aventure, quel objet
chaque récompense donne et quels circuits jouent les coupes de gemmes (options)."""
from dataclasses import asdict, dataclass
import random

from . import __version__, rewards
from .data import ARENAS, CRYSTAL_PADS, CUP_PADS, CUPS, HUBS, LEVELS, RACE_PADS, TRACKS

ORIGINS = ("CTR", "CNK", "GP")
CUP_MODES = ("non", "coupes", "circuits")  # coupes d'origine / 5 coupes du jeu / 4 circuits au hasard
PAD_MODES = ("origine", "nombres", "hasard")
CHALLENGE_MODES = ("origine", "ouverts", "hasard")


@dataclass
class Settings:
    shuffle_tracks: bool = True
    track_origins: tuple = ORIGINS     # d'où viennent les circuits tirés
    shuffle_arenas: bool = True
    arena_origins: tuple = ("CTR", "CNK")
    allow_duplicates: bool = False     # le même circuit derrière deux portails
    shuffle_rewards: bool = False      # trophées, clés, gemmes, jetons CTR et reliques mélangés
    shuffle_cups: str = "non"          # circuits des coupes de gemmes, voir CUP_MODES
    pad_conditions: str = "origine"    # courses, Slide / Turbo, arènes, coupes : voir PAD_MODES
    challenges: str = "origine"        # défi CTR et relique d'un portail : origine / ouverts / hasard
    skip_hints: bool = False           # confort : indices d'Aku Aku marqués comme déjà vus
    shuffle_locations: bool = False    # emplacements des portails (courses, arènes, coupes, Slide, Turbo) mélangés


def _draw(rng, pads, pool, shuffle, allow_duplicates):
    if not shuffle:
        return {pad.vanilla: pad.vanilla for pad in pads}
    if not allow_duplicates and len(pool) < len(pads):
        raise ValueError(f"{len(pool)} niveaux pour {len(pads)} portails : autoriser les doublons "
                         "ou ajouter des origines")
    picked = rng.choices(pool, k=len(pads)) if allow_duplicates else rng.sample(pool, len(pads))
    return {pad.vanilla: level for pad, level in zip(pads, picked)}


def _draw_cups(rng, mode):
    """Les 4 circuits de chaque coupe de gemmes, désignés par [n° de coupe du jeu, place] (voir data.CUPS)."""
    if mode == "coupes":  # 5 coupes du jeu, sans doublon, avec leurs circuits dans leur ordre
        picked = rng.sample(range(len(CUPS)), len(CUP_PADS))
        return {color: [[cup, place] for place in range(4)] for color, cup in zip(CUP_PADS, picked)}
    where = {}  # circuit -> première [coupe, place] qui le contient
    for cup, (_, levels) in enumerate(CUPS):
        for place, level in enumerate(levels):
            where.setdefault(level, [cup, place])
    picked = rng.sample(sorted(where), 4 * len(CUP_PADS))  # 20 circuits différents, 4 par coupe
    return {color: [where[level] for level in picked[4 * i:4 * i + 4]] for i, color in enumerate(CUP_PADS)}


def _draw_locations(rng):
    """Emplacements des portails : {portail: emplacement}, une permutation des portails déplaçables."""
    pads = list(rewards.SPOT_HUB)
    spots = rng.sample(pads, len(pads))
    return dict(zip(pads, spots))


def _draw_conditions(rng, settings, tries=300):
    """Conditions d'ouverture (et emplacements des portails) tirées puis vérifiées : tout doit rester atteignable avec
    les récompenses (mélangées ou d'origine). Rend (conditions, placement des récompenses ou None)."""
    vanilla = {loc: loc.vanilla for loc in rewards.LOCATIONS}
    # portails déplacés : une condition d'origine garde son type, son nombre s'ajuste au monde de l'emplacement
    repair = "nombres" if settings.shuffle_locations and settings.pad_conditions == "origine" else settings.pad_conditions
    for _ in range(tries):
        locations = _draw_locations(rng) if settings.shuffle_locations else None
        conds = rewards.draw_conditions(rng, settings.pad_conditions, settings.challenges, locations)
        if not rewards.possible(conds):
            continue
        if not settings.shuffle_rewards or settings.shuffle_locations:
            conds = rewards.repair_conditions(rng, conds, vanilla, repair, settings.challenges)
            if not conds or not rewards.beatable(vanilla, conds):
                continue
            if not settings.shuffle_rewards:
                return conds, None
        try:
            return conds, rewards.shuffle(rng, tries=10, conds=conds)
        except RuntimeError:
            continue
    raise RuntimeError("impossible de tirer des conditions d'ouverture atteignables (essais épuisés)")


def generate(seed, settings=None):
    """La graine complète, sous une forme prête à écrire en JSON."""
    settings = settings or Settings()
    rng = random.Random(seed)
    tracks = [t.id for t in TRACKS if t.origin in settings.track_origins]
    arenas = [a.id for a in ARENAS if a.origin in settings.arena_origins]
    plan = {
        "version": __version__,
        "seed": seed,
        "settings": asdict(settings),
        "race_pads": _draw(rng, RACE_PADS, tracks, settings.shuffle_tracks, settings.allow_duplicates),
        "crystal_pads": _draw(rng, CRYSTAL_PADS, arenas, settings.shuffle_arenas, settings.allow_duplicates),
    }
    if settings.shuffle_cups not in CUP_MODES:
        raise ValueError(f"mode de coupes inconnu : {settings.shuffle_cups}")
    if settings.pad_conditions not in PAD_MODES or settings.challenges not in CHALLENGE_MODES:
        raise ValueError(f"conditions inconnues : {settings.pad_conditions} / {settings.challenges}")
    placement = None
    if (settings.pad_conditions, settings.challenges) != ("origine", "origine") or settings.shuffle_locations:
        plan["conditions"], placement = _draw_conditions(rng, settings)
        if settings.shuffle_locations:
            plan["locations"] = plan["conditions"].pop("locations")
    if settings.shuffle_rewards:
        plan["rewards"] = rewards.to_plan(placement or rewards.shuffle(rng))
    if settings.shuffle_cups != "non":  # après les récompenses : leur tirage ne dépend pas de cette option
        plan["cups"] = _draw_cups(rng, settings.shuffle_cups)
    return plan


def _pad_name(key):
    """Nom d'un portail déplaçable (clé de rewards.SPOT_HUB)."""
    if key.startswith("cup_"):
        return CUPS[CUP_PADS[key[4:]][1]][0]
    return LEVELS[key].name


def _launches(plan, key):
    """Ce que lance un portail déplaçable (le nom montré par son bandeau avec l'option « noms »)."""
    if key.startswith("cup_"):
        return _pad_name(key)
    level = plan["race_pads"].get(key) or plan["crystal_pads"].get(key) or key
    return LEVELS[level].name


def spoiler(plan):
    """Journal lisible : portail -> niveau tiré."""
    lines = [f"CTR Nitro-Fueled Randomizer {plan['version']} - graine {plan['seed']}", ""]
    pads = [(p, "race_pads") for p in RACE_PADS] + [(p, "crystal_pads") for p in CRYSTAL_PADS]
    for hub in HUBS:
        lines.append(f"[{hub}]")
        for pad, kind in pads:
            if pad.hub == hub:
                new = LEVELS[plan[kind][pad.vanilla]]
                lines.append(f"  {LEVELS[pad.vanilla].name:<16} -> {new.name} ({new.origin})")
        if hub == "Gemstone Valley" and plan.get("cups"):
            for color, levels in plan["cups"].items():
                names = ", ".join(LEVELS[CUPS[cup][1][place]].name for cup, place in levels)
                whole = {cup for cup, _ in levels}
                same = f" ({CUPS[levels[0][0]][0]})" if len(whole) == 1 else ""
                lines.append(f"  {CUPS[CUP_PADS[color][1]][0]:<16} -> {names}{same}")
    if plan.get("conditions"):
        text = rewards.cond_text
        conds = plan["conditions"]
        lines += ["", "[Conditions] portail d'origine : pour la course ; pour le défi CTR et la relique"]
        for zone, (first, second) in conds["pads"].items():
            lines.append(f"  {LEVELS[zone].name:<16} : {text(first)} ; {text(second)}")
        for zone, cond in conds["special"].items():
            lines.append(f"  {LEVELS[zone].name:<16} : {text(cond)}")
        bosses = {boss.zone: boss.name for boss in rewards.BOSSES}
        for zone, trophies in conds["bosses"].items():
            lines.append(f"  {'garage ' + bosses[zone]:<16} : {trophies} trophées")
        for zone, cond in conds["arenas"].items():
            lines.append(f"  {LEVELS[zone].name:<16} : {text(cond)}")
        for color, cond in conds["cups"].items():
            lines.append(f"  {CUPS[CUP_PADS[color][1]][0]:<16} : {text(cond)}")
    if plan.get("locations"):
        lines += ["", "[Emplacements] ce que lance le portail posé à chaque endroit du hub (portail d'origine)"]
        at = {spot: pad for pad, spot in plan["locations"].items()}
        for hub in HUBS:
            spots = [spot for spot in rewards.SPOT_HUB if rewards.SPOT_HUB[spot] == hub]
            if spots:
                lines.append(f"  {hub}")
            for spot in spots:
                pad = at[spot]
                lines.append(f"    place de {_pad_name(spot):<16} : {_launches(plan, pad):<22} ({_pad_name(pad)})")
    if plan.get("rewards"):
        lines += ["", "[Récompenses] lieu (portail d'origine) -> objet reçu"]
        for zone, bits, item in plan["rewards"]:
            loc = next(loc for loc in rewards.LOCATIONS if loc.zone == zone and loc.bits == bits)
            # une coupe garde son nom (sa fiche est celle de son premier circuit)
            place = loc.label if bits in rewards.CUP_OF else LEVELS[zone].name + " : " + loc.label.split(" : ")[1]
            lines.append(f"  {place:<36} -> {rewards.ITEM_NAMES[item]}")
    return "\n".join(lines) + "\n"
