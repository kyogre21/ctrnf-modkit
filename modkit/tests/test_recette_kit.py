# Recette du CTRNF Mod Kit (21/10/2026), sans le jeu. Lancer depuis le dossier modkit : python -m pytest -q tests
# Règles : aucun processus n'est démarré (launch.start, os.startfile et subprocess.Popen sont remplacés), les vrais
# réglages (~/.ctrnf_*.json) ne sont jamais lus en écriture ni modifiés (Path.home et les CONFIG des mods sont détournés
# vers un dossier temporaire), le vrai dossier du port n'est que lu.
# Les tests marqués @unittest.expectedFailure décrivent un défaut constaté : ils passeront (« XPASS ») une fois corrigé.
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading
import time
import unittest
from unittest import mock

from tests.fake import make_port
from ctrnf_modkit import config, launch, port
from ctrnf_modkit.modules import ABSENT, FOREIGN, PRESENT, REGISTRY, Autosplitter, Randomizer, Stickers

REAL_PORT = Path(r"C:\Users\jimmy\Desktop\CTR-NitroFueled-PC-portable-windows\OCTR-NitroFueled-PC-portable")
REAL_HOME = Path(os.path.expanduser("~"))
GAME_EXE = "sacredfire.exe"


def no_process(*args, **kwargs):
    raise AssertionError(f"un processus aurait été démarré : {args}")


