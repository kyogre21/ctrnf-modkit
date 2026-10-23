CTR Nitro-Fueled Mod Kit (kyogre21)
===================================

(English version: README_EN.txt)

Les mods de kyogre21 pour Crash Team Racing Nitro-Fueled sur PC (port CTR-NitroFueled-PC / OCTR-NitroFueled-PC,
jeu en version 01.21), réunis dans un seul dépôt.

Le Mod Kit
----------
CTRNF-ModKit.exe réunit tous les mods dans une seule fenêtre : choisir une fois le dossier du port, activer les mods
voulus (un onglet par mod), voir les fichiers qu'ils ont posés, tout désinstaller d'un clic, puis « Lancer le jeu »,
qui ouvre le launcher officiel du port. En cas de plantage du jeu, le kit affiche un rapport lisible à copier.
Le kit est en français ou en anglais (liste « Langue » en haut à droite).
Code source : dossier modkit.

Les mods
--------
- Randomizer (dossier randomizer) : mélange le mode Aventure (circuits, récompenses, coupes, conditions
  d'ouverture, emplacements des portails), toujours finissable, avec des options de confort.
  Programme : CTRNF-Randomizer.exe. Mode d'emploi : randomizer\README.txt.
- Autocollants (dossier autocollants) : remplace les autocollants des karts (et leurs icônes du menu) par vos
  propres images.
  Programme : CTRNF-Stickers.exe. Mode d'emploi : autocollants\README.txt.
- Autosplitter LiveSplit, version ALPHA (dossier autosplitter) : coupe le chrono tout seul pendant le mode
  Aventure. Tout début de développement. Mode d'emploi : autosplitter\README.txt.
- Confort (onglet du Mod Kit) : les options de confort du randomizer sur le jeu d'origine, sans graine (cible des
  reliques par palier, réserve de boost, podiums rapides, indices d'Aku Aku), et « Recommencer / Continuer » à la
  fin de chaque course relique (gagnée ou perdue), pour retenter un meilleur palier sans repasser par le hub.
  Partie et sauvegardes inchangées.
Les programmes de chaque mod restent disponibles seuls, mais le Mod Kit les contient tous.

Télécharger
-----------
Les programmes prêts à lancer (rien à installer) sont dans la page « Releases » :
https://github.com/kyogre21/ctrnf-modkit/releases/latest
Windows peut afficher « Windows a protégé votre ordinateur » (programme non signé) : cliquer sur
« Informations complémentaires » puis « Exécuter quand même ».

Utiliser plusieurs mods ensemble
--------------------------------
Les mods sont faits pour aller ensemble. Aucun ne modifie les fichiers du jeu : chacun pose ses propres petites
archives dans le dossier archives du jeu, et elles ne se chevauchent pas :
- autocollants : archives\update3.pak ;
- randomizer : archives\update4.pak (mini-carte des reliques) et archives\update_hub3.pak (podiums rapides),
  plus patches\Randomizer.xml dans le dossier du port ;
- confort : patches\Confort.xml, archives\update_hub3.pak (podiums rapides) et archives\update5.pak
  (Recommencer / Continuer). Quand Confort.xml est là, ses réglages remplacent ceux de confort de la graine
  (aucune option posée deux fois).
Le jeu lit update3.pak, update4.pak puis update5.pak dans l'ordre et s'arrête au premier absent : quand une place
manque avant l'une de ces archives (pas d'autocollants, par exemple), le kit y pose un « bouche-trou » (un fichier
du jeu recopié à l'identique, sans effet), retiré quand il ne sert plus.

Ce dépôt ne contient aucun fichier du jeu : il faut posséder le jeu.

Crédits
-------
- Auteur : kyogre21.
- Idée du randomizer inspirée du CTR-Randomizer d'icebound777 pour la version PS1
  (https://github.com/icebound777/CTR-Randomizer-Standalone, licence MIT).
- Port PC : CTR-NitroFueled-PC et sa version OCTR-NitroFueled-PC.

Licence : MIT (fichier LICENSE). Vous pouvez utiliser, modifier et repartager ces mods, à condition de garder le
nom de l'auteur.
