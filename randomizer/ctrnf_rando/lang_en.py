"""Traduction anglaise du randomizer : texte français du code -> texte anglais (mêmes {champs})."""
EN = {
    # aide des options
    "Le dossier du port CTR-NitroFueled-PC (celui qui contient bin, patches et out). Le logiciel vérifie que le jeu est "
    "bien la version 1.21 attendue par le patch.":
        "The CTR-NitroFueled-PC port folder (the one containing bin, patches and out). The tool checks that the game "
        "is the 1.21 version the patch expects.",
    "La graine décide de tout le tirage : la même graine avec les mêmes réglages donne la même partie. Laissez vide "
    "pour en tirer une au hasard.":
        "The seed decides the whole shuffle: the same seed with the same settings gives the same game. Leave it empty "
        "to draw a random one.",
    "Chaque portail de course du mode Aventure charge un circuit tiré au hasard. La récompense reste celle du portail.":
        "Each race warp pad in Adventure mode loads a randomly drawn track. The reward stays the warp pad's.",
    "Où piocher les circuits : CTR (les 18 circuits de 1999), CNK (Crash Nitro Kart) et GP (circuits du Grand Prix). "
    "Il en faut au moins 18 sans les doublons.":
        "Where tracks are drawn from: CTR (the 18 tracks from 1999), CNK (Crash Nitro Kart) and GP (Grand Prix "
        "tracks). At least 18 are needed without duplicates.",
    "Autorise le même circuit derrière plusieurs portails.": "Allows the same track behind several warp pads.",
    "Les 4 défis cristaux se jouent dans des arènes tirées au hasard (CTR et CNK).":
        "The 4 crystal challenges are played in randomly drawn arenas (CTR and CNK).",
    "Au hub, le bandeau et les menus de chaque portail affichent le nom du circuit qu'il charge.":
        "In the hub, each warp pad's banner and menus show the name of the track it loads.",
    "Mélange les trophées, clés de boss, gemmes, jetons CTR et paliers de relique. Une logique garantit que la partie "
    "peut toujours être finie. Les objets qui tournent au-dessus d'un portail montrent ce qu'il donne ; l'écran de fin "
    "de course montre l'objet reçu.":
        "Shuffles trophies, boss keys, gems, CTR tokens and relic tiers. A logic makes sure the game can always be "
        "finished. The items spinning above a warp pad show what it gives; the end-of-race screen shows the item "
        "received.",
    "Coupes de gemmes de Gem Stone Valley. D'origine : rien ne change. Coupe au hasard : chaque portail joue une coupe "
    "tirée parmi les 16 du jeu. Circuits au hasard : chaque coupe est faite de 4 circuits tirés. Il y a toujours 5 "
    "coupes à jouer. En « circuits au hasard », les 20 courses sont tirées parmi 38 circuits (tous sauf Turbo Track et "
    "Retro Stadium, qui ne sont dans aucune coupe du jeu), sans circuit en double.":
        "Gem cups of Gem Stone Valley. Original: nothing changes. Random cup: each warp pad plays a cup drawn among "
        "the game's 16. Random tracks: each cup is made of 4 drawn tracks. There are always 5 cups to play. With "
        "\"random tracks\", the 20 races are drawn among 38 tracks (all except Turbo Track and Retro Stadium, which "
        "are in no cup of the game), with no duplicate track.",
    "Ce qu'il faut pour ouvrir la course de chaque portail, Slide Coliseum, Turbo Track, les arènes et les coupes. "
    "Nombres au hasard : le même type que le jeu, en nombre tiré. Tout au hasard : trophées, clés, reliques, gemmes ou "
    "jetons d'une couleur. Toujours atteignable ; deux portails de la plage restent ouverts au départ. Les garages de "
    "boss gardent 4, 8, 12 et 16 trophées.":
        "What is needed to open each warp pad's race, Slide Coliseum, Turbo Track, the arenas and the cups. Random "
        "numbers: the same type as the game, in a drawn number. Everything random: trophies, keys, relics, gems or "
        "tokens of one color. Always reachable; two warp pads on the beach stay open at the start. Boss garages keep "
        "4, 8, 12 and 16 trophies.",
    "Défi CTR et course aux reliques d'un portail, une fois son trophée gagné. D'origine : il faut des clés. Ouverts : "
    "jouables tout de suite. Au hasard : il faut un nombre tiré de trophées, de clés, de reliques, de gemmes ou de "
    "jetons d'une couleur (toujours atteignable).":
        "A warp pad's CTR challenge and relic race, once its trophy is won. Original: keys are needed. Open: playable "
        "right away. Random: a drawn number of trophies, keys, relics, gems or tokens of one color is needed (always "
        "reachable).",
    "Les indices d'Aku Aku sont marqués comme déjà vus : ils ne coupent plus la partie. Les cinématiques d'ouverture "
    "des portes déjà ouvertes par vos clés sont aussi passées (le jeu les gardait pour le retour d'un boss).":
        "Aku Aku's hints are marked as already seen: they no longer interrupt the game. The opening cutscenes of doors "
        "already opened by your keys are skipped too (the game kept them for after a boss).",
    "Hors dérapage, la barre de dérapage (style classique, celle de CTR) montre votre réserve de boost : elle se "
    "remplit quand vous enchaînez les turbos et se vide quand la réserve s'épuise (pleine = 5 s ou plus).":
        "When not drifting, the drift bar (classic style, the CTR one) shows your boost reserve: it fills up as you "
        "chain boosts and empties as the reserve runs out (full = 5 s or more).",
    "En course aux reliques, la cible affichée sous le chrono commence au temps platine ; quand votre chrono le "
    "dépasse, elle passe au temps or, puis au temps saphir (avec l'icône et la couleur du palier). Les récompenses ne "
    "changent pas.":
        "In relic races, the target shown under the timer starts at the platinum time; when your time goes past it, "
        "it switches to the gold time, then to the sapphire time (with the tier's icon and color). Rewards don't "
        "change.",
    "Au podium, l'écran « appuyez pour passer » s'ouvre dès le début au lieu d'attendre la fin de l'animation (posé "
    "dans le dossier du jeu : archives/update_hub3.pak). Si vous ne passez pas, le podium garde sa dernière pose.":
        "On the podium, the \"press to skip\" screen opens right at the start instead of waiting for the end of the "
        "animation (placed in the game folder: archives/update_hub3.pak). If you don't skip, the podium keeps its "
        "last pose.",
    "Les portails changent de place entre eux : une bataille peut se trouver là où était Crash Cove, une coupe sur la "
    "plage, etc. Le décor reste en place, mais ce qui s'y lance, ses objets et sa condition suivent le portail. Les "
    "garages de boss ne bougent pas. Toujours finissable : les conditions s'adaptent au monde où chaque portail arrive.":
        "Warp pads swap places: a battle can be where Crash Cove was, a cup on the beach, etc. The scenery stays in "
        "place, but what it launches, its items and its requirement follow the warp pad. Boss garages don't move. "
        "Always beatable: requirements adapt to the world each warp pad lands in.",
    "Le code de partage contient la graine et tous les réglages (circuits, récompenses, conditions, confort…). "
    "Donnez-le à vos adversaires : en le collant ici puis « Utiliser », ils ont exactement la même partie (même "
    "empreinte). « Copier » donne le code de la graine et des réglages affichés.":
        "The share code contains the seed and all settings (tracks, rewards, requirements, comfort…). Give it to your "
        "opponents: by pasting it here then \"Use\", they get exactly the same game (same fingerprint). \"Copy\" "
        "gives the code of the seed and settings shown.",
    "Règle d'un coup les options du tirage. Les options de confort ne changent pas.":
        "Sets the shuffle options in one click. Comfort options don't change.",
    "À la fin d'une course relique, gagnée ou perdue, le menu propose Recommencer (en haut) et Continuer (en dessous) "
    "pour retenter un meilleur palier sans repasser par le hub. Sélectionné : Continuer si une relique vient d'être "
    "gagnée, sinon Recommencer. Continuer sans nouvelle relique ramène au hub sans podium (posé dans le dossier du jeu : "
    "archives/update5.pak).":
        "At the end of a relic race, won or lost, the menu offers Restart (top) and Continue (below) to try for a "
        "better tier without going back to the hub. Selected: Continue if a relic was just won, otherwise Restart. "
        "Continue without a new relic goes back to the hub without a podium (placed in the game folder: "
        "archives/update5.pak).",
    "Tire la graine, pose le patch dans le dossier patches du port et enregistre la graine et son journal dans le "
    "dossier graines_randomizer du port. Commencez ensuite une nouvelle aventure.":
        "Draws the seed, places the patch in the port's patches folder and saves the seed and its log in the port's "
        "graines_randomizer folder. Then start a new adventure.",

    # préréglages
    "Découverte": "Discovery",
    "Classique": "Classic",
    "Chaos": "Chaos",
    "Circuits et arènes mélangés, le reste comme dans le jeu : pour une première partie.":
        "Tracks and arenas shuffled, the rest as in the game: for a first run.",
    "Circuits, arènes et récompenses mélangés, coupes au hasard, conditions en nombres au hasard.":
        "Tracks, arenas and rewards shuffled, random cups, requirements in random numbers.",
    "Tout au hasard : récompenses, coupes circuit par circuit, conditions, défis et emplacements des portails.":
        "Everything random: rewards, cups track by track, requirements, challenges and warp pad locations.",

    # fenêtre
    "Passez la souris sur une option pour voir son aide.": "Hover over an option to see its help.",
    "Jeu et graine": "Game and seed",
    "Dossier du port :": "Port folder:",
    "(choisi dans l'Accueil)": "(chosen in Home)",
    "Parcourir…": "Browse…",
    "Graine :": "Seed:",
    "Au hasard": "Random",
    "Code de partage :": "Share code:",
    "Utiliser": "Use",
    "Copier": "Copy",
    "Préréglages :": "Presets:",
    "Circuits": "Tracks",
    "Quel circuit (ou quelle arène) charge chaque portail du mode Aventure. La récompense reste celle du portail.":
        "Which track (or arena) each Adventure mode warp pad loads. The reward stays the warp pad's.",
    "Mélanger les circuits derrière les portails": "Shuffle the tracks behind the warp pads",
    "Circuits tirés parmi :": "Tracks drawn from:",
    "Autoriser le même circuit derrière plusieurs portails": "Allow the same track behind several warp pads",
    "Mélanger les arènes des défis cristaux": "Shuffle the crystal challenge arenas",
    "Afficher au hub le nom du circuit joué": "Show the name of the played track in the hub",
    "Récompenses": "Rewards",
    "Ce que donne chaque course gagnée : trophée, clé de boss, gemme, jeton CTR ou palier de relique. Mélangées, elles "
    "restent toujours atteignables.":
        "What each won race gives: trophy, boss key, gem, CTR token or relic tier. Shuffled, they always stay "
        "reachable.",
    "Mélanger les récompenses": "Shuffle the rewards",
    "Coupes": "Cups",
    "À Gem Stone Valley, 5 portails de coupe (rouge, bleue, verte, jaune, violette) font jouer 4 courses à la suite. Ce "
    "réglage choisit les circuits de ces coupes ; il y a toujours 5 coupes à jouer.":
        "In Gem Stone Valley, 5 cup warp pads (red, blue, green, yellow, purple) play 4 races in a row. This setting "
        "chooses the tracks of these cups; there are always 5 cups to play.",
    "D'origine : chaque portail garde ses 4 circuits": "Original: each warp pad keeps its 4 tracks",
    "Coupe au hasard : chaque portail joue une des 16 coupes du jeu (Arcade, CNK, Grand Prix…)":
        "Random cup: each warp pad plays one of the game's 16 cups (Arcade, CNK, Grand Prix…)",
    "Circuits au hasard : chaque coupe est faite de 4 circuits tirés, sans circuit en double":
        "Random tracks: each cup is made of 4 drawn tracks, with no duplicate track",
    "Conditions": "Requirements",
    "Ce qu'il faut pour ouvrir les portails. Les conditions tirées au hasard restent toujours atteignables.":
        "What is needed to open the warp pads. Randomly drawn requirements always stay reachable.",
    "Courses des portails, Slide Coliseum, Turbo Track, arènes et coupes :":
        "Warp pad races, Slide Coliseum, Turbo Track, arenas and cups:",
    "D'origine (trophées, clés, reliques, gemmes et jetons du jeu)": "Original (the game's trophies, keys, relics, gems and tokens)",
    "Nombres au hasard (même type que le jeu)": "Random numbers (same type as the game)",
    "Tout au hasard (trophées, clés, reliques, gemmes ou jetons)": "Everything random (trophies, keys, relics, gems or tokens)",
    "Défi CTR et course aux reliques (une fois le trophée du portail gagné) :":
        "CTR challenge and relic race (once the warp pad's trophy is won):",
    "D'origine (1 à 4 clés selon le monde)": "Original (1 to 4 keys depending on the world)",
    "Ouverts tout de suite": "Open right away",
    "Condition au hasard (trophées, clés, reliques, gemmes ou jetons)": "Random requirement (trophies, keys, relics, gems or tokens)",
    "Les garages de boss gardent 4, 8, 12 et 16 trophées.": "Boss garages keep 4, 8, 12 and 16 trophies.",
    "Portails": "Warp pads",
    "Où se trouve chaque portail du hub (courses, arènes de bataille, coupes, Slide Coliseum, Turbo Track).":
        "Where each hub warp pad is (races, battle arenas, cups, Slide Coliseum, Turbo Track).",
    "Mélanger les emplacements des portails": "Shuffle the warp pad locations",
    "Confort": "Comfort",
    "Pour jouer plus vite et mieux voir ce qui se passe.": "To play faster and better see what's going on.",
    "Passer les indices d'Aku Aku et les cinématiques des portes": "Skip Aku Aku's hints and the door cutscenes",
    "Afficher la réserve de boost dans la barre de dérapage": "Show the boost reserve in the drift bar",
    "Pouvoir passer les podiums dès le début": "Skip podiums right from the start",
    "Reliques : viser le platine, puis l'or, puis le saphir pendant la course":
        "Relics: aim for platinum, then gold, then sapphire during the race",
    "Générer et installer": "Generate and install",
    "Ouvrir le journal": "Open log",
    "Dossier du port CTR-NitroFueled-PC": "CTR-NitroFueled-PC port folder",
    "Choisissez le dossier du port.": "Choose the port folder.",
    "Préréglage « {name} » appliqué (options de confort inchangées).": "Preset \"{name}\" applied (comfort options unchanged).",
    "Code de partage refusé : {error}.": "Share code rejected: {error}.",
    "Code {code} : graine {seed} et réglages chargés. Cliquez sur « Générer et installer ».":
        "Code {code}: seed {seed} and settings loaded. Click \"Generate and install\".",
    "Choisissez une graine (ou « Au hasard ») pour avoir son code de partage.":
        "Choose a seed (or \"Random\") to get its share code.",
    "Code de partage copié : {code}": "Share code copied: {code}",
    "Le dossier du port n'est pas bon : voir le message en haut de la fenêtre.":
        "The port folder isn't right: see the message at the top of the window.",
    "La graine doit être un nombre de 0 à 4294967295 (ou vide pour un tirage au hasard).":
        "The seed must be a number from 0 to 4294967295 (or empty for a random draw).",
    "Le jeu est ouvert : le patch ne servira qu'au prochain lancement. Continuer ?":
        "The game is open: the patch will only apply at the next launch. Continue?",
    "Impossible de tirer cette graine : {error}": "Couldn't draw this seed: {error}",
    "Impossible d'écrire les fichiers : {error}": "Couldn't write the files: {error}",
    "Empreinte : {mark}": "Fingerprint: {mark}",
    "Graine {seed} installée (empreinte {mark}).": "Seed {seed} installed (fingerprint {mark}).",
    "Patch : {file}": "Patch: {file}",
    "Journal : {file}": "Log: {file}",
    "Code de partage : {code} (vos adversaires le collent pour avoir la même partie)":
        "Share code: {code} (your opponents paste it to get the same game)",
    "Lancez le jeu et commencez une nouvelle aventure (une ancienne partie ne correspond plus).":
        "Launch the game and start a new adventure (an old save no longer matches).",

    # vérification du port et installation
    "ce n'est pas le dossier du port (bin/sacredfire.exe introuvable)": "this isn't the port folder (bin/sacredfire.exe not found)",
    "dossier « patches » introuvable": "\"patches\" folder not found",
    "jeu pas encore préparé : lancez-le une fois avec le port (out/eboot.elf introuvable)":
        "game not prepared yet: launch it once with the port (out/eboot.elf not found)",
    "version du jeu inattendue (il faut CUSA13795 v1.21) : {n} endroit(s) différent(s)":
        "unexpected game version (CUSA13795 v1.21 is needed): {n} spot(s) differ",
    "inconnue": "unknown",
    " (dossier du jeu introuvable dans launcher.ini : podiums rapides et mini-carte des reliques indisponibles)":
        " (game folder not found in launcher.ini: fast podiums and relic minimap unavailable)",
    "port {version}, jeu CUSA13795 v1.21 vérifié": "port {version}, game CUSA13795 v1.21 verified",
    "{file} existe et n'est pas un patch de ce randomizer : rien n'est écrit":
        "{file} exists and isn't a patch from this randomizer: nothing written",
    "{file} présent : les options de confort viennent de l'onglet Confort du kit (celles de cette graine ne sont pas "
    "posées).":
        "{file} present: the comfort options come from the kit's Comfort tab (this seed's ones aren't installed).",
    "{file} {what} dans {folder}": "{file} {what} in {folder}",
    "posée": "installed",
    "retirée": "removed",
    "bouche-trou posé": "placeholder installed",
    "bouche-trou retiré": "placeholder removed",
    "Dossier du jeu introuvable (launcher.ini du port, game_dir) : podiums rapides et « Recommencer / Continuer » non "
    "installés.":
        "Game folder not found (port's launcher.ini, game_dir): fast podiums and \"Restart / Continue\" not installed.",
    "Dossier du jeu introuvable (launcher.ini du port, game_dir) : podiums rapides et mini-carte des reliques non "
    "installés.":
        "Game folder not found (port's launcher.ini, game_dir): fast podiums and relic minimap not installed.",
    "{file} : version du jeu inattendue (il faut CUSA13795 v1.21)": "{file}: unexpected game version (CUSA13795 v1.21 is needed)",
    "{file} existe déjà et n'est pas une archive du randomizer : rien n'est écrit":
        "{file} already exists and isn't a randomizer archive: nothing written",
    "dossier « patches » introuvable dans {folder}": "\"patches\" folder not found in {folder}",
    "{file} existe et n'est pas un patch du kit : rien n'est écrit": "{file} exists and isn't a kit patch: nothing written",
    "{file} posé ({n} option(s) dans le patch)": "{file} installed ({n} option(s) in the patch)",
    "{file} : ses options de confort sont retirées (Confort.xml s'en charge)":
        "{file}: its comfort options are removed (Confort.xml handles them)",
    "Dossier du jeu introuvable (launcher.ini du port, game_dir) : podiums rapides non installés.":
        "Game folder not found (port's launcher.ini, game_dir): fast podiums not installed.",
    "{file} retiré": "{file} removed",
    "{file} n'a plus d'options de confort : générez la graine à nouveau pour les remettre.":
        "{file} no longer has comfort options: generate the seed again to put them back.",

    # tirage et code de partage
    "aucune origine de circuits choisie (CTR, CNK ou GP)": "no track origin chosen (CTR, CNK or GP)",
    "{levels} niveaux pour {pads} portails : autoriser les doublons ou ajouter des origines":
        "{levels} levels for {pads} warp pads: allow duplicates or add origins",
    "impossible de tirer des conditions d'ouverture atteignables (essais épuisés)":
        "couldn't draw reachable opening requirements (attempts exhausted)",
    "mode de coupes inconnu : {mode}": "unknown cup mode: {mode}",
    "conditions inconnues : {pads} / {challenges}": "unknown requirements: {pads} / {challenges}",
    "graine hors limites": "seed out of range",
    "un code de partage a 12 caractères (lettres et chiffres)": "a share code has 12 characters (letters and digits)",
    "code mal recopié (la lettre de contrôle ne correspond pas)": "code copied wrong (the check letter doesn't match)",
    "code fait avec une autre version du randomizer": "code made with another version of the randomizer",
    "code mal recopié": "code copied wrong",
}
