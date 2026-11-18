"""Étape 1 de la chaîne (section 6.1) : darija en lettres latines ou arabes -> français.

Les automobilistes d'Oran écrivent souvent « el moteur ysakhen bezaf » ou « الموتور يسخن بزاف ». Le reste de la
chaîne (recherche, classifieur, garde-fou, règles de sûreté) travaille en français : on remplace ici les tournures et
les mots courants par leur équivalent français. Les mots français déjà présents sont gardés tels quels ; les mots
arabes non reconnus sont retirés (le garde-fou décide ensuite s'il reste assez de sens).

Lexique écrit par l'équipe (propriétaire DALIL), à faire relire et enrichir par des locuteurs d'Oran. Mesure :
`ml/evaluate.py --test data/test/audit_ecriture_oran.jsonl` (réglage) et `audit_ecriture_oran_controle.jsonl`
(contrôle, jamais utilisé pour écrire ce lexique).
"""
from __future__ import annotations

import re
import unicodedata

from .normalize import strip_accents

# --- Darija en lettres latines -----------------------------------------------------------------
# Tournures (plusieurs mots) d'abord : la négation « ma …ch » change le sens du verbe.
LATIN_PHRASES: dict[str, str] = {
    # démarrage
    "ma tdemarich": "ne demarre pas", "ma ydemarich": "ne demarre pas", "ma tdemarrich": "ne demarre pas",
    "ma tdemarach": "ne demarre pas", "ma demaratch": "ne demarre pas", "ma theza9ch": "ne demarre pas",
    "ma tqela3ch": "ne demarre pas", "ma tkela3ch": "ne demarre pas", "ma tqlaach": "ne demarre pas",
    # allumage d'un feu ou d'un voyant
    "ma ycha3elch": "ne s allume pas", "ma tcha3elch": "ne s allume pas", "ma ych3elch": "ne s allume pas",
    "ma yche3elch": "ne s allume pas", "ma ycha3lch": "ne s allume pas",
    # climatisation, chauffage
    "ma tberredch": "ne refroidit pas", "ma yberredch": "ne refroidit pas", "ma tbarredch": "ne refroidit pas",
    "ma ybarredch": "ne refroidit pas", "ma tbardch": "ne refroidit pas",
    "ma ysakhanch": "ne chauffe pas", "ma tsakhanch": "ne chauffe pas", "ma ysakhench": "ne chauffe pas",
    # vitesses, freins, montée, charge
    "ma tedkhelch": "ne rentre pas", "ma yedkhelch": "ne rentre pas", "ma tdkhelch": "ne rentre pas",
    "ma dkhaltch": "ne rentre pas",
    "ma yechedch": "freine mal", "ma tchedch": "freine mal", "ma ychedch": "freine mal", "ma yched": "freine mal",
    "ma tetla3ch": "ne monte pas", "ma tla3ch": "ne monte pas", "ma tetlaach": "ne monte pas",
    "ma tcharjich": "ne charge pas", "ma tchargich": "ne charge pas", "ma ycharjich": "ne charge pas",
    # circonstances
    "ki ndir contact": "en tournant la cle", "ki ndir el contact": "en tournant la cle",
    "ki nfreini": "au freinage", "ki nfrini": "au freinage", "ki nfreiner": "au freinage",
    "ki ndour": "en tournant le volant", "ki ndor": "en tournant le volant",
    "ki nemchi": "en roulant", "ki nsog": "en roulant", "ki nsou9": "en roulant",
    "ki nbeddel": "en changeant de vitesse", "ki nbedel": "en changeant de vitesse", "ki nbadel": "en changeant de vitesse",
    "ki nchaal": "au demarrage", "ki nche3el": "au demarrage",
    "yakel zit": "consomme de l huile", "takel zit": "consomme de l huile", "yakoul zit": "consomme de l huile",
    "yakol zit": "consomme de l huile",
    "el ma": "liquide de refroidissement", "l ma": "liquide de refroidissement", "el maa": "liquide de refroidissement",
    "kol sbah": "le matin", "f sbah": "le matin", "fi sbah": "le matin",
    "tak tak": "claquement", "tek tek": "claquement", "tac tac": "claquement", "tok tok": "claquement",
    "ta3 l essence": "d essence", "ta3 lessence": "d essence", "ta3 essence": "d essence",
    "sbah lkhir": "bonjour", "sba7 lkhir": "bonjour",
}

