"""Patch du jeu (format XML shadPS4, lu au démarrage par le port PC) pour une graine.

Le port applique les fichiers `patches/*.xml` au code du jeu (`eboot.bin` 01.21) avant de le lancer.
Le patch ajoute trois détours, placés dans une zone vide à la fin du segment de code :

1. Chargement d'un niveau (fonction 0x9b1fc0, qui exécute « loadmap <zone> ») : si la zone en cours
   est le hub et que la zone demandée est dans la table, le jeu charge le remplaçant. Depuis une
   course (« Recommencer ») ou depuis le menu principal, rien ne change.
2. Récompenses (fonction 0x1076470 : trophée, reliques…) : si la zone récompensée est un remplaçant
   de la table, la récompense va à la zone d'origine, donc au portail emprunté.
3. Test « déjà gagné ? » (fonction 0x1037f30) : même règle. En fin de course, le jeu ne donne
   rien si la fiche de la zone jouée a déjà la récompense ; c'est donc la fiche du portail qu'on
   lui fait lire.

Option « noms » : au hub, le tableau des circuits lit le nom de chaque portail par
getHubZoneNameFromIndex (0x1037f90), et le bandeau du portail le reçoit de 0xe4ac10. Deux détours y
remplacent le nom du portail par celui du niveau qu'il charge (noms notés par CODE3 en arrivant au hub).

Les trois détours ne jouent que pour les courses simples, courses aux reliques, défis CTR et défis
cristaux (mode lu dans le gestionnaire de partie). Les courses de boss et les coupes restent celles
du jeu d'origine, avec leurs récompenses.

Option « récompenses » : le jeu garde ses bits de récompense (le lieu gagné) mais l'objet reçu change.
Le jeu recalcule tous les compteurs de la partie d'après les bits des fiches de circuits (0xfdf260, à la
fin de chaque fonction de récompense et au hub). Une enveloppe de ce recalcul retire, pour chaque lieu
gagné de la table de la graine, ce que le jeu lui a compté et ajoute 1 au compteur de l'objet tiré.
Pendant le recalcul d'origine, le détour 3 ne redirige rien (chaque fiche compte pour elle-même).
Affichage : chaque fonction de fin de course (trophée, relique, clé, jeton, jeton violet) note les bits gagnés
dans le gestionnaire de partie (+0xd54), d'où l'écran de fin de course (icône, texte) et l'animation du hub
tirent l'objet à montrer. Une enveloppe de chacune y met le bit de l'objet tiré. Les objets qui flottent
au-dessus d'un portail montrent les objets tirés (un par palier de relique pas encore gagné) ; les menus
gardent ceux du jeu (lieux faits), sauf la rangée des gemmes, qui montre les gemmes possédées.

Option « conditions » : ce qu'il faut pour ouvrir chaque portail de course (la course, puis le défi CTR et la
relique), Slide Coliseum, Turbo Track, chaque garage de boss, chaque arène et chaque coupe vient d'une table écrite
dans le patch (trophées, clés, reliques, gemmes ou jetons d'une couleur).

Option « indices » : les indices d'Aku Aku sont marqués comme déjà vus (ils ne coupent plus la partie), ainsi que les
cinématiques d'ouverture des portes que les clés de la partie ouvrent déjà.

Option « réserve » : hors dérapage, la barre de dérapage classique montre la réserve de boost.

Option « emplacements » : les portails (courses, arènes, coupes, Slide, Turbo) changent de place entre eux ; le
patch déplace leurs objets au chargement des cartes du hub, avant que le jeu les construise.

Option « coupes » : chaque portail de coupe de gemmes joue 4 circuits tirés (une coupe du jeu, ou 4 circuits
pris dans les coupes du jeu) ; la gemme reste rangée sur la fiche du portail.

Le code des détours ne dépend pas de la graine ; il est assemblé une fois pour toutes (source et
outils de vérification dans le dépôt d'étude). Seules les tables changent.
Adresses : position dans `eboot.elf` du port + 0x400000 (base des patchs du port).
"""
from .data import CUP_PADS, CUPS

EBOOT_BASE = 0x400000

LOADMAP = 0x9b1fc0
REWARD = 0x1076470
REWARDED = 0x1037f30
HUBNAME = 0x1037f90  # option « noms »
BANNER = 0xe4ac10  # option « noms »
CODE1, CODE2, HUBSTR, TABLE = 0x2330000, 0x2330100, 0x2330200, 0x2330300
HUBMAP, HUBMAP_SIZE = 0x2330280, 64  # option « noms » : n° de portail -> entrée de la table (voir hub_map)
CUPMAP = 0x23302c0  # option « coupes » : 5 × 8 octets, voir cup_map
CODE8 = 0x233a800  # option « coupes » : détour du départ d'une coupe
# Départ d'une coupe depuis un portail de Gem Stone Valley : l'appel en CUP_CALL charge le 1er circuit. CODE8 le
# remplace : les 4 circuits de la coupe en cours deviennent ceux de CUPMAP (n° de coupe du jeu, place, voir
# data.CUPS), puis la course se lance sur le premier. La gemme reste rangée sur la fiche du portail. Les coupes du
# jeu ne donnent que des noms : la liste de la coupe en cours reçoit les vraies poignées des fiches de ces circuits
# (fonction du jeu 0x14bea20), que le jeu lit entre les courses.
CUP_CALL = 0xe692d2
# Option « conditions » : CONDTABLE[n° de portail] (32 octets : genre, type 1, nombre 1, type 2, nombre 2 ; genre 1
# course, 2 garage, 3 arène, 4 coupe). Course : 1 = la course, 2 = le défi CTR et la relique (une fois le trophée du
# portail gagné) ; Slide Coliseum et Turbo Track n'ont que la 2e (les deux sont écrites). Garage : nombre 1 =
# trophées. Arène et coupe : une seule condition. Types = ce que le jeu sait compter (COND_TYPES). Les détours (CODE9)
# refont « ouvert ? » et « condition affichée » de chaque sorte de portail d'après la table ; un portail sans ligne
# garde le travail d'origine.
CONDTABLE, CODE9, COND_ROW = 0x2339000, 0x233aa00, 32
COND_TYPES = {"trophy": 2, "key": 4, "relics": 0x10, "gems": 0x20000, "token_red": 0x40, "token_blue": 0x80,
              "token_purple": 0x100, "token_green": 0x200, "token_yellow": 0x400}
