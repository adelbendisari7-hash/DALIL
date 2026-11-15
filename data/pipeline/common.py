"""Socle commun du pipeline de données (étape 6) : chemins, format des enregistrements, téléchargements.

Format unique d'un enregistrement traité (une ligne JSONL dans data/processed/<source>.jsonl) :

    id            identifiant stable, préfixé par la source ("nhtsa_complaints:11749524")
    source        identifiant de la source (voir sources/__init__.py et data/sources/<id>.md)
    kind          complaint | recall | qa | stat | fault_type
    lang          langue du texte d'origine (en, fr, zh)
    text          texte d'origine, jamais modifié
    text_fr       traduction française (None tant que la traduction n'a pas tourné ; = text si lang == fr)
    url           lien vers l'élément d'origine (attribution)
    license       licence de la source (obligatoire : un enregistrement sans licence est refusé au chargement)
    attribution   mention à afficher (auteur, éditeur)
    vehicle       {make, model, year, dalil_brand, dalil_model} si connu
    categories    familles de pièces DALIL (slugs de part_categories), de la plus probable à la moins probable
    family        famille de niveau 1 (slug) si une sous-famille n'a pas pu être déterminée
    fault         panne type DALIL (slug de faults) si l'étiquette est sûre, sinon None
    label_quality keyword+component | keyword | component | manual | None  (comment l'étiquette a été obtenue)
    synthetic     True si le texte est généré (jamais utilisé pour l'évaluation)
    meta          champs propres à la source
"""
from __future__ import annotations

import hashlib
import io
import json
import struct
import sys
import time
import zlib
from collections.abc import Iterable, Iterator
from dataclasses import asdict, dataclass, field
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
SEED = DATA / "seed"
USER_AGENT = "dalil-data-pipeline/0.1 (projet universitaire)"

if str(ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(ROOT / "backend"))


@dataclass
class Record:
    id: str
    source: str
    kind: str
    lang: str
    text: str
    license: str
    url: str | None = None
    attribution: str | None = None
    text_fr: str | None = None
    vehicle: dict | None = None
    categories: list[str] = field(default_factory=list)
    family: str | None = None
    fault: str | None = None
    label_quality: str | None = None
    synthetic: bool = False
    meta: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.lang == "fr" and self.text_fr is None:
            self.text_fr = self.text


def write_jsonl(path: Path, records: Iterable[Record | dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(asdict(r) if isinstance(r, Record) else r, ensure_ascii=False) + "\n")
            n += 1
    tmp.replace(path)  # écriture atomique : un fichier interrompu n'écrase pas le précédent
    return n


def read_jsonl(path: Path) -> Iterator[dict]:
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def client() -> httpx.Client:
    return httpx.Client(timeout=120, follow_redirects=True, headers={"User-Agent": USER_AGENT})


def download(url: str, dest: Path, refresh: bool = False, log=print) -> Path:
    """Téléchargement avec cache : rejouer le pipeline ne retélécharge pas ce qui est déjà là."""
    if dest.exists() and dest.stat().st_size > 0 and not refresh:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    log(f"  téléchargement {url}")
    with client() as c, c.stream("GET", url) as r:
        r.raise_for_status()
        with tmp.open("wb") as f:
            for chunk in r.iter_bytes(1 << 20):
                f.write(chunk)
    tmp.replace(dest)
    return dest


def get_json(c: httpx.Client, url: str, params: dict | None = None, retries: int = 4) -> dict:
    for attempt in range(retries):
        try:
            r = c.get(url, params=params)
            if r.status_code in (429, 500, 502, 503, 504):
                raise httpx.HTTPStatusError("temporaire", request=r.request, response=r)
            if r.status_code == 400 and r.headers.get("content-type", "").startswith("application/json"):
                return r.json()  # l'API NHTSA répond 400 avec un corps valide quand il n'y a aucun résultat
            r.raise_for_status()
            return r.json()
        except (httpx.HTTPError, json.JSONDecodeError):
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
    return {}


class ZipMemberStream(io.RawIOBase):
    """Lit en flux le premier fichier d'une archive zip distante, sans la stocker sur le disque.

    Gère la compression Deflate (8) et Deflate64 (9, utilisée par les fichiers MOT, que le module
    zipfile de Python ne sait pas lire) grâce à inflate64.

    Reprise automatique : si le serveur coupe la connexion (fréquent sur 1 Go), le flux se reconnecte
    et redemande la suite à partir de l'octet exact où il s'était arrêté (en-tête HTTP Range).
    """

    MAX_RESUMES = 8

    def __init__(self, url: str):
        self._url = url
        self._received = 0
        self._resumes = 0
        self._cm = None
        self._open(0)
        self._buf = b""
        self._done = False
        head = self._read_raw(30)
        sig, _, _, method, _, _, _, _, _, name_len, extra_len = struct.unpack("<IHHHHHIIIHH", head[:30])
        if sig != 0x04034B50:
            raise ValueError("signature zip inattendue")
        self.member_name = self._read_raw(name_len).decode("utf-8", "replace")
        self._read_raw(extra_len)
        if method == 8:
            d = zlib.decompressobj(-15)
            self._inflate = d.decompress
            self._is_eof = lambda: d.eof
        elif method == 9:
            import inflate64

            d64 = inflate64.Inflater()
            self._inflate = d64.inflate
            self._is_eof = lambda: getattr(d64, "eof", False)
        else:
            raise ValueError(f"méthode de compression non gérée : {method}")
        self._out = b""

    def _open(self, offset: int) -> None:
        if self._cm is not None:
            try:
                self._cm.__exit__(None, None, None)
            except Exception:
                pass
        headers = {"Range": f"bytes={offset}-"} if offset else {}
        self._cm = client().stream("GET", self._url, headers=headers)
        self._resp = self._cm.__enter__()
        self._resp.raise_for_status()
        if offset and self._resp.status_code != 206:
            raise IOError("le serveur ne sait pas reprendre un téléchargement (pas de réponse 206)")
        self._chunks = self._resp.iter_bytes()  # sans taille de bloc : chaque morceau dès réception, décompte exact pour la reprise

    def _next_raw(self) -> bytes:
        """Bloc compressé suivant ; b"" en fin de fichier. Reprend après une coupure réseau."""
        while True:
            try:
                chunk = next(self._chunks, b"")
                self._received += len(chunk)
                return chunk
            except (httpx.TransportError, httpx.RemoteProtocolError):
                self._resumes += 1
                if self._resumes > self.MAX_RESUMES:
                    raise
                time.sleep(min(2 ** self._resumes, 30))
                self._open(self._received)

    def _read_raw(self, n: int) -> bytes:
        while len(self._buf) < n:
            chunk = self._next_raw()
            if not chunk:
                break
            self._buf += chunk
        out, self._buf = self._buf[:n], self._buf[n:]
        return out

    def readable(self) -> bool:
        return True

    def readinto(self, b) -> int:
        while not self._out and not self._done:
            if self._is_eof():
                self._done = True
                break
            raw = self._buf or self._next_raw()
            self._buf = b""
            if not raw:
                self._done = True
                break
            self._out = self._inflate(raw)
        n = min(len(b), len(self._out))
        b[:n] = self._out[:n]
        self._out = self._out[n:]
        return n

    def close(self) -> None:
        try:
            self._cm.__exit__(None, None, None)
        finally:
            super().close()
