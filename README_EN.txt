CTR Nitro-Fueled Mod Kit (kyogre21)
===================================

(Version française : README.txt. The programs themselves are in French; each mod's README_EN.txt gives button and
option names in French with their English meaning.)

kyogre21's mods for Crash Team Racing Nitro-Fueled on PC (CTR-NitroFueled-PC / OCTR-NitroFueled-PC port, game
version 01.21), gathered in a single repository.

The Mod Kit
-----------
CTRNF-ModKit.exe gathers every mod in one window: pick the port folder once, enable the mods you want (one tab per
mod), see the files they placed, uninstall everything in one click, then "Lancer le jeu" (Launch the game), which
opens the port's official launcher. If the game crashes, the kit shows a readable report to copy.
The kit is in English or French ("Language" list at the top right).
Source code: modkit folder.

The mods
--------
- Randomizer (randomizer folder): shuffles the Adventure mode (tracks, rewards, cups, unlock conditions, warp pad
  locations), always beatable, with comfort options.
  Program: CTRNF-Randomizer.exe. Guide: randomizer\README_EN.txt.
- Stickers (autocollants folder): replaces the kart stickers (and their menu icons) with your own images.
  Program: CTRNF-Stickers.exe. Guide: autocollants\README_EN.txt.
- LiveSplit autosplitter, ALPHA version (autosplitter folder): splits automatically during Adventure mode. Very
  early development. Guide: autosplitter\README_EN.txt.
- Comfort (Mod Kit tab): the randomizer's comfort options on the original game, without a seed (relic race target
  per tier, boost reserve, fast podiums, Aku Aku hints), and "Restart / Continue" at the end of every relic race
  (won or lost), to try for a better tier without going back to the hub. Your game and saves do not change.
Each mod's program is still available on its own, but the Mod Kit contains them all.

Download
--------
The ready-to-run programs (nothing to install) are on the "Releases" page:
https://github.com/kyogre21/ctrnf-modkit/releases/latest
Windows may show "Windows protected your PC" (unsigned program): click "More info" then "Run anyway".

Using several mods together
---------------------------
The mods are made to work together. None of them modifies the game files: each one places its own small archives
in the game's archives folder, and they never overlap:
- stickers: archives\update3.pak;
- randomizer: archives\update4.pak (relic minimap) and archives\update_hub3.pak (fast podiums),
  plus patches\Randomizer.xml in the port folder;
- comfort: patches\Confort.xml, archives\update_hub3.pak (fast podiums) and archives\update5.pak
  (Restart / Continue). When Confort.xml is there, its settings replace the seed's comfort settings (no option is
  applied twice).
The game reads update3.pak, update4.pak then update5.pak in order and stops at the first missing one: when a slot
is empty before one of these archives (no stickers, for example), the kit places a "placeholder" there (a game file
copied unchanged, no effect), removed once it is no longer needed.

This repository contains no game files: you must own the game.

Credits
-------
- Author: kyogre21.
- Randomizer idea inspired by icebound777's CTR-Randomizer for the PS1 version
  (https://github.com/icebound777/CTR-Randomizer-Standalone, MIT license).
- PC port: CTR-NitroFueled-PC and its OCTR-NitroFueled-PC version.

License: MIT (LICENSE file). You may use, modify and share these mods, as long as you keep the author's name.
