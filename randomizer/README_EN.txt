CTR Nitro-Fueled Randomizer
===========================

(Version française : README.txt. The program itself is in French; button and option names are given below in
French with their English meaning.)

Randomizer for the Adventure mode of Crash Team Racing Nitro-Fueled, played on PC with the
OCTR-NitroFueled-PC port v0.5.1 or newer (https://github.com/Ryu7w7/OCTR-NitroFueled-PC). Older ports crash or
freeze during loading screens.

What it can shuffle:
- the tracks behind the warp pads (40 tracks: CTR, Crash Nitro Kart, Grand Prix) and the arenas of the crystal
  challenges (12 arenas);
- the rewards (trophies, boss keys, gems, CTR tokens, relics);
- the gem cups;
- what it takes to open each warp pad (trophies, keys, relics, gems or tokens);
- the locations of the warp pads in the hub (a battle or a cup can sit where a race used to be).
A logic check makes sure every seed can always be completed at 100%.
Comfort (« Confort » tab, each option has its own checkbox):
- skip Aku Aku's hints and the opening cutscenes of doors your keys have already opened;
- show your boost reserve in the drift bar (classic style) when you are not drifting;
- skip podiums right from the start, without waiting for the end of the animation.
With shuffled rewards, the hub minimap only ticks a warp pad once its 3 relics are won.

Good to know: the Slide Coliseum and Turbo Track pads only offer a relic race, as in the original game (no
trophy, no CTR challenge). They keep working this way whatever track they launch and wherever they are placed:
a pad that launches, say, Jungle Boogie may therefore only offer a relic.

Requirements
------------
- the game (version 01.21) installed with the PC port;
- nothing else: CTRNF-Randomizer.exe contains everything.

How to use
----------
1. Download CTRNF-Randomizer.exe from the repository's "Releases" page
   (https://github.com/kyogre21/ctrnf-modkit/releases/latest) and run it.
   Windows may show "Windows protected your PC" (unsigned program): click "More info" then "Run anyway".
2. Pick the port folder (the one containing bin, patches and out). The window checks the game version.
3. Type a seed (« Graine », or leave it empty), set the options in the tabs (hover an option to see its help).
4. Click « Générer et installer » (Generate and install): the patch goes into the port's patches folder, the seed
   and its spoiler log into graines_randomizer.
5. Start the game and begin a NEW adventure.

To play the normal game again: delete patches\Randomizer.xml in the port folder.

Files placed in the game folder
-------------------------------
Fast podiums and the relic ticks on the minimap change two game scripts. The program reads them from your own
archives, changes a few bytes and stores them in small archives of its own, which the game loads at startup, in
the game's archives folder (found through the port's launcher.ini):
- archives\update4.pak: relic ticks on the minimap (with shuffled rewards);
- archives\update_hub3.pak: podiums skippable from the start.
The game files are never modified: deleting these two archives restores the original game. The program removes
an archive itself when its option is turned off. It never touches archives\update3.pak, which belongs to the
sticker tool (autocollants folder of this repository).

With Python 3.10 or newer installed, you can also run the source code: « Lancer le randomizer.bat »,
or without a window: python -m ctrnf_rando --help

This repository contains no game files: you must own the game.

What's new
----------
0.4.0
- « Confort » (comfort) tab, new box (ticked by default): in relic races, the target shown under the timer starts
  at the platinum time. Once your timer goes past it, it switches to the gold time, then to the sapphire time, with
  that tier's icon and colour. Rewards do not change.
- The share code includes this option. Codes made with 0.3.x can still be read.

0.3.1
- Fixed: in a brand-new adventure (before the game was restarted once), a race you won could give nothing: the race
  was still offered and the item never came. It happened when the warp pad launches an Adventure track whose own
  original warp pad was already won (e.g. a pad that launches Crash Cove, after winning the Crash Cove pad). Game
  started with an older version: restart the game once, then play the race again.

0.3.0
- Share code: after « Générer et installer », a 12-character code (e.g. D0W0-09N5-2EH9) holds the seed and every
  option, comfort included. Your opponents paste it and click « Utiliser » (Use): same game, same fingerprint. Ideal
  to race on the same seed. A check letter catches typos.
- Presets: Découverte (Discovery), Classique (Classic) and Chaos buttons set the shuffle options in one click
  (comfort options are not changed).
- The randomizer can also be used inside the CTRNF Mod Kit (one tab).
- Fixed: no track origin ticked with "duplicates" did nothing; a seed like "²" crashed.
- update4.pak / update_hub3.pak are written in one go (never half-written, even with the game open); a
  Randomizer.xml that is not ours is never overwritten; launcher.ini with quotes is read correctly.

0.2.0
- « Confort » tab: two new checkboxes, ticked by default.
  - Boost reserve: when you are not drifting, the drift bar (classic style) shows your boost reserve. It fills up
    as you chain boosts (full = 5 s or more).
  - Fast podiums: the "press to skip" screen opens right at the start of the podium animation.
- The Aku Aku hints checkbox also skips the opening cutscenes of doors your keys have already opened.
- Shuffled rewards: the hub minimap only ticks a warp pad once its 3 relics are won.
- Fixed: the boss key you won stayed hidden behind the driver on the podium.
- Fixed: the boss cutscene now plays at the number of trophies its garage asks for, no longer when every race
  of the world is won.
- Fixed: in the progress menus, a cup moved onto a race row showed wrong icons; the row now shows the cup's
  name, without icons.
- « Lancer le randomizer.bat » points to CTRNF-Randomizer.exe when Python is not installed.
A seed generated with an earlier version must be generated again (same number) to get these additions.

0.1.1
- Fixed: crash when moving on to the 2nd race of a cup; "open" glow on a closed warp pad; progress menus
  showing the original pad instead of the one placed there.

Credits
-------
- Idea inspired by icebound777's CTR-Randomizer for the PS1 version
  (https://github.com/icebound777/CTR-Randomizer-Standalone, MIT license).
- PC port: CTR-NitroFueled-PC and its OCTR-NitroFueled-PC version.

License: MIT (LICENSE file).