class Base(unittest.TestCase):
    """Dossier temporaire, maison détournée, et aucun démarrage de processus possible."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.home = self.base / "maison"
        self.home.mkdir()
        from ctrnf_rando import app
        from ctrnf_stickers import core
        self.patches = [mock.patch("pathlib.Path.home", return_value=self.home),
                        mock.patch.object(app, "CONFIG", self.home / ".ctrnf_randomizer.json"),
                        mock.patch.object(core, "CONFIG", self.home / ".ctrnf_stickers.json"),
                        mock.patch("subprocess.Popen", side_effect=no_process),
                        mock.patch.object(launch, "start", side_effect=no_process)]
        if hasattr(os, "startfile"):
            self.patches.append(mock.patch("os.startfile", side_effect=no_process))
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.tmp.cleanup()


# --- 1. Dossier du port --------------------------------------------------------------------------------------------
class PortRecette(Base):
    @unittest.skipUnless((REAL_PORT / "launcher.ini").is_file(), "vrai port absent")
    def test_vrai_port_lecture_seule(self):
        info = port.resolve(REAL_PORT)
        self.assertTrue(info.ok, info.messages)
        self.assertTrue(info.game_dir.is_dir())
        self.assertEqual(info.archives, info.game_dir / "archives")
        self.assertTrue(port.is_launcher(info.launcher))
        self.assertIsNotNone(info.python)
        # le kit et les deux mods trouvent le même dossier archives
        from ctrnf_rando import archives
        from ctrnf_stickers import core
        self.assertEqual(info.archives, archives.game_archives(REAL_PORT))
        self.assertEqual(info.archives, core.find_archives(REAL_PORT))
        for mode in launch.MODES:                       # jamais bin/sacredfire.exe directement
            p = launch.plan(info, mode, env={})
            self.assertFalse(any(GAME_EXE in a.lower() for a in p.argv), p.argv)

    def ini(self, text, raw=False):
        folder, game = make_port(self.base)
        data = text.format(game=game).encode("utf-8") if not raw else text
        (folder / "launcher.ini").write_bytes(data)
        return folder, game

    def test_ini_crlf_bom_guillemets(self):
        folder, game = self.ini("\ufeff# commentaire\r\n; autre\r\n[launcher]\r\n  game_dir = \"{game}\"  \r\n"
                                "ui_language=fr\r\n")
        info = port.resolve(folder)
        self.assertEqual(info.game_dir, game)
        self.assertEqual(info.archives, game / "archives")

    def test_ini_barre_finale_et_slashs(self):
        folder, game = make_port(self.base)
        (folder / "launcher.ini").write_text(f"game_dir={str(game).replace(os.sep, '/')}/\n", encoding="utf-8")
        self.assertEqual(port.resolve(folder).archives, game / "archives")

    def test_ini_game_dir_absent_ou_faux(self):
        folder, game = self.ini("base_dir=x\nui_language=en\n")
        info = port.resolve(folder)
        self.assertTrue(info.ok)
        self.assertIsNone(info.game_dir)
        self.assertTrue(any("non renseigné" in m for m in info.messages))
        (folder / "launcher.ini").write_text("game_dir=Z:\\nulle\\part\n", encoding="utf-8")
        info = port.resolve(folder)
        self.assertTrue(info.ok)
        self.assertIsNone(info.archives)
        self.assertTrue(any("archives du jeu introuvables" in m for m in info.messages))
        (folder / "launcher.ini").unlink()                # pas de launcher.ini du tout
        self.assertIsNone(port.resolve(folder).game_dir)

    def test_ini_illisible(self):
        folder, _ = self.ini(b"\xff\xfeg\x00a\x00m\x00e\x00", raw=True)   # UTF-16 : rien ne plante
        self.assertIsNone(port.resolve(folder).game_dir)

    def test_ini_cle_en_double_meme_dossier_partout(self):
        # BUG : clé game_dir en double -> le kit prend la 1re, le randomizer (configparser) ne trouve rien et les
        # autocollants essaient toutes les valeurs : trois réponses différentes pour le même port.
        folder, game = self.ini("game_dir=Z:\\ancien\ngame_dir={game}\n")
        from ctrnf_rando import archives
        from ctrnf_stickers import core
        self.assertEqual(port.resolve(folder).archives, archives.game_archives(folder))
        self.assertEqual(port.resolve(folder).archives, core.find_archives(folder))

    def test_chemins_espaces_accents_tm(self):
        base = self.base / "Mes jeux é à ™ (copie)"
        base.mkdir()
        folder, game = make_port(base)
        renamed = folder / "Crash™ Team Racing Nitro-Fueled.exe"
        (folder / "CTR-NitroFueled-PC.exe").rename(renamed)
        info = port.resolve(folder)
        self.assertTrue(info.ok, info.messages)
        self.assertEqual(info.archives, game / "archives")
        self.assertEqual(info.launcher, renamed)
        p = launch.plan(info, "launcher", env={})
        self.assertEqual(p.argv, [str(renamed)])

    def test_launcher_renomme_et_faux_exe(self):
        folder, _ = make_port(self.base, launcher=False)
        (folder / "Mon launcher.exe").write_bytes(b"MZ" + port.LAUNCHER_MARK)
        (folder / "CTR-NitroFueled-PC.exe").write_bytes(b"MZ sans manifeste")   # nom connu mais pas le launcher
        self.assertEqual(port.resolve(folder).launcher.name, "Mon launcher.exe")

    def test_port_invalide_sans_launcher_cherche(self):
        info = port.resolve(self.base / "rien")
        self.assertFalse(info.ok)
        self.assertIsNone(info.launcher)


# --- 2. Plans de lancement -----------------------------------------------------------------------------------------
class LaunchRecette(Base):
    ENV = {"PATH": "p", "SystemRoot": "C:\\Windows", "_MEIPASS2": "x", "_PYI_APPLICATION_HOME_DIR": "y",
           "_PYI_ARCHIVE_FILE": "z", "TCL_LIBRARY": "t", "TK_LIBRARY": "k", "PYTHONHOME": "h", "PYTHONPATH": "pp"}

    def test_matrice(self):
        """Chaque mode × launcher présent/absent × python présent/absent × dossier du jeu présent/absent."""
        n = 0
        for has_launcher in (True, False):
            for has_python in (True, False):
                for has_game in (True, False):
                    for bat in (False, True):
                        sub = self.base / f"cas{n}"
                        sub.mkdir()
                        n += 1
                        folder, game = make_port(sub, launcher=has_launcher, python=has_python)
                        if bat:
                            (folder / "Jugar sin launcher.bat").write_text("@echo off\r\n", encoding="utf-8")
                        if not has_game:
                            (folder / "launcher.ini").write_text("ui_language=en\n", encoding="utf-8")
                        info = port.resolve(folder)
                        for mode in launch.MODES:
                            label = (mode, has_launcher, has_python, has_game, bat)
                            try:
                                p = launch.plan(info, mode, "--play", env=self.ENV)
                            except ValueError as error:
                                # refus attendu : pas de launcher (ou secours demandé) et pas de dossier du jeu, ou
                                # aucun démarrage de secours possible
                                launcher_used = mode != "secours" and has_launcher
                                self.assertFalse(launcher_used, label)
                                self.assertTrue(not has_game or (not has_python and not bat), (label, error))
                                self.assertTrue(str(error), label)
                                continue
                            self.assertFalse(any(GAME_EXE in a.lower() for a in p.argv), label)
                            self.assertEqual(p.cwd, folder, label)
                            self.assertEqual(set(p.env), {"PATH", "SystemRoot"} | (set() if p.shell else
                                                                                  {"BB_GAME_DIR"}), label)
                            if mode != "secours" and has_launcher:
                                self.assertTrue(p.shell, label)
                                self.assertEqual(p.argv[1:], ["--play"] if mode == "direct" else [], label)
                            else:
                                self.assertFalse(p.shell, label)
                                self.assertEqual(p.env["BB_GAME_DIR"], str(game), label)
                                if has_python:
                                    self.assertEqual(p.argv[1:], ["-X", "utf8", "run.py"], label)
                                else:
                                    self.assertEqual(p.argv[:2], ["cmd", "/c"], label)

    def test_direct_sans_argument(self):
        folder, _ = make_port(self.base)
        self.assertEqual(launch.plan(port.resolve(folder), "direct", "", env={}).argv[1:], [])

    def test_start_ne_part_que_par_le_plan(self):
        """launch.start (vrai code) avec os.startfile et Popen remplacés : arguments transmis tels quels."""
        folder, _ = make_port(self.base)
        info = port.resolve(folder)
        real_start = self.patches[4].temp_original
        with mock.patch("os.startfile", create=True) as startfile, mock.patch("subprocess.Popen") as popen:
            self.assertIsNone(real_start(launch.plan(info, "direct", env={})))
            startfile.assert_called_once_with(str(info.launcher), arguments="--play", cwd=str(folder))
            real_start(launch.plan(info, "secours", env={"PATH": "p"}))
            argv = popen.call_args[0][0]
            self.assertEqual(argv[1:], ["-X", "utf8", "run.py"])
            self.assertEqual(popen.call_args[1]["env"]["BB_GAME_DIR"], str(info.game_dir))


# --- 3. Réglages ---------------------------------------------------------------------------------------------------
class ConfigRecette(Base):
    def test_migration_depuis_les_vrais_anciens_reglages(self):
        copied = 0
        for name in (".ctrnf_randomizer.json", ".ctrnf_stickers.json"):
            if (REAL_HOME / name).is_file():
                shutil.copyfile(REAL_HOME / name, self.home / name)   # copie : l'original n'est que lu
                copied += 1
        if not copied:
            self.skipTest("pas d'anciens réglages sur ce PC")
        before = {p.name: p.read_bytes() for p in self.home.iterdir()}
        conf = config.Config()
        rando = json.loads((self.home / ".ctrnf_randomizer.json").read_text(encoding="utf-8"))
        self.assertEqual(conf.data["port"], rando.get("port", ""))
        self.assertNotIn("port", conf.module("randomizer"))
        self.assertNotIn("version", conf.module("randomizer"))
        self.assertEqual(conf.module("randomizer")["cups"], rando["cups"])
        self.assertEqual(set(conf.module("stickers")) <= {"cutout", "icon"}, True)
        for name, data in before.items():                  # anciens fichiers intacts
            self.assertEqual((self.home / name).read_bytes(), data)
        self.assertTrue(config.path().is_file())

    def test_migration_anciens_illisibles(self):
        (self.home / ".ctrnf_randomizer.json").write_text("[1, 2]", encoding="utf-8")
        (self.home / ".ctrnf_stickers.json").write_text("{pas du json", encoding="utf-8")
        conf = config.Config()
        self.assertEqual(conf.data["port"], "")
        self.assertEqual(conf.module("stickers"), {})

    def test_fichier_casse_puis_recasse(self):
        config.path().write_text("{1", encoding="utf-8")
        config.Config()
        self.assertEqual((self.home / ".ctrnf_modkit.json.bak").read_text(encoding="utf-8"), "{1")
        config.path().write_text("{2", encoding="utf-8")
        config.Config()
        # constat : la 2e casse écrase la 1re copie .bak (une seule copie gardée)
        self.assertEqual((self.home / ".ctrnf_modkit.json.bak").read_text(encoding="utf-8"), "{2")

    def test_format_futur_jamais_ecrit(self):
        config.path().write_text(json.dumps({"format": 2, "port": "X", "nouveau": 1}), encoding="utf-8")
        conf = config.Config()
        self.assertTrue(conf.read_only)
        conf.data["port"] = "Y"
        conf.save()
        conf.set_module("stickers", {"cutout": True})
        self.assertEqual(json.loads(config.path().read_text(encoding="utf-8")),
                         {"format": 2, "port": "X", "nouveau": 1})

    def test_types_inattendus_format(self):
        # BUG : config.py:202 compare « format » sans vérifier son type : {"format": "1"} -> TypeError, le kit ne
        # s'ouvre pas.
        config.path().write_text(json.dumps({"format": "1", "port": ""}), encoding="utf-8")
        config.Config()

    def test_types_inattendus_launch_enabled(self):
        # BUG : config.py:206-210 recopie tel quel un « launch » ou « enabled » qui n'a pas le bon type ; la fenêtre
        # plante ensuite (window.py:94 et 150).
        config.path().write_text(json.dumps({"format": 1, "launch": None, "enabled": None}), encoding="utf-8")
        conf = config.Config()
        self.assertIsInstance(conf.data["launch"], dict)
        self.assertIsInstance(conf.data["enabled"], list)

    def test_sauvegardes_des_modules_dans_la_meme_fenetre(self):
        conf = config.Config(self.base / "kit.json")
        conf.data["port"] = "P"
        conf.set_module("randomizer", {"port": "AUTRE", "cups": "coupes"})
        conf.set_module("stickers", {"folder": "AUTRE", "cutout": True})
        data = json.loads((self.base / "kit.json").read_text(encoding="utf-8"))
        self.assertEqual(data["port"], "P")
        self.assertEqual(data["modules"]["randomizer"], {"cups": "coupes"})
        self.assertEqual(data["modules"]["stickers"], {"cutout": True})

    def test_deux_kits_ouverts(self):
        # Défaut mineur : deux fenêtres du kit ouvertes en même temps -> la dernière qui enregistre écrase tout le
        # fichier (save() réécrit toutes les données en mémoire).
        a, b = config.Config(self.base / "kit.json"), config.Config(self.base / "kit.json")
        a.set_module("randomizer", {"cups": "coupes"})
        b.set_module("stickers", {"cutout": True})
        data = json.loads((self.base / "kit.json").read_text(encoding="utf-8"))
        self.assertEqual(data["modules"]["randomizer"], {"cups": "coupes"})


# --- 4. Fichiers des mods et désinstallation -----------------------------------------------------------------------
class Ctx:
    def __init__(self, folder, conf):
        self.port = port.resolve(folder)
        self.config = conf


class ModulesRecette(Base):
    def setUp(self):
        super().setUp()
        self.folder, self.game = make_port(self.base)
        self.archives = self.game / "archives"
        self.ctx = Ctx(self.folder, config.Config(self.base / "kit.json"))

    def real_xml(self, seed=77):
        """Un vrai Randomizer.xml, fabriqué par le randomizer (sans archive : récompenses et podiums désactivés)."""
        from ctrnf_rando import app
        from ctrnf_rando.generator import Settings
        app.install(seed, Settings(shuffle_rewards=False, fast_podiums=False), self.folder)
        return self.folder / "patches" / "Randomizer.xml"

    def test_vrai_patch_reconnu_et_graines_gardees(self):
        from ctrnf_rando import archives
        xml = self.real_xml()
        (self.archives / "update4.pak").write_bytes(archives.pak_bytes({archives.MINIMAP.name: b"x"}))
        (self.archives / "update_hub3.pak").write_bytes(archives.pak_bytes({archives.PODIUM.name: b"y"}))
        m = Randomizer()
        self.assertEqual({f.path.name: f.state for f in m.files(self.ctx)},
                         {"Randomizer.xml": PRESENT, "update4.pak": PRESENT, "update_hub3.pak": PRESENT})
        self.assertEqual(m.status(self.ctx), "graine 77 installée")
        seeds = sorted(p.name for p in (self.folder / "graines_randomizer").iterdir())
        (self.folder / "patches" / "Autre.xml").write_text("<Patch/>", encoding="utf-8")
        report = m.uninstall(self.ctx)
        self.assertEqual(len(report), 3, report)
        self.assertFalse(xml.exists())
        self.assertFalse((self.archives / "update4.pak").exists())
        self.assertFalse((self.archives / "update_hub3.pak").exists())
        self.assertEqual(sorted(p.name for p in (self.folder / "graines_randomizer").iterdir()), seeds)
        self.assertTrue((self.folder / "patches" / "Autre.xml").exists())
        for name in port.ARCHIVES:
            self.assertTrue((self.archives / name).exists())

    def test_fichiers_etrangers_jamais_supprimes(self):
        from ctrnf_rando import archives
        from ctrnf_stickers import iga
        xml = self.folder / "patches" / "Randomizer.xml"
        xml.write_text('<Patch><Metadata Name="Randomizer" Author="quelquun"/></Patch>', encoding="utf-8")
        (self.archives / "update4.pak").write_bytes(archives.pak_bytes({archives.MINIMAP.name: b"x", "b": b"y"}))
        (self.archives / "update_hub3.pak").write_bytes(b"pas une archive")
        iga.write({"textures/autre.igz": b"x"}, self.archives / "update3.pak")
        dest = self.base / "LiveSplit"
        dest.mkdir()
        (dest / "CTRNF.asl").write_text("// autre script\n", encoding="utf-8")
        self.ctx.config.data["modules"]["autosplitter"] = {"dest": str(dest)}
        before = {p: p.read_bytes() for p in (xml, dest / "CTRNF.asl", *self.archives.iterdir())}
        for m in REGISTRY:
            self.assertTrue(all(f.state == FOREIGN for f in m.files(self.ctx)), m.id)
            m.uninstall(self.ctx)
        for p, data in before.items():
            self.assertEqual(p.read_bytes(), data, p)

    def test_autosplitter_refuse_un_asl_etranger(self):
        from ctrnf_modkit.modules import ModuleError
        dest = self.base / "LiveSplit"
        dest.mkdir()
        (dest / "CTRNF.asl").write_text("// mon script à moi\n", encoding="utf-8")
        with self.assertRaises(ModuleError):
            Autosplitter().install(self.ctx, dest)
        self.assertEqual((dest / "CTRNF.asl").read_text(encoding="utf-8"), "// mon script à moi\n")
        self.assertNotIn("dest", self.ctx.config.module("autosplitter"))

    def test_autosplitter_copie_modifiee_par_le_joueur(self):
        # Écart à la spec (§7 : « à nous » si SHA-256 = version publiée) : modules.py:200 ne regarde que la 1re ligne.
        # Un CTRNF.asl retouché par le joueur est donc écrasé par « Copier » et supprimé par « Tout désinstaller ».
        m = Autosplitter()
        dest = self.base / "LiveSplit"
        dest.mkdir()
        m.install(self.ctx, dest)
        target = dest / "CTRNF.asl"
        target.write_bytes(target.read_bytes() + "\n// mes réglages perso\n".encode("utf-8"))
        m.uninstall(self.ctx)
        self.assertTrue(target.exists())

    def test_autocollants_archive_reelle(self):
        from ctrnf_stickers import iga, names
        sticker = names.STICKER[0] + "Sticker_7" + names.STICKER[1]
        icon = names.ICON[0] + "133" + names.ICON[1]
        iga.write({sticker: b"a", icon: b"b"}, self.archives / "update3.pak")
        m = Stickers()
        self.assertEqual(m.files(self.ctx)[0].state, PRESENT)
        self.assertEqual(m.status(self.ctx), "1 autocollant(s) remplacé(s)")   # l'icône n'est pas comptée
        done = m.uninstall(self.ctx)                        # retiré, mais copié d'abord (les images du joueur)
        self.assertEqual(len(done), 1)
        self.assertTrue(done[0].startswith("update3.pak retiré (copie : "), done)
        self.assertTrue(list(Path.home().glob("CTRNF Mod Kit - sauvegardes/update3_*.pak")))
        iga.write({sticker: b"a", "textures/autre.igz": b"c"}, self.archives / "update3.pak")   # mélangée
        self.assertEqual(m.files(self.ctx)[0].state, FOREIGN)
        self.assertEqual(m.uninstall(self.ctx), [])

    def test_archive_vide_ou_tronquee(self):
        (self.archives / "update3.pak").write_bytes(b"")
        (self.archives / "update4.pak").write_bytes(b"IGA\x1a")
        for m in REGISTRY:
            for f in m.files(self.ctx):
                self.assertNotEqual(f.state, PRESENT, f.path)


# --- 5. Fenêtre du kit ---------------------------------------------------------------------------------------------
class WindowBase(Base):
    def setUp(self):
        super().setUp()
        try:
            import tkinter as tk
            self.root = tk.Tk()
        except Exception as error:
            self.skipTest(f"pas de fenêtre possible : {error}")
        from ctrnf_modkit import window
        from ctrnf_rando import app
        self.window = window
        self.real_poll = window.KitWindow.poll
        self.box = mock.MagicMock()
        self.box.askokcancel.return_value = True
        self.box.askyesno.return_value = True
        self.running = set()          # noms des processus « en cours » (faux tasklist)
        more = [mock.patch.object(window, "messagebox", self.box),
                mock.patch.object(port, "running", side_effect=self.fake_running),
                mock.patch.object(app, "game_running", return_value=False),
                mock.patch.object(window.KitWindow, "poll", lambda self: None)]
        for p in more:
            p.start()
        self.patches += more
        self.started = []
        self.patches[4].stop()        # launch.start : on enregistre les plans au lieu de lever
        self.start = mock.patch.object(launch, "start", side_effect=lambda p: self.started.append(p))
        self.start.start()
        self.patches[4] = self.start

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass
        super().tearDown()

    def fake_running(self, *names):
        return {n.lower() for n in names} & self.running

    def kit(self, folder="", **data):
        conf = config.Config(self.base / "kit.json")
        conf.data["port"] = str(folder)
        conf.data.update(data)
        conf.save()
        self.conf = conf
        self.win = self.window.KitWindow(self.root, conf)
        return self.win

    def open(self, mod_id):
        self.win.notebook.select(self.win.tabs[mod_id])
        self.win.build_current()
        children = self.win.tabs[mod_id].winfo_children()
        self.assertEqual(len(children), 1)
        return children[0]

    def settle(self, timeout=3.0):
        """Laisse passer l'attente de 400 ms du dossier du port."""
        end = time.time() + timeout
        while self.win.ctx._pending and time.time() < end:
            self.root.update()
            time.sleep(0.02)
        self.root.update()
        self.assertIsNone(self.win.ctx._pending)

    def saved(self):
        return json.loads((self.base / "kit.json").read_text(encoding="utf-8"))


