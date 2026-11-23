"""Langue de l'interface des autocollants (réglée par le CTRNF Mod Kit ; le logiciel autonome reste en français).
Les textes restent écrits en français dans le code ; tr() rend leur traduction anglaise (lang_en.py) ou espagnole (lang_es.py)."""

current = "fr"


def set_language(code):
    global current
    current = code if code in ("fr", "en", "es") else "fr"


def tr(text, **values):
    """`text` dans la langue choisie ; les {champs} sont remplis avec `values`."""
    table = {}
    try:  # traduction absente : on reste en français plutôt que de bloquer la fenêtre
        if current == "en":
            from .lang_en import EN as table
        elif current == "es":
            from .lang_es import ES as table
    except ImportError:
        table = {}
    text = table.get(text, text)
    return text.format(**values) if values else text
