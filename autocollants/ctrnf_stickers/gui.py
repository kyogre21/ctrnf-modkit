"""Petit logiciel des autocollants : choisir le dossier du jeu, choisir un autocollant, le remplacer par une image.
Lancement : python -m ctrnf_stickers"""
from pathlib import Path
import struct
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from . import __version__, core
from .i18n import tr

TITLE = f'CTR Nitro-Fueled Autocollants {__version__}'
PREVIEW = 200  # côté des aperçus, en pixels
ICON_PREVIEW = 110
IMAGES = [('Images', '*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tga'), ('Tous les fichiers', '*.*')]  # traduits à l'usage


def checker(w, h, step=8):
    """Damier gris clair, pour voir la transparence."""
    img = Image.new('RGBA', (w, h), (255, 255, 255, 255))
    dark = Image.new('RGBA', (step, step), (204, 204, 204, 255))
    for y in range(0, h, step):
        for x in range((y // step) % 2 * step, w, 2 * step):
            img.paste(dark, (x, y))
    return img


class App(ttk.Frame):
    def __init__(self, root, context=None):
        """root : la fenêtre (logiciel autonome) ou, avec `context`, l'onglet du CTRNF Mod Kit qui la reçoit : le
        dossier (celui du port) et les réglages viennent alors du kit."""
        super().__init__(root, padding=10)
        self.root = root.winfo_toplevel()
        self.context = context
        if context is None:
            root.title(TITLE)
            root.minsize(900, 600)
            self.grid(sticky='nsew')
            root.columnconfigure(0, weight=1)
            root.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        conf = context.module_config() if context else core.load_config()
        self.game = None
        self.shown = []  # noms courts affichés dans la liste, dans l'ordre
        self.photos = {}  # garde les images des aperçus (sinon tkinter les perd)

        self.folder = context.port_var if context else tk.StringVar(value=conf.get('folder', ''))
        if context:
            context.on_port_change(self.load)
        self.kind = tk.StringVar(value='stickers')
        self.cutout = tk.BooleanVar(value=conf.get('cutout', False))
        self.with_icon = tk.BooleanVar(value=conf.get('icon', True))
        self.search = tk.StringVar()
        self.search.trace_add('write', lambda *_: self.fill())

        self.build_game().grid(row=0, column=0, columnspan=2, sticky='ew')
        self.build_list().grid(row=1, column=0, sticky='nsw', pady=(8, 0))
        self.build_view().grid(row=1, column=1, sticky='nsew', padx=(10, 0), pady=(8, 0))
        self.status = ttk.Label(self, text='', foreground='#555')
        self.status.grid(row=2, column=0, columnspan=2, sticky='w', pady=(8, 0))
        self.load()

    def build_game(self):
        box = ttk.LabelFrame(self, text=tr('Jeu'), padding=8)
        box.columnconfigure(0, weight=1)
        ttk.Entry(box, textvariable=self.folder, state='readonly' if self.context else 'normal').grid(
            row=0, column=0, sticky='ew')
        if not self.context:
            ttk.Button(box, text=tr('Parcourir…'), command=self.browse).grid(row=0, column=1, padx=(6, 0))
        self.game_label = ttk.Label(box, text='')
        self.game_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(4, 0))
        ttk.Label(box, text=tr("Dossier du port, choisi dans l'Accueil du kit.") if self.context else
                  tr('Le dossier du jeu (celui qui contient « archives »), ou le dossier du port.'),
                  foreground='#555').grid(row=2, column=0, columnspan=2, sticky='w')
        return box

    def build_list(self):
        box = ttk.Frame(self)
        box.rowconfigure(3, weight=1)
        ttk.Radiobutton(box, text=tr('Autocollants du kart'), value='stickers', variable=self.kind,
                        command=self.fill).grid(row=0, column=0, sticky='w')
        ttk.Radiobutton(box, text=tr('Icônes du menu'), value='icons', variable=self.kind,
                        command=self.fill).grid(row=1, column=0, sticky='w')
        ttk.Entry(box, textvariable=self.search).grid(row=2, column=0, columnspan=2, sticky='ew', pady=(6, 4))
        self.listbox = tk.Listbox(box, width=44, activestyle='none', exportselection=False)
        self.listbox.grid(row=3, column=0, sticky='ns')
        bar = ttk.Scrollbar(box, orient='vertical', command=self.listbox.yview)
        bar.grid(row=3, column=1, sticky='ns')
        self.listbox.configure(yscrollcommand=bar.set)
        self.listbox.bind('<<ListboxSelect>>', lambda _: self.show())
        ttk.Label(box, text=tr('● = remplacé'), foreground='#555').grid(row=4, column=0, sticky='w', pady=(4, 0))
        return box

    def build_view(self):
        box = ttk.LabelFrame(self, text=tr('Autocollant'), padding=8)
        self.name_label = ttk.Label(box, text=tr('Choisissez un autocollant dans la liste.'), font=('', 10, 'bold'))
        self.name_label.grid(row=0, column=0, columnspan=2, sticky='w')
        self.size_label = ttk.Label(box, text='', foreground='#555')
        self.size_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(0, 8))
        self.views = {}
        for col, (key, text, side) in enumerate((('current', 'Dans le jeu', PREVIEW), ('original', "D'origine", PREVIEW),
                                                 ('icon', 'Icône du menu', ICON_PREVIEW))):
            ttk.Label(box, text=tr(text)).grid(row=2, column=col, sticky='w')
            view = tk.Canvas(box, width=side, height=side, highlightthickness=1, highlightbackground='#999',
                             background='white')
            view.grid(row=3, column=col, sticky='nw', padx=(0, 10))
            self.views[key] = view
        buttons = ttk.Frame(box)
        buttons.grid(row=4, column=0, columnspan=3, sticky='w', pady=(10, 0))
        self.replace_button = ttk.Button(buttons, text=tr('Remplacer par une image…'), command=self.replace)
        self.replace_button.grid(row=0, column=0)
        self.restore_button = ttk.Button(buttons, text=tr("Remettre l'original"), command=self.restore)
        self.restore_button.grid(row=0, column=1, padx=(6, 0))
        self.export_button = ttk.Button(buttons, text=tr('Enregistrer en PNG…'), command=self.export)
        self.export_button.grid(row=0, column=2, padx=(6, 0))
        ttk.Checkbutton(box, text=tr("Détourer l'image (enlever le fond uni autour du dessin, puis recadrer)"),
                        variable=self.cutout, command=self.save).grid(row=5, column=0, columnspan=3, sticky='w',
                                                                      pady=(8, 0))
        ttk.Checkbutton(box, text=tr('Remplacer aussi son icône dans le menu de personnalisation'),
                        variable=self.with_icon, command=self.save).grid(row=6, column=0, columnspan=3, sticky='w')
        ttk.Label(box, text=tr("L'image est ajustée à la taille de l'autocollant sans être déformée ; la "
                               "transparence (PNG) est gardée. Les changements comptent au prochain lancement du jeu."),
                  foreground='#555', wraplength=540, justify='left').grid(row=7, column=0, columnspan=3, sticky='w',
                                                                          pady=(10, 0))
        ttk.Button(box, text=tr("Tout remettre d'origine"), command=self.restore_all).grid(
            row=8, column=0, columnspan=3, sticky='w', pady=(16, 0))
        self.set_buttons(None)
        return box

    # --- jeu ---

    def browse(self):
        if self.context:  # le dossier commun du kit est celui du port : il se change dans l'Accueil
            return
        folder = filedialog.askdirectory(title=tr('Dossier du jeu'), initialdir=self.folder.get() or None)
        if folder:
            self.folder.set(folder)
            self.load()

    def load(self):
        self.game = None
        text = self.folder.get().strip()
        if text:
            try:
                found = self.context.archives() if self.context else None
                self.game = core.Game(found or core.find_archives(text))
            except (ValueError, OSError, struct.error) as error:  # archive vide ou abîmée comprise
                self.game_label.configure(text=f'✗ {error}', foreground='#b00')
            else:
                self.game_label.configure(text=f'✓ {self.game.folder}', foreground='#070')
                self.save()
        else:
            self.game_label.configure(text=tr('Choisissez le dossier du jeu.'), foreground='#555')
        self.fill()

    # --- liste ---

    def fill(self):
        keep = self.selected()
        self.listbox.delete(0, 'end')
        self.shown = []
        if not self.game:
            self.show()
            return
        changed = self.game.changed()
        names = self.game.stickers() if self.kind.get() == 'stickers' else self.game.icons()
        want = self.search.get().strip().lower()
        for short in names:
            if want in short.lower():
                self.shown.append(short)
                self.listbox.insert('end', ('● ' if short in changed else '   ') + short)
        if keep in self.shown:
            i = self.shown.index(keep)
            self.listbox.selection_set(i)
            self.listbox.see(i)
        self.say(tr('{n} remplacé(s)', n=len(changed)) if changed else tr('Aucun autocollant remplacé.'))
        self.show()

    def selected(self):
        sel = self.listbox.curselection()
        return self.shown[sel[0]] if sel and sel[0] < len(self.shown) else None

    # --- aperçu ---

    def picture(self, key, img):
        view = self.views[key]
        view.delete('all')
        side = int(view['width'])
        if isinstance(img, str):
            view.create_text(side // 2 + 1, side // 2 + 1, text=img, fill='#777', width=side - 10, justify='center')
            return
        if img is None:
            return
        img = img.copy()
        img.thumbnail((side, side), Image.Resampling.LANCZOS)
        if img.width < side // 2:  # petites icônes : on agrandit, en gardant les pixels nets
            k = side // img.width
            img = img.resize((img.width * k, img.height * k), Image.Resampling.NEAREST)
        back = checker(img.width, img.height)
        back.alpha_composite(img)
        self.photos[key] = ImageTk.PhotoImage(back)
        view.create_image(side // 2 + 1, side // 2 + 1, image=self.photos[key])

    def show(self):
        short = self.selected()
        for key in self.views:
            self.picture(key, None)
        if not short:
            self.name_label.configure(text=tr('Choisissez un autocollant dans la liste.'))
            self.size_label.configure(text='')
            self.set_buttons(None)
            return
        self.name_label.configure(text=short)
        try:
            original = self.game.original(short)
            w, h, levels, *_ = core.texture.layout(original)
            ok = core.texture.supported(original)
            if ok:
                self.picture('original', core.texture.to_image(original))
                self.picture('current', core.texture.to_image(self.game.current(short)))
            ico = self.game.icon(short)
            if ico:
                self.picture('icon', core.texture.to_image(self.game.current(ico)))
            elif not short.startswith(core.ICON_TAG):
                self.picture('icon', tr("pas d'icône connue"))
        except (ValueError, OSError) as error:
            self.size_label.configure(text=tr('Illisible : {error}', error=error))
            self.set_buttons(None)
            return
        self.size_label.configure(text=tr('{w} × {h} pixels', w=w, h=h) + ('' if ok else tr(' — format non géré, pas modifiable')))
        self.set_buttons(short if ok else None)

    def set_buttons(self, short):
        changed = bool(short and self.game and {short, self.game.icon(short)} & self.game.changed())
        self.replace_button.configure(state='normal' if short else 'disabled')
        self.export_button.configure(state='normal' if short else 'disabled')
        self.restore_button.configure(state='normal' if changed else 'disabled')

    # --- actions ---

    def busy(self, on):
        self.root.config(cursor='watch' if on else '')
        self.root.update_idletasks()

    def warn_running(self):
        return not core.game_running() or messagebox.askokcancel(
            TITLE, tr("Le jeu est ouvert : le changement ne se verra qu'au prochain lancement. Continuer ?"))

    def replace(self):
        short = self.selected()
        if not short:
            return
        path = filedialog.askopenfilename(title=tr('Image pour {name}', name=short),
                                          filetypes=[(tr(label), pattern) for label, pattern in IMAGES])
        if not path or not self.warn_running():
            return
        self.busy(True)
        try:
            with Image.open(path) as img:
                self.game.replace(short, core.texture.cut_out(img) if self.cutout.get() else img,
                                  icon=self.with_icon.get())
        except (ValueError, OSError) as error:
            messagebox.showerror(TITLE, tr('Impossible de remplacer {name} : {error}', name=short, error=error))
            return
        finally:
            self.busy(False)
        self.fill()
        how = tr(' (détourée)') if self.cutout.get() else ''
        if self.with_icon.get() and self.game.icon(short):
            how += tr(', icône du menu aussi')
        self.say(tr('{name} remplacé par {image}{how}. Relancez le jeu pour le voir.', name=short,
                    image=Path(path).name, how=how))

    def restore(self):
        short = self.selected()
        if not short or not self.warn_running():
            return
        try:
            self.game.restore(short)
        except OSError as error:
            messagebox.showerror(TITLE, tr('Impossible de remettre {name} : {error}', name=short, error=error))
            return
        self.fill()
        self.say(tr("{name} remis d'origine.", name=short))

    def restore_all(self):
        if not self.game or not self.game.changed():
            return
        if not messagebox.askokcancel(TITLE, tr("Remettre tous les autocollants d'origine ? (supprime {file} du "
                                                "dossier archives)", file=core.OURS)):
            return
        try:
            self.game.restore_all()
        except (OSError, ValueError) as error:
            messagebox.showerror(TITLE, tr('Impossible de supprimer {file} : {error}', file=core.OURS, error=error))
            return
        self.fill()
        self.say(tr("Tout est remis d'origine."))

    def export(self):
        short = self.selected()
        if not short:
            return
        path = filedialog.asksaveasfilename(title=tr('Enregistrer en PNG'), defaultextension='.png',
                                            initialfile=f'{short}.png', filetypes=[('PNG', '*.png')])
        if not path:
            return
        try:
            core.texture.to_image(self.game.current(short)).save(path)
        except (ValueError, OSError) as error:
            messagebox.showerror(TITLE, tr("Impossible d'enregistrer : {error}", error=error))
            return
        self.say(tr('Enregistré : {path}', path=path))

    def save(self):
        values = {'folder': self.folder.get().strip(), 'cutout': self.cutout.get(), 'icon': self.with_icon.get()}
        if self.context:
            self.context.save_module_config(values)
        else:
            core.save_config(values)

    def say(self, text):
        self.status.configure(text=text)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
