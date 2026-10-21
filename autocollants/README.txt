CTR Nitro-Fueled Autocollants
=============================

(English version: README_EN.txt)

Petit logiciel pour remplacer les autocollants des karts de Crash Team Racing Nitro-Fueled (et leurs icônes dans le
menu de personnalisation) par ses propres images, sur PC avec le port CTR-NitroFueled-PC
(https://github.com/GetLostIn/CTR-NitroFueled-PC).

Les archives du jeu ne sont jamais modifiées : les images remplacées vont dans une petite archive à part,
archives\update3.pak, que le jeu charge au démarrage après ses propres mises à jour.

Il faut
-------
- le jeu (version 01.21) installé avec le port PC ;
- rien d'autre : le programme CTRNF-Stickers.exe contient tout.

Utilisation
-----------
1. Télécharger CTRNF-Stickers.exe dans la page « Releases » du dépôt
   (https://github.com/kyogre21/ctrnf-stickers/releases/latest) et le lancer.
   Windows peut afficher « Windows a protégé votre ordinateur » (programme non signé) : cliquer sur
   « Informations complémentaires » puis « Exécuter quand même ».
2. Choisir le dossier du jeu (celui qui contient « archives », par exemple CUSA13795-1.21) ou le dossier du port
   (le logiciel lit alors son launcher.ini).
3. Choisir un autocollant dans la liste (ou une icône du menu), regarder l'aperçu.
4. « Remplacer par une image… » : PNG, JPG, WebP, GIF, BMP, TGA… L'image est ajustée à la taille de l'autocollant
   sans être déformée ; la transparence d'un PNG est gardée. C'est enregistré tout de suite.
   Option « Détourer l'image » (décochée au départ) : le fond uni autour du dessin (blanc, couleur unie…) devient
   transparent et l'image est recadrée sur le dessin. Pratique pour un logo trouvé sur fond blanc ; à laisser
   décochée pour une image qui doit garder son fond.
5. Lancer le jeu (ou le relancer s'il était ouvert : il ne lit les autocollants qu'au démarrage).

Bon à savoir
------------
- « Enregistrer en PNG… » sort l'image d'un autocollant : pratique pour la retoucher puis la remettre.
- Dans le menu de personnalisation, chaque autocollant a une icône, qui est une image à part. Avec la case
  « Remplacer aussi son icône » (cochée au départ), elle est remplacée en même temps que l'autocollant, et
  « Remettre l'original » remet les deux. Le lien autocollant ↔ icône est une table du logiciel (icons.py), faite
  en comparant les images : 225 autocollants ont leur icône. Les autres (doubles chiffres Sticker_00 à 09, Twilight
  Tour, Sour Patch Kids…) n'ont pas d'icône connue ; leur icône se change à la main dans la liste « Icônes du menu ».
- Pour tout remettre d'origine : bouton « Tout remettre d'origine », ou supprimer archives\update3.pak.

Avec Python 3.10 ou plus récent installé, on peut aussi lancer le code source : « Lancer les autocollants.bat ».
Fabriquer l'exe : « Construire exe.bat » (résultat dans dist).

Ce dépôt ne contient aucun fichier du jeu : il faut posséder le jeu.

Licence : MIT (fichier LICENSE).