LATIN_WORDS: dict[str, str] = {
    # véhicule
    "tomobil": "voiture", "tonobil": "voiture", "tomobile": "voiture", "tomobila": "voiture", "siyara": "voiture",
    "sayara": "voiture", "loto": "voiture", "lauto": "voiture", "tomobiltek": "voiture",
    # bruits et symptômes
    "ysoni": "fait du bruit", "tsoni": "fait du bruit", "ysonni": "fait du bruit", "tsonni": "fait du bruit",
    "ysouni": "fait du bruit",
    "ysafar": "siffle grince", "ysaffar": "siffle grince", "tsaffar": "siffle grince", "tsafar": "siffle grince",
    "ysafro": "sifflent grincent", "tsafro": "sifflent grincent", "ysaffro": "sifflent grincent",
    "ysakhen": "chauffe surchauffe", "tsakhen": "chauffe surchauffe", "sakhen": "chauffe", "sakhna": "chauffe",
    "ysekhen": "chauffe surchauffe", "tsekhen": "chauffe surchauffe",
    "tfargh": "se decharge", "yfargh": "se decharge", "tfregh": "se decharge", "tferegh": "se decharge",
    "tetfa": "cale s eteint", "ytfa": "cale s eteint", "tfat": "cale s eteint", "tetfi": "cale s eteint",
    "yertajef": "vibre", "tertajef": "vibre", "yerjef": "vibre", "terjef": "vibre",
    "tdegdeg": "cogne tape", "ydegdeg": "cogne tape", "ydagdag": "cogne tape",
    "ytertek": "cliquette", "tertek": "cliquette",
    "ytirri": "tire d un cote", "tjebed": "tire d un cote", "yjebed": "tire d un cote",
    "t3ayi": "peine perte de puissance", "y3ayi": "peine perte de puissance",
    "dkhan": "fumee", "dokhan": "fumee", "dokhkhan": "fumee",
    "k7al": "noire", "kahla": "noire", "k7ala": "noire", "ke7la": "noire",
    "byed": "blanche", "bayda": "blanche", "beyda": "blanche", "byad": "blanche",
    "ri7a": "odeur", "riha": "odeur", "re7a": "odeur",
    "l7ri9": "brule", "lahri9": "brule", "7ri9": "brule",
    "zit": "huile",
    "yan9as": "baisse", "tan9as": "baisse", "yan9es": "baisse", "tan9es": "baisse", "yna9es": "baisse", "yen9es": "baisse",
    "cha3el": "allume", "ycha3el": "allume", "mcha3el": "allume", "yche3el": "allume", "che3el": "allume",
    "mkesser": "casse", "mkasser": "casse", "fini": "use",
    "yokhrej": "sort", "tokhrej": "sort",
    # organes
    "roda": "roue", "rouda": "roue", "fran": "frein", "franat": "freins",
    # mots outils
    "bezaf": "beaucoup", "bzaf": "beaucoup", "bzzaf": "beaucoup", "ghir": "seulement",
    "kayen": "il y a", "kayn": "il y a", "f": "dans", "fi": "dans", "ta3": "de", "ki": "quand", "w": "et",
    "men": "de", "el": "le", "sbah": "matin", "kol": "chaque",
    # hors sujet courant (aide le garde-fou à reconnaître une question sans panne)
    "chhal": "combien", "9edach": "combien", "soum": "prix", "soume": "prix", "lyoum": "aujourd hui",
    "win": "ou", "nelga": "trouver", "nechri": "acheter", "nbi3": "vendre", "nbie": "vendre", "jdida": "neuve",
    "jdid": "neuf", "nheb": "je veux", "wach": "est ce que", "labas": "ca va", "khouya": "mon frere",
    "mlih": "bien", "ydir": "faire",
}

# --- Arabe (darija ou arabe standard, en lettres arabes) ----------------------------------------
AR_PHRASES: dict[str, str] = {
    "ما تديماريش": "ne demarre pas", "ماتديماريش": "ne demarre pas", "ما تقلعش": "ne demarre pas",
    "ماتقلعش": "ne demarre pas", "ما يقلعش": "ne demarre pas", "ما تخدمش": "ne demarre pas",
    "ما يبردش": "ne refroidit pas", "ما تبردش": "ne refroidit pas", "مايبردش": "ne refroidit pas",
    "ماتشارجيش": "ne charge pas", "ما تشارجيش": "ne charge pas", "ما يشارجيش": "ne charge pas",
    "ما يشعلش": "ne s allume pas", "ما تشعلش": "ne s allume pas",
    "كي نفريني": "au freinage", "كي نفرين": "au freinage",
    "صباح الخير": "bonjour",
}

