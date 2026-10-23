"""Langue de l'interface du randomizer (réglée par le CTRNF Mod Kit ; le logiciel autonome reste en français).
Les textes restent écrits en français dans le code ; tr() rend leur traduction anglaise (lang_en.py)."""

current = "fr"


def set_language(code):
    global current
    current = code if code in ("fr", "en") else "fr"


def tr(text, **values):
    """`text` dans la langue choisie ; les {champs} sont remplis avec `values`."""
    if current == "en":
        try:
            from .lang_en import EN
        except ImportError:  # traduction absente : on reste en français plutôt que de bloquer la fenêtre
            EN = {}
        text = EN.get(text, text)
    return text.format(**values) if values else text
