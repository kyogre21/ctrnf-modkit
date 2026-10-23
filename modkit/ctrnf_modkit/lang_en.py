"""Traduction anglaise du kit : texte français du code -> texte anglais (mêmes {champs})."""
EN = {
    # fenêtre
    "CTRNF Mod Kit {version} — par {author}": "CTRNF Mod Kit {version} — by {author}",
    "Mods pour Crash Team Racing Nitro-Fueled (PC)   ·   version {version}   ·   par {author}":
        "Mods for Crash Team Racing Nitro-Fueled (PC)   ·   version {version}   ·   by {author}",
    "Langue :": "Language:",
    "Accueil": "Home",
    "À propos": "About",
    "{name} (alpha)": "{name} (alpha)",
    " Jeu ": " Game ",
    "Dossier du port :": "Port folder:",
    "Parcourir…": "Browse…",
    "Voir le rapport": "View report",
    " Mods ": " Mods ",
    "Ouvrir": "Open",
    " Fichiers posés par les mods ": " Files placed by the mods ",
    "Fichier": "File",
    "Dossier": "Folder",
    "Mod": "Mod",
    "État": "Status",
    "Taille": "Size",
    "Actualiser": "Refresh",
    "Ouvrir le dossier du jeu": "Open game folder",
    "Tout désinstaller…": "Uninstall everything…",
    "Aucun mod ne modifie les fichiers du jeu : chacun pose ses propres fichiers, et un fichier qui n'est pas à lui "
    "n'est jamais touché.":
        "No mod modifies the game's files: each one places its own files, and a file that isn't its own is never "
        "touched.",
    "Auteur : {author}": "Author: {author}",
    "Licence MIT : utilisation, modification et partage autorisés, en gardant le nom de l'auteur.":
        "MIT license: use, modification and sharing allowed, as long as the author's name is kept.",
    "Crédits : idée du randomizer inspirée du CTR-Randomizer d'icebound777 (version PS1, MIT). Le jeu tourne avec le "
    "port CTR-NitroFueled-PC / OCTR-NitroFueled-PC (GPL), que le kit lance sans l'inclure. Sans affiliation avec Sony, "
    "Activision ou Beenox.":
        "Credits: randomizer idea inspired by icebound777's CTR-Randomizer (PS1 version, MIT). The game runs on the "
        "CTR-NitroFueled-PC / OCTR-NitroFueled-PC port (GPL), which the kit launches without including it. Not "
        "affiliated with Sony, Activision or Beenox.",
    "Copier les versions": "Copy versions",
    "Jeu fermé": "Game closed",
    "● Jeu en cours": "● Game running",
    "● Launcher ouvert": "● Launcher open",
    "Jeu en cours": "Game running",
    "Lancer le jeu": "Launch the game",
    "Démarrage…": "Starting…",
    "{name} est décoché : son onglet est caché, mais ses fichiers restent dans le jeu (le mod s'applique toujours) :"
    "\n{listing}\n\nLe jeu est ouvert : fermez-le, puis utilisez « Tout désinstaller » pour les supprimer.":
        "{name} is unchecked: its tab is hidden, but its files are still in the game (the mod still applies):"
        "\n{listing}\n\nThe game is open: close it, then use \"Uninstall everything\" to remove them.",
    "{name} est décoché : son onglet est caché. Ses fichiers sont encore dans le jeu, donc le mod s'applique "
    "toujours :\n{listing}\n\nOui : SUPPRIMER ces fichiers (le mod ne s'appliquera plus au jeu).\nNon : les garder "
    "(le mod reste actif, seul l'onglet est caché).":
        "{name} is unchecked: its tab is hidden. Its files are still in the game, so the mod still applies:"
        "\n{listing}\n\nYes: DELETE these files (the mod will no longer apply to the game).\nNo: keep them (the mod "
        "stays active, only the tab is hidden).",
    "Rien à retirer.": "Nothing to remove.",
    "{name} est désactivé : cochez-le pour ouvrir son onglet.": "{name} is disabled: check it to open its tab.",
    "{name} indisponible : {why}": "{name} unavailable: {why}",
    "{name} : erreur à l'ouverture ({error})": "{name}: error while opening ({error})",
    "Dossier du jeu : {folder} (lu dans launcher.ini)": "Game folder: {folder} (read from launcher.ini)",
    ". Les archives des mods y sont posées : elles servent aussi aux autres ports qui l'utilisent.":
        ". The mods' archives are placed there: they also apply to other ports that use it.",
    "Le jeu s'est arrêté : {why}.": "The game stopped: {why}.",
    "port à choisir": "choose the port",
    "état illisible ({error})": "unreadable status ({error})",
    "{n} Ko": "{n} KB",
    "Journal du port illisible : {error}": "Unreadable port log: {error}",
    "fenêtre": "window",
    "Dossier du port CTR-NitroFueled-PC / OCTR": "CTR-NitroFueled-PC / OCTR port folder",
    "Vos autocollants (update3.pak) sont d'abord copiés dans « {folder} ».":
        "Your stickers (update3.pak) are first copied to \"{folder}\".",
    "Non touchés (pas à nous) : ": "Not touched (not ours): ",
    "Le jeu est ouvert : fermez-le avant de désinstaller.": "The game is open: close it before uninstalling.",
    "Choisissez d'abord le bon dossier du port (avec le dossier du jeu trouvé) : sans lui, le kit ne peut pas savoir ce "
    "qui est posé.":
        "First choose the right port folder (with the game folder found): without it, the kit can't know what is "
        "installed.",
    "Aucun fichier des mods n'est posé.": "No mod files are installed.",
    "Retirer ces fichiers ? Le jeu redeviendra celui d'origine (vos graines et vos sauvegardes sont gardées)."
    "\n\n{listing}":
        "Remove these files? The game will be back to the original (your seeds and saves are kept).\n\n{listing}",
    "Le jeu est déjà ouvert.": "The game is already open.",
    "Lancer quand même ?": "Launch anyway?",
    "Le launcher est déjà ouvert : cliquez sur JOUER dans sa fenêtre.":
        "The launcher is already open: click PLAY in its window.",
    "Le jeu est déjà en train de démarrer.": "The game is already starting.",
    "Impossible de démarrer : {error}": "Couldn't start: {error}",
    "Port : {version}": "Port: {version}",
    "inconnu": "unknown",
    "Versions copiées.": "Versions copied.",
    "Changement de langue impossible :\n\n{trace}\n\n(gardé dans {log})":
        "Couldn't change the language:\n\n{trace}\n\n(kept in {log})",
    "Le kit n'a pas pu démarrer :\n\n{trace}\n\n(gardé dans {log})": "The kit couldn't start:\n\n{trace}\n\n(kept in {log})",
    "Réglages faits par une version plus récente du kit : ils ne seront pas modifiés.":
        "Settings made by a newer version of the kit: they won't be changed.",

    # mods
    "Randomizer": "Randomizer",
    "Autocollants": "Stickers",
    "Autosplitter": "Autosplitter",
    "Confort": "Comfort",
    "Mélange le mode Aventure (circuits, récompenses, coupes, conditions, portails), toujours finissable.":
        "Shuffles Adventure mode (tracks, rewards, cups, requirements, warp pads), always beatable.",
    "Remplace les autocollants des karts (et leurs icônes du menu) par vos propres images.":
        "Replaces the kart stickers (and their menu icons) with your own images.",
    "Script LiveSplit : chrono coupé tout seul pendant le mode Aventure (lecture seule du jeu).":
        "LiveSplit script: the timer splits by itself during Adventure mode (reads the game only).",
    "Options de confort sur le jeu d'origine, sans randomizer (reliques, réserve de boost, podiums…).":
        "Quality-of-life options on the original game, without the randomizer (relics, boost reserve, podiums…).",
    "posé par le mod": "placed by the mod",
    "absent": "absent",
    "étranger (non touché)": "foreign (not touched)",
    "posée": "installed",
    "retirée": "removed",
    "patch de la graine": "seed patch",
    "mini-carte des reliques": "relic minimap",
    "podiums rapides": "fast podiums",
    "autocollants remplacés": "replaced stickers",
    "script LiveSplit": "LiveSplit script",
    "options de confort": "comfort options",
    "Recommencer / Continuer des reliques": "relic Restart / Continue",
    "bouche-trou posé": "placeholder installed",
    "bouche-trou retiré": "placeholder removed",
    "{n} fichier(s) posé(s)": "{n} file(s) installed",
    "rien d'installé": "nothing installed",
    "aucune graine installée": "no seed installed",
    "graine {seed} installée": "seed {seed} installed",
    "graine installée": "seed installed",
    "{file} retiré": "{file} removed",
    "Archives du randomizer sans graine installée ({files}) : faites « Tout désinstaller » ou générez une graine.":
        "Randomizer archives without an installed seed ({files}): use \"Uninstall everything\" or generate a seed.",
    "Le patch « Randomizer » est désactivé dans l'onglet des patchs du launcher : la graine ne sera pas appliquée.":
        "The \"Randomizer\" patch is disabled in the launcher's patches tab: the seed won't be applied.",
    "{name} manquant : pip install -r autocollants/requirements.txt":
        "{name} missing: pip install -r autocollants/requirements.txt",
    "aucun autocollant remplacé": "no sticker replaced",
    "{n} autocollant(s) remplacé(s)": "{n} sticker(s) replaced",
    "{file} retiré (copie : {copy})": "{file} removed (copy: {copy})",
    "pas encore copié": "not copied yet",
    "CTRNF.asl copié, à jour": "CTRNF.asl copied, up to date",
    "CTRNF.asl copié, version différente": "CTRNF.asl copied, different version",
    "{file} est notre script retouché à la main : rien n'est écrit": "{file} is our script edited by hand: nothing written",
    "{file} existe et n'est pas notre script : rien n'est écrit": "{file} exists and isn't our script: nothing written",
    "{file} retiré de {folder}": "{file} removed from {folder}",
    "{n} option(s) installée(s)": "{n} option(s) installed",
    "Confort.xml posé, aucune option": "Confort.xml installed, no option",
    "Le patch « Confort » est désactivé dans l'onglet des patchs du launcher : les options de confort ne seront pas "
    "appliquées.":
        "The \"Confort\" patch is disabled in the launcher's patches tab: the comfort options won't be applied.",

    # lancement
    "Ouvrir le launcher (recommandé)": "Open the launcher (recommended)",
    "Démarrer directement (launcher sans fenêtre)": "Start directly (launcher without window)",
    "Démarrage de secours (run.py, sans les réglages du launcher)": "Fallback start (run.py, without the launcher's settings)",
    "Le dossier du port n'est pas bon : voir l'accueil.": "The port folder isn't right: see Home.",
    "Dossier du jeu non renseigné (launcher.ini, game_dir) : ouvrez une fois le launcher du port et choisissez le jeu.":
        "Game folder not set (launcher.ini, game_dir): open the port's launcher once and choose the game.",
    "Launcher du port introuvable dans {folder}, et pas de démarrage de secours possible (python\\python.exe ou run.py "
    "manquant).":
        "Port launcher not found in {folder}, and no fallback start possible (python\\python.exe or run.py missing).",
    "dernier lancement {when}": "last launch {when}",
    "dernier lancement": "last launch",
    "archives chargées : ": "archives loaded: ",
    "aucune des nôtres": "none of ours",
    "randomizer appliqué ({n} écritures)": "randomizer applied ({n} writes)",
    "randomizer non appliqué": "randomizer not applied",
    "fin normale": "normal exit",
    "run.py a refusé de démarrer (pseudo, réglages ou fichiers manquants : voir les dernières lignes)":
        "run.py refused to start (username, settings or missing files: see the last lines)",
    "vérification du jeu échouée (dossier du jeu absent ou mauvaise version)":
        "game check failed (game folder missing or wrong version)",
    "erreur du port au démarrage (souvent libwinpthread-1.dll : il faut OCTR v0.5.1 ou plus récent)":
        "port error at startup (often libwinpthread-1.dll: OCTR v0.5.1 or newer is needed)",
    "interrompu (Ctrl+C)": "interrupted (Ctrl+C)",
    "fermé par Ctrl+C ou par la fermeture de sa console": "closed by Ctrl+C or by closing its console",
    "plantage mémoire (segmentation fault)": "memory crash (segmentation fault)",
    "plantage mémoire : violation d'accès (le jeu a lu ou écrit une adresse interdite)":
        "memory crash: access violation (the game read or wrote a forbidden address)",
    "plantage : dépassement de pile": "crash: stack overflow",
    "plantage : erreur fatale détectée par le programme (0xC0000409)": "crash: fatal error detected by the program (0xC0000409)",
    "plantage : instruction illégale (processeur ou GPU non pris en charge ?)":
        "crash: illegal instruction (unsupported CPU or GPU?)",
    "plantage mémoire : tas corrompu (0xC0000374)": "memory crash: corrupted heap (0xC0000374)",
    "erreur inconnue": "unknown error",
    "pas de code de fin (le jeu tourne encore, ou il a été tué)": "no exit code (the game is still running, or was killed)",
    "code {code} : {meaning}": "code {code}: {meaning}",

    # dossier du port
    "Choisissez le dossier du port.": "Choose the port folder.",
    "ce n'est pas le dossier du port (bin/sacredfire.exe introuvable)": "this isn't the port folder (bin/sacredfire.exe not found)",
    "dossier « patches » introuvable": "\"patches\" folder not found",
    "port {version}": "port {version}",
    "version inconnue": "unknown version",
    "dossier du jeu non renseigné (launcher.ini, game_dir) : ouvrez une fois le launcher du port et choisissez le jeu":
        "game folder not set (launcher.ini, game_dir): open the port's launcher once and choose the game",
    "archives du jeu introuvables dans {folder}": "game archives not found in {folder}",
    "launcher du port introuvable (démarrage de secours seulement)": "port launcher not found (fallback start only)",

    # rapports
    "Port : {folder} ({version})": "Port: {folder} ({version})",
    "Dossier du jeu : {folder}": "Game folder: {folder}",
    "Mods activés : ": "Enabled mods: ",
    "{name} : fichiers illisibles ({error})": "{name}: unreadable files ({error})",
    "Graine du randomizer : {seed}": "Randomizer seed: {seed}",
    "Le jeu s'est arrêté : {why}": "The game stopped: {why}",
    "Lancé le {when}, journal : {log}": "Launched on {when}, log: {log}",
    "Patchs appliqués : ": "Applied patches: ",
    "aucun": "none",
    "Dernières lignes du journal ({n}) :": "Last lines of the log ({n}):",
    "Plantage pendant la création des pilotes IA : défaut connu des anciennes versions du port, corrigé dans OCTR "
    "v0.5.1 ou plus récent.":
        "Crash while creating the AI racers: known bug of older port versions, fixed in OCTR v0.5.1 or newer.",
    "Code 3 au démarrage : mettre à jour le port (OCTR v0.5.1 ou plus récent).":
        "Code 3 at startup: update the port (OCTR v0.5.1 or newer).",
    "Si le plantage revient au même endroit, refaites l'essai sans le randomizer (« Tout désinstaller » ou décochez-le) "
    "pour savoir s'il en est la cause, et envoyez ce rapport.":
        "If the crash happens again at the same spot, try again without the randomizer (\"Uninstall everything\" or "
        "uncheck it) to know whether it's the cause, and send this report.",
    "Copier le rapport": "Copy report",
    "Enregistrer…": "Save…",
    "Ouvrir le journal": "Open log",
    "Fermer": "Close",
    "Copié : collez-le dans votre message.": "Copied: paste it into your message.",
    "Enregistrer le rapport": "Save report",
    "rapport_ctrnf.txt": "ctrnf_report.txt",
    "Texte": "Text",
    "Enregistré : {path}": "Saved: {path}",
    "CTRNF Mod Kit — le jeu s'est arrêté": "CTRNF Mod Kit — the game stopped",
    "Erreur du kit ({where}) :": "Kit error ({where}):",
    "CTRNF Mod Kit — erreur": "CTRNF Mod Kit — error",
    "Une erreur est survenue dans le kit. Copiez le rapport et envoyez-le (il est aussi gardé dans {log}).":
        "An error occurred in the kit. Copy the report and send it (it's also kept in {log}).",

    # onglet Confort
    "Ces options marchent sur le jeu d'origine, sans randomizer : votre partie et vos sauvegardes ne changent pas. Avec "
    "une graine du randomizer installée, ce sont les réglages de cet onglet qui comptent.":
        "These options work on the original game, without the randomizer: your game and saves don't change. With a "
        "randomizer seed installed, the settings of this tab are the ones that count.",
    " Options ": " Options ",
    "Reliques : viser le platine, puis l'or, puis le saphir pendant la course":
        "Relics: aim for platinum, then gold, then sapphire during the race",
    "Afficher la réserve de boost dans la barre de dérapage": "Show the boost reserve in the drift bar",
    "Pouvoir passer les podiums dès le début": "Skip podiums right from the start",
    "Passer les indices d'Aku Aku et les cinématiques des portes": "Skip Aku Aku's hints and the door cutscenes",
    "Fin des courses relique : Recommencer / Continuer, gagnée ou perdue":
        "End of relic races: Restart / Continue, won or lost",
    "Installer le confort": "Install comfort",
    "Retirer": "Remove",
    "Le patch est lu au lancement du jeu : relancez-le s'il est ouvert.":
        "The patch is read when the game starts: restart it if it's open.",
    "Choisissez d'abord le dossier du port dans l'onglet Accueil (il doit être vérifié).":
        "First choose the port folder in the Home tab (it must be verified).",
    "Le jeu est ouvert : le confort ne servira qu'au prochain lancement. Continuer ?":
        "The game is open: comfort will only apply at the next launch. Continue?",
    "Installation impossible : {error}": "Couldn't install: {error}",
    "Impossible de retirer : {error}": "Couldn't remove: {error}",
    "Dossier du port pas encore choisi ou pas vérifié (onglet Accueil).": "Port folder not chosen or not verified yet (Home tab).",
    "État : {state}.": "Status: {state}.",

    # onglet Autosplitter
    "Version alpha : tout début de développement. Le départ et les splits trophée / clé sont à valider en jeu, la fin "
    "contre Oxide coupe encore à la cinématique, et il n'y a pas de retrait des chargements. Vos retours sont les "
    "bienvenus !":
        "Alpha version: very early development. The start and the trophy / key splits still have to be checked in "
        "game, the end against Oxide still splits at the cutscene, and load times aren't removed. Feedback welcome!",
    "Le script LiveSplit lit la partie en cours (sans rien changer au jeu) et coupe le chrono tout seul pendant le mode "
    "Aventure, avec ou sans randomizer.":
        "The LiveSplit script reads the current game (without changing anything) and splits the timer by itself "
        "during Adventure mode, with or without the randomizer.",
    "Dossier où copier CTRNF.asl :": "Folder to copy CTRNF.asl to:",
    "Copier CTRNF.asl": "Copy CTRNF.asl",
    "Ouvrir le dossier": "Open folder",
    "Télécharger LiveSplit": "Download LiveSplit",
    "Dans LiveSplit": "In LiveSplit",
    "Réglages du script": "Script settings",
    "Limites de cette version": "Limits of this version",
    "1. Installer LiveSplit (livesplit.org), version 1.8 ou plus récente.":
        "1. Install LiveSplit (livesplit.org), version 1.8 or newer.",
    "2. Clic droit sur LiveSplit > « Edit Layout… » > « + » > « Control » > « Scriptable Auto Splitter ».":
        "2. Right-click LiveSplit > \"Edit Layout…\" > \"+\" > \"Control\" > \"Scriptable Auto Splitter\".",
    "3. Double-cliquer sur la ligne ajoutée, « Browse… », choisir CTRNF.asl (le dossier ci-dessus).":
        "3. Double-click the added line, \"Browse…\", choose CTRNF.asl (the folder above).",
    "4. Cocher ce qui doit couper le chrono, puis OK et enregistrer le layout.":
        "4. Check what should split the timer, then OK and save the layout.",
    "5. Préparer ses splits (clic droit > « Edit Splits… ») : un segment par split attendu, dans l'ordre.":
        "5. Set up your splits (right-click > \"Edit Splits…\"): one segment per expected split, in order.",
    "Départ auto : une partie neuve (rien gagné, aucune cinématique vue) arrive en jeu.":
        "Auto start: a new game (nothing won, no cutscene seen) gets into gameplay.",
    "Splits au choix : trophée, clé de boss, Oxide battu, vraie fin (cochés) ; relique, gemme, jeton CTR.":
        "Splits to choose: trophy, boss key, Oxide beaten, true ending (checked); relic, gem, CTR token.",
    "Charger une autre sauvegarde ne coupe pas le chrono.": "Loading another save doesn't split the timer.",
    "Pas encore de retrait des temps de chargement : le chrono compte le temps réel.":
        "Load times aren't removed yet: the timer counts real time.",
    "La fin contre Oxide coupe à la cinématique ; le split à la ligne d'arrivée est en préparation.":
        "The end against Oxide splits at the cutscene; the split at the finish line is in progress.",
    "Dossier pour CTRNF.asl": "Folder for CTRNF.asl",
    "Choisissez d'abord un dossier existant (par exemple celui de LiveSplit).":
        "First choose an existing folder (for example LiveSplit's).",
    "{file} est le script du kit retouché à la main. Le remplacer par la version du kit (vos changements seront "
    "perdus) ?":
        "{file} is the kit's script edited by hand. Replace it with the kit's version (your changes will be lost)?",
    "Copie impossible : {error}": "Couldn't copy: {error}",
    "CTRNF.asl copié : {file}": "CTRNF.asl copied: {file}",
    "✗ CTRNF.asl introuvable dans le kit.": "✗ CTRNF.asl not found in the kit.",
    "Version du script : {version} ; {state}.": "Script version: {version}; {state}.",
}
