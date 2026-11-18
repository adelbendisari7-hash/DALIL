"""Anonymise une collecte d'annonces Ouedkniss (JSONL) avant tout usage dans DALIL.

    python data/scripts/anonymiser_ouedkniss.py ENTREE.jsonl SORTIE.jsonl [--csv SORTIE.csv]

- Retire les champs qui identifient un vendeur ou une annonce : seller_id, seller_username, url, image_url.
- Remplace l'identifiant d'annonce par une empreinte (HMAC avec un sel aléatoire, jamais enregistré) : les doublons
  restent repérables dans le fichier, mais l'annonce ne peut plus être retrouvée sur le site.
- Efface du titre et de la description : numéros de téléphone algériens (mobiles 05/06/07, fixes 02 à 04, avec ou
  sans +213 / 00213, séparateurs compris, chiffres arabes compris), adresses e-mail, liens, comptes « @ ».
- Garde le reste (marque, modèle, version, année, motorisation, kilométrage, prix, wilaya, date) : seules des
  statistiques agrégées en sont tirées (docs/etude-marche-algerie.md). Autorisation d'Ouedkniss : data/SOURCES.md.

Le script ne modifie ni ne supprime le fichier d'entrée. Rejouable : relancé, il réécrit la sortie.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import hmac
import json
import re
import secrets
from collections import Counter
from pathlib import Path

DROP_FIELDS = ("seller_id", "seller_username", "url", "image_url")
TEXT_FIELDS = ("title", "description")
ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
# Séparateurs entre groupes de chiffres : jusqu'à 5 signes non alphanumériques (« 05//50//12 », « 05 - 50 », « 05''50 »,
# « 05🔹50 »). Un numéro commence toujours par 0[2-7] ou 213 : les années, kilométrages et prix ne sont pas touchés.
SEP = r"(?:[^\w\n]|[_xX]){0,5}"  # « _ » et « x » aussi : « Contactez_05_50_… », « 05x50x12x34x56 »
# Chiffres cachés entre des lettres arabes pour échapper aux filtres (« 0سيا5ر5ة0 … ») : mobiles seulement.
AR_SEP = r"[\s؀-ۿ]{0,6}"
PATTERNS = [
    # mobiles : 0X ou +213 X ou 00213 X, puis 8 chiffres (X = 5, 6 ou 7)
    ("[téléphone]", re.compile(rf"(?<!\d)(?:(?:\+|00){SEP}213{SEP}0?|0){SEP}[5-7](?:{SEP}\d){{8}}(?!\d)")),
    # mobiles dont les chiffres sont séparés par des lettres arabes
    ("[téléphone]", re.compile(rf"(?<!\d)0{AR_SEP}[5-7](?:{AR_SEP}\d){{8}}(?!\d)")),
    # mobiles dont les chiffres sont séparés par une ou deux lettres ou signes quelconques (« 0550123H4567 »)
    ("[téléphone]", re.compile(r"(?<!\d)0[^\d\n]{0,2}[5-7](?:[^\d\n]{0,2}\d){8}(?!\d)")),
    # mobiles écrits sans le 0 initial : 9 chiffres collés commençant par 5, 6 ou 7
    ("[téléphone]", re.compile(r"(?<!\d)[5-7]\d{8}(?!\d)")),
    # fixes : 0 + indicatif 2 à 4 + 7 chiffres (ex. 041 23 45 67), avec ou sans +213
    ("[téléphone]", re.compile(rf"(?<!\d)(?:(?:\+|00){SEP}213{SEP}0?|0){SEP}[2-4](?:{SEP}\d){{7}}(?!\d)")),
    ("[e-mail]", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    ("[lien]", re.compile(r"(?:https?://|www\.)\S*", re.IGNORECASE)),
    ("[compte]", re.compile(r"(?<![\w@])@[^\s@]{2,}")),
]


def scrub(text: str, counts: Counter) -> str:
    # Émojis chiffres (0️⃣ = chiffre + U+FE0F + U+20E3) -> chiffres ; chiffres arabes -> chiffres latins
    t = (text or "").replace("️", "").replace("⃣", "").translate(ARABIC_DIGITS)
    for label, pat in PATTERNS:
        t, n = pat.subn(label, t)
        counts[label] += n
    return t


def anonymize(row: dict, salt: bytes, counts: Counter) -> dict:
    out = {k: v for k, v in row.items() if k not in DROP_FIELDS}
    if row.get("id") is not None:
        out["id"] = hmac.new(salt, str(row["id"]).encode(), hashlib.sha256).hexdigest()[:16]
    for f in TEXT_FIELDS:
        if out.get(f):
            out[f] = scrub(out[f], counts)
    return out


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entree", type=Path)
    ap.add_argument("sortie", type=Path)
    ap.add_argument("--csv", type=Path, help="écrire aussi une version CSV")
    args = ap.parse_args(argv)
    if args.entree.resolve() == args.sortie.resolve():
        raise SystemExit("la sortie doit être un autre fichier que l'entrée")

    salt = secrets.token_bytes(32)  # jamais écrit : l'empreinte ne peut pas être inversée
    counts: Counter = Counter()
    n = 0
    fields: list[str] = []
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    with args.entree.open(encoding="utf-8") as src, args.sortie.open("w", encoding="utf-8") as dst:
        for line in src:
            if not line.strip():
                continue
            row = anonymize(json.loads(line), salt, counts)
            for k in row:
                if k not in fields:
                    fields.append(k)
            dst.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
    if args.csv:
        with args.sortie.open(encoding="utf-8") as src, args.csv.open("w", newline="", encoding="utf-8-sig") as dst:
            w = csv.DictWriter(dst, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            for line in src:
                w.writerow(json.loads(line))
    print(f"{n} annonces anonymisées -> {args.sortie}")
    print(f"champs retirés : {', '.join(DROP_FIELDS)} ; identifiant remplacé par une empreinte")
    print("masqués dans les textes :", dict(counts) or "rien")


if __name__ == "__main__":
    main()