COND_RACE, COND_BOSS, COND_ARENA, COND_CUP = 1, 2, 3, 4
# Option « emplacements » : un portail = 3 objets des cartes du hub (`maps/Octane/H100_Hub/H100_Hub_HubZone(s)_*.igz`,
# toujours chargées avec le hub) : X_HubZone (entité de la logique : +0x20 position, +0x30 rotation dont +0x68 = cap),
# X_Teleporter (entité qui déclenche, +0x20) et X_SpawnPoint (point d'arrivée, +0x10). Le socle (X_warp, entité de
# H100_Hub_Art_Common.igz, voir WARPS) part avec eux : le tourbillon « portail ouvert » s'affiche sur lui. CODE11
# enveloppe la fin du chargement d'un fichier IGZ (IGZ_FINISH, rdi = chargeur, liste racine en +0xb8) : chaque objet
# de la liste racine dont la position est dans PADTABLE prend celle de son nouvel emplacement (et son cap).
# PADTABLE : lignes de 32 octets = ancienne position, nouvelle position (12 octets chacune), cap, champ (0x20 entité,
# 0x10 point ; 0 = fin) ; une ligne ne sert qu'une fois par fichier (HubZone avant Teleporter, même position).
# Le monde d'un portail est noté dans la liste des portails du hub (CHUBZoneList, vtable HUBZONE_LIST, CHUBZone +0x38 ;
# il décide des objets flottants montrés et de la mini-carte au retour d'une course) : AREATABLE[n° de portail] =
# monde de son nouvel emplacement (0 = inchangé).
# La mini-carte a 5 régions (une par monde) qui listent les entités HubZone à montrer : MINIMAP (appelée par CODE11)
# refait ces listes pour que chaque région montre les portails posés chez elle. Ces entités sont dans d'autres
# fichiers : tant qu'elles ne sont pas chargées, l'entrée vaut bit 63 + n° du renvoi (MINIMAP_INDEX : portail de
# chaque n°) et le jeu la complète plus tard d'après ce n° ; MINIMAP échange alors les n° (IDXTABLE[n°] = monde de
# l'emplacement du portail). Une entrée déjà complétée est classée d'après sa position (SPOTTABLE : position de
# l'entité HubZone de chaque emplacement et son monde ; 16 octets par ligne, fin = monde 0). Si les deux cas se
# mélangent, les portails déjà complétés sont remis en attente (fonction du jeu 0x154ff10) et tous sont échangés par
# leur n°.
IGZ_FINISH = 0x154b330
HUBZONE_LIST = 0x274ea00
WORLDS = [1] * 6 + [3] * 5 + [4] * 6 + [5] * 6 + [3] + [2] * 8  # monde d'origine de chaque n° de portail
PAD_FIELDS = (0x20, 0x20, 0x10)  # HubZone, Teleporter, SpawnPoint
# Option « indices » : le pourcentage de la partie (PERCENT, appelé au chargement et après chaque récompense) est
# enveloppé (CODE10) pour marquer comme vus les 23 indices d'Aku Aku (slot+0x48, un bit par indice). Après le travail
# d'origine (qui recalcule les compteurs), CODE10 note aussi comme vues (slot+0x4c) les cinématiques d'ouverture des
# portes que les clés de la partie (slot+0x10) ouvrent déjà : le jeu ne les joue qu'au retour d'un boss, même pour une
# porte ouverte depuis longtemps. DOOR_CUTSCENES : (clés, bits de EOctaneAdventureCutscene).
PERCENT, CODE10 = 0xfdf0f0, 0x233af80
DOOR_CUTSCENES = ((1, 0x2000), (2, 0x4000 | 0x10000 | 0x20000), (3, 0x8000))
# Option « réserve » : la barre de dérapage classique (scripts Octane_BoostBar) se remplit d'après getDriftRatio_VSC,
# qui appelle 0x1041c60 en RATIO_CALL. L'appel va à RESERVE : le ratio du dérapage s'il n'est pas nul, sinon le plus
# grand temps restant des boosts actifs du kart (CKartBoostComponent+0x28) divisé par 5 s, borné à 1. La barre ne lit
# ce ratio qu'entre un départ et un arrêt de mise à jour, et ignore un départ quand elle tourne déjà : la fin d'un
# dérapage (STOP_DRIFT) et la fin de la jauge du départ turbo / de la remise en piste (STOP_START) font l'arrêt d'origine
# puis un départ « dérapage » (RESERVE_START) ; le début de cette jauge (START_TIMING) fait un arrêt avant son départ
# (TIMING_START).
RESERVE, RESERVE_START, TIMING_START = 0x2323000, 0x2323180, 0x23231a0
RATIO_CALL, STOP_DRIFT, STOP_START, START_TIMING = 0x112eb08, 0xe2d5df, 0xe7cc28, 0xe7d2d5
CODE3 = 0x233a000  # option « noms »
CODE4 = 0x233b000
CODE5 = 0x233b200  # option « noms »
CODE6 = 0x233b300  # option « noms »
STATE, STATE_END = 0x2bee700, 0x2bef000  # mémoire lecture/écriture libre (fin du segment de données)
INRECALC = STATE + 0x400  # drapeau « recalcul des compteurs en cours »
RECALC = 0xfdf260  # recalcul des compteurs de la partie (option « récompenses »)
CODE7 = 0x233b400  # option « récompenses » : enveloppe du recalcul, SHOW, enveloppes, PAD3D_WON, PAD3D_MODEL
SHOW = 0x233b4d0  # option « récompenses » : objet à montrer pour (zone jouée, bits)
# Objets en 3D au-dessus d'un portail (option « récompenses ») : deux appels de la fonction qui les crée sont
# détournés, celui des bits gagnés de la fiche (WON_CALL) et celui du modèle d'un objet (MODEL_CALL). Les menus
# (tableau des circuits, progression) restent ceux du jeu : ils montrent les lieux faits.
WON_CALL, MODEL_CALL = 0xdff1d3, 0xdff1e2
PAD3D_WON = 0x233b7f0  # la relique reste tant qu'un de ses paliers n'est pas gagné
PAD3D_MODEL = 0x233b860  # modèle de l'objet tiré ; un objet par palier de relique pas gagné
# Rangée des gemmes du menu (option « récompenses ») : getAllCollectiblesForIndex est enveloppé (GEMROW) pour que,
# aux 5 portails de coupe, une gemme s'allume quand on la possède (aucun autre écran ne compte les gemmes).
GETALL = 0x10379c0
GEMROW = 0x233b960
REWARDS = 0x2332000  # table de l'option « récompenses »
# Une ligne : nom de zone (64 octets), bit, compteur de l'objet tiré, compteur compté par le jeu, paliers
# de relique au-dessus, bit de l'objet tiré, n° de portail du hub (u32 chacun).
REWARD_RECORD = 88
# N° de portail du hub (index des CHUBZone) de chaque lieu ; la clé de boss est rangée dans la fiche du circuit
# du boss mais montrée au garage du boss.
HUB_INDEX = {"t111_crash_cove": 0, "t112_roos_tubes": 1, "t113_mystery_caves": 2, "t114_sewer_speedway": 3,
             "a115_skull_rock": 4, "t131_coco_park": 6, "t133_papus_pyramid": 7, "t134_dingo_canyon": 8,
             "t132_tiger_temple": 9, "t141_blizzard_bluff": 11, "t142_dragon_mines": 12, "t144_tiny_arena": 13,
             "t143_polar_pass": 14, "a145_rocky_road": 15, "t151_ngin_labs": 17, "t152_cortex_castle": 18,
             "t153_hot_air_skyway": 19, "t154_oxide_station": 20, "a155_nitro_court": 21, "a135_rampage_ruins": 23,
             "t121_slide_coliseum": 30, "t122_turbo_track": 31}
BOSS_INDEX = {"t112_roos_tubes": 5, "t133_papus_pyramid": 10, "t142_dragon_mines": 16, "t153_hot_air_skyway": 22}
KEY = 4
# Coupes de gemmes : n° du portail de la coupe pour chaque gemme (bit), de 0x1000 rouge à 0x10000 jaune.
CUP_INDEX = {0x1000: 29, 0x2000: 28, 0x4000: 25, 0x8000: 27, 0x10000: 26}
# Compteur (position dans la fiche de la partie) que le jeu compte pour chaque bit (gemmes : mises à 1).
VANILLA = {2: 0xc, 4: 0x10, 0x10: 0x28, 0x20: 0x2c, 8: 0x30, 0x40: 0x34, 0x80: 0x38, 0x100: 0x3c,
           0x200: 0x40, 0x400: 0x44, 0x1000: 0x14, 0x2000: 0x18, 0x4000: 0x1c, 0x8000: 0x20, 0x10000: 0x24}
# Une fiche ne compte que sa meilleure relique : un palier n'a rien compté si un palier au-dessus est là.
HIGHER = {0x10: 0x20 | 8, 0x20: 8}
ITEM_BIT = {counter: bit for bit, counter in VANILLA.items()}  # objet (compteur) -> bit montré par le jeu
CAVE_END = 0x233c078
RECORD, NAME = 128, 64  # une entrée = zone d'origine (64 octets) + zone de remplacement (64 octets)
HUB = "octane/h100_hub/h100_hub"

# Détour du chargement (assemblé à CODE1).
CODE1_BYTES = bytes.fromhex(
    "50515241504885ff0f8483000000488b0533de79004885c074778b80400d000083f81f776cb92a0100000fa3c173"
    "62488b05a23c78004885c07456488b80c00000004885c0744a488d15b201000031c9448a040a443a040875374584"
    "c07404ffc1ebed488d1596020000803a00742231c98a040a3a040f750b84c07410ffc183f94072ed4881c2800000"
    "00ebdd488d7a4041585a5958554889e54156e9251f68fe")
# Détour des récompenses (assemblé à CODE2).
CODE2_BYTES = bytes.fromhex(
    "505152565741504151415241534885ff7476488b052fdd79004885c0746a8b804c0d000083f81f775fb92a010000"
    "0fa3c17355488b47104885c0744c488d15bd010000803a00744031c9448a440a40443a0408750c4584c07410ffc1"
    "83f94072e94881c280000000ebd9488b3da73a7b004885ff74124889d6e8a2e1cffe4885c074054889442420415b"
    "415a415941585f5e5a5958554889e541574156e9d662d4fe")
# Détour du test « déjà gagné ? » (assemblé à CODE4) : le même que CODE2, mais qui remplace la
# sauvegarde de la zone (CZoneInfo+0x160) au lieu de la zone, et rien pendant le recalcul des compteurs.
# Aventure neuve (pas encore rechargée) : la sauvegarde n'a pas de nom ; il est alors pris à la zone en cours
# (0x102e040), seulement si la sauvegarde est la sienne.
CODE4_BYTES = bytes.fromhex(
    "50515256574150415141524153833dec3a8b00000f85cf0000004885ff0f84c6000000488b051e2e79004885c00f"
    "84b60000008b804c0d000083f81f0f87a7000000b92a0100000fa3c10f8399000000488b47104885c0745e488d15"
    "a052ffff803a000f848000000031c9448a440a40443a0408750c4584c07410ffc183f94072e94881c280000000eb"
    "d5488b3d868b7a004885ff74524889d6e88132cffe4885c07445488b80600100004885c074394889442420eb3248"
    "8b3d5a8b7a004885ff7426e8782fcffe4885c0741c488b4c242048398860010000750e488b40104885c07405e970"
    "ffffff415b415a415941585f5e5a5958554889e541574156e935cecffe")
