import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from tests.fake import make_port
from ctrnf_modkit import config, launch, port
from ctrnf_modkit.modules import ABSENT, FOREIGN, PRESENT, REGISTRY, Autosplitter, Randomizer, Stickers


class PortTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_good_port(self):
        folder, game_dir = make_port(self.base)
        info = port.resolve(folder)
        self.assertTrue(info.ok, info.messages)
        self.assertEqual(info.version, "v0.5.3-windows")
        self.assertEqual(info.game_dir, game_dir)          # BOM, commentaire et guillemets de launcher.ini
        self.assertEqual(info.archives, game_dir / "archives")
        self.assertEqual(info.launcher.name, "CTR-NitroFueled-PC.exe")  # autre.exe n'a pas le manifeste
        self.assertEqual(info.messages, ["port v0.5.3-windows"])

    def test_same_as_the_mods(self):
        from ctrnf_rando import archives
        from ctrnf_stickers import core
        folder, game_dir = make_port(self.base)
        (folder / "launcher.ini").write_text(f"# CTR-NitroFueled-PC launcher\ngame_dir={game_dir}\n", encoding="utf-8")
        self.assertEqual(port.resolve(folder).archives, archives.game_archives(folder))
        self.assertEqual(port.resolve(folder).archives, core.find_archives(folder))

    def test_bad_folders(self):
        self.assertFalse(port.resolve("").ok)
        info = port.resolve(self.base)
        self.assertFalse(info.ok)
        self.assertEqual(len(info.messages), 2)
        folder, _ = make_port(self.base, game=False, launcher=False)
        info = port.resolve(folder)
        self.assertTrue(info.ok)
        self.assertIsNone(info.archives)
        self.assertIsNone(info.launcher)
        self.assertTrue(any("archives du jeu introuvables" in m for m in info.messages))
        self.assertTrue(any("launcher du port introuvable" in m for m in info.messages))

    def test_launcher_choice(self):
        folder, _ = make_port(self.base)
        renamed = folder / "Mon launcher.exe"
        renamed.write_bytes(b"MZ" + port.LAUNCHER_MARK)
        os.utime(renamed, (2e9, 2e9))                      # le plus récent l'emporte
        self.assertEqual(port.find_launcher(folder), renamed)
        self.assertEqual(port.find_launcher(folder, forced=folder / "autre.exe"), folder / "autre.exe")


class LaunchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_plans(self):
        folder, game_dir = make_port(self.base)
        info = port.resolve(folder)
        env = {"PATH": "x", "_MEIPASS2": "y", "TCL_LIBRARY": "z", "_PYI_APPLICATION_HOME_DIR": "w"}
        p = launch.plan(info, "launcher", env=env)
        self.assertEqual((p.argv, p.cwd, p.shell), ([str(info.launcher)], folder, True))
        self.assertEqual(p.env, {"PATH": "x"})                       # rien de l'exe du kit ne passe au jeu
        self.assertEqual(launch.plan(info, "direct", "--play", env=env).argv[1:], ["--play"])
        p = launch.plan(info, "secours", env=env)
        self.assertEqual(p.argv[1:], ["-X", "utf8", "run.py"])
        self.assertEqual(p.env["BB_GAME_DIR"], str(game_dir))        # obligatoire : le jeu n'est pas dans le port
        self.assertFalse(p.shell)

    def test_fallbacks(self):
        folder, game_dir = make_port(self.base, launcher=False, python=False)
        (folder / "Jugar sin launcher.bat").write_text("@echo off\r\n", encoding="utf-8")
        p = launch.plan(port.resolve(folder), "launcher", env={})
        self.assertEqual(p.argv[:2], ["cmd", "/c"])                  # pas de launcher ni de python : le .bat
        self.assertEqual(p.env["BB_GAME_DIR"], str(game_dir))
        (folder / "Jugar sin launcher.bat").unlink()
        with self.assertRaises(ValueError):
            launch.plan(port.resolve(folder), "launcher", env={})
        with self.assertRaises(ValueError):
            launch.plan(port.resolve(self.base), "launcher", env={})  # port invalide

    def test_last_run(self):
        folder, _ = make_port(self.base)
        (folder / "last_run_Kyogre21.log").write_text(
            "--- SacredFire launch 2026-10-21 10:11:47\nPatches: external Randomizer.xml/Randomizer (70 writes)\n"
            "Loading app:/archives/update.pak.\nLoading app:/archives/update3.pak.\nLoading app:/archives/update4.pak.\n"
            "app:/archives/update5.pak not found.\nLoading app:/archives/update_hub3.pak.\n", encoding="utf-8")
        text = launch.last_run_summary(folder)
        self.assertIn("2026-10-21 10:11:47", text)
        self.assertIn("update3.pak, update4.pak, update_hub3.pak", text)
        self.assertNotIn("update5", text)
        self.assertIn("70 écritures", text)


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.patch = mock.patch("pathlib.Path.home", return_value=self.home)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()

    def test_migration(self):
        folder, _ = make_port(self.home)
        (self.home / ".ctrnf_randomizer.json").write_text(json.dumps(
            {"port": str(folder), "rewards": True, "cups": "coupes", "version": "0.2.0"}), encoding="utf-8")
        (self.home / ".ctrnf_stickers.json").write_text(json.dumps(
            {"folder": "C:/ailleurs", "cutout": True, "icon": False}), encoding="utf-8")
        conf = config.Config()
        self.assertEqual(conf.data["port"], str(folder))
        self.assertEqual(conf.module("randomizer"), {"rewards": True, "cups": "coupes"})
        self.assertEqual(conf.module("stickers"), {"cutout": True, "icon": False})
        self.assertTrue(config.path().is_file())
        # les anciens fichiers ne bougent pas
        self.assertIn("version", json.loads((self.home / ".ctrnf_randomizer.json").read_text(encoding="utf-8")))

    def test_broken_and_future(self):
        config.path().write_text("{pas du json", encoding="utf-8")
        conf = config.Config()
        self.assertTrue((self.home / ".ctrnf_modkit.json.bak").is_file())
        self.assertIn("illisibles", conf.warning)
        config.path().write_text(json.dumps({"format": 99, "port": "X"}), encoding="utf-8")
        conf = config.Config()
        self.assertTrue(conf.read_only)
        conf.set_module("randomizer", {"a": 1})
        self.assertEqual(json.loads(config.path().read_text(encoding="utf-8"))["format"], 99)  # pas écrasé

    def test_module_values(self):
        conf = config.Config()
        conf.set_module("stickers", {"folder": "x", "port": "y", "version": "z", "cutout": True})
        self.assertEqual(config.Config().module("stickers"), {"cutout": True})


class ModulesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.folder, self.game = make_port(self.base)
        self.archives = self.game / "archives"
        self.ctx = SimpleNamespace(port=port.resolve(self.folder), config=config.Config(self.base / "kit.json"))
        self.home = mock.patch("pathlib.Path.home", return_value=self.base)  # copies de sécurité hors du vrai dossier
        self.home.start()

    def tearDown(self):
        self.home.stop()
        self.tmp.cleanup()

    def test_no_overlap(self):
        self.ctx.config.data["modules"]["autosplitter"] = {"dest": str(self.base)}
        paths = [p for m in REGISTRY for p, _ in m.owned(self.ctx)]
        self.assertEqual(len(paths), 5)
        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual({m.id for m in REGISTRY}, set(config.MODULES))

    def test_randomizer_files(self):
        from ctrnf_rando import archives
        m = Randomizer()
        self.assertEqual([f.state for f in m.files(self.ctx)], [ABSENT] * 3)
        (self.folder / "patches" / "Randomizer.xml").write_text(
            '<!-- CTR Nitro-Fueled Randomizer 0.2.0, graine 77. -->\n<Metadata Name="Randomizer" Author="kyogre21">',
            encoding="utf-8")
        (self.archives / "update4.pak").write_bytes(archives.pak_bytes({archives.MINIMAP.name: b"x"}))
        (self.archives / "update_hub3.pak").write_bytes(archives.pak_bytes({"autre/script.igz": b"x"}))
        states = {f.path.name: f.state for f in m.files(self.ctx)}
        self.assertEqual(states, {"Randomizer.xml": PRESENT, "update4.pak": PRESENT, "update_hub3.pak": FOREIGN})
        self.assertEqual(m.status(self.ctx), "graine 77 installée")
        report = m.uninstall(self.ctx)
        self.assertFalse((self.folder / "patches" / "Randomizer.xml").exists())
        self.assertFalse((self.archives / "update4.pak").exists())
        self.assertTrue((self.archives / "update_hub3.pak").exists())  # pas à nous : gardée
        self.assertEqual(len(report), 2)

    def test_randomizer_warnings(self):
        from ctrnf_rando import archives
        m = Randomizer()
        (self.archives / "update4.pak").write_bytes(archives.pak_bytes({archives.MINIMAP.name: b"x"}))
        self.assertIn("sans graine", m.warnings(self.ctx)[0])
        (self.folder / "patches" / "Randomizer.xml").write_text('<Metadata Name="Randomizer" Author="kyogre21">',
                                                                encoding="utf-8")
        (self.folder / "patches.json").write_text(json.dumps({"disabled": ["Randomizer.xml/Randomizer"]}),
                                                  encoding="utf-8")
        self.assertIn("désactivé", m.warnings(self.ctx)[0])

    def test_stickers_files(self):
        from ctrnf_stickers import core, iga, names
        m = Stickers()
        target = self.archives / "update3.pak"
        iga.write({"textures/autre.igz": b"x"}, target)
        self.assertEqual(m.files(self.ctx)[0].state, FOREIGN)
        self.assertEqual(m.uninstall(self.ctx), [])
        self.assertTrue(target.exists())
        with self.assertRaises(ValueError):                    # l'outil autonome ne la supprime pas non plus
            core.Game.restore_all(SimpleNamespace(folder=self.archives))
        name = names.STICKER[0] + "Sticker_42" + names.STICKER[1]
        iga.write({name: b"x"}, target)
        self.assertEqual(m.files(self.ctx)[0].state, PRESENT)
        self.assertEqual(m.status(self.ctx), "1 autocollant(s) remplacé(s)")
        m.uninstall(self.ctx)
        self.assertFalse(target.exists())

    def test_autosplitter(self):
        m = Autosplitter()
        self.assertEqual(m.version(), "0.1.1-alpha")
        self.assertEqual(m.status(self.ctx), "pas encore copié")
        dest = self.base / "LiveSplit"
        dest.mkdir()
        (dest / "CTRNF.asl").write_text("// un autre script", encoding="utf-8")
        with self.assertRaises(Exception):
            m.install(self.ctx, dest)                          # pas notre script : rien n'est écrit
        (dest / "CTRNF.asl").unlink()
        m.install(self.ctx, dest)
        self.assertEqual(m.status(self.ctx), "CTRNF.asl copié, à jour")
        m.uninstall(self.ctx)
        self.assertFalse((dest / "CTRNF.asl").exists())


