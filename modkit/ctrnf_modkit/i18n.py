"""Langue de l'interface. Les textes restent écrits en français dans le code ; tr() rend leur traduction anglaise
(lang_en.py) ou espagnole (lang_es.py, demandée sur GitHub le 23/10/2026) quand cette langue est choisie. Le kit règle
aussi la langue des onglets du randomizer et des autocollants, qui ont leur propre tr()."""

LANGUAGES = {"fr": "Français", "en": "English", "es": "Español"}
current = "fr"


def set_language(code):
    global current
    current = code if code in LANGUAGES else "fr"
    try:
        from ctrnf_rando import i18n as rando
        rando.set_language(current)
    except ImportError:
        pass
    try:
        from ctrnf_stickers import i18n as stickers
        stickers.set_language(current)
    except ImportError:
        pass


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
