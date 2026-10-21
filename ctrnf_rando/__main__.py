"""python -m ctrnf_rando [--seed N] [--out dossier] [--origins CTR,CNK,GP] [--doublons] [--sans-arenes]
                       [--recompenses] [--coupes coupes|circuits] [--conditions nombres|hasard]
                       [--defis ouverts|hasard] [--emplacements] [--sans-indices] [--reserve]
                       [--patch fichier.xml [--noms]]
(les archives du dossier du jeu, podiums rapides et mini-carte des reliques, ne sont posées que par la fenêtre)"""
import argparse
import json
from pathlib import Path
import random

from .generator import CHALLENGE_MODES, CUP_MODES, ORIGINS, PAD_MODES, Settings, generate, spoiler
from .patch import patch_xml
from .rewards import patch_rows


def main():
    parser = argparse.ArgumentParser(prog="ctrnf_rando", description="Tire une graine de randomizer.")
    parser.add_argument("--seed", type=int, help="graine (au hasard si absente)")
    parser.add_argument("--out", type=Path, default=Path("seeds"), help="dossier de sortie")
    parser.add_argument("--origins", default=",".join(ORIGINS),
                        help="origines des circuits tirés, parmi CTR,CNK,GP")
    parser.add_argument("--doublons", action="store_true", help="autoriser un même circuit deux fois")
    parser.add_argument("--sans-arenes", action="store_true", help="garder les arènes d'origine")
    parser.add_argument("--recompenses", action="store_true",
                        help="mélanger les trophées, clés, gemmes, jetons CTR et reliques (avec une logique)")
    parser.add_argument("--coupes", choices=CUP_MODES[1:],
                        help="coupes de gemmes : 5 coupes tirées parmi les 16 du jeu (coupes) ou 4 circuits au hasard "
                             "par coupe (circuits)")
    parser.add_argument("--conditions", choices=PAD_MODES[1:],
                        help="ce qu'il faut pour ouvrir la course de chaque portail, Slide Coliseum, Turbo Track, les "
                             "arènes et les coupes : nombre tiré, type d'origine (nombres), ou type et nombre tirés "
                             "parmi trophées, clés, reliques, gemmes et jetons (hasard) ; toujours atteignable")
    parser.add_argument("--defis", choices=CHALLENGE_MODES[1:],
                        help="défi CTR et relique d'un portail : ouverts dès son trophée gagné (ouverts), ou besoin "
                             "tiré au hasard parmi trophées, clés, reliques, gemmes et jetons (hasard)")
    parser.add_argument("--emplacements", action="store_true",
                        help="mélange les emplacements des portails au hub (courses, arènes, coupes, Slide, Turbo ; "
                             "pas les garages de boss) ; toujours finissable")
    parser.add_argument("--sans-indices", action="store_true",
                        help="confort : les indices d'Aku Aku sont marqués comme déjà vus (ils ne coupent plus la partie)")
    parser.add_argument("--reserve", action="store_true",
                        help="confort : hors dérapage, la barre de dérapage montre la réserve de boost")
    parser.add_argument("--patch", type=Path,
                        help="écrire aussi le patch du jeu (ex. <port>/patches/Randomizer.xml)")
    parser.add_argument("--noms", action="store_true",
                        help="avec --patch : au hub, les portails affichent le nom du circuit joué")
    args = parser.parse_args()

    origins = tuple(o.strip().upper() for o in args.origins.split(",") if o.strip())
    unknown = set(origins) - set(ORIGINS)
    if unknown:
        parser.error(f"origine inconnue : {', '.join(sorted(unknown))}")
    seed = args.seed if args.seed is not None else random.SystemRandom().randrange(1 << 32)
    settings = Settings(track_origins=origins, allow_duplicates=args.doublons,
                        shuffle_arenas=not args.sans_arenes, shuffle_rewards=args.recompenses,
                        shuffle_cups=args.coupes or "non", pad_conditions=args.conditions or "origine",
                        challenges=args.defis or "origine", skip_hints=args.sans_indices,
                        shuffle_locations=args.emplacements, boost_reserve=args.reserve)
    plan = generate(seed, settings)

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / f"graine_{seed}.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    text = spoiler(plan)
    (args.out / f"graine_{seed}_spoiler.txt").write_text(text, encoding="utf-8")
    print(text)
    if args.patch:
        try:
            rows = patch_rows(plan["rewards"]) if plan.get("rewards") else None
            xml = patch_xml(plan, rename=args.noms, rewards=rows)
        except ValueError as error:
            parser.error(str(error))
        args.patch.write_text(xml, encoding="utf-8", newline="\n")
        print(f"Patch écrit : {args.patch}")


if __name__ == "__main__":
    main()