def iga_game(base, stickers=("Sticker_1", "Sticker_2")):
    """Faux port dont les archives du jeu sont de vraies archives IGA (des noms d'autocollants, pas d'images)."""
    from ctrnf_stickers import iga, names
    folder, game = make_port(base)
    for pak in port.ARCHIVES:
        iga.write({names.STICKER[0] + s + names.STICKER[1]: b"x" for s in stickers} if pak == "stickers.pak"
                  else {"autre/" + pak: b"x"}, game / "archives" / pak)
    return folder, game


class WindowRecette(WindowBase):
    def test_onglets_titre_et_masquage(self):
        folder, _ = make_port(self.base)
        win = self.kit(folder)
        for m in REGISTRY:
            child = self.open(m.id)
            self.assertNotIsInstance(child, __import__("tkinter").ttk.Label, m.id)
        self.assertEqual(self.root.title(), "CTRNF Mod Kit 0.1.0 — par kyogre21")
        win.toggle(REGISTRY[2], False)
        self.assertEqual(win.notebook.tab(win.tabs["autosplitter"], "state"), "hidden")
        win.open_tab(REGISTRY[2])
        self.assertIn("désactivé", win.message.cget("text"))
        win.toggle(REGISTRY[2], True)
        self.assertEqual(win.notebook.tab(win.tabs["autosplitter"], "state"), "normal")
        names = [win.notebook.tab(t, "text") for t in win.notebook.tabs()]
        self.assertEqual(names, ["Accueil", "Randomizer", "Autocollants", "Autosplitter (alpha)", "À propos"])
        self.assertEqual(self.saved()["enabled"], ["randomizer", "stickers", "autosplitter"])

    def test_onglet_desactive_au_demarrage_et_onglet_casse(self):
        folder, _ = make_port(self.base)
        win = self.kit(folder, enabled=["autosplitter"])
        self.assertEqual(win.notebook.tab(win.tabs["randomizer"], "state"), "hidden")
        with mock.patch.object(Autosplitter, "build_tab", side_effect=RuntimeError("cassé")):
            label = self.open("autosplitter")
        self.assertIn("erreur à l'ouverture", label.cget("text"))
        self.assertEqual(self.root.title(), "CTRNF Mod Kit 0.1.0 — par kyogre21")

    def test_autocollants_indisponibles(self):
        folder, _ = make_port(self.base)
        self.kit(folder)
        with mock.patch.object(Stickers, "available", return_value=(False, "numpy manquant")):
            label = self.open("stickers")
        self.assertIn("indisponible", label.cget("text"))

    def test_changer_de_port_rafraichit_tout(self):
        bad = self.base / "pas un port"
        bad.mkdir()
        good, game = iga_game(self.base)
        win = self.kit(bad)
        rando, stickers = self.open("randomizer"), self.open("stickers")
        self.assertTrue(win.port_label.cget("text").startswith("✗"))
        self.assertTrue(stickers.game_label.cget("text").startswith("✗"))
        self.assertEqual(stickers.listbox.size(), 0)
        win.ctx.port_var.set(str(good))
        self.assertIsNotNone(win.ctx._pending)              # pas tout de suite : attente de 400 ms
        self.settle()
        self.assertTrue(win.port_label.cget("text").startswith("✓"), win.port_label.cget("text"))
        self.assertIn(str(game), win.game_label.cget("text"))
        self.assertEqual(stickers.game_label.cget("text"), f"✓ {game / 'archives'}")
        self.assertEqual(stickers.listbox.size(), 2)
        self.assertIn("out/eboot.elf", rando.status.cget("text"))   # le randomizer a revérifié le port
        self.assertEqual(self.saved()["port"], str(good))
        self.assertIs(rando.port, win.ctx.port_var)
        self.assertIs(stickers.folder, win.ctx.port_var)

    @unittest.skipUnless((REAL_PORT / "launcher.ini").is_file(), "vrai port absent")
    def test_autocollants_avec_le_vrai_port(self):
        real_conf = REAL_HOME / ".ctrnf_modkit.json"
        conf_before = real_conf.stat().st_mtime if real_conf.exists() else None
        win = self.kit(REAL_PORT)
        before = {p.name: p.stat().st_mtime for p in port.resolve(REAL_PORT).archives.iterdir()}
        stickers = self.open("stickers")
        self.assertTrue(stickers.game_label.cget("text").startswith("✓"))
        self.assertGreater(stickers.listbox.size(), 100)
        stickers.listbox.selection_set(0)
        stickers.show()                                     # aperçu lu, rien d'écrit
        self.assertIn("pixels", stickers.size_label.cget("text"))
        rando = self.open("randomizer")
        self.assertTrue(rando.status.cget("text").startswith("✓"), rando.status.cget("text"))
        self.assertTrue(win.port_label.cget("text").startswith("✓"))
        after = {p.name: p.stat().st_mtime for p in port.resolve(REAL_PORT).archives.iterdir()}
        self.assertEqual(before, after)
        # les vrais réglages ne sont pas touchés (le fichier peut exister : le joueur a déjà ouvert le kit)
        self.assertEqual(real_conf.stat().st_mtime if real_conf.exists() else None, conf_before)

    def test_generer_en_mode_kit(self):
        from ctrnf_rando import app
        folder, _ = make_port(self.base)
        win = self.kit(folder)
        stickers = self.open("stickers")
        rando = self.open("randomizer")
        rando.seed.set("123")
        rando.cups.set("coupes")
        with mock.patch.object(app, "check_port", return_value=(True, ["ok"])), \
                mock.patch.object(app, "install", return_value=({}, "ABCD-EF01", self.base / "j.txt", [])) as inst:
            rando.generate()
        inst.assert_called_once()
        self.assertEqual(inst.call_args[0][2], str(folder))
        stickers.cutout.set(True)
        stickers.save()                                     # l'autre onglet enregistre juste après
        data = self.saved()
        self.assertEqual(data["port"], str(folder))
        self.assertEqual(data["modules"]["randomizer"]["cups"], "coupes")
        self.assertNotIn("port", data["modules"]["randomizer"])
        self.assertEqual(data["modules"]["stickers"]["cutout"], True)
        self.assertFalse((self.home / ".ctrnf_randomizer.json").exists())   # pas les réglages autonomes
        self.assertFalse((self.home / ".ctrnf_stickers.json").exists())
        self.assertIn("ABCD-EF01", rando.print_label.cget("text"))

    def test_accueil_a_jour_apres_une_graine(self):
        # BUG : après « Générer et installer » (ou un autocollant remplacé), l'accueil garde l'ancien état jusqu'à
        # « Actualiser » : rien n'appelle KitWindow.refresh (window.py:50 ne fait que construire l'onglet).
        from ctrnf_rando import app
        folder, _ = make_port(self.base)
        win = self.kit(folder)
        rando = self.open("randomizer")
        rando.seed.set("77")

        def install(seed, settings, port_folder, rename=True):
            (Path(port_folder) / "patches" / "Randomizer.xml").write_text(
                '<!-- graine 77 -->\n<Metadata Name="Randomizer" Author="kyogre21">', encoding="utf-8")
            return {}, "ABCD-EF01", self.base / "j.txt", []
        with mock.patch.object(app, "check_port", return_value=(True, ["ok"])), \
                mock.patch.object(app, "install", side_effect=install):
            rando.generate()
        win.notebook.select(0)                              # retour à l'accueil
        self.root.update()
        self.assertEqual(win.mod_status["randomizer"].cget("text"), "graine 77 installée")

    def test_parcourir_des_autocollants_change_le_port_commun(self):
        # BUG : dans le kit, « Parcourir… » de l'onglet Autocollants demande le « Dossier du jeu » et l'écrit dans
        # le dossier COMMUN du port (gui.py:130-134 des autocollants, self.folder = context.port_var) : l'accueil et
        # le randomizer passent en ✗, « Lancer le jeu » est refusé, et ce mauvais dossier est enregistré.
        folder, game = iga_game(self.base)
        win = self.kit(folder)
        stickers = self.open("stickers")
        with mock.patch("tkinter.filedialog.askdirectory", return_value=str(game)):
            stickers.browse()
        self.settle()
        self.assertTrue(win.ctx.port.ok, win.ctx.port.messages)

    def test_port_tape_puis_fermeture_rapide(self):
        # Défaut mineur : le dossier tapé n'est enregistré qu'après 400 ms ; fermer avant le perd (window.py:339).
        folder, _ = make_port(self.base)
        win = self.kit("")
        win.ctx.port_var.set(str(folder))
        win.close()
        self.assertEqual(json.loads((self.base / "kit.json").read_text(encoding="utf-8"))["port"], str(folder))

    def test_set_running(self):
        folder, _ = make_port(self.base)
        win = self.kit(folder)
        win.set_running({"sacredfire.exe"})
        self.assertEqual(str(win.launch_button.cget("state")), "disabled")
        self.assertEqual(win.game_state.cget("text"), "● Jeu en cours")
        win.set_running({"ctr-nitrofueled-pc.exe"})
        self.assertEqual(win.game_state.cget("text"), "● Launcher ouvert")
        self.assertEqual(str(win.launch_button.cget("state")), "normal")
        win.set_running(set())
        self.assertEqual(win.game_state.cget("text"), "Jeu fermé")

    def test_poll_dans_un_thread_puis_fermeture(self):
        """Le tasklist tourne dans un thread ; son résultat est repris au tour suivant, dans le thread de Tk."""
        folder, _ = make_port(self.base)
        win = self.kit(folder)
        errors = []
        old_hook = threading.excepthook
        threading.excepthook = lambda args: errors.append(args.exc_value)
        try:
            self.running = {"sacredfire.exe"}
            calls = []

            def tour():
                before = set(threading.enumerate())
                self.real_poll(win)
                for t in set(threading.enumerate()) - before:
                    t.join(2)
            with mock.patch.object(self.window, "POLL_MS", 60000):
                tour()
                self.assertEqual(win.game_state.cget("text"), "Jeu fermé")   # pas encore repris
                tour()
                self.assertEqual(win.game_state.cget("text"), "● Jeu en cours")
                self.assertEqual(str(win.launch_button.cget("state")), "disabled")

                def slow(*names):
                    time.sleep(0.4)
                    calls.append(names)
                    return set()
                port.running.side_effect = slow
                self.real_poll(win)
                win.close()                                 # fermeture pendant le tasklist
                time.sleep(0.8)
            self.assertEqual(len(calls), 1)
            self.assertEqual(errors, [])
        finally:
            threading.excepthook = old_hook

    def test_rapport_de_plantage_une_seule_fois(self):
        folder, _ = make_port(self.base)
        log = folder / "last_run_Joueur.log"
        log.write_text("--- SacredFire launch 2026-10-21 12:00:00\nPatches: external Randomizer.xml/Randomizer "
                       "(70 writes)\nCreating AI controlled racer\n--- the game ended with code -1073741819\n",
                       encoding="utf-8")
        win = self.kit(folder)
        self.assertIn("violation d'accès", win.last_label.cget("text"))
        before = len(self.root.winfo_children())
        win.check_crash()
        win.check_crash()                                   # même lancement : pas de 2e fenêtre
        tops = [w for w in self.root.winfo_children() if w.winfo_class() == "Toplevel"]
        self.assertEqual(len(self.root.winfo_children()) - before, 1)
        self.assertEqual(len(tops), 1)
        text = tops[0].text.get("1.0", "end")
        self.assertIn("Randomizer.xml/Randomizer (70)", text)
        self.assertIn("AI controlled racer", text)


