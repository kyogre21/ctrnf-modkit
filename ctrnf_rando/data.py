"""Circuits, arènes et portails du mode Aventure de CTR Nitro-Fueled.

Les identifiants sont les noms internes du jeu (nom des archives `.pak`, et chemin
`octane/<id>/<id>` que le jeu charge). Les noms affichés ne servent qu'au journal.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Level:
    id: str      # nom interne, ex. "t111_crash_cove"
    name: str    # nom affiché
    origin: str  # "CTR", "CNK" ou "GP" (Grand Prix)


TRACKS = [
    # Crash Team Racing (1999)
    Level("t111_crash_cove", "Crash Cove", "CTR"),
    Level("t112_roos_tubes", "Roo's Tubes", "CTR"),
    Level("t113_mystery_caves", "Mystery Caves", "CTR"),
    Level("t114_sewer_speedway", "Sewer Speedway", "CTR"),
    Level("t121_slide_coliseum", "Slide Coliseum", "CTR"),
    Level("t122_turbo_track", "Turbo Track", "CTR"),
    Level("t131_coco_park", "Coco Park", "CTR"),
    Level("t132_tiger_temple", "Tiger Temple", "CTR"),
    Level("t133_papus_pyramid", "Papu's Pyramid", "CTR"),
    Level("t134_dingo_canyon", "Dingo Canyon", "CTR"),
    Level("t141_blizzard_bluff", "Blizzard Bluff", "CTR"),
    Level("t142_dragon_mines", "Dragon Mines", "CTR"),
    Level("t143_polar_pass", "Polar Pass", "CTR"),
    Level("t144_tiny_arena", "Tiny Arena", "CTR"),
    Level("t151_ngin_labs", "N. Gin Labs", "CTR"),
    Level("t152_cortex_castle", "Cortex Castle", "CTR"),
    Level("t153_hot_air_skyway", "Hot Air Skyway", "CTR"),
    Level("t154_oxide_station", "Oxide Station", "CTR"),
    # Crash Nitro Kart (2003)
    Level("t211_inferno_island", "Inferno Island", "CNK"),
    Level("t212_jungle_boogie", "Jungle Boogie", "CNK"),
    Level("t213_tiny_temple", "Tiny Temple", "CNK"),
    Level("t221_meteor_gorge", "Meteor Gorge", "CNK"),
    Level("t222_barin_ruins", "Barin Ruins", "CNK"),
    Level("t223_deep_sea_driving", "Deep Sea Driving", "CNK"),
    Level("t231_out_of_time", "Out of Time", "CNK"),
    Level("t232_clockwork_wumpa", "Clockwork Wumpa", "CNK"),
    Level("t233_thunder_struck", "Thunder Struck", "CNK"),
    Level("t241_assembly_lane", "Assembly Lane", "CNK"),
    Level("t242_android_alley", "Android Alley", "CNK"),
    Level("t243_electron_avenue", "Electron Avenue", "CNK"),
    Level("t255_hyper_spaceway", "Hyper Spaceway", "CNK"),
    # Grand Prix (mises à jour gratuites)
    Level("t155_sony_stadium", "Retro Stadium", "GP"),
    Level("t501_july_world_tour", "Twilight Tour", "GP"),
    Level("t502_back_in_time", "Prehistoric Playground", "GP"),
    Level("t503_september_spyro", "Spyro Circuit", "GP"),
    Level("t504_october_spooky", "Nina's Nightmare", "GP"),
    Level("t505_nitro_festival", "Koala Carnival", "GP"),
    Level("t506_luminous", "Gingerbread Joyride", "GP"),
    Level("t507_dry_land", "Megamix Mania", "GP"),
    Level("t508_toxic", "Drive-Thru", "GP"),
]

ARENAS = [
    Level("a115_skull_rock", "Skull Rock", "CTR"),
    Level("a135_rampage_ruins", "Rampage Ruins", "CTR"),
    Level("a145_rocky_road", "Rocky Road", "CTR"),
    Level("a155_nitro_court", "Nitro Court", "CTR"),
    Level("a191_parking_lot", "Parking Lot", "CTR"),
    Level("a192_the_north_bowl", "The North Bowl", "CTR"),
    Level("a193_lab_basement", "Lab Basement", "CTR"),
    Level("a214_temple_turmoil", "Temple Turmoil", "CNK"),
    Level("a224_frozen_frenzy", "Frozen Frenzy", "CNK"),
    Level("a234_desert_storm", "Desert Storm", "CNK"),
    Level("a244_magnetic_mayhem", "Magnetic Mayhem", "CNK"),
    Level("a254_terra_drome", "Terra Drome", "CNK"),
]

LEVELS = {level.id: level for level in TRACKS + ARENAS}


@dataclass(frozen=True)
class WarpPad:
    hub: str
    vanilla: str  # circuit ou arène d'origine de ce portail


HUBS = ["N. Sanity Beach", "The Lost Ruins", "Glacier Park", "Citadel City", "Gemstone Valley"]

# Portails de course (trophées, puis jeton CTR et relique sur le même circuit).
RACE_PADS = [
    WarpPad("N. Sanity Beach", "t111_crash_cove"),
    WarpPad("N. Sanity Beach", "t112_roos_tubes"),
    WarpPad("N. Sanity Beach", "t113_mystery_caves"),
    WarpPad("N. Sanity Beach", "t114_sewer_speedway"),
    WarpPad("The Lost Ruins", "t131_coco_park"),
    WarpPad("The Lost Ruins", "t132_tiger_temple"),
    WarpPad("The Lost Ruins", "t133_papus_pyramid"),
    WarpPad("The Lost Ruins", "t134_dingo_canyon"),
    WarpPad("Glacier Park", "t141_blizzard_bluff"),
    WarpPad("Glacier Park", "t142_dragon_mines"),
    WarpPad("Glacier Park", "t143_polar_pass"),
    WarpPad("Glacier Park", "t144_tiny_arena"),
    WarpPad("Citadel City", "t151_ngin_labs"),
    WarpPad("Citadel City", "t152_cortex_castle"),
    WarpPad("Citadel City", "t153_hot_air_skyway"),
    WarpPad("Citadel City", "t154_oxide_station"),
    WarpPad("Gemstone Valley", "t121_slide_coliseum"),
    WarpPad("Gemstone Valley", "t122_turbo_track"),
]

# Portails des défis cristaux (une arène par monde).
CRYSTAL_PADS = [
    WarpPad("N. Sanity Beach", "a115_skull_rock"),
    WarpPad("The Lost Ruins", "a135_rampage_ruins"),
    WarpPad("Glacier Park", "a145_rocky_road"),
    WarpPad("Citadel City", "a155_nitro_court"),
]


# Coupes du jeu, dans l'ordre de leur liste en mémoire (lue le 18/10/2026) : 4 circuits chacune, dans l'ordre de course.
# Le patch désigne un circuit par (n° de coupe, place) : il réutilise les circuits déjà rangés dans ces coupes.
CUPS = [
    ("Arcade CTR 1", ["t111_crash_cove", "t132_tiger_temple", "t141_blizzard_bluff", "t131_coco_park"]),
    ("Arcade CTR 2", ["t113_mystery_caves", "t133_papus_pyramid", "t152_cortex_castle", "t144_tiny_arena"]),
    ("Arcade CTR 3", ["t112_roos_tubes", "t134_dingo_canyon", "t142_dragon_mines", "t114_sewer_speedway"]),
    ("Arcade CTR 4", ["t143_polar_pass", "t151_ngin_labs", "t153_hot_air_skyway", "t121_slide_coliseum"]),
    ("Coupe rouge", ["t111_crash_cove", "t113_mystery_caves", "t141_blizzard_bluff", "t133_papus_pyramid"]),
    ("Coupe bleue", ["t132_tiger_temple", "t114_sewer_speedway", "t142_dragon_mines", "t151_ngin_labs"]),
    ("Coupe verte", ["t112_roos_tubes", "t131_coco_park", "t143_polar_pass", "t152_cortex_castle"]),
    ("Coupe jaune", ["t134_dingo_canyon", "t144_tiny_arena", "t153_hot_air_skyway", "t154_oxide_station"]),
    ("Coupe violette", ["t112_roos_tubes", "t133_papus_pyramid", "t142_dragon_mines", "t153_hot_air_skyway"]),
    ("Arcade CNK 1", ["t211_inferno_island", "t221_meteor_gorge", "t241_assembly_lane", "t255_hyper_spaceway"]),
    ("Arcade CNK 2", ["t242_android_alley", "t213_tiny_temple", "t233_thunder_struck", "t222_barin_ruins"]),
    ("Arcade CNK 3", ["t212_jungle_boogie", "t223_deep_sea_driving", "t231_out_of_time", "t243_electron_avenue"]),
    ("Grand Prix 1", ["t232_clockwork_wumpa", "t154_oxide_station", "t501_july_world_tour", "t502_back_in_time"]),
    ("Grand Prix 2", ["t503_september_spyro", "t504_october_spooky", "t505_nitro_festival", "t506_luminous"]),
    ("Grand Prix 3", ["t507_dry_land", "t231_out_of_time", "t501_july_world_tour", "t134_dingo_canyon"]),
    ("Grand Prix 4", ["t508_toxic", "t255_hyper_spaceway", "t154_oxide_station", "t243_electron_avenue"]),
]

# Portails des coupes de gemmes (Gem Stone Valley) : couleur -> (n° de portail du hub, coupe d'origine).
CUP_PADS = {"red": (29, 4), "blue": (28, 5), "green": (27, 6), "yellow": (26, 7), "purple": (25, 8)}
