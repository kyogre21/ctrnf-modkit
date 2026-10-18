CTR Nitro-Fueled Randomizer
===========================

Randomizer pour le mode Aventure de Crash Team Racing Nitro-Fueled, joué sur PC avec le port
CTR-NitroFueled-PC (https://github.com/GetLostIn/CTR-NitroFueled-PC).

Ce qu'il peut mélanger :
- les circuits derrière les portails (40 circuits : CTR, Crash Nitro Kart, Grand Prix) et les arènes des
  défis cristaux (12 arènes) ;
- les récompenses (trophées, clés de boss, gemmes, jetons CTR, reliques) ;
- les coupes de gemmes ;
- ce qu'il faut pour ouvrir chaque portail (trophées, clés, reliques, gemmes ou jetons) ;
- les emplacements des portails au hub (une bataille ou une coupe peut se trouver à la place d'une course).
Une logique vérifie que chaque graine peut toujours être finie à 100 %.
Confort : les indices d'Aku Aku peuvent être passés.

Il faut
-------
- le jeu (version 01.21) installé avec le port PC ;
- rien d'autre : le programme CTRNF-Randomizer.exe contient tout.

Utilisation
-----------
1. Télécharger CTRNF-Randomizer.exe dans la page « Releases » du dépôt
   (https://github.com/kyogre21/ctrnf-randomizer/releases) et le lancer.
   Windows peut afficher « Windows a protégé votre ordinateur » (programme non signé) : cliquer sur
   « Informations complémentaires » puis « Exécuter quand même ».
2. Choisir le dossier du port (celui qui contient bin, patches et out). La fenêtre vérifie la version du jeu.
3. Taper une graine (ou la laisser vide), régler les options dans les onglets (la souris sur une option
   affiche son aide).
4. Cliquer sur « Générer et installer » : le patch est posé dans le dossier patches du port, la graine et
   son journal dans graines_randomizer.
5. Lancer le jeu et commencer une NOUVELLE aventure.

Pour rejouer au jeu normal : supprimer patches\Randomizer.xml dans le dossier du port.

Avec Python 3.10 ou plus récent installé, on peut aussi lancer le code source : « Lancer le randomizer.bat »,
ou sans fenêtre : python -m ctrnf_rando --help

Ce dépôt ne contient aucun fichier du jeu : il faut posséder le jeu.

Crédits
-------
- Idée inspirée du CTR-Randomizer d'icebound777 pour la version PS1
  (https://github.com/icebound777/CTR-Randomizer-Standalone, licence MIT).
- Port PC : CTR-NitroFueled-PC.

Licence : MIT (fichier LICENSE).
