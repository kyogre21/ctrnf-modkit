CTR Nitro-Fueled Stickers
=========================

(Version française : README.txt. The program itself is in French; button and option names are given below in
French with their English meaning.)

Small program to replace the kart stickers of Crash Team Racing Nitro-Fueled (and their icons in the
customization menu) with your own images, on PC with the CTR-NitroFueled-PC port
(https://github.com/GetLostIn/CTR-NitroFueled-PC).

The game archives are never modified: replaced images go into a small separate archive,
archives\update3.pak, which the game loads at startup after its own updates.

Requirements
------------
- the game (version 01.21) installed with the PC port;
- nothing else: CTRNF-Stickers.exe contains everything.

How to use
----------
1. Download CTRNF-Stickers.exe from the repository's "Releases" page
   (https://github.com/kyogre21/ctrnf-stickers/releases/latest) and run it.
   Windows may show "Windows protected your PC" (unsigned program): click "More info" then "Run anyway".
2. Pick the game folder (the one containing "archives", for example CUSA13795-1.21) or the port folder
   (the program then reads its launcher.ini).
3. Pick a sticker in the list (or a menu icon) and look at the preview.
4. « Remplacer par une image… » (Replace with an image…): PNG, JPG, WebP, GIF, BMP, TGA… The image is fitted to
   the sticker's size without being stretched; PNG transparency is kept. It is saved right away.
   « Détourer l'image » option (Cut out the image, unticked by default): the plain background around the drawing
   (white, solid color…) becomes transparent and the image is cropped to the drawing. Handy for a logo found on a
   white background; leave it unticked for an image that must keep its background.
5. Start the game (or restart it if it was open: it only reads stickers at startup).

Good to know
------------
- « Enregistrer en PNG… » (Save as PNG…) exports a sticker's image: handy to edit it and put it back.
- In the customization menu, each sticker has an icon, which is a separate image. With the « Remplacer aussi son
  icône » checkbox (Also replace its icon, ticked by default), it is replaced together with the sticker, and
  « Remettre l'original » (Restore the original) restores both. The sticker ↔ icon link is a table in the program
  (icons.py), built by comparing the images: 225 stickers have their icon. The others (double digits Sticker_00
  to 09, Twilight Tour, Sour Patch Kids…) have no known icon; their icon can be changed by hand in the « Icônes
  du menu » list (Menu icons).
- To restore everything: « Tout remettre d'origine » button (Restore everything), or delete
  archives\update3.pak.

With Python 3.10 or newer installed, you can also run the source code: « Lancer les autocollants.bat ».
Building the exe: « Construire exe.bat » (output in dist).

This repository contains no game files: you must own the game.

License: MIT (LICENSE file).
