"""Traduction anglaise : aucun texte oublié, mêmes {champs} qu'en français, et la liste déroulante du kit refait la
fenêtre dans l'autre langue sans la fermer."""
import ast
from pathlib import Path
import string
import tempfile
import unittest

from tests.fake import make_port
from ctrnf_modkit import config, i18n
from ctrnf_modkit.modules import REGISTRY

REPO = Path(__file__).resolve().parents[2]
PACKAGES = {"ctrnf_modkit": REPO / "modkit" / "ctrnf_modkit", "ctrnf_rando": REPO / "randomizer" / "ctrnf_rando",
            "ctrnf_stickers": REPO / "autocollants" / "ctrnf_stickers"}
TABLES = {"HELP", "PRESETS", "BOXES", "STEPS", "SETTINGS", "LIMITS", "MODES", "EXIT_CODES", "IMAGES"}
# textes passés à tr() par une variable (ni littéral, ni tableau ci-dessus)
EXTRA = {
    "ctrnf_modkit": ["Randomizer", "Autocollants", "Autosplitter", "Confort", "posé par le mod", "absent",
                     "étranger (non touché)", "posée", "retirée", "bouche-trou posé", "bouche-trou retiré",
                     "patch de la graine", "mini-carte des reliques", "podiums rapides", "autocollants remplacés",
                     "script LiveSplit", "options de confort", "Recommencer / Continuer des reliques", "Dans LiveSplit", "Réglages du script",
                     "Limites de cette version",
                     "Réglages faits par une version plus récente du kit : ils ne seront pas modifiés."],
    "ctrnf_rando": ["Circuits", "Récompenses", "Coupes", "Conditions", "Portails", "Confort", "Classique", "Chaos",
                    "Découverte", "posée", "retirée", "bouche-trou posé", "bouche-trou retiré"],
    "ctrnf_stickers": ["Dans le jeu", "D'origine", "Icône du menu", "Images", "Tous les fichiers"],
}


def _texts(node):
    return [n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _shown(s):
    return any(c.isalpha() for c in s) and (" " in s or "{" in s or any(ord(c) > 127 for c in s) or s[:1].isupper())


def keys(folder):
    """Textes à traduire : littéraux de tr(...) et chaînes des tableaux de textes affichés."""
    out = set()
    for path in folder.glob("*.py"):
        if path.name in ("lang_en.py", "i18n.py"):
            continue
        for n in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(n, ast.Call) and n.args and getattr(n.func, "id", getattr(n.func, "attr", "")) == "tr":
                out.update(s for s in _texts(n.args[0]) if _shown(s))
            if isinstance(n, ast.Assign) and any(getattr(t, "id", "") in TABLES for t in n.targets):
                out.update(s for s in _texts(n.value) if _shown(s) and not s.startswith("*."))
            if isinstance(n, ast.Call) and getattr(n.func, "attr", "") in ("page", "choices"):
                for a in n.args[1:]:
                    out.update(s for s in _texts(a) if _shown(s) and " " in s)
    return out


def fields(text):
    return sorted(f for _, f, _, _ in string.Formatter().parse(text) if f)


class TranslationTest(unittest.TestCase):
    def test_nothing_missing(self):
        import importlib
        for package, folder in PACKAGES.items():
            en = importlib.import_module(f"{package}.lang_en").EN
            wanted = keys(folder) | set(EXTRA[package])
            missing = sorted(wanted - en.keys())
            self.assertEqual(missing, [], package)
            for fr, english in en.items():
                self.assertEqual(fields(fr), fields(english), f"{package} : {fr!r}")

    def test_modules_and_tables(self):
        from ctrnf_modkit import launch
        from ctrnf_modkit.lang_en import EN
        for m in REGISTRY:
            self.assertIn(m.name, EN)
            self.assertIn(m.description, EN)
        for text in list(launch.MODES.values()) + list(launch.EXIT_CODES.values()):
            self.assertIn(text, EN)

    def test_tr(self):
        from ctrnf_rando import i18n as rando
        from ctrnf_stickers import i18n as stickers
        try:
            i18n.set_language("en")
            self.assertEqual((rando.current, stickers.current), ("en", "en"))  # le kit règle les onglets des mods
            self.assertEqual(i18n.tr("{n} Ko", n=3), "3 KB")
            self.assertEqual(i18n.tr("texte inconnu"), "texte inconnu")    # pas traduit : reste tel quel
            i18n.set_language("xx")
            self.assertEqual(i18n.current, "fr")
            self.assertEqual(i18n.tr("{n} Ko", n=3), "3 Ko")
        finally:
            i18n.set_language("fr")

    def test_dropdown(self):
        try:
            import tkinter as tk
            root = tk.Tk()
        except Exception as error:
            self.skipTest(f"pas de fenêtre possible : {error}")
        tmp = tempfile.TemporaryDirectory()
        try:
            from ctrnf_modkit import window
            folder, _ = make_port(Path(tmp.name))
            conf = config.Config(Path(tmp.name) / "kit.json")
            conf.data["port"] = str(folder)
            conf.data["language"] = "fr"
            win = window.KitWindow(root, conf)
            for language, home, title in (("English", "Home", "by kyogre21"), ("Français", "Accueil", "par kyogre21")):
                win.language.set(language)
                win.change_language()
                root.update()
                kits = [c for c in root.winfo_children() if isinstance(c, window.KitWindow)]
                self.assertEqual(len(kits), 1)                      # une seule fenêtre, refaite
                win = kits[0]
                self.assertTrue(root.winfo_exists())
                self.assertIn(title, root.title())
                self.assertEqual(win.notebook.tab(0, "text"), home)
                for m in REGISTRY:                                   # chaque onglet se construit sans erreur
                    win.notebook.select(win.tabs[m.id])
                    win.build_current()
                    children = win.tabs[m.id].winfo_children()
                    self.assertNotIsInstance(children[0], tk.ttk.Label, f"{language} {m.id}")
                self.assertEqual(config.Config(Path(tmp.name) / "kit.json").data["language"],
                                 "en" if language == "English" else "fr")
        finally:
            i18n.set_language("fr")
            root.destroy()
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
