LiveSplit autosplitter (CTR Nitro-Fueled, PC port) — ALPHA
==========================================================

(Version française : README.txt)

File: CTRNF.asl. LiveSplit loads it and splits automatically during Adventure mode, on the PC port
(CTR-NitroFueled-PC / OCTR-NitroFueled-PC, game version 01.21). It only reads the game: it changes nothing. It works
with or without the randomizer (with shuffled rewards, it splits on the item you receive).

Install
-------
1. Install LiveSplit (https://livesplit.org), version 1.8 or newer.
2. Right-click LiveSplit > "Edit Layout…" > "+" > "Control" > "Scriptable Auto Splitter".
3. Double-click the new row, "Browse…", pick CTRNF.asl.
4. Tick what should split (see below), then OK and save the layout.
5. Set up your splits (right-click > "Edit Splits…"): one segment per expected split, in order.

Settings
--------
- Auto start: the timer starts when a fresh save (nothing won, no cutscene viewed) gets in game.
- Splits, each one ticked separately:
  trophy won (on), boss key won (on), relic (off), gem (off), CTR token (off),
  Oxide beaten the 1st time (on), Oxide beaten in the 2nd challenge = true ending (on).
Loading another save does not trigger a split.

Not yet: load time removal (the timer counts real time).

ALPHA version: very early development. To be checked in game (auto start, each split type, Oxide ending).