# Option « récompenses » (assemblé à CODE7) : enveloppe du recalcul des compteurs, SHOW, une enveloppe par
# fonction de fin de course (adresses dans REWARD_FUNCS), PAD3D_WON, PAD3D_MODEL puis GEMROW.
CODE7_BYTES = bytes.fromhex(
    "53415441554989fc4d85e4741b31c041894424144189442418418944241c41894424204189442424c705ce368b00"
    "01000000e87c000000c705bf368b00000000004d85e47467488d1db36bffff803b00745b488b3dbf877a004885ff"
    "744f4889dee8ba2ecffe4885c0743c4c8ba8600100004d85ed74304c89ef8b7340e83e00000084c074218b734c85"
    "f6740c4c89efe82b00000084c075078b434841ff0c048b434441ff04044883c358eba0415d415c5bc3554889e541"
    "574156e9a83dcafe554889e541574156e96bcacffecccccc53415441554989fc4189f54d85e40f84bf000000488b"
    "055d2979004885c0746d8b804c0d000083f81f7762b92a0100000fa3c17358498b4424104885c00f849000000048"
    "8d15e64dffff803a00743e31c9448a440a40443a0408750c4584c07410ffc183f94072e94881c280000000ebd948"
    "8b3dd0867a004885ff74104889d6e8cb2dcffe4885c074034989c44d8b4424104d85c0743c488d1d926affff803b"
    "00743044396b40751f41f7c500f00100751c31c98a040b413a0408750b84c0740dffc183f94072ec4883c358ebd0"
    "8b4350eb0231c0415d415c5bc3cccccccccc53415441554989fc4989f58b9f540d0000c787540d000000000000e8"
    "32000000418b8424540d000085c0750a41899c24540d0000eb164c89ef89c6e8e0feffff85c0740841898424540d"
    "0000415d415c5bc3554889e541574156e93936cafecc53415441554989fc4989f58b9f540d0000c787540d000000"
    "000000e832000000418b8424540d000085c0750a41899c24540d0000eb164c89ef89c6e880feffff85c074084189"
    "8424540d0000415d415c5bc3554889e541574156e9c940cafecc53415441554989fc4989f58b9f540d0000c78754"
    "0d000000000000e832000000418b8424540d000085c0750a41899c24540d0000eb164c89ef89c6e820feffff85c0"
    "740841898424540d0000415d415c5bc3554889e541574156e9a943cafecc53415441554989fc4989f58b9f540d00"
    "00c787540d000000000000e832000000418b8424540d000085c0750a41899c24540d0000eb164c89ef89c6e8c0fd"
    "ffff85c0740841898424540d0000415d415c5bc3554889e541574156e91949cafecc53415441554989fc4989f58b"
    "9f540d0000c787540d000000000000e832000000418b8424540d000085c0750a41899c24540d0000eb164c89ef89"
    "c6e860fdffff85c0740841898424540d0000415d415c5bc3554889e541574156e9c946cafecc53415441554989fc"
    "4989f58b9f540d0000c787540d000000000000e832000000418b8424540d000085c0750a41899c24540d0000eb16"
    "4c89ef89c6e800fdffff85c0740841898424540d0000415d415c5bc3554889e541574156e92949cafecc53415441"
    "55448b6de8e8b2abd3fe4189c483e03883f838742341f7c410000000741abe10000000e8190000004885db740b41"
    "83e4ef4181cc000000804489e0415d415c5bc3488d1dc467ffff803b00741144396b54750539734074084883c358"
    "ebea31dbc3cccccccccccccccccccccc5341544155415641574989ff448b6de8e8c20000004885db740883fe1074"
    "108b73504c89ffe806ebc0fee99e00000041f7c410000080752bbe10000000e8950000004885db74038b73504c89"
    "ffe8deeac0fe4885c0740c4c89f7488b7018e89d3eacfe41f7c420000000752bbe20000000e8610000004885db74"
    "038b73504c89ffe8aaeac0fe4885c0740c4c89f7488b7018e8693eacfe41f7c408000000752bbe08000000e82d00"
    "00004885db74038b73504c89ffe876eac0fe4885c0740c4c89f7488b7018e8353eacfe31c0415f415e415d415c5b"
    "c3488d1dc266ffff803b00741144396b54750539734074084883c358ebea31dbc3cccccccccccccccccc53415441"
    "554989f44189fde8740000004489e883e81983f8057363488b05c62479004885c07457488b90c00d00004885d274"
    "4b498b04244885c074428b480c4c8b402031db39cb7d354d8b0cd84d85c97428418b410ca900f00100741d0fbcc0"
    "83f80c721583f81077108d0485e4ffffff833c0200410f9f4110ffc3ebc7415d415c5bc3554889e541574156e9d7"
    "bfcffe")
# Option « indices » (assemblé à CODE10) : voir PERCENT.
CODE10_BYTES = bytes.fromhex(
    "534889fb488b87c00d00004885c07407814848ffffff00e83c000000488b8bc00d00004885c9742e8b51104531c083fa017c1f4181c8"
    "0020000083fa027c134181c80040030083fa037c074181c8008000004409414c5bc3554889e541574156e91341cafe")
# Option « réserve » (assemblé à RESERVE, RESERVE_START, TIMING_START) : voir RESERVE.
RESERVE_BYTES = bytes.fromhex(
    "554889e54157415641554154534883ec084989fe4889f3c703000000004d85f60f84d2000000488b3553157a0031d24c89f7e8598f0bfe"
    "4885c0741a4889c7e8cc96b6fec5fa1103c5f057c9c5f82ec10f87a2000000488b35bb0f7a0031d24c89f7e8298f0bfe4885c00f848800"
    "0000488b40284885c0747f4863480c4c8b78204d8d34cfc745d0000000004d39f773444d8b274983c7084d85e474ef4d8b6c24104d85ed"
    "74e54c89e7e8a1bfb0fec4c17a58451cc4c17a584524c4c17a58442428c4c17a5c442418c5fa5f45d0c5fa1145d0ebb7b8cdcc4c3ec5f9"
    "6ec8c5fa1045d0c5fa59c1b80000803fc5f96ec8c5fa5dc1c5fa11034883c4085b415c415d415e415f5dc3")
RESERVE_START_BYTES = bytes.fromhex("57e81aa6b0fe5fbe01000000e91f06b2fe")
TIMING_START_BYTES = bytes.fromhex("57564883ec08e8f5a5b0fe4883c4085e5fe9fa05b2fe")
CALL_RATIO = bytes.fromhex("e8f3441f01")
SIG_RATIO = "e8 53 31 f1 ff 48 8b 43 10 c5 fa 10 45 d4 4c 89 f7 48 8b 70 08 e8 8e ca 34 ff 48 8b 7d d8 48 85"
CALL_STOP_DRIFT = bytes.fromhex("e89c5b4f01")
SIG_STOP_DRIFT = "e8 bc 01 00 00 48 8d 05 bd 49 cc 01 8b 1d c7 7e c3 01 48 8b 38 80 7f 6c 00 0f 84 32 01 00 00 e8"
CALL_STOP_START = bytes.fromhex("e853654a01")
SIG_STOP_START = "e8 73 0b fb ff c6 83 89 00 00 00 01 48 89 df 8b b3 8c 00 00 00 e8 0e 54 fb ff 49 8b 04 24 48 3b"
CALL_START_TIMING = bytes.fromhex("e8c65e4a01")
SIG_START_TIMING = "e8 d6 64 fc ff c6 83 89 00 00 00 00 48 89 df 8b b3 8c 00 00 00 e8 61 4d fb ff 41 c6 06 01 5b 41"
# Option « conditions » (assemblé à CODE9) : voir CONDTABLE.
CODE9_BYTES = bytes.fromhex(
    "31c0488b0d3f3479004885c9747d488b89c00d00004885c9747183fe0275048b410cc383fe0475048b4110c383fe"
    "10750a8b412803412c034130c381fe0000020075108b411403411803411c034120034124c383fe4075048b4134c3"
    "81fe8000000075048b4138c381fe0001000075048b413cc381fe0002000075048b4140c381fe0004000075038b41"
    "44c34531c04c8b4f104d85c9741f418b411083f8207316c1e0054c8d0555e5ffff4901c04183380075034531c0c3"
    "418b7004e83fffffff31d2413b40087d05baffffff7f4189513441c7413804000000418b700ce81dffffff31d241"
    "3b40107d05baffffff7f4189513cc3cccccccccccccccccccccce887ffffff4d85c07405e8a9ffffff554889e541"
    "574156e9dcfdb2fecccccccc53415441554889fb4989f44989d5e8bdfdb2fe4189c24889dfe84effffff4d85c074"
    "2a4183fa027512418b401041890424418b400c41894500eb3a418b400841890424418b400441894500eb284183fa"
    "027512418b413c41890424418b413841894500eb10418b41344189042441c7450002000000415d415c5bc3cccccc"
    "cccce8e7feffff4d85c07408418b400841894130488b058f327900418b5130488b80c00d000083faff740739500c"
    "0f9dc0c3418b493483f9ff74073948100f9dc0c331c0c3cccccccccccccccccccccccccce897feffff4d85c07411"
    "418b7004e8fdfdffff413b40080f9dc0c3be04000000418b5130e8e7fdffff39d00f9dc0c3cce867feffff4d85c0"
    "740d418b40088906418b40048902c3418b41308906c70204000000c3cccccccccccccccccccccccce837feffff4d"
    "85c07411418b7004e89dfdffff413b40080f9dc0c3418b7130418b5134e888fdffff39d00f9dc0c3cccce807feff"
    "ff4d85c0740d418b40088906418b40048902c3418b41348906418b41308902c3cccccccccccccccccccccccce8d7"
    "fdffff4d85c0741b418338017507e8f3fdffffeb0e418338027508418b400841894130554889e541574156e9e681"
    "aefe")