AR_WORDS: dict[str, str] = {
    "سياره": "voiture", "طوموبيل": "voiture", "طونوبيل": "voiture", "لوطو": "voiture", "طوموبيلتي": "voiture",
    "فرامل": "freins", "فران": "frein", "فرانات": "freins", "فرين": "frein", "مكابح": "freins",
    "تصفر": "siffle grince", "يصفر": "siffle grince", "يصفرو": "sifflent grincent",
    "موتور": "moteur", "محرك": "moteur",
    "يسخن": "chauffe surchauffe", "تسخن": "chauffe surchauffe", "سخن": "chauffe",
    "بطاريه": "batterie", "باطري": "batterie", "باتري": "batterie", "بطري": "batterie",
    "تفرغ": "se decharge", "يفرغ": "se decharge",
    "صوت": "bruit", "حس": "bruit", "يصوني": "fait du bruit", "تصوني": "fait du bruit",
    "روضه": "roue", "عجله": "roue", "رويده": "roue",
    "قدام": "avant", "قداميه": "avant", "لور": "arriere",
    "دخان": "fumee", "كحل": "noire", "كحله": "noire", "ابيض": "blanche", "بيضه": "blanche",
    "ريحه": "odeur", "رائحه": "odeur", "زيت": "huile",
    "شكمان": "echappement", "اشابمون": "echappement",
    "كليماتيزور": "climatisation", "كليم": "climatisation", "مكيف": "climatisation",
    "ليسانس": "essence", "ليصانص": "essence", "بنزين": "essence", "مازوت": "gasoil",
    "فيتاس": "vitesse", "ضو": "phare", "فار": "phare", "فوليون": "volant", "فولون": "volant",
    "امبرياج": "embrayage", "امورتيسور": "amortisseur", "راديتور": "radiateur",
    "طريق": "route", "صباح": "matin", "بزاف": "beaucoup", "كاين": "il y a", "في": "dans", "كي": "quand",
    # hors sujet courant
    "نحب": "je veux", "نبيع": "vendre", "نشري": "acheter", "شحال": "combien", "سوم": "prix", "كيراك": "ca va",
}
AR_PREFIXES = ("وال", "فال", "بال", "لل", "ال", "و", "ف", "ب")
ARABIC_RE = re.compile(r"[؀-ۿ]")
AR_WORD_RE = re.compile(r"[؀-ۿ]+")


def _norm_ar(s: str) -> str:
    """Forme canonique : sans diacritiques ni tatouil, alifs unifiés, ة -> ه, ى -> ي."""
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if unicodedata.category(c) != "Mn").replace("ـ", "")
    return re.sub("[أإآ]", "ا", s).replace("ة", "ه").replace("ى", "ي")


def _ar_word(w: str) -> str | None:
    if w in AR_WORDS:
        return AR_WORDS[w]
    for p in AR_PREFIXES:
        if w.startswith(p) and len(w) - len(p) >= 2 and w[len(p):] in AR_WORDS:
            return AR_WORDS[w[len(p):]]
    return None


def _replace_phrases(t: str, phrases: dict[str, str]) -> str:
    for k in sorted(phrases, key=len, reverse=True):
        t = re.sub(rf"(?<!\w){re.escape(k)}(?!\w)", f" {phrases[k]} ", t)
    return t


def to_french(text: str) -> tuple[str, str]:
    """Rend (texte en français, langue) ; langue : « fr », « dz » (darija en lettres latines) ou « ar »
    (lettres arabes). Un texte déjà en français ressort inchangé."""
    raw = (text or "").strip()
    if not raw:
        return raw, "fr"
    if ARABIC_RE.search(raw):
        t = _replace_phrases(_norm_ar(raw.lower()), {_norm_ar(k): v for k, v in AR_PHRASES.items()})
        out = []
        for tok in re.split(r"(\s+)", t):
            if not AR_WORD_RE.fullmatch(tok or "x"):
                out.append(tok)  # mots latins, chiffres, codes OBD, tournures déjà traduites
                continue
            fr = _ar_word(tok)
            if fr:
                out.append(fr)  # mot arabe inconnu : retiré
        return re.sub(r"\s+", " ", "".join(out)).strip(), "ar"
    t = strip_accents(raw.lower()).replace("’", "'").replace("'", " ")
    t = re.sub(r"\s+", " ", t)
    phrased = _replace_phrases(t, LATIN_PHRASES)
    words = re.split(r"(\s+)", phrased)
    hits = 0
    for i, w in enumerate(words):
        if w in LATIN_WORDS:
            words[i] = LATIN_WORDS[w]
            hits += 1
    out = re.sub(r"\s+", " ", "".join(words)).strip()
    if phrased == t and hits <= _french_like_hits(t):
        return raw, "fr"  # français ordinaire : on rend le texte d'origine, accents compris
    return out, "dz"


# Mots du lexique latin qui existent aussi en français courant : leur seule présence ne fait pas d'un texte de la darija.
_FRENCH_HOMOGRAPHS = {"f", "fi", "w", "men", "el", "fini", "mlih", "win", "ki", "soum"}


def _french_like_hits(t: str) -> int:
    return sum(1 for w in t.split() if w in _FRENCH_HOMOGRAPHS)
