CTR Nitro-Fueled Randomizer
===========================

(English version: README_EN.txt)

Randomizer pour le mode Aventure de Crash Team Racing Nitro-Fueled, joué sur PC avec le port
OCTR-NitroFueled-PC v0.5.1 ou plus récent (https://github.com/Ryu7w7/OCTR-NitroFueled-PC). Les ports plus
anciens plantent ou se figent pendant les chargements.

Ce qu'il peut mélanger :
- les circuits derrière les portails (40 circuits : CTR, Crash Nitro Kart, Grand Prix) et les arènes des
  défis cristaux (12 arènes) ;
- les récompenses (trophées, clés de boss, gemmes, jetons CTR, reliques) ;
- les coupes de gemmes ;
- ce qu'il faut pour ouvrir chaque portail (trophées, clés, reliques, gemmes ou jetons) ;
- les emplacements des portails au hub (une bataille ou une coupe peut se trouver à la place d'une course).
Une logique vérifie que chaque graine peut toujours être finie à 100 %.
Confort (onglet « Confort », chaque option se coche à part) :
- passer les indices d'Aku Aku et les cinématiques d'ouverture des portes déjà ouvertes par vos clés ;
- afficher la réserve de boost dans la barre de dérapage (style classique), quand vous ne dérapez pas ;
- pouvoir passer les podiums dès le début, sans attendre la fin de l'animation.
Avec les récompenses mélangées, la mini-carte du hub ne coche un portail que quand ses 3 reliques sont gagnées.

Bon à savoir : les portails Slide Coliseum et Turbo Track ne proposent qu'une course à relique, comme dans
le jeu d'origine (ni trophée, ni défi CTR). Ils gardent ce fonctionnement quel que soit le circuit qu'ils
lancent et l'endroit où ils sont posés : un portail qui lance par exemple Jungle Boogie peut donc ne
proposer qu'une relique.

Il faut
-------
- le jeu (version 01.21) installé avec le port PC ;
- rien d'autre : le programme CTRNF-Randomizer.exe contient tout.

Utilisation
-----------
1. Télécharger CTRNF-Randomizer.exe dans la page « Releases » du dépôt
   (https://github.com/kyogre21/ctrnf-modkit/releases/latest) et le lancer.
   Windows peut afficher « Windows a protégé votre ordinateur » (programme non signé) : cliquer sur
   « Informations complémentaires » puis « Exécuter quand même ».
2. Choisir le dossier du port (celui qui contient bin, patches et out). La fenêtre vérifie la version du jeu.
3. Taper une graine (ou la laisser vide), régler les options dans les onglets (la souris sur une option
   affiche son aide).
4. Cliquer sur « Générer et installer » : le patch est posé dans le dossier patches du port, la graine et
   son journal dans graines_randomizer.
5. Lancer le jeu et commencer une NOUVELLE aventure.

Pour rejouer au jeu normal : supprimer patches\Randomizer.xml dans le dossier du port.

Fichiers posés dans le dossier du jeu
-------------------------------------
Les podiums rapides et la coche des reliques sur la mini-carte modifient deux scripts du jeu. Le logiciel les
lit dans vos archives, les modifie de quelques octets et les pose dans de petites archives à lui, que le jeu
charge au démarrage, dans le dossier archives du jeu (trouvé grâce à launcher.ini du port) :
- archives\update4.pak : coche des reliques sur la mini-carte (avec les récompenses mélangées) ;
- archives\update_hub3.pak : podiums passables dès le début.
Les fichiers du jeu ne sont jamais modifiés : supprimer ces deux archives remet le jeu d'origine. Le logiciel
retire lui-même une archive quand l'option correspondante est coupée. Il ne touche jamais à
archives\update3.pak, qui appartient à l'outil des autocollants (dossier autocollants de ce dépôt).

Avec Python 3.10 ou plus récent installé, on peut aussi lancer le code source : « Lancer le randomizer.bat »,
ou sans fenêtre : python -m ctrnf_rando --help

Ce dépôt ne contient aucun fichier du jeu : il faut posséder le jeu.

Nouveautés
----------
0.2.0
- Onglet « Confort » : deux nouvelles cases, cochées par défaut.
  - Réserve de boost : quand vous ne dérapez pas, la barre de dérapage (style classique) montre votre
    réserve de boost. Elle se remplit quand vous enchaînez les turbos (pleine = 5 s ou plus).
  - Podiums rapides : l'écran « appuyez pour passer » s'ouvre dès le début de l'animation du podium.
- La case des indices d'Aku Aku passe aussi les cinématiques d'ouverture des portes déjà ouvertes par vos clés.
- Récompenses mélangées : la mini-carte du hub ne coche un portail que quand ses 3 reliques sont gagnées.
- Corrigé : la clé de boss gagnée restait cachée derrière le pilote sur le podium.
- Corrigé : la cinématique du boss se lance au nombre de trophées demandé par son garage, et non plus quand
  toutes les courses du monde sont gagnées.
- Corrigé : dans les menus de progression, une coupe déplacée sur une ligne de course faussait les icônes ;
  la ligne montre maintenant le nom de la coupe, sans icône.
- « Lancer le randomizer.bat » renvoie vers CTRNF-Randomizer.exe quand Python n'est pas installé.
Une graine générée avec une version précédente doit être regénérée (même numéro) pour avoir ces ajouts.

0.1.1
- Corrigé : plantage au passage à la 2e course d'une coupe ; halo « ouvert » sur un portail fermé ; menus de
  progression qui montraient le portail d'origine au lieu de celui posé à cet endroit.

Crédits
-------
- Idée inspirée du CTR-Randomizer d'icebound777 pour la version PS1
  (https://github.com/icebound777/CTR-Randomizer-Standalone, licence MIT).
- Port PC : CTR-NitroFueled-PC et sa version OCTR-NitroFueled-PC.

Licence : MIT (fichier LICENSE).