# Option « coupes » (assemblé à CODE8) : voir CUP_CALL.
CODE8_BYTES = bytes.fromhex(
    "535541544155415641574883ec284989fc4989f54189d64189cf4489c589e883e81983f8050f83f0000000488d1d"
    "8e5affff488d1cc3803bff0f84dc000000498b8424800d00004885c00f84cb00000083780c040f85c1000000488b"
    "05d7f379004885c00f84b1000000488b80880100004885c00f84a100000031c90fb6144b3b500c0f839200000044"
    "0fb6444b014183f8040f83820000004c8b48204d8b0cd14d85c974754d8b49204d85c9746c4f8b0cc14d85c97463"
    "4983791000745c4c890cccffc183f90472b231db488b3d45937a004885ff7443488b04dc488b7010e83b3acffe48"
    "85c07431488904dcffc383fb0472d74c8b2c2431db498bbc24800d0000488b7f20488d3cdf488b34dce80c4118ff"
    "ffc383fb0472e04c89e74c89ee4489f24489f94189e84883c428415f415e415d415c5d5be9b33fcafe")
# Option « noms » : le détour du chargement commence par un appel à CODE3, qui renomme les
# portails en arrivant au hub et remet les noms en le quittant (état en mémoire à STATE).
CODE1_NOMS_BYTES = bytes.fromhex(
    "e8fb9f000050515241504885ff0f8483000000488b052ede79004885c074778b80400d000083f81f776cb92a0100"
    "000fa3c17362488b059d3c78004885c07456488b80c00000004885c0744a488d15ad01000031c9448a040a443a04"
    "0875374584c07404ffc1ebed488d1591020000803a00742231c98a040a3a040f750b84c07410ffc183f94072ed48"
    "81c280000000ebdd488d7a4041585a5958554889e54156e9201f68fe")
CODE3_BYTES = bytes.fromhex(
    "5051525657415041514152415353415441554989fc4d85e40f845d0100004c89e7488d35d861ffffe87e01000084"
    "c07539488b05a09c77004885c00f843a010000488bb8c00000004885ff0f842a010000488d35a861ffffe84e0100"
    "0084c00f8416010000e9ba000000833d8f468b00000f85040100004c8d2d8262ffff488d1d8b468b0041807d0000"
    "744e31c048890348894308488943104c89eee8ed0000004885c07427488903488b88a000000048894b08498d7540"
    "e8d10000004885c0740b488b88a000000048894b104981c5800000004883c318ebab4c8d2d1f62ffff488d1d2846"
    "8b0041807d00007429488b034885c07414488b4b104885c9740bf0ff41f8488988a00000004981c5800000004883"
    "c318ebd0c705de458b0001000000eb57833dd5458b0000744e4c8d2dcc61ffff488d1dd5458b0041807d0000742f"
    "4c89eee8440000004885c07415483b037510488b4b084885c97407488988a00000004981c5800000004883c318eb"
    "cac70585458b0000000000415d415c5b415b415a415941585f5e5a5958c3488b3d839a7a004885ff740e4883ec08"
    "e87d41cffe4883c408c331c0c331c98a040f3a040e750c84c0740548ffc1ebefb001c331c0c3")
# Option « noms », détour de getHubZoneNameFromIndex (assemblé à CODE5) : appelle la fonction d'origine,
# puis, au hub, donne au portail (reconnu à son numéro, voir hub_map) le nom de son remplaçant.
CODE5_BYTES = bytes.fromhex(
    "57564883ec08e84d0000004883c4085e5f505152833de5348b000074374885f6743289f883f840732b488d155050"
    "ffff0fb6040285c0741c488d0440488d15cd348b00488b4cc2f84885c97407f0ff41f848890e5a5958c3554889e5"
    "41574156e933cdcffe")
# Option « noms », détour du bandeau (assemblé à CODE6) : au hub, le bandeau d'un portail (reconnu à son
# numéro, voir hub_map) reçoit le nom de son remplaçant.
CODE6_BYTES = bytes.fromhex(
    "5052833df7338b0000743e4d85f67439498b46104885c074308b401083f8407328488d15584fffff0fb6040285c0"
    "7419488d0440488d15d5338b00488d44c2f84883380074034889c65a58554889e541574156e9c0f8b0fe")
# Sauts posés à l'entrée des trois fonctions (en écrasant 6, 8 et 8 octets d'instructions entières).
JUMP_LOADMAP = bytes.fromhex("e93be0970190")
JUMP_REWARD = bytes.fromhex("e98b9c2b01909090")
JUMP_REWARDED = bytes.fromhex("e9cb303001909090")
JUMP_HUBNAME = bytes.fromhex("e96b323001909090")
JUMP_BANNER = bytes.fromhex("e9eb064f01909090")
# Code d'origine à l'entrée des trois fonctions : si le jeu n'est pas la version attendue, le port
# ne trouve pas ces octets et ignore le patch au lieu de l'appliquer au mauvais endroit.
SIG_LOADMAP = "55 48 89 e5 41 56 53 48 81 ec 30 01 00 00 4c 8b 35 c3 50 e5 01 48 89 fb 89 f1 48 85 db 49 8b 06"
SIG_REWARD = "55 48 89 e5 41 57 41 56 41 55 41 54 53 50 48 8b 05 c3 2f a5 01 49 89 fd 4c 8b 3d a1 d6 a6 01 41"
SIG_REWARDED = "55 48 89 e5 41 57 41 56 41 54 53 48 8b 05 06 15 a9 01 49 89 fc 4c 8b 3d e4 bb aa 01 41 89 f6 48"
SIG_HUBNAME = "55 48 89 e5 41 57 41 56 41 54 53 41 89 fe 48 8b 3d 5b a6 ab 01 49 89 f7 48 8d 35 61 0d dc 00 e8"
SIG_BANNER = "55 48 89 e5 41 57 41 56 41 54 53 48 8d 05 86 73 ca 01 49 89 fe 8b 1d 8d a8 c1 01 49 89 f7 48 8b"
JUMP_RECALC = bytes.fromhex("e99bc13501909090")
SIG_RECALC = "55 48 89 e5 41 57 41 56 41 55 41 54 53 48 81 ec 98 00 00 00 48 8b 05 1d 7e 82 01 48 85 ff 48 8b"
# Appels posés à la place des deux appels d'origine (5 octets chacun).
CALL_WON = bytes.fromhex("e818c65301")
SIG_WON = "e8 d8 71 27 00 41 89 c4 31 db eb 21 4c 89 ff e8 a9 b1 14 00 48 85 c0 74 2a 48 8b 70 18 4c 89 f7"
CALL_MODEL = bytes.fromhex("e879c65301")
SIG_MODEL = "e8 a9 b1 14 00 48 85 c0 74 2a 48 8b 70 18 4c 89 f7 e8 68 05 00 00 eb 1c 66 0f 1f 44 00 00 be 01"
# Fonctions de fin de course (option « récompenses ») : (fonction, son enveloppe dans CODE7, saut posé à son
# entrée, signature).
REWARD_FUNCS = [
    (0xfdec40, 0x233b5b0, bytes.fromhex("e96bc93501909090"),  # trophée
     "55 48 89 e5 41 57 41 56 41 55 41 54 53 48 83 ec 18 4c 8b 2d 40 84 82 01 48 89 f3 49 89 fc 41 89"),
    (0xfdf730, 0x233b610, bytes.fromhex("e9dbbe3501909090"),  # relique
     "55 48 89 e5 41 57 41 56 53 50 49 89 f7 49 89 fe 89 d3 49 8b bf 60 01 00 00 89 de e8 e0 87 05 00"),
    (0xfdfa70, 0x233b670, bytes.fromhex("e9fbbb3501909090"),  # clé de boss
     "55 48 89 e5 41 57 41 56 41 55 41 54 53 48 83 ec 18 48 8b 1d 10 76 82 01 41 89 d6 49 89 f7 49 89"),
    (0xfe0040, 0x233b6d0, bytes.fromhex("e98bb63501909090"),  # jeton CTR
     "55 48 89 e5 41 57 41 56 53 50 49 89 f7 48 89 fb 41 89 d6 49 8b bf 60 01 00 00 44 89 f6 e8 ce 7e"),
    (0xfdfe50, 0x233b730, bytes.fromhex("e9dbb83501909090"),  # jeton violet
     "55 48 89 e5 41 57 41 56 53 50 49 89 f7 48 89 fb 41 89 d6 49 8b bf 60 01 00 00 44 89 f6 e8 be 80"),
    (0xfe0110, 0x233b790, bytes.fromhex("e97bb63501909090"),  # gemme (fin d'une coupe)
     "55 48 89 e5 41 57 41 56 41 55 41 54 53 48 83 ec 28 4c 8b 25 70 6f 82 01 48 89 f3 49 89 fd 41 89"),
]
# Podium (option « récompenses ») : la clé n'a pas de point où se poser sur le podium (elle restait cachée derrière le
# pilote). KEYSPOT remplace l'appel de la table des objets (KEY_CALL) dans getRewardEntityFromRace et cherche aussi le
# trophée quand ce point est vide ; KEYSPOT2 (KEY_NAME) prend alors le point du trophée. L'objet montré ne change pas.
KEYSPOT, KEYSPOT2, KEY_CALL, KEY_NAME = 0x2322a00, 0x2322a40, 0x1039e66, 0x1039e90
KEYSPOT_BYTES = bytes.fromhex("57e88a79c2fe5f4531ff4885c0741d488b48104885c97405803900750f50be02000000e86879c2fe4989c758c3")
KEYSPOT2_BYTES = bytes.fromhex("4883c3104d85ff7404498d5f104c39e3c3")
CALL_KEY = bytes.fromhex("e8958b2e01")
SIG_KEY = "e8 25 05 f1 ff 48 89 c3 48 85 db 74 4a 48 8b 43 18 49 8b 3e 48 85 c0 49 89 06 74 04 f0 ff 40 08"
CALL_KEY_NAME = bytes.fromhex("e8ab8b2e016690")
SIG_KEY_NAME = "48 83 c3 10 4c 39 e3 74 24 49 8b 34 24 48 85 f6 75 28 49 c7 04 24 00 00 00 00 48 8b 03 48 85 c0"
# Cinématique du boss (options « récompenses » et « emplacements ») : le jeu la lançait quand toutes les courses à
# trophée posées dans le monde étaient gagnées, alors que le garage s'ouvre au nombre de trophées. Le test des courses
# est sauté (BOSS_SKIP) et BOSSTALK, appelé à la fin du test (BOSS_OK), demande les trophées du garage du monde
# (BOSSREQ, voir boss_req).
BOSSTALK, BOSSREQ, BOSS_SKIP, BOSS_OK = 0x2322a80, 0x2322b00, 0xe4c0fc, 0xe4c146
BOSSTALK_BYTES = bytes.fromhex(
    "488b1d11464e00488b7db841b6018b45c083f8087329488d0d630000008b0c8185c9741b488b059db37a00488b80c00d00004885c07405"
    "39480c7d034531f6c3")