class LaunchWindowRecette(WindowBase):
    def setUp(self):
        super().setUp()
        self.folder, self.game = make_port(self.base)

    def go(self, mode):
        self.win.mode.set(launch.MODES[mode])
        self.win.launch()

    def test_lancement_normal_et_mode_enregistre(self):
        self.kit(self.folder)
        self.go("launcher")
        self.assertEqual(len(self.started), 1)
        self.assertTrue(self.started[0].shell)
        self.assertEqual(self.saved()["launch"]["mode"], "launcher")
        self.go("secours")                                  # bloqué : « Démarrage… » pendant 15 s
        self.assertEqual(len(self.started), 1)
        self.win.end_starting()
        self.go("secours")
        self.assertEqual(self.started[1].argv[1:], ["-X", "utf8", "run.py"])
        self.assertEqual(self.saved()["launch"]["mode"], "secours")
        for p in self.started:
            self.assertFalse(any(GAME_EXE in a.lower() for a in p.argv))
        self.assertIn("run.py", self.win.message.cget("text"))

    def test_jeu_deja_ouvert(self):
        self.kit(self.folder)
        self.running = {"sacredfire.exe"}
        for mode in launch.MODES:
            self.go(mode)
        self.assertEqual(self.started, [])
        self.assertEqual(self.box.showinfo.call_count, 3)

    def test_launcher_deja_ouvert(self):
        self.kit(self.folder)
        self.running = {"ctr-nitrofueled-pc.exe"}
        self.go("launcher")
        self.go("direct")
        self.assertEqual(self.started, [])
        self.assertIn("JOUER", self.box.showinfo.call_args[0][1])
        self.go("secours")                                  # le secours ne passe pas par le launcher
        self.assertEqual(len(self.started), 1)

    def test_launcher_renomme_deja_ouvert(self):
        # BUG : le launcher trouvé par son manifeste peut avoir un autre nom (spec §6, « launcher renommé ») mais
        # window.py:315 ne cherche que les deux noms connus : un 2e launcher est ouvert.
        (self.folder / "CTR-NitroFueled-PC.exe").unlink()
        (self.folder / "Mon launcher.exe").write_bytes(b"MZ" + port.LAUNCHER_MARK)
        self.kit(self.folder)
        self.running = {"mon launcher.exe"}
        self.go("launcher")
        self.assertEqual(self.started, [])

    def test_double_clic_sur_lancer(self):
        # BUG : deux clics rapprochés (le jeu n'apparaît dans tasklist qu'après quelques secondes) démarrent deux
        # fois le jeu en secours (deux sacredfire.exe sur la même sauvegarde) ou deux launchers (window.py:299-323).
        self.kit(self.folder)
        self.go("secours")
        self.go("secours")
        self.assertEqual(len(self.started), 1)

    def test_avertissements_et_refus(self):
        from ctrnf_rando import archives
        self.kit(self.folder)
        (self.game / "archives" / "update4.pak").write_bytes(archives.pak_bytes({archives.MINIMAP.name: b"x"}))
        self.box.askokcancel.return_value = False
        self.go("launcher")
        self.assertEqual(self.started, [])
        self.assertIn("sans graine", self.box.askokcancel.call_args[0][1])
        self.box.askokcancel.return_value = True
        self.go("launcher")
        self.assertEqual(len(self.started), 1)

    def test_erreurs_de_plan_et_de_demarrage(self):
        bad = self.base / "faux"
        bad.mkdir()
        self.kit(bad)
        self.go("launcher")
        self.assertIn("pas bon", self.box.showerror.call_args[0][1])
        self.win.ctx.port_var.set(str(self.folder))
        self.settle()
        self.start.stop()
        with mock.patch.object(launch, "start", side_effect=OSError("refusé")):
            self.go("launcher")
        self.start.start()
        self.assertIn("Impossible de démarrer", self.box.showerror.call_args[0][1])
        (self.folder / "launcher.ini").write_text("ui_language=en\n", encoding="utf-8")
        self.go("secours")
        self.assertIn("non renseigné", self.box.showerror.call_args[0][1])
        self.assertEqual(self.started, [])


