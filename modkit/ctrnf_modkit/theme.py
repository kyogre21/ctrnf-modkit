"""Apparence du kit : thème Sun Valley (sv-ttk, style Windows 11) s'il est installé, sinon le thème Windows de ttk ;
couleurs et styles communs."""
import tkinter as tk
from tkinter import font, ttk

DARK = "#1c2230"     # bandeau du haut
ACCENT = "#ff7a00"   # orange CTR
MUTED = "#5f6b7a"
OK = "#1a7f37"
BAD = "#c62828"
ALPHA_BG = "#fff4e0"
ALPHA_FG = "#a15c00"


def apply(root):
    """Applique le thème ; rend True si sv-ttk est utilisé."""
    style = ttk.Style(root)
    try:
        import sv_ttk
        sv_ttk.set_theme("light", root)
        modern = True
    except Exception:  # sv-ttk absent (code source sans la dépendance) : thème Windows, sinon « clam »
        modern = False
        style.theme_use("vista" if "vista" in style.theme_names() else "clam")
    base = font.nametofont("TkDefaultFont").actual("family")
    style.configure("Muted.TLabel", foreground=MUTED)
    style.configure("Ok.TLabel", foreground=OK)
    style.configure("Bad.TLabel", foreground=BAD)
    style.configure("Section.TLabel", font=(base, 11, "bold"))
    style.configure("Name.TLabel", font=(base, 10, "bold"))
    style.configure("Alpha.TLabel", background=ALPHA_BG, foreground=ALPHA_FG, font=(base, 8, "bold"), padding=(6, 1))
    style.configure("Big.TButton", font=(base, 11, "bold"), padding=(18, 8))
    style.configure("Big.Accent.TButton", font=(base, 11, "bold"), padding=(18, 8))
    return modern


def launch_style(modern):
    return "Big.Accent.TButton" if modern else "Big.TButton"


def header(parent, title, subtitle, link_text, on_link):
    """Bandeau sombre du haut : nom, sous-titre et lien."""
    bar = tk.Frame(parent, background=DARK, padx=18, pady=12)
    base = font.nametofont("TkDefaultFont").actual("family")
    left = tk.Frame(bar, background=DARK)
    left.pack(side="left")
    tk.Label(left, text=title, background=DARK, foreground="white", font=(base, 18, "bold")).pack(anchor="w")
    tk.Label(left, text=subtitle, background=DARK, foreground="#b8c0cc", font=(base, 9)).pack(anchor="w")
    link = tk.Label(bar, text=link_text, background=DARK, foreground=ACCENT, cursor="hand2", font=(base, 9, "underline"))
    link.pack(side="right", anchor="s")
    link.bind("<Button-1>", lambda _: on_link())
    return bar


def alpha_banner(parent, text):
    """Encadré « version alpha »."""
    box = tk.Frame(parent, background=ALPHA_BG, padx=12, pady=8, highlightthickness=1, highlightbackground="#f0c27a")
    base = font.nametofont("TkDefaultFont").actual("family")
    tk.Label(box, text="ALPHA", background=ACCENT, foreground="white", font=(base, 8, "bold"), padx=6).pack(
        side="left", anchor="n")
    tk.Label(box, text=text, background=ALPHA_BG, foreground=ALPHA_FG, justify="left", wraplength=780,
             font=(base, 9)).pack(side="left", padx=(10, 0))
    return box