JUMP_BOSS_SKIP = bytes.fromhex("eb07")
SIG_BOSS_SKIP = "74 07 89 c1 83 e1 02 74 0a 8b 55 c0 21 c3 f6 c3 04 74 8f 48 8b 1d 82 af 9b 01 48 8b 7d b8 45 31"
CALL_BOSS_OK = bytes.fromhex("e835694d01660f1f840000000000")
SIG_BOSS_OK = "48 8b 1d 4b af 9b 01 48 8b 7d b8 41 b6 01 48 85 ff 75 c9 eb cc 31 ff 8b 55 c0 e9 02 ff ff ff 45"
BOSS_AREA = {"t112_roos_tubes": 1, "t133_papus_pyramid": 3, "t142_dragon_mines": 4, "t153_hot_air_skyway": 5}
JUMP_GETALL = bytes.fromhex("e99b3f3001909090")
SIG_GETALL = "55 48 89 e5 41 57 41 56 41 55 41 54 53 48 83 ec 28 48 8b 05 e8 93 a8 01 49 89 f4 41 89 fd 49 8b"
CALL_CUP = bytes.fromhex("e829154d01")
SIG_CUP = "e8 19 56 17 00 48 8b 05 6a 4b c6 01 c7 80 68 0d 00 00 00 00 00 00 e9 cb fc ff ff 48 8d ba 88 0d"
COND_FUNCS = [  # (fonction, son détour, saut posé à son entrée, signature)
    (0xe6a8f0, 0x233ab00, bytes.fromhex("e90b024d01909090"),  # état d'un portail de course
     "55 48 89 e5 41 57 41 56 41 54 53 48 8b 05 46 35 c6 01 49 89 fc 45 31 f6 49 8b 4c 24 10 4c 8b b8"),
    (0xe69ec0, 0x233ab20, bytes.fromhex("e95b0c4d01"),  # condition affichée d'un portail de course
     "55 48 89 e5 41 57 41 56 53 50 49 89 d6 49 89 f7 48 89 fb e8 18 0a 00 00 83 f8 02 75 1b 48 8b 43"),
    (0xe53290, 0x233aba0, bytes.fromhex("e90b794e01"),  # garage de boss ouvert ?
     "48 8b 4f 10 48 8b 05 ad ab c7 01 8b 51 30 48 8b 80 c0 0d 00 00 83 fa ff 74 07 39 50 0c 0f 9d c0"),
    (0xe51ed0, 0x233abf0, bytes.fromhex("e91b8d4e01"),  # arène ouverte ?
     "48 8b 05 71 bf c7 01 48 8b 4f 10 48 8b 80 c0 0d 00 00 8b 40 10 3b 41 30 0f 9d c0 c3 90 90 90 90"),
    (0xe51ef0, 0x233ac20, bytes.fromhex("e92b8d4e01"),  # condition affichée d'une arène
     "48 8b 47 10 8b 40 30 89 06 c7 02 04 00 00 00 c3 e9 1b 1a fd ff 90 90 90 90 90 90 90 90 90 90 90"),
    (0xe68d70, 0x233ac50, bytes.fromhex("e9db1e4d01"),  # coupe ouverte ?
     "48 8b 05 d1 50 c6 01 31 c9 48 8b 90 c0 0d 00 00 48 8b 47 10 8b 70 30 81 fe ff 00 00 00 7e 1d 81"),
    (0xe68de0, 0x233ac80, bytes.fromhex("e99b1e4d01"),  # condition affichée d'une coupe
     "48 8b 47 10 8b 48 34 89 0e 8b 40 30 89 02 c3 90 55 48 89 e5 41 57 41 56 53 50 48 89 fb 49 89 d6"),
    (0xe22ec0, 0x233acb0, bytes.fromhex("e9eb7d5101909090"),  # activation d'un composant de portail
     "55 48 89 e5 41 57 41 56 41 55 41 54 53 48 83 ec 48 4c 8b 2d c0 41 9e 01 49 89 fc 31 d2 49 8b 45"),
]
JUMP_PERCENT = bytes.fromhex("e98bbe3501909090")
SIG_PERCENT = "55 48 89 e5 41 57 41 56 41 55 41 54 53 50 48 89 fb 48 8b bb c0 0d 00 00 e8 53 01 00 00 4c 8b a3"
CODE11_BYTES = bytes.fromhex(
    "5341544155415641574881ec800000004889fbe8180100004189c785c00f85f9000000488b83b80000004885c00f"
    "84e9000000448b60104c8b68204d85ed0f84d800000031c04889e7b910000000f348ab4531f64539e60f83b70000"
    "004b8b7cf50041ffc64885ff74ea488b07488d158ce942004839d07459488d358017000031c98b561c85d274cb80"
    "3c0c00753b488b06483b041775328b46083b4417087529c6040c01488b460c488904178b46148944170883fa2075"
    "9b488b47304885c074928b5618895068eb8a4883c620ffc1ebb08b4f1083f9207605b920000000488b77204885f6"
    "0f8468ffffff488d158d02000085c90f8459ffffffffc90fb6040a85c074ee4c8b04ce4d85c074e541894038ebdf"
    "4889dfe8e41000004489f84881c480000000415f415e415d415c5bc3554889e541574156e9fbb122ff")
CODE11, AREATABLE, PADTABLE, PADTABLE_ROWS, SPOTTABLE = 0x2320000, 0x2320380, 0x2321800, 128, 0x2321000
JUMP_IGZ = bytes.fromhex("e9cb4cdd00909090")
SIG_IGZ = "55 48 89 e5 41 57 41 56 41 55 41 54 53 48 83 ec 78 48 89 fb e8 37 1f 00 00 85 c0 0f 85 13 09 00"
MINIMAP_BYTES = bytes.fromhex(
    "5341544155415641574881ec400200004989ffc7042400000000488b87b80000004885c00f848d020000448b6010"
    "4c8b68204d85ed0f847c0200004531f64539e6733c4b8b7cf50041ffc64885ff74ee488b07488d15d6e132004839"
    "d0740c488d1522e432004839d075d38b042483f80573cb48897cc408ffc0890424ebbf4531e4443b24240f83fe00"
    "00004a8b7ce40841ffc4488b7f304885ff74e5448b77104c8b6f204d85ed74d84585f674d341ffce4b8b44f50048"
    "85c079ee480fbaf03f4883f84073e34c8d05f2feffff41803c000074d54531e4443b24240f83a80000004a8b7ce4"
    "0841ffc4488b7f304885ff74e5448b77104c8b6f204d85ed74d84585f674d341ffce4b8b54f5004881fa00000100"
    "72ea4885d278e5498b47684885c074dc8b480c83f9407605b940000000488b70204885f674c64c8d057ffeffff85"
    "c97ebbffc9483b14ce75f441803c080074ac480fbae93f4b8d44f5004889084889842430020000498dbf88000000"
    "488db42430020000488d942438020000e88beb22ffe976ffffff4531c94531d2443b1424734c4a8b7cd40841ffc2"
    "488b7f304885ff74e98b4f10488b77204885f674dd85c974d9ffc9488b14cee89600000085c074ed4183f92073e7"
    "4589c849c1e0044a89540430428944043841ffc1ebd14531d2443b14240f83c80000004a8b7cd40841ffc2488b7f"
    "304885ff74e58b4f10488b77204885f674d985c974d5ffc9488b14cee83d00000085c074ed25000100004409d089"
    "c34531db4539cb73db4589d849c1e00442395c043875144a8b440430488904ce42c744043800000000ebb941ffc3"
    "ebd44885d2745778314881fa00000100724c4c8d0591fbffff418b400c85c0743f4d8b184c3b5a20750a458b5808"
    "443b5a28742c4983c010ebdf4889d0480fbaf03f4883f84073164c8d051bfdffff410fb6040085c074080d000100"
    "00c331c0c34881c440020000415f415e415d415c5bc3")