class WindowTest(unittest.TestCase):
    def test_window(self):
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
            win = window.KitWindow(root, conf)
            self.assertIn("par kyogre21", root.title())
            names = [win.notebook.tab(t, "text") for t in win.notebook.tabs()]
            self.assertEqual(names, ["Accueil", "Randomizer", "Autocollants", "Autosplitter (alpha)", "À propos"])
            for m in REGISTRY:                                  # chaque onglet se construit dans le kit
                win.notebook.select(win.tabs[m.id])
                win.build_current()
                children = win.tabs[m.id].winfo_children()
                self.assertEqual(len(children), 1)
                self.assertNotIsInstance(children[0], __import__("tkinter").ttk.Label, m.id)  # pas d'erreur
            self.assertIn("par kyogre21", root.title())       # les mods n'ont pas pris le titre
            rando = win.tabs["randomizer"].winfo_children()[0]
            self.assertIs(rando.port, win.ctx.port_var)         # un seul dossier pour tous
            self.assertEqual(len(win.files.get_children()), 4)  # 3 fichiers du randomizer, 1 des autocollants
            win.toggle(REGISTRY[1], False)
            self.assertNotIn("stickers", conf.data["enabled"])
            self.assertEqual(win.notebook.tab(win.tabs["stickers"], "state"), "hidden")
        finally:
            root.destroy()
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main()


class ReportTest(unittest.TestCase):
    def test_crash_report(self):
        from ctrnf_modkit import report
        with tempfile.TemporaryDirectory() as tmp:
            folder, _ = make_port(Path(tmp))
            (folder / "last_run.log").write_text(
                "--- SacredFire launch 2026-10-19 09:20:10\nPatches: external CrashTeamRacing.xml/60 FPS Unlock (1 writes)\n"
                "Patches: external Randomizer.xml/Randomizer (70 writes)\n"
                "NOTICE: [Net]:  adding new AI controlled racer (spawnedDriver valid)\n"
                "--- the game ended with code 3221225477\n", encoding="utf-8")
            rep = launch.last_run_report(folder)
            self.assertTrue(rep["crashed"])
            self.assertEqual(rep["code"], 0xC0000005)
            self.assertIn("violation d'accès", rep["meaning"])
            self.assertIn(("CrashTeamRacing.xml/60 FPS Unlock", "1"), rep["patches"])  # noms avec espaces
            tips = report.hints(rep)
            self.assertTrue(any("OCTR v0.5.1" in t for t in tips))
            self.assertTrue(any("sans le randomizer" in t for t in tips))
            ctx = SimpleNamespace(port=port.resolve(folder), config=config.Config(Path(tmp) / "kit.json"))
            text = report.crash_text(ctx, rep)
            for part in ("0xc0000005", "Randomizer.xml/Randomizer (70)", "CTRNF Mod Kit", "v0.5.3-windows",
                         "--- the game ended with code 3221225477"):
                self.assertIn(part, text)
            (folder / "last_run.log").write_text("--- SacredFire launch 2026-10-21 10:11:47\n"
                                                 "--- the game ended with code 0\n", encoding="utf-8")
            self.assertFalse(launch.last_run_report(folder)["crashed"])
            (folder / "last_run.log").write_text("--- SacredFire launch 2026-10-21 10:11:47\nen cours\n", encoding="utf-8")
            self.assertIsNone(launch.last_run_report(folder)["code"])   # jeu encore ouvert : pas un plantage
            self.assertFalse(launch.last_run_report(folder)["crashed"])
        self.assertEqual(launch.code_text(1), "code 1 : run.py a refusé de démarrer (pseudo, réglages ou fichiers "
                                              "manquants : voir les dernières lignes)")
