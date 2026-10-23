"""Confort « Recommencer / Continuer » : à la fin de chaque course relique, gagnée ou perdue, le menu propose
Recommencer (en haut) et Continuer (en dessous). Le jeu n'offrait que Continuer après une relique gagnée.

Trois fichiers du jeu sont modifiés (validé en jeu le 23/10/2026) et livrés dans `update5.pak` :
- `Octane_EndRaceMenu_Root` (update.pak) : après le test « en ligne ? », un test « course relique ? » (mode 3) montre
  le groupe Continuer et le groupe Recommencer / Quitter avec Quitter caché, joue l'animation CupButtons (Continuer
  passe sous Recommencer), relie Recommencer et Continuer pour la navigation, et met le focus sur Continuer si une
  relique vient d'être gagnée, sinon sur Recommencer. La fin est celle du menu à 2 boutons.
- `ui/Octane_EndRaceMenu` (update2.pak) : Continuer reçoit la table d'animations de Quitter (CupButtons -> sa place).
- `Octane_EndRaceMenu_Continue` (update.pak) : en course relique, Continuer passe par le test des coupes (podium et
  retour « victoire » seulement si une relique a été gagnée, sinon simple retour au hub : pas de podium fantôme).

Les positions plus bas sont celles des fichiers du jeu v1.21, vérifiés par leur empreinte avant toute modification."""
import hashlib

from .i18n import tr

RELIC_RACE = 3  # eOctaneRaceMode

ROOT = "vsc/UI/Octane_EndRaceMenu/Octane_EndRaceMenu_Root.igz"
CONTINUE = "vsc/UI/Octane_EndRaceMenu/Octane_EndRaceMenu_Continue.igz"
MENU = "ui/Octane_EndRaceMenu.igz"
SOURCES = {ROOT: "update.pak", CONTINUE: "update.pak", MENU: "update2.pak"}

# Root
IF_ONLINE = 0x2f18         # TestBool « mode de jeu == en ligne » ; FAUX (+0x20) -> GOALS
GOALS = 0x3420             # getRaceGoalsCompleted -> menu d'origine
GET_RACE_MODE = 0x3490     # getRaceMode
CMP_CUP = 0x10a0           # Compare(mode == 6)
TEST_CUP = 0x1170
SHOW_BUTTONS001 = 0x12e8   # showPlaceable(Null_Asset_Buttons001 : Continuer seul)
HIDE_BUTTONS = 0x13c8      # hidePlaceable(Null_Asset_Buttons : Recommencer / Quitter)
FOCUS_CONTINUE = 0x1668    # setFocus(Continuer)
FOCUS_RESTART = 0x2d60     # setFocus(Recommencer) -> TWO_BUTTONS_END
TWO_BUTTONS_END = 0x2ac0   # fin du menu à 2 boutons
CUP_ANIM = 0x1930          # playAnimation(self, AnimationTag_CupButtons)
SEND_NAV = 0x1a28          # CGuiEventNavigationItemUpdateNavigation (sens par défaut)
SEND_NAV_DIR = 0x1c08      # idem, sens 1
ICON008 = 0x1a80           # accesseur de Quitter
SELF = 0x1078              # accesseur du placeable du script
DIR1 = 0x1d38              # constante 1
# ui/Octane_EndRaceMenu
CONTINUE_BTN = 0x1160      # Comp__Menu_ButtonWithIcon002 (Continuer)
QUIT_BTN = 0xa10           # Comp__Menu_ButtonWithIcon008 (Quitter)
ANIM_TABLE = 0xf0          # igGuiPlaceable : table d'animations
# Continue
SWITCH = 0x4740            # aiguillage sur le mode de course
PODIUM = 0x1918            # podium (cas 3, 5, 8, 1)
CUP_GOALS = 0x3dd8         # getRaceGoalsCompleted -> podium ou returnToHUB (cas des coupes en Aventure)
CUP_TEST = 0x3e20

SHA256 = {ROOT: "719bef8d92d78a949951354324c3d935627d0ad6a3ded530ce4b91466c207bd1",  # fichiers d'origine (jeu v1.21)
          CONTINUE: "5d37c8262be27d10a19d52438e90752f3187e6d3524cf24c4cd8484c8c827b27",
          MENU: "7e378ecaaea31ee78c1e0e2623e157a1eec26ab50cb0005fc114478dd555bdec"}


def _check(cond, what):
    if not cond:
        raise ValueError(tr("{file} : version du jeu inattendue (il faut CUSA13795 v1.21)", file=what))


class _Graph:
    """Ajout de nœuds de script copiés sur des nœuds existants."""

    def __init__(self, z):
        self.z = z
        self.known = set(z.objects)  # objets d'origine (compteur de références augmenté quand on les relie)

    def link(self, at, target):
        if target is None:
            self.z.set_u64(at, 0)
        else:
            self.z.set_ptr(at, target)
            if target in self.known:
                self.z.add_ref(target)

    def args(self, node):
        z = self.z
        return [z.ptr(z.ptr(node + 0x20) + 8 * i) for i in range(z.u64(node + 0x10))]

    def action(self, template, args, nxt):
        """Copie d'un appel de fonction (même fonction), avec d'autres arguments et une autre suite."""
        z = self.z
        at = z.new_object(template, 0x40, 8 * len(args))
        z.set_u64(at + 0x10, len(args))
        z.set_u64(at + 0x18, 0x0110000000000000 | 8 * len(args))
        z.set_ptr(at + 0x20, at + 0x40)
        for i, a in enumerate(args):
            self.link(at + 0x40 + 8 * i, a)
        self.link(at + 0x28, nxt)
        z.set_u64(at + 0x30, 0)
        z.add_fixup("RNEX", at + 0x38)
        return at

    def send(self, template, target, args, nxt):
        """Copie d'un envoi d'événement (même événement, mêmes champs) vers une autre cible."""
        z = self.z
        at = z.new_object(template, 0x58)
        lst = z.new_object(z.ptr(template + 0x20), 0x28, 8 * len(args))
        z.set_ptr(lst + 0x20, lst + 0x28)
        for i, a in enumerate(args):
            self.link(lst + 0x28 + 8 * i, a)
        fields = z.ptr(template + 0x38)
        blk = z.copy(fields, 0x18)
        rnex = set(z.fixups("RNEX"))
        for i in range(3):
            if fields + 8 * i in rnex:
                z.add_fixup("RNEX", blk + 8 * i)
        z.add_fixup("RNEX", at + 0x10)
        self.link(at + 0x18, target)
        z.set_ptr(at + 0x20, lst)
        z.set_ptr(at + 0x38, blk)
        self.link(at + 0x48, nxt)
        return at