IDXTABLE, IDX_COUNT, MINIMAP = 0x23211c0, 64, 0x2321200
# Menus de progression (liste des circuits d'un monde, menu Progression) : chaque ligne vient d'un n° de portail donné
# par 0x1038c50 (portails d'origine du monde, appelée en ROW_CALL par le nœud getHUBZoneIndexForRaceInArea_VSC).
# ROWMAP l'appelle puis remplace ce n° par celui du portail posé à cet endroit (ROWTABLE) : nom et icônes de la ligne
# sont ceux du portail qu'on y voit. Le script de ces lignes n'a d'icône que pour les trophées, clés, reliques, jetons et
# le défi d'Oxide (ROW_TYPES), et sa boucle sur les objets s'arrête (et saute ensuite des objets) sur un autre type :
# ROWMAP note le n° rendu (+ 1) dans ROWFLAG, et ROWMASK (appelé en ROW_MASK_AT, lecture des objets du portail dans
# getAllCollectiblesForIndex) ne garde que ROW_TYPES pour ce n° : une coupe posée sur une ligne montre son nom, sans icône.
ROWMAP, ROWTABLE, ROW_CALL = 0x2322800, 0x2322900, 0x1116307
ROWMASK, ROW_MASK_AT, ROWFLAG = 0x2322940, 0x1037aa5, STATE + 0x500
ROW_TYPES = 0x407fe
ROWMAP_BYTES = bytes.fromhex("52e84a64d1fe5a8b0283f8207317488d0deb0000000fb60c0181f9ff000000740489c88902ffc08905d3c38c00c3")
ROWMASK_BYTES = bytes.fromhex("448b7128418d55013b15b2c28c0075074181e6fe070400c7059fc28c000000000031dbc3")
CALL_ROW = bytes.fromhex("e8f4c42001")
CALL_ROW_MASK = bytes.fromhex("e896ae2e0190")
SIG_ROW = "e8 44 29 f2 ff 48 8b 43 10 8b 55 d4 4c 89 f7 48 8b 70 10 e8 31 6d 36 ff 49 8b 04 24 48 3b 45 d8"
SIG_ROW_MASK = "44 8b 71 28 31 db 4c 89 65 b8 44 89 6d d4 48 89 45 c0 66 0f 1f 84 00 00 00 00 00 ba 01 00 00 00"
MINIMAP_INDEX = {  # n° de renvoi de la mini-carte : portail
    1: "t111_crash_cove", 2: "t113_mystery_caves", 3: "t112_roos_tubes", 4: "t114_sewer_speedway",
    5: "a115_skull_rock", 8: "t122_turbo_track", 9: "t121_slide_coliseum", 10: "cup_blue", 11: "cup_red",
    12: "cup_yellow", 13: "cup_purple", 14: "cup_green", 17: "t134_dingo_canyon", 18: "t131_coco_park",
    19: "t133_papus_pyramid", 20: "t132_tiger_temple", 21: "a135_rampage_ruins", 23: "t141_blizzard_bluff",
    25: "t142_dragon_mines", 26: "t143_polar_pass", 27: "a145_rocky_road", 28: "t144_tiny_arena",
    31: "t152_cortex_castle", 32: "t153_hot_air_skyway", 33: "t151_ngin_labs", 34: "a155_nitro_court",
    35: "t154_oxide_station",
}
SPOTS = {  # emplacement : position de HubZone, Teleporter, SpawnPoint (3 flottants), cap de HubZone, de Teleporter
    "t111_crash_cove": ("388efcc6141013450000a743", "3882fcc6232b13454e577f42", "e176f2c6a4381345d6e51439",
                        "", ""),
    "t112_roos_tubes": ("4d7719c7144d4e4600c03044", "4d7719c7144d4e4600c03044", "2ce813c7a42b4a460b9ecb43",
                        "efed1cbe", "efed1cbe"),
    "t113_mystery_caves": ("cd2ec5c6cdf27a4600805b44", "cd2ec5c6cdf27a4600805b44", "b87bc6c60a436946f98b0e44",
                           "efed1cbe", "efed1cbe"),
    "t114_sewer_speedway": ("488c57c6db24994500402044", "488c57c6db24994500402044", "0af76ec648449a457dae9f43",
                            "efed1cbe", "efed1cbe"),
    "a115_skull_rock": ("8a81d9c6891376450080d443", "8a81d9c6891376450080d443", "0fc9e2c62570704575490841",
                        "", ""),
    "t121_slide_coliseum": ("80dc85c63de52dc60000a543", "80dc85c63de52dc60000a543", "24ae84c6779a1bc66bd46a41",
                            "47e4bd3f", "47e4bd3f"),
    "t122_turbo_track": ("7bfa6fc6f64f2fc60000a543", "7bfa6fc6f64f2fc60000a543", "529f6ec6ae4f1cc6d2d88041",
                         "47e4bd3f", "47e4bd3f"),
    "t131_coco_park": ("e19287c433ba3cc60000ba44", "e19287c433ba3cc60000ba44", "e9d4e341c3d749c668259144",
                       "b5611cbf", "b5611cbf"),
    "t132_tiger_temple": ("9a2c344633c1f2c60000b944", "9a2c344633c1f2c60000b944", "e13f34466c3dfdc631009144",
                          "e00fc9bf", "e00fc9bf"),
    "t133_papus_pyramid": ("c2ad10463dca3bc600a02445", "c2ad10463dca3bc600a02445", "8a840f4648e34fc6cb791045",
                           "693bd4bf", "693bd4bf"),
    "t134_dingo_canyon": ("57db0f467b73c6c600002545", "57db0f467b73c6c600002545", "e1311f46330ac0c600781045",
                          "bcb8323f", "bcb8323f"),
    "a135_rampage_ruins": ("6603914633ebbcc600c02445", "6603914633ebbcc600c02445", "a49987462434bdc6e97c1045",
                           "", ""),
    "t141_blizzard_bluff": ("a4b73a460432f5c50080bc44", "a4b73a460432f5c50080bc44", "7b684f4675d20bc614f69044",
                            "b2611cbf", "b3611cbf"),
    "t142_dragon_mines": ("f62da7466ddcd7c50040ba44", "f62da7466ddcd7c50040ba44", "c8009c466d19d1c5b0be9044",
                          "50e43d40", "50e43d40"),
    "t143_polar_pass": ("b23a86c5145fec4500009c42", "b23a86c5145fec4500009c42", "2b3b2cc5d14bf9452ed89bc3",
                        "920a063f", "920a063f"),
    "t144_tiny_arena": ("b338a0468f25904571d59b44", "b338a0468f25904571d59b44", "ec71994635aa55458cb23c44",
                        "aa611cc0", "aa611cc0"),
    "a145_rocky_road": ("fa8f0846a8864c4300009443", "fa8f0846a8864c4300009443", "08ca0946faa6ad44c0fb0541",
                        "0abef5bf", "0abef5bf"),
    "t151_ngin_labs": ("7f1dad459226174700804ec4", "7f1dad459226174700804ec4", "1d8fac45acc3104764ab8fc4",
                       "1e3611c0", "1e3611c0"),
    "t152_cortex_castle": ("98da7fc5cf29014700e0d3c4", "98da7fc5cf29014700e0d3c4", "85b528c5ca540147d315fbc4",
                           "960a863f", "960a863f"),
    "t153_hot_air_skyway": ("335083c58d86034700e0b844", "335083c58d86034700e0b844", "e3e323c512640347b6339144",
                            "c1b8b2bd", "c1b8b2bd"),
    "t154_oxide_station": ("a45177468a92034700401944", "a45177468a92034700401944", "8f245e46e15b0347ddb59343",
                           "d90f49c0", "d90f49c0"),
    "a155_nitro_court": ("7b07234603510c4700801344", "7b07234603510c4700801344", "b8b22246fd2c074788959343",
                         "d80fc93f", "d80fc93f"),
    "cup_red": ("149775c60a2dfdc600c0b044", "149775c60a2dfdc600c0b044", "a4ba81c6bdb1f6c600108644",
                "b8b048bf", "b8b048bf"),
    "cup_blue": ("574e95c640de09c700c0b044", "574e95c640de09c700c0b044", "e65995c61cd304c7b8ca8644",
                 "bbb4bdbf", "bbb4bdbf"),
    "cup_green": ("a97388c6b1f703c700c0b044", "a97388c6b1f703c700c0b044", "52e08cc65763ffc60adf8644",
                  "92b382bf", "92b382bf"),
    "cup_yellow": ("2e2fa3c61ff304c700c0b044", "2e2fa3c61ff304c700c0b044", "c80f9ec60d8600c700108644",
                   "c7f205c0", "c7f205c0"),
    "cup_purple": ("bd15b1c6a91800c700c0b044", "bd15b1c6a91800c700c0b044", "8fbfa9c63836f9c6a0da8644",
                   "6d7527c0", "6d7527c0"),
}
WARPS = {  # emplacement : position du socle (X_warp, 3 flottants), son cap
    "t111_crash_cove": ("f19bfcc606ad154506f2e742", "f563ffbe"),
    "t112_roos_tubes": ("ca7119c7cd094e46a47ff643", "55f83440"),
    "t113_mystery_caves": ("001cc5c6522d7b46a71d2544", "00000000"),
    "t114_sewer_speedway": ("852857c6377098457cb2d643", "664e2fc0"),
    "a115_skull_rock": ("245cd9c69cf0764539f45943", "f563ffbe"),
    "t121_slide_coliseum": ("9f0f86c6e1482ec64e31ea42", "0b983440"),
    "t122_turbo_track": ("33c46fc6c3b12fc6edbeec42", "0b983440"),
    "t131_coco_park": ("d7ab87c4a44e3dc677729f44", "0b983440"),
    "t132_tiger_temple": ("b830344624e8f2c6faae9e44", "0b983440"),
    "t133_papus_pyramid": ("ee9f104633623cc656661745", "66134740"),
    "t134_dingo_canyon": ("fdbc0f468071c6c6e3ab1745", "0b983440"),
    "a135_rampage_ruins": ("a4119146141fbdc63b6f1745", "0b983440"),
    "t141_blizzard_bluff": ("d79c3a465e18f6c5c50ca244", "0b983440"),
    "t142_dragon_mines": ("e62ca746a074d7c591f19e44", "00000000"),
    "t143_polar_pass": ("68c685c52934ec4556de10c3", "29c409bf"),
    "t144_tiny_arena": ("9a3ea046cb448f456c995b44", "07433740"),
    "a145_rocky_road": ("8d6e084668d23d439f8bc142", "0b983440"),
    "t151_ngin_labs": ("2902ad456e0c174779ad80c4", "0b983440"),
    "t152_cortex_castle": ("173e80c5a42a01470e69edc4", "0b983440"),
    "t153_hot_air_skyway": ("b24883c5df620347624c9f44", "0b983440"),
    "t154_oxide_station": ("ec3c77463d790347c887cc43", "0b983440"),
    "a155_nitro_court": ("1feb224685490c47d04cc143", "0b983440"),
    "cup_red": ("ecc475c6f675fdc69ce09444", "0b983440"),
    "cup_blue": ("cd6f95c6a6e109c771f59444", "0b983440"),
    "cup_green": ("9f7888c66e1404c768399544", "0b983440"),
    "cup_yellow": ("b85ca3c65a0905c706599544", "0b983440"),
    "cup_purple": ("f1f3b0c6572200c74c0b9544", "0b983440"),
}
SIG_EMPTY = " ".join(["00"] * 16)


