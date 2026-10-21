Autosplitter LiveSplit (CTR Nitro-Fueled, port PC) — ALPHA
==========================================================

(English version: README_EN.txt)

Fichier : CTRNF.asl. LiveSplit le charge et coupe le chrono tout seul pendant le mode Aventure, sur le port PC
(CTR-NitroFueled-PC / OCTR-NitroFueled-PC, jeu en version 01.21). Il ne fait que lire la partie : il ne change rien au
jeu. Il marche avec ou sans le randomizer (avec les récompenses mélangées, il coupe sur l'objet reçu).

Installation
------------
1. Installer LiveSplit (https://livesplit.org), version 1.8 ou plus récente.
2. Clic droit sur LiveSplit > « Edit Layout… » > « + » > « Control » > « Scriptable Auto Splitter ».
3. Double-cliquer sur la ligne ajoutée, « Browse… », choisir CTRNF.asl.
4. Cocher ce qui doit couper le chrono (voir ci-dessous), puis OK et enregistrer le layout.
5. Préparer ses splits (clic droit > « Edit Splits… ») : un segment par split attendu, dans l'ordre.

Réglages
--------
- Départ auto : le chrono part quand une partie neuve (rien gagné, aucune cinématique vue) arrive en jeu.
- Splits, chacun se coche à part :
  trophée gagné (oui), clé de boss gagnée (oui), relique (non), gemme (non), jeton CTR (non),
  Oxide battu la 1re fois (oui), Oxide battu au 2e défi = vraie fin (oui).
Charger une autre sauvegarde ne déclenche pas de split.

Pas encore : retrait des temps de chargement (le chrono compte le temps réel).

Version ALPHA : tout début de développement. À vérifier en jeu (départ auto, chaque type de split, fin d'Oxide).
