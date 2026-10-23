"""Langue de l'interface. Les textes restent écrits en français dans le code ; tr() rend leur traduction anglaise
(lang_en.py) quand l'anglais est choisi. Le kit règle aussi la langue des onglets du randomizer et des autocollants,
qui ont leur propre tr()."""

LANGUAGES = {"fr": "Français", "en": "English"}
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
    if current == "en":
        try:
            from .lang_en import EN
        except ImportError:  # traduction absente : on reste en français plutôt que de bloquer la fenêtre
            EN = {}
        text = EN.get(text, text)
    return text.format(**values) if values else text