def zone(level_id):
    return f"octane/{level_id}/{level_id}"


def swaps(plan):
    """[(zone d'origine, remplaçant)] des portails qui changent, dans l'ordre des portails."""
    pairs = []
    for kind in ("race_pads", "crystal_pads"):
        pairs += [(pad, level) for pad, level in plan[kind].items() if pad != level]
    return pairs


def table(pairs):
    out = b""
    for source, target in pairs:
        a, b = zone(source).encode(), zone(target).encode()
        if len(a) >= NAME or len(b) >= NAME:
            raise ValueError(f"nom de zone trop long : {source} / {target}")
        out += a.ljust(NAME, b"\0") + b.ljust(NAME, b"\0")
    out += b"\0" * RECORD  # entrée vide = fin de table
    if TABLE + len(out) > CAVE_END:
        raise ValueError(f"{len(pairs)} remplacements : la table dépasse la place libre")
    return out


def hub_map(pairs):
    """Option « noms » : pour chaque n° de portail du hub, le n° (à partir de 1) de l'entrée de la table dont il
    est le portail d'origine, 0 sinon. Le nom affiché par un portail ne vient pas toujours de la fiche de son
    circuit (« Labo de N.Gin » / « Labo N.Gin ») : les détours reconnaissent donc le portail à son numéro."""
    out = bytearray(HUBMAP_SIZE)
    for i, (source, _) in enumerate(pairs):
        hub = HUB_INDEX.get(source)
        if hub is not None:
            out[hub] = i + 1
    return bytes(out)


def cond_table(conds):
    """CONDTABLE d'après les conditions de la graine (voir rewards.draw_conditions)."""
    out = bytearray(COND_ROW * 32)

    def put(hub, genre, first, second=("trophy", 0)):
        row = (genre, COND_TYPES[first[0]], first[1], COND_TYPES[second[0]], second[1])
        out[COND_ROW * hub:COND_ROW * hub + 20] = b"".join(int(v).to_bytes(4, "little", signed=True) for v in row)
    for zone, (first, second) in conds["pads"].items():
        put(HUB_INDEX[zone], COND_RACE, first, second)
    for zone, cond in conds["special"].items():
        put(HUB_INDEX[zone], COND_RACE, cond, cond)
    for zone, trophies in conds["bosses"].items():
        put(BOSS_INDEX[zone], COND_BOSS, ("trophy", trophies))
    for zone, cond in conds["arenas"].items():
        put(HUB_INDEX[zone], COND_ARENA, cond)
    for color, cond in conds["cups"].items():
        put(CUP_PADS[color][0], COND_CUP, cond)
    return bytes(out)


def portal_index(key):
    """N° de portail du hub d'un portail déplaçable (clé de SPOTS)."""
    return CUP_PADS[key[4:]][0] if key.startswith("cup_") else HUB_INDEX[key]


def area_table(locations):
    """AREATABLE : pour chaque portail déplacé, le monde de son emplacement."""
    out = bytearray(32)
    for pad, spot in locations.items():
        if pad != spot:
            out[portal_index(pad)] = WORLDS[portal_index(spot)]
    return bytes(out)


def row_table(locations):
    """ROWTABLE : pour chaque endroit (n° de son portail d'origine), le n° du portail posé là (0xff = inchangé)."""
    out = bytearray(b"\xff" * 32)
    for pad, spot in locations.items():
        if pad != spot:
            out[portal_index(spot)] = portal_index(pad)
    return bytes(out)


def boss_req(conds=None):
    """BOSSREQ : trophées du garage de chaque monde (n° 1 plage, 3 ruines, 4 glacier, 5 Citadel), d'après les
    conditions de la graine, sinon ceux du jeu."""
    bosses = (conds or {}).get("bosses") or {"t112_roos_tubes": 4, "t133_papus_pyramid": 8, "t142_dragon_mines": 12,
                                             "t153_hot_air_skyway": 16}
    out = bytearray(32)
    for zone, trophies in bosses.items():
        out[4 * BOSS_AREA[zone]:4 * BOSS_AREA[zone] + 4] = trophies.to_bytes(4, "little")
    return bytes(out)


def spot_table():
    """SPOTTABLE : position de l'entité HubZone de chaque emplacement et son monde, par n° de portail."""
    keys = sorted(SPOTS, key=portal_index)
    return b"".join(bytes.fromhex(SPOTS[k][0]) + WORLDS[portal_index(k)].to_bytes(4, "little") for k in keys) + bytes(16)


def idx_table(locations):
    """IDXTABLE : monde de l'emplacement du portail de chaque n° de renvoi de la mini-carte (0 = pas un portail)."""
    out = bytearray(IDX_COUNT)
    for k, key in MINIMAP_INDEX.items():
        out[k] = WORLDS[portal_index(locations.get(key, key))]
    return bytes(out)


def pad_table(locations):
    """PADTABLE d'après les emplacements de la graine ({portail: emplacement}, clés de SPOTS)."""
    rows = b""
    for pad, spot in locations.items():
        if pad == spot:
            continue
        old, new = SPOTS[pad], SPOTS[spot]
        for i, field in enumerate(PAD_FIELDS):
            yaw = new[3 + i] if i < 2 else ""
            rows += (bytes.fromhex(old[i]) + bytes.fromhex(new[i]) + (bytes.fromhex(yaw) if yaw else bytes(4))
                     + field.to_bytes(4, "little"))
        rows += (bytes.fromhex(WARPS[pad][0]) + bytes.fromhex(WARPS[spot][0]) + bytes.fromhex(WARPS[spot][1])
                 + (0x20).to_bytes(4, "little"))  # le socle
    if len(rows) // 32 >= PADTABLE_ROWS:
        raise ValueError("trop de portails déplacés")
    return rows + bytes(32)


def cup_map(cups):
    """CUPMAP : pour les portails 25 à 29, 4 × (n° de coupe du jeu, place 0 à 3) ; 0xff = coupe d'origine.
    cups : {couleur: [[coupe, place]] × 4} (forme de la graine)."""
    out = bytearray(b"\xff" * 40)
    for color, levels in cups.items():
        if color not in CUP_PADS or len(levels) != 4:
            raise ValueError(f"coupe inconnue : {color}")
        at = (CUP_PADS[color][0] - 25) * 8
        for i, (cup, place) in enumerate(levels):
            if not (0 <= cup < len(CUPS) and 0 <= place < 4):
                raise ValueError(f"circuit de coupe inconnu : coupe {cup}, place {place}")
            out[at + 2 * i:at + 2 * i + 2] = bytes((cup, place))
    return bytes(out)


def reward_table(rows):
    """rows : [(zone, bits, position du compteur de l'objet tiré)] -> table de l'option « récompenses »."""
    out = b""
    for level_id, bits, counter in rows:
        name = zone(level_id).encode()
        if len(name) >= NAME:
            raise ValueError(f"nom de zone trop long : {level_id}")
        if bits not in VANILLA or counter not in ITEM_BIT:
            raise ValueError(f"récompense inconnue : bit {bits:#x}, compteur {counter:#x}")
        hub = CUP_INDEX[bits] if bits in CUP_INDEX else (BOSS_INDEX if bits == KEY else HUB_INDEX).get(level_id)
        if hub is None:
            raise ValueError(f"pas de portail connu pour {level_id} (bit {bits:#x})")
        out += name.ljust(NAME, b"\0") + b"".join(int(v).to_bytes(4, "little") for v in (
            bits, counter, VANILLA[bits], HIGHER.get(bits, 0), ITEM_BIT[counter], hub))
    out += b"\0" * REWARD_RECORD
    if REWARDS + len(out) > CODE3:
        raise ValueError(f"{len(rows)} récompenses : la table dépasse la place libre")
    return out