class UninstallWindowRecette(WindowBase):
    def setUp(self):
        super().setUp()
        self.folder, self.game = make_port(self.base)
        self.archives = self.game / "archives"

    def install_all(self):
        from ctrnf_rando import archives
        from ctrnf_stickers import iga, names
        (self.folder / "patches" / "Randomizer.xml").write_text(
            '<!-- graine 5 -->\n<Metadata Name="Randomizer" Author="kyogre21">', encoding="utf-8")
        (self.archives / "update4.pak").write_bytes(archives.pak_bytes({archives.MINIMAP.name: b"x"}))
        (self.archives / "update_hub3.pak").write_bytes(archives.pak_bytes({"pas/a/nous": b"x"}))   # étrangère
        iga.write({names.STICKER[0] + "Sticker_1" + names.STICKER[1]: b"x"}, self.archives / "update3.pak")
        (self.folder / "graines_randomizer").mkdir()
        (self.folder / "graines_randomizer" / "graine_5.json").write_text("{}", encoding="utf-8")

    def test_tout_desinstaller(self):
        self.install_all()
        win = self.kit(self.folder)
        self.running = {"sacredfire.exe"}
        win.uninstall_all()
        self.assertIn("fermez-le", self.box.showerror.call_args[0][1])
        self.assertTrue((self.archives / "update3.pak").exists())
        self.running = set()
        self.box.askokcancel.return_value = False
        win.uninstall_all()
        self.assertTrue((self.archives / "update3.pak").exists())
        listing = self.box.askokcancel.call_args[0][1]
        self.assertIn("update3.pak", listing)
        self.assertNotIn("update_hub3.pak", listing)       # l'étrangère n'est pas proposée
        self.box.askokcancel.return_value = True
        win.uninstall_all()
        report = self.box.showinfo.call_args[0][1]
        self.assertIn("Randomizer.xml retiré", report)
        self.assertIn("update4.pak retirée", report)
        self.assertIn("update3.pak retiré", report)
        self.assertIn("Non touchés (pas à nous) : update_hub3.pak", report)
        self.assertTrue((self.archives / "update_hub3.pak").exists())
        self.assertTrue((self.folder / "graines_randomizer" / "graine_5.json").exists())
        win.uninstall_all()
        self.assertEqual(self.box.showinfo.call_args[0][1], "Aucun fichier des mods n'est posé.")
        self.assertEqual(win.mod_status["randomizer"].cget("text"), "aucune graine installée")

    def test_tout_desinstaller_avec_un_mauvais_dossier(self):
        # Défaut d'interface : dossier du port faux (ou ancien dossier après une mise à jour) -> « Aucun fichier des
        # mods n'est posé », alors que rien n'a pu être vérifié et que les archives restent dans le dossier du jeu.
        self.install_all()
        bad = self.base / "ancien port"
        bad.mkdir()
        win = self.kit(bad)
        win.uninstall_all()
        text = (self.box.showinfo.call_args or self.box.showerror.call_args)[0][1]
        self.assertIn("dossier du port", text.lower())

    def test_desactiver_un_mod_avec_fichiers(self):
        self.install_all()
        win = self.kit(self.folder)
        self.box.askyesno.return_value = False
        win.toggle(REGISTRY[1], False)
        self.assertTrue((self.archives / "update3.pak").exists())
        win.toggle(REGISTRY[1], True)
        self.box.askyesno.return_value = True
        win.toggle(REGISTRY[1], False)
        self.assertFalse((self.archives / "update3.pak").exists())
        self.assertTrue((self.folder / "patches" / "Randomizer.xml").exists())   # les autres mods ne bougent pas
        self.assertEqual(win.mod_status["stickers"].cget("text"), "aucun autocollant remplacé")

    def test_desactiver_un_mod_erreur_muette(self):
        # BUG : toggle() (window.py:172-174) jette le rapport de uninstall() : une suppression refusée par Windows
        # (fichier ouvert par le jeu) n'est jamais signalée ; et le jeu ouvert n'est pas vérifié.
        self.install_all()
        win = self.kit(self.folder)
        with mock.patch.object(Stickers, "uninstall", side_effect=PermissionError("[WinError 32] fichier utilisé")):
            win.toggle(REGISTRY[1], False)
        shown = [c[0][1] for c in self.box.showerror.call_args_list + self.box.showinfo.call_args_list]
        self.assertTrue(any("WinError 32" in text for text in shown), shown)


