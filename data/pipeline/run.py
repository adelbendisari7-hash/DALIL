"""Pipeline de données de diagnostic (étape 6), rejouable par une commande.

    python data/pipeline/run.py all                          # collecte + chargement + rapport (sans traduction)
    python data/pipeline/run.py all --translate opus         # idem avec traduction (GPU conseillé : Kaggle)
    python data/pipeline/run.py collect --sources rappelconso,cvffad --limit 100
    python data/pipeline/run.py translate --sources nhtsa_complaints --limit 300 --review 200
    python data/pipeline/run.py load                         # base de connaissances + jeux d'entraînement
    python data/pipeline/run.py report

Chaque étape lit et écrit des fichiers (data/raw -> data/processed) : on peut relancer n'importe
laquelle sans refaire les autres. Les téléchargements sont mis en cache dans data/raw/.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # dossier data/ -> paquet « pipeline »

from pipeline.common import PROCESSED, write_jsonl  # noqa: E402
from pipeline.load import export_training, load_source, summary  # noqa: E402
from pipeline.sources import SOURCES, Context  # noqa: E402


def collectors() -> dict:
    from pipeline.sources import cvffad, mot, nhtsa, rappelconso, stackexchange

    return {
        "nhtsa_complaints": nhtsa.collect_complaints, "nhtsa_recalls": nhtsa.collect_recalls,
        "rappelconso": rappelconso.collect, "mot_uk": mot.collect,
        "stackexchange_mechanics": stackexchange.collect, "cvffad": cvffad.collect,
    }


def path_for(source_id: str) -> Path:
    return PROCESSED / f"{source_id}.jsonl"


def cmd_collect(ids: list[str], ctx: Context) -> None:
    funcs = collectors()
    for sid in ids:
        t0 = time.time()
        ctx.log(f"[collecte] {sid}")
        n = write_jsonl(path_for(sid), funcs[sid](ctx))
        s = summary(path_for(sid))
        ctx.log(f"  {n} enregistrements, {s['with_family']} reliés à la taxonomie, {s['with_fault']} à une panne type "
                f"({time.time() - t0:.0f} s)")


def cmd_translate(ids: list[str], backend: str, limit: int | None, review: int, log, redo_uppercase: bool = False) -> None:
    from pipeline.translate import Translator, review_sample, translate_file

    tr = Translator(backend=backend, log=log)
    for sid in ids:
        p = path_for(sid)
        if not p.exists():
            continue
        done, remaining = translate_file(p, tr, limit, redo_uppercase=redo_uppercase)
        log(f"[traduction] {sid} : {done} traduits, {remaining} restants")
    if review:
        out = review_sample([path_for(s) for s in ids if path_for(s).exists()], n=review)
        if out:
            log(f"[traduction] échantillon de relecture : {out}")


def cmd_load(ids: list[str], log) -> None:
    from app.db import SessionLocal

    with SessionLocal() as db:
        for sid in ids:
            p = path_for(sid)
            if not p.exists():
                log(f"[chargement] {sid} : rien à charger (lancer la collecte)")
                continue
            res = load_source(db, sid, p)
            n_train = export_training(sid, p)
            log(f"[chargement] {sid} : {res['chunks']} passages ({res['chunks_fr']} en français, indexés), {n_train} exemples d'entraînement")


def cmd_report(log) -> Path:
    lines = [
        "# Rapport du pipeline de données (étape 6)", "",
        f"Généré le {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC par `python data/pipeline/run.py report`.", "",
        "| Source | Licence | Enregistrements | Reliés à une famille | À une sous-famille | À une panne type | Traduits / en français |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    data = {}
    for sid, spec in SOURCES.items():
        p = path_for(sid)
        if not p.exists():
            lines.append(f"| {spec.name} | {spec.license} | non collectée | | | | |")
            continue
        s = summary(p)
        data[sid] = s
        pct = lambda k: f"{s[k]} ({s[k] * 100 // max(s['records'], 1)} %)"  # noqa: E731
        lines.append(f"| {spec.name}{' (synthétique)' if spec.synthetic else ''} | {spec.license} | {s['records']} | "
                     f"{pct('with_family')} | {pct('with_category')} | {pct('with_fault')} | {pct('translated_fr')} |")
    lines += ["", "Les étiquettes sont obtenues par mots-clés (voir `data/pipeline/taxonomy_map.py`) : elles servent à "
              "l'entraînement, jamais à l'évaluation, qui se fait sur le jeu de test d'Oran annoté par des mécaniciens."]
    out = PROCESSED / "report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (PROCESSED / "report.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"[rapport] {out}")
    return out


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["all", "collect", "translate", "load", "report"])
    ap.add_argument("--sources", default="all", help=f"liste séparée par des virgules parmi : {', '.join(SOURCES)}")
    ap.add_argument("--limit", type=int, default=None, help="nombre maximal d'enregistrements par source (essais)")
    ap.add_argument("--refresh", action="store_true", help="ignorer le cache et retélécharger")
    ap.add_argument("--translate", "--backend", dest="backend", default=None, choices=["opus", "none"],
                    help="moteur de traduction (all : aucune traduction par défaut ; translate : opus par défaut)")
    ap.add_argument("--review", type=int, default=0, help="taille de l'échantillon de relecture des traductions")
    ap.add_argument("--mot-year", type=int, default=2023)
    ap.add_argument("--redo-uppercase", action="store_true", help="retraduire les textes écrits en capitales")
    args = ap.parse_args(argv)

    ids = list(SOURCES) if args.sources == "all" else [s.strip() for s in args.sources.split(",")]
    unknown = [s for s in ids if s not in SOURCES]
    if unknown:
        ap.error(f"source(s) inconnue(s) : {', '.join(unknown)}")
    log = lambda m: print(m, flush=True)  # noqa: E731
    ctx = Context(limit=args.limit, refresh=args.refresh, options={"mot_year": args.mot_year}, log=log)

    if args.command in ("all", "collect"):
        cmd_collect(ids, ctx)
    if args.command == "translate" or (args.command == "all" and args.backend == "opus"):
        cmd_translate(ids, args.backend or "opus", args.limit, args.review, log, redo_uppercase=args.redo_uppercase)
    if args.command in ("all", "load"):
        cmd_load(ids, log)
    if args.command in ("all", "report", "collect", "load"):
        cmd_report(log)


if __name__ == "__main__":
    main()