MAX_WRITE = 4096  # le port refuse une écriture plus longue (« bad patch entry »)


def _line(address, data, signature):
    """Une ou plusieurs lignes <Line> (au plus MAX_WRITE octets chacune ; seules les zones vides, de
    signature SIG_EMPTY, sont assez grandes pour être coupées)."""
    if len(data) > MAX_WRITE and signature != SIG_EMPTY:
        raise ValueError("seule une zone vide peut recevoir une écriture coupée en morceaux")
    return "".join(
        f'            <Line Type="bytes" Address="{address + at + EBOOT_BASE:#010x}" '
        f'Value="{data[at:at + MAX_WRITE].hex()}"\n'
        f'                  Signature="{signature}"/>\n'
        for at in range(0, len(data), MAX_WRITE))


def patch_xml(plan, rename=False, rewards=None):
    """Le fichier `Randomizer.xml` de cette graine, à poser dans le dossier `patches` du port.
    rename : au hub, chaque portail affiche le nom du niveau qu'il charge.
    rewards : [(zone, bits, position du compteur)] des récompenses mélangées (voir rewards.patch_rows)."""
    pairs = swaps(plan)
    targets = [t for _, t in pairs]
    if len(set(targets)) != len(targets):
        raise ValueError("un même niveau derrière deux portails : la récompense ne saurait pas "
                         "à quel portail aller (désactiver --doublons pour fabriquer le patch)")
    data = table(pairs)
    if TABLE + len(data) > REWARDS and rewards:
        raise ValueError(f"{len(pairs)} remplacements : la table touche celle des récompenses")
    if rename and (TABLE + len(data) > CODE3 or STATE + 16 + 24 * len(pairs) > INRECALC):
        raise ValueError(f"{len(pairs)} remplacements : trop pour l'option « noms »")
    lines = (_line(CODE1, CODE1_NOMS_BYTES if rename else CODE1_BYTES, SIG_EMPTY)
             + _line(CODE2, CODE2_BYTES, SIG_EMPTY)
             + _line(HUBSTR, HUB.encode() + b"\0", SIG_EMPTY)
             + (_line(HUBMAP, hub_map(pairs), SIG_EMPTY) if rename else "") + _line(TABLE, data, SIG_EMPTY)
             + (_line(CODE3, CODE3_BYTES, SIG_EMPTY) if rename else "") + _line(CODE4, CODE4_BYTES, SIG_EMPTY)
             + (_line(CODE5, CODE5_BYTES, SIG_EMPTY) + _line(CODE6, CODE6_BYTES, SIG_EMPTY) if rename else "")
             + _line(LOADMAP, JUMP_LOADMAP, SIG_LOADMAP) + _line(REWARD, JUMP_REWARD, SIG_REWARD)
             + _line(REWARDED, JUMP_REWARDED, SIG_REWARDED)
             + (_line(HUBNAME, JUMP_HUBNAME, SIG_HUBNAME) + _line(BANNER, JUMP_BANNER, SIG_BANNER)
                if rename else ""))
    if rewards:
        lines += (_line(REWARDS, reward_table(rewards), SIG_EMPTY) + _line(CODE7, CODE7_BYTES, SIG_EMPTY)
                  + _line(RECALC, JUMP_RECALC, SIG_RECALC))
        for func, _, jump, sig in REWARD_FUNCS:
            lines += _line(func, jump, sig)
        lines += _line(WON_CALL, CALL_WON, SIG_WON) + _line(MODEL_CALL, CALL_MODEL, SIG_MODEL)
        lines += _line(GETALL, JUMP_GETALL, SIG_GETALL)
        lines += (_line(KEYSPOT, KEYSPOT_BYTES, SIG_EMPTY) + _line(KEYSPOT2, KEYSPOT2_BYTES, SIG_EMPTY)
                  + _line(KEY_CALL, CALL_KEY, SIG_KEY) + _line(KEY_NAME, CALL_KEY_NAME, SIG_KEY_NAME))
    if plan.get("conditions"):
        lines += _line(CONDTABLE, cond_table(plan["conditions"]), SIG_EMPTY) + _line(CODE9, CODE9_BYTES, SIG_EMPTY)
        for func, _, jump, sig in COND_FUNCS:
            lines += _line(func, jump, sig)
    if plan.get("locations") and any(pad != spot for pad, spot in plan["locations"].items()):
        lines += (_line(CODE11, CODE11_BYTES, SIG_EMPTY) + _line(AREATABLE, area_table(plan["locations"]), SIG_EMPTY)
                  + _line(PADTABLE, pad_table(plan["locations"]), SIG_EMPTY) + _line(SPOTTABLE, spot_table(), SIG_EMPTY)
                  + _line(IDXTABLE, idx_table(plan["locations"]), SIG_EMPTY) + _line(MINIMAP, MINIMAP_BYTES, SIG_EMPTY)
                  + _line(IGZ_FINISH, JUMP_IGZ, SIG_IGZ)
                  + _line(ROWMAP, ROWMAP_BYTES, SIG_EMPTY) + _line(ROWTABLE, row_table(plan["locations"]), SIG_EMPTY)
                  + _line(ROWMASK, ROWMASK_BYTES, SIG_EMPTY)
                  + _line(ROW_CALL, CALL_ROW, SIG_ROW) + _line(ROW_MASK_AT, CALL_ROW_MASK, SIG_ROW_MASK))
    if rewards or (plan.get("locations") and any(pad != spot for pad, spot in plan["locations"].items())):
        lines += (_line(BOSSTALK, BOSSTALK_BYTES, SIG_EMPTY)
                  + _line(BOSSREQ, boss_req(plan.get("conditions")), SIG_EMPTY)
                  + _line(BOSS_SKIP, JUMP_BOSS_SKIP, SIG_BOSS_SKIP) + _line(BOSS_OK, CALL_BOSS_OK, SIG_BOSS_OK))
    if plan["settings"].get("skip_hints"):
        lines += _line(CODE10, CODE10_BYTES, SIG_EMPTY) + _line(PERCENT, JUMP_PERCENT, SIG_PERCENT)
    if plan["settings"].get("boost_reserve"):
        lines += (_line(RESERVE, RESERVE_BYTES, SIG_EMPTY) + _line(RESERVE_START, RESERVE_START_BYTES, SIG_EMPTY)
                  + _line(TIMING_START, TIMING_START_BYTES, SIG_EMPTY) + _line(RATIO_CALL, CALL_RATIO, SIG_RATIO)
                  + _line(STOP_DRIFT, CALL_STOP_DRIFT, SIG_STOP_DRIFT) + _line(STOP_START, CALL_STOP_START, SIG_STOP_START)
                  + _line(START_TIMING, CALL_START_TIMING, SIG_START_TIMING))
    if plan.get("cups"):
        lines += (_line(CUPMAP, cup_map(plan["cups"]), SIG_EMPTY) + _line(CODE8, CODE8_BYTES, SIG_EMPTY)
                  + _line(CUP_CALL, CALL_CUP, SIG_CUP))
    listing = "".join(f"     {s} -> {t}\n" for s, t in pairs)
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            f'<!-- CTR Nitro-Fueled Randomizer {plan["version"]}, graine {plan["seed"]}.\n'
            '     Remplace le niveau chargé derrière chaque portail et donne la récompense au portail.\n'
            f'{listing}-->\n'
            '<Patch>\n    <TitleID>\n        <ID>CUSA13795</ID>\n    </TitleID>\n'
            '    <Metadata Title="Crash Team Racing Nitro-Fueled" Name="Randomizer" Author="kyogre21"\n'
            f'              PatchVer="{plan["version"]}" AppVer="01.21" AppElf="eboot.bin" isEnabled="true">\n'
            '        <PatchList>\n' + lines + '        </PatchList>\n    </Metadata>\n</Patch>\n')


def signature_sites():
    """[(adresse, octets d'origine)] de toutes les écritures posées sur le code du jeu : le logiciel s'en sert pour
    vérifier que `eboot.elf` est bien la version attendue (CUSA13795 v1.21)."""
    sites = [(LOADMAP, SIG_LOADMAP), (REWARD, SIG_REWARD), (REWARDED, SIG_REWARDED), (HUBNAME, SIG_HUBNAME),
             (BANNER, SIG_BANNER), (RECALC, SIG_RECALC), (WON_CALL, SIG_WON), (MODEL_CALL, SIG_MODEL),
             (GETALL, SIG_GETALL), (CUP_CALL, SIG_CUP), (PERCENT, SIG_PERCENT),
             (IGZ_FINISH, SIG_IGZ), (ROW_CALL, SIG_ROW), (ROW_MASK_AT, SIG_ROW_MASK), (KEY_CALL, SIG_KEY),
             (KEY_NAME, SIG_KEY_NAME),
             (BOSS_SKIP, SIG_BOSS_SKIP), (BOSS_OK, SIG_BOSS_OK), (RATIO_CALL, SIG_RATIO), (STOP_DRIFT, SIG_STOP_DRIFT),
             (STOP_START, SIG_STOP_START), (START_TIMING, SIG_START_TIMING)]
    sites += [(func, sig) for func, _, _, sig in REWARD_FUNCS + COND_FUNCS]
    return [(address, bytes.fromhex(sig.replace(" ", ""))) for address, sig in sites]