# --- 7. Fenêtres autonomes inchangées ------------------------------------------------------------------------------
class StandaloneRecette(WindowBase):
    def test_randomizer_autonome(self):
        from ctrnf_rando import app, gui
        (self.home / ".ctrnf_randomizer.json").write_text(json.dumps({"port": "C:/x", "cups": "circuits"}),
                                                          encoding="utf-8")
        a = gui.App(self.root)
        self.assertEqual(self.root.title(), gui.TITLE)
        self.assertEqual(a.port.get(), "C:/x")
        self.assertEqual(a.cups.get(), "circuits")
        folder, _ = make_port(self.base)
        a.port.set(str(folder))
        a.seed.set("9")
        with mock.patch.object(app, "check_port", return_value=(True, ["ok"])), \
                mock.patch.object(app, "install", return_value=({}, "AAAA-BBBB", self.base / "j.txt", [])):
            a.generate()
        saved = json.loads((self.home / ".ctrnf_randomizer.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["port"], str(folder))
        self.assertIn("version", saved)
        self.assertFalse(config.path().exists())            # le kit n'est pas concerné

    def test_autocollants_autonomes(self):
        from ctrnf_stickers import gui
        folder, game = iga_game(self.base)
        (self.home / ".ctrnf_stickers.json").write_text(json.dumps({"folder": str(game), "cutout": True}),
                                                        encoding="utf-8")
        a = gui.App(self.root)
        self.assertEqual(self.root.title(), gui.TITLE)
        self.assertEqual(a.listbox.size(), 2)
        self.assertTrue(a.cutout.get())
        saved = json.loads((self.home / ".ctrnf_stickers.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["folder"], str(game))
        self.assertFalse(config.path().exists())


if __name__ == "__main__":
    unittest.main()
