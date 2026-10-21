// Autosplitter LiveSplit pour Crash Team Racing Nitro-Fueled, port PC (CTR-NitroFueled-PC / OCTR, jeu v1.21).
// LiveSplit autosplitter for Crash Team Racing Nitro-Fueled, PC port (CTR-NitroFueled-PC / OCTR, game v1.21).
// Auteur / author : kyogre21 - https://github.com/kyogre21/ctrnf-modkit (licence MIT)
// Version : 0.1.1-alpha
// ALPHA : tout début de développement, à valider en jeu.
//
// Lit la partie en cours (lecture seule) : compteurs du mode Aventure et cinématiques vues.
// Reads the current game (read only): Adventure mode counters and viewed cutscenes.
// Le programme du jeu est chargé à l'adresse fixe 0x800000000 dans sacredfire.exe.

state("sacredfire") {}

startup
{
    settings.Add("start", true, "Départ auto : nouvelle aventure / Auto start: new adventure");
    settings.SetToolTip("start", "Démarre quand une partie neuve (aucun objet, aucune cinématique vue) arrive en jeu.\n"
        + "Starts when a fresh save (no items, no cutscene viewed) gets in game.");
    settings.Add("splits", true, "Splits (version alpha : à valider en jeu)");
    settings.Add("trophy", true, "Trophée gagné / Trophy won", "splits");
    settings.Add("key", true, "Clé de boss gagnée / Boss key won", "splits");
    settings.Add("relic", false, "Relique gagnée / Relic won", "splits");
    settings.Add("gem", false, "Gemme gagnée / Gem won", "splits");
    settings.Add("token", false, "Jeton CTR gagné / CTR token won", "splits");
    settings.Add("oxide1", true, "Oxide battu (1re fois) / Oxide beaten (1st time)", "splits");
    settings.Add("oxide2", true, "Oxide battu (2e défi, vraie fin) / Oxide beaten (2nd challenge, true ending)", "splits");
}

init
{
    current.slot = 0L;
    current.trophies = current.keys = current.gems = current.relics = current.tokens = current.total = 0;
    current.cutscenes = 0;
    current.zone = "";
    vars.lastRead = "";
    vars.lastZone = "";
    vars.zoneChanged = false;
}

update
{
    // Le jeu recalcule ses compteurs en partant de zéro (après chaque récompense, au hub…) : une lecture peut tomber
    // au milieu. Une valeur n'est donc prise que si deux lectures de suite sont identiques ; sinon on garde la
    // précédente, et `old` / `current` ne voient jamais d'état intermédiaire.
    IntPtr gm = game.ReadPointer((IntPtr)0x802acde48);                               // COctaneGameManager*
    IntPtr slot = gm == IntPtr.Zero ? IntPtr.Zero : game.ReadPointer(gm + 0xdc0);    // COctaneSaveSlotData*
    int[] c = new int[16];  // 0 trophées, 1 clés, 2-6 gemmes, 7-9 reliques (saphir, or, platine), 10-14 jetons CTR
    if (slot != IntPtr.Zero)
    {
        for (int i = 0; i < 15; i++)
            c[i] = game.ReadValue<int>(slot + 0xc + 4 * i);
        c[15] = game.ReadValue<int>(slot + 0x4c);                                      // cinématiques vues
    }
    string read = ((long)slot).ToString() + ":" + string.Join(",", c);
    bool stable = read == vars.lastRead;
    vars.lastRead = read;
    if (stable)
    {
        current.slot = (long)slot;
        current.trophies = c[0];
        current.keys = c[1];
        current.gems = c[2] + c[3] + c[4] + c[5] + c[6];
        current.relics = c[7] + c[8] + c[9];  // meilleur palier par circuit : saphir -> or ne change pas la somme
        current.tokens = c[10] + c[11] + c[12] + c[13] + c[14];
        int total = 0;
        for (int i = 0; i < 15; i++)
            total += c[i];
        current.total = total;
        current.cutscenes = c[15];
    }
    else
    {
        current.slot = old.slot;
        current.trophies = old.trophies;
        current.keys = old.keys;
        current.gems = old.gems;
        current.relics = old.relics;
        current.tokens = old.tokens;
        current.total = old.total;
        current.cutscenes = old.cutscenes;
    }
    IntPtr client = game.ReadPointer((IntPtr)0x802ab3cd8);                            // CClient*
    IntPtr name = client == IntPtr.Zero ? IntPtr.Zero : game.ReadPointer(client + 0xc0);  // zone en cours
    current.zone = name == IntPtr.Zero ? "" : (game.ReadString(name, ReadStringType.UTF8, 64) ?? "");
    // changement de zone, en sautant les lectures vides (nom absent pendant un chargement)
    vars.zoneChanged = current.zone != "" && vars.lastZone != "" && current.zone != vars.lastZone;
    if (current.zone != "")
        vars.lastZone = current.zone;
}

start
{
    // partie neuve (rien gagné, aucune cinématique vue) qui passe d'un menu à une zone de jeu
    return settings["start"] && current.slot != 0 && current.total == 0 && current.cutscenes == 0
        && vars.zoneChanged && !current.zone.Contains("startscreen") && !current.zone.Contains("menu");
}

split
{
    // autre sauvegarde chargée (ou retour aux menus) : pas de split
    if (current.slot != old.slot || current.slot == 0 || current.total < old.total || current.total > old.total + 3)
        return false;
    int seen = current.cutscenes & ~old.cutscenes;
    return settings["trophy"] && current.trophies > old.trophies
        || settings["key"] && current.keys > old.keys
        || settings["relic"] && current.relics > old.relics
        || settings["gem"] && current.gems > old.gems
        || settings["token"] && current.tokens > old.tokens
        || settings["oxide1"] && (seen & 0x800) != 0    // Oxide Outro 1
        || settings["oxide2"] && (seen & 0x1000) != 0;  // Oxide Outro 2
}
