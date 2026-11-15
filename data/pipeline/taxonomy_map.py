"""Correspondance texte -> taxonomie des pièces DALIL (section 6, couche 1).

Règles par mots-clés, transparentes et testées : chaque étiquette produite peut être expliquée.
- Anglais : expressions régulières écrites à la main (NHTSA, MOT, Stack Exchange).
- Français : noms et synonymes de data/seed/part_categories.json + compléments (RappelConso).
- Composants NHTSA : famille de niveau 1 quand le texte ne permet pas de descendre plus bas.
Quand plusieurs règles se déclenchent, la correspondance la plus longue (la plus précise) passe devant.

Ces étiquettes sont « faibles » (label_quality = keyword | component) : elles servent à
l'entraînement, jamais à l'évaluation, qui se fait sur le jeu de test d'Oran annoté à la main.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache

from .common import SEED

# --- Anglais -----------------------------------------------------------------
# (slug, motif). Ordre indifférent : la plus longue correspondance l'emporte.
EN_RULES: list[tuple[str, str]] = [
    ("plaquettes-arriere", r"rear (brake )?pads?"),
    ("plaquettes-avant", r"(front )?brake pads?|brake pad\(s\)|pads? (are |were )?(worn|wearing)|friction (material|lining)"),
    ("disques-frein", r"brake (dis[ck]s?|rotors?)|\brotors?\b|warped (rotor|disc)|brake dis[ck]\(s\)"),
    ("machoires-frein", r"brake (shoes?|drums?|linings?)|\bdrums?\b"),
    ("etrier-frein", r"calipers?|brake cylinders?|wheel cylinders?"),
    ("flexible-frein", r"brake (hoses?|lines?|pipes?)|flexible brake|rigid brake pipe"),
    ("maitre-cylindre", r"master cylinder"),
    ("liquide-frein", r"brake fluid"),
    ("filtre-huile", r"oil filter"),
    ("filtre-air", r"(engine )?air filter"),
    ("filtre-carburant", r"fuel filter"),
    ("filtre-habitacle", r"cabin (air )?filter|pollen filter"),
    ("bougies-allumage", r"spark plugs?"),
    ("bobine-allumage", r"ignition coils?|coil packs?|coil on plug"),
    ("bougies-prechauffage", r"glow plugs?"),
    ("kit-distribution", r"timing (belt|chain)s?|cam(shaft)? sprockets?|timing kit"),
    ("courroie-accessoires", r"(serpentine|drive|fan|accessory|auxiliary|alternator) belts?"),
    ("galet-tendeur", r"(belt )?tensioner|idler pulley"),
    ("pompe-eau", r"water pump"),
    ("thermostat", r"thermostat"),
    ("radiateur", r"radiator(?! fan)"),
    ("durite-refroidissement", r"(coolant|radiator|heater) hoses?"),
    ("ventilateur-radiateur", r"(cooling|radiator) fans?"),
    ("sonde-temperature", r"coolant temp(erature)? sensor"),
    ("vase-expansion", r"expansion tank|coolant (reservoir|tank)|overflow tank"),
    ("amortisseurs", r"shock absorbers?|\bstruts?\b|\bshocks\b|\bdampers?\b"),
    ("ressorts", r"(coil|suspension|road|leaf) springs?"),
    ("coupelles", r"strut (mounts?|bearings?)|top mounts?"),
    ("silentblocs", r"\bbush(ing)?(es|s)?\b"),
    ("roulements-roue", r"wheel bearings?|hub bearings?|hub assembl(y|ies)"),
    ("cardans", r"cv (joints?|boots?|axles?)|constant velocity|drive ?shafts?|half ?shafts?|axle shafts?"),
    ("triangles", r"control arms?|wishbones?|lower arms?|suspension arms?"),
    ("biellette-stabilisatrice", r"(sway|stabili[sz]er|anti-roll) bar links?|end links?|stabili[sz]er links?"),
    ("rotules-direction", r"ball joints?|(tie|track) rod ends?"),
    ("biellettes-direction", r"(inner )?(tie|track) rods?(?! end)"),
    ("cremaillere", r"steering rack|rack and pinion|steering gear( box)?|steering box"),
    ("pompe-direction", r"power steering (pump|fluid)|power steering"),
    ("kit-embrayage", r"clutch(?! (cable|master|slave|pedal))"),
    ("cable-embrayage", r"clutch (cable|master cylinder|slave cylinder|pedal)"),
    ("volant-moteur", r"flywheel|dual mass"),
    ("boite-vitesses", r"(automatic |manual )?transmission(?! (fluid cooler|line))|gear ?box|\bcvt\b"),
    ("batterie", r"(12 ?v(olt)? )?battery|batteries"),
    ("alternateur", r"alternator|charging system"),
    ("demarreur", r"starter( motor)?\b|starter solenoid"),
    ("ampoules", r"head ?lamps?|head ?lights?|tail ?(lamps?|lights?)|(light )?bulbs?|stop lamps?|brake lights?|turn signal (lamp|bulb)s?"),
    ("sonde-lambda", r"o2 sensors?|oxygen sensors?|lambda"),
    ("debitmetre", r"mass air ?flow|\bmaf\b"),
    ("capteur-pression-admission", r"\bmap sensor|manifold (absolute )?pressure"),
    ("capteur-vilebrequin", r"crank(shaft)? (position )?sensor"),
    ("capteur-arbre-came", r"cam(shaft)? (position )?sensor"),
    ("capteur-cliquetis", r"knock sensor"),
    ("vanne-egr", r"\begr\b"),
    ("papillon-motorise", r"throttle body|electronic throttle|idle air control"),
    ("injecteurs", r"(fuel )?injectors?"),
    ("pompe-carburant", r"fuel pumps?|high pressure (fuel )?pump"),
    ("regulateur-pression", r"fuel pressure regulator"),
    ("turbocompresseur", r"turbo(charger)?s?\b"),
    ("joint-culasse", r"head gaskets?"),
    ("joint-cache-culbuteurs", r"(valve|rocker|cam) cover gaskets?"),
    ("support-moteur", r"(engine|motor|transmission) mount(ing)?s?"),
    ("huile-moteur", r"oil (change|leaks?|consumption)|engine oil|burning oil"),
    ("catalyseur", r"catalytic converters?|\bcats?\b(?! ?5)|\bdpf\b|particulate filter"),
    ("silencieux", r"exhaust (system|pipes?|leaks?|manifold)|mufflers?|silencers?"),
    ("compresseur-clim", r"a/?c compressors?|air condition(ing|er)? compressor|air condition(ing|er)"),
    ("condenseur", r"(a/?c )?condensers?"),
]

# Composants NHTSA (champ « components », séparés par « : » ou « , ») -> famille de niveau 1.
NHTSA_COMPONENT_FAMILY = [
    ("ENGINE AND ENGINE COOLING:ENGINE COOLING", "refroidissement"),
    ("ENGINE COOLING", "refroidissement"),
    ("SERVICE BRAKES", "freinage"),
    ("PARKING BRAKE", "freinage"),
    ("STEERING", "direction"),
    ("SUSPENSION", "suspension"),
    ("POWER TRAIN", "transmission"),
    ("FUEL/PROPULSION SYSTEM", "alimentation"),
    ("FUEL SYSTEM", "alimentation"),
    ("ELECTRICAL SYSTEM", "electricite"),
    ("EXTERIOR LIGHTING", "electricite"),
    ("EXHAUST SYSTEM", "echappement"),
    ("ENGINE", "moteur"),
    ("WHEELS", "train-roulant"),
]

# Compléments français (RappelConso, retours) en plus des synonymes de la taxonomie.
FR_EXTRA: list[tuple[str, str]] = [
    ("plaquettes-avant", r"plaquettes? de frein"),
    ("liquide-frein", r"liquide de frein"),
    ("flexible-frein", r"(flexible|conduite|canalisation)s? de frein"),
    ("etrier-frein", r"etriers? de frein"),
    ("pompe-carburant", r"pompe (a|de) (carburant|essence|gasoil)|fuite de carburant"),
    ("injecteurs", r"injecteurs?"),
    ("rotules-direction", r"rotules?"),
    ("cremaillere", r"cremaillere|colonne de direction|boitier de direction"),
    ("cardans", r"arbres? de transmission|cardans?"),
    ("ampoules", r"feux|eclairage|phares?|feu stop"),
    ("batterie", r"batterie"),
    ("boite-vitesses", r"boite de vitesses?|boite automatique"),
    ("support-moteur", r"supports? (du )?moteur"),
    ("roulements-roue", r"roulements? de roue|moyeux?"),
    ("triangles", r"bras de suspension|triangles?"),
    ("silencieux", r"(ligne|systeme|tuyau) d'echappement"),
]

FR_FAMILY_HINTS: list[tuple[str, str]] = [
    ("freinage", r"\bfrein|freinage"),
    ("direction", r"\bdirection\b|braquage"),
    ("suspension", r"suspension"),
    ("alimentation", r"carburant|essence|gazole|gasoil"),
    ("electricite", r"electrique|cablage|faisceau|court-circuit"),
    ("moteur", r"\bmoteur\b"),
    ("refroidissement", r"refroidissement|surchauffe"),
    ("transmission", r"transmission|embrayage"),
    ("echappement", r"echappement"),
]


def _norm(s: str) -> str:
    from app.services.diagnosis.normalize import strip_accents

    return re.sub(r"\s+", " ", strip_accents((s or "").lower())).strip()


@lru_cache
def taxonomy() -> dict:
    data = json.loads((SEED / "part_categories.json").read_text(encoding="utf-8"))
    parent, fr_rules, names = {}, [], {}
    for fam in data["families"]:
        names[fam["slug"]] = fam["name_fr"]
        for ch in fam["children"]:
            parent[ch["slug"]] = fam["slug"]
            names[ch["slug"]] = ch["name_fr"]
            # mots trop génériques exclus : ils feraient correspondre n'importe quel texte
            for term in [ch["name_fr"], *ch.get("synonyms", [])]:
                t = _norm(term)
                if len(t) >= 4 and t not in {"huile", "pot", "boite", "transmission", "direction", "courroie"}:
                    fr_rules.append((ch["slug"], r"\b" + re.escape(t) + r"s?\b"))
    fr_rules += FR_EXTRA
    return {"parent": parent, "names": names, "fr": [(s, re.compile(p)) for s, p in fr_rules],
            "en": [(s, re.compile(p)) for s, p in EN_RULES], "fr_family": [(s, re.compile(p)) for s, p in FR_FAMILY_HINTS]}


def _match(rules, text: str) -> list[str]:
    hits: dict[str, int] = {}
    for slug, rx in rules:
        for m in rx.finditer(text):
            hits[slug] = max(hits.get(slug, 0), len(m.group(0)))
    # la plus longue correspondance d'abord ; à égalité, l'ordre des règles
    return [s for s, _ in sorted(hits.items(), key=lambda x: -x[1])]


def categories_en(text: str) -> list[str]:
    return _match(taxonomy()["en"], (text or "").lower())


def categories_fr(text: str) -> list[str]:
    return _match(taxonomy()["fr"], _norm(text))


def family_fr(text: str) -> str | None:
    hits = _match(taxonomy()["fr_family"], _norm(text))
    return hits[0] if hits else None


def family_of(slug: str | None) -> str | None:
    if slug is None:
        return None
    return taxonomy()["parent"].get(slug, slug)


def nhtsa_family(components: str) -> str | None:
    comp = (components or "").upper()
    for key, fam in NHTSA_COMPONENT_FAMILY:
        if key in comp:
            return fam
    return None


def reconcile(cats: list[str], family: str | None) -> tuple[list[str], str | None, str | None]:
    """Garde les sous-familles cohérentes avec la famille déclarée par la source, si possible.

    Renvoie (catégories, famille, qualité de l'étiquette).
    """
    if cats and family:
        same = [c for c in cats if family_of(c) == family]
        if same:  # le texte et la source sont d'accord : étiquette la plus sûre
            return same[:3], family, "keyword+component"
    if cats:
        return cats[:3], family_of(cats[0]), "keyword"
    if family:
        return [], family, "component"
    return [], None, None


@lru_cache
def primary_part_to_fault() -> dict[str, str]:
    """Sous-famille -> panne type, seulement quand une seule panne a cette pièce comme pièce principale."""
    faults = json.loads((SEED / "faults.json").read_text(encoding="utf-8"))["faults"]
    owners: dict[str, list[str]] = {}
    for f in faults:
        main = max(f["parts"].items(), key=lambda x: x[1])[0]
        owners.setdefault(main, []).append(f["slug"])
    return {part: fs[0] for part, fs in owners.items() if len(fs) == 1}


def fault_for(categories: list[str], quality: str | None = "keyword") -> str | None:
    """Panne type seulement pour une étiquette par mots-clés (sans désaccord avec la source)."""
    if quality not in ("keyword", "keyword+component", "manual"):
        return None
    return primary_part_to_fault().get(categories[0]) if categories else None