def patch_root(data):
    from .igz import Igz
    z = Igz(data)
    g = _Graph(z)
    _check(z.kind(IF_ONLINE) == "igVscTestBoolNode" and z.ptr(IF_ONLINE + 0x20) == GOALS, ROOT)
    _check(z.ptr(GET_RACE_MODE + 0x28) == CMP_CUP and z.ptr(CMP_CUP + 0x28) == TEST_CUP, ROOT)
    _check(z.ptr(SEND_NAV + 0x18) == ICON008 and z.ptr(FOCUS_RESTART + 0x28) == TWO_BUTTONS_END, ROOT)
    race_acc, bool_acc = z.ptr(CMP_CUP + 0x10), z.ptr(CMP_CUP + 0x20)
    icon002, icon007 = g.args(FOCUS_CONTINUE)[0], g.args(FOCUS_RESTART)[0]
    goals_acc = g.args(GOALS)[0]

    # de la fin vers le début : chaque nœud connaît sa suite
    focus_continue = g.action(FOCUS_CONTINUE, [icon002, None], TWO_BUTTONS_END)
    test_goals = z.new_object(TEST_CUP, 0x28)
    g.link(test_goals + 0x10, goals_acc)
    g.link(test_goals + 0x18, focus_continue)
    g.link(test_goals + 0x20, FOCUS_RESTART)
    nav = g.action(GOALS, [goals_acc], test_goals)
    for target, item in ((icon007, icon002), (icon002, icon007)):
        nav = g.send(SEND_NAV_DIR, target, [SELF, DIR1, item], nav)
        nav = g.send(SEND_NAV, target, [SELF, None, item], nav)
    anim = g.action(CUP_ANIM, g.args(CUP_ANIM), nav)
    hide_quit = g.action(HIDE_BUTTONS, [ICON008], anim)
    show_pair = g.action(SHOW_BUTTONS001, g.args(HIDE_BUTTONS), hide_quit)
    show_continue = g.action(SHOW_BUTTONS001, g.args(SHOW_BUTTONS001), show_pair)
    relic = z.copy(z.ptr(CMP_CUP + 0x18), 0x18)  # constante « mode de course »
    z.add_fixup("RVTB", relic)
    z.set_u64(relic + 0x10, RELIC_RACE)
    test = z.new_object(TEST_CUP, 0x28)
    g.link(test + 0x10, bool_acc)
    g.link(test + 0x18, show_continue)
    g.link(test + 0x20, GOALS)
    compare = z.new_object(CMP_CUP, 0x30)
    g.link(compare + 0x10, race_acc)
    z.set_ptr(compare + 0x18, relic)
    g.link(compare + 0x20, bool_acc)
    g.link(compare + 0x28, test)
    z.set_ptr(IF_ONLINE + 0x20, g.action(GET_RACE_MODE, [race_acc], compare))
    return z.build()


def patch_menu(data):
    from .igz import Igz
    z = Igz(data)
    table = z.ptr(QUIT_BTN + ANIM_TABLE)
    _check(z.kind(CONTINUE_BTN) == "igGuiPlaceable" and z.u64(CONTINUE_BTN + ANIM_TABLE) == 0, MENU)
    _check(table is not None and z.kind(table) == "igGuiAnimationTable", MENU)
    z.set_ptr(CONTINUE_BTN + ANIM_TABLE, table)
    z.add_ref(table)
    return z.build()


def patch_continue(data):
    from .igz import Igz
    z = Igz(data)
    table = z.ptr(SWITCH + 0x18)
    values, keys = z.ptr(table + 0x18), z.ptr(table + 0x28)
    slots = [i for i in range((z.u64(table + 0x10) & 0xFFFFFF) // 8) if z.u32(keys + 4 * i) == RELIC_RACE]
    _check(len(slots) == 1 and z.ptr(values + 8 * slots[0]) == PODIUM, CONTINUE)
    _check(z.ptr(CUP_GOALS + 0x28) == CUP_TEST and z.ptr(CUP_TEST + 0x18) == PODIUM, CONTINUE)
    z.set_ptr(values + 8 * slots[0], CUP_GOALS)
    z.add_ref(CUP_GOALS)
    return z.build()


PATCHES = {ROOT: patch_root, CONTINUE: patch_continue, MENU: patch_menu}


def build(read):
    """{nom: contenu modifié} des 3 fichiers ; `read(archive, nom)` lit un fichier d'une archive du jeu."""
    out = {}
    for name, pak in SOURCES.items():
        data = read(pak, name)
        if hashlib.sha256(data).hexdigest() != SHA256[name]:
            raise ValueError(tr("{file} : version du jeu inattendue (il faut CUSA13795 v1.21)", file=name))
        out[name] = PATCHES[name](data)
    return out
