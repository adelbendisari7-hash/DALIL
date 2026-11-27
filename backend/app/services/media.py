"""Photos des produits et des devantures (plan côté magasin, phase 2 ; décision du 27/11/2026).

- Le téléphone réduit et réencode l'image avant l'envoi (1 280 px, JPEG, ~200 Ko) ; le serveur n'accepte que du JPEG
  d'1 Mo au plus, vérifie le contenu (pas l'extension) et **retire les métadonnées** (segments APP1 à APP15 : EXIF avec
  la position GPS, XMP, modèle du téléphone ; commentaires) par une lecture des segments JPEG, sans dépendance.
- Nom de fichier tiré au hasard ; stockage derrière une interface unique (`Storage`), sur le disque aujourd'hui
  (`data/uploads/`, hors git), remplaçable par un stockage en ligne à la mise en ligne.
- Aucune reconnaissance automatique : une photo illustre, elle ne remplit jamais une fiche.
"""
from __future__ import annotations

import re
import secrets
from pathlib import Path

from ..config import get_settings

MAX_BYTES = 1_000_000
MAX_SIDE = 4096
KINDS = ("produits", "devantures", "demandes")
NAME_RE = re.compile(r"^[0-9a-f]{32}\.jpg$")
# Marqueurs JPEG sans longueur (pas de segment derrière)
_STANDALONE = {0x01, *range(0xD0, 0xD8)}


class InvalidImage(ValueError):
    pass


def clean_jpeg(data: bytes) -> bytes:
    """JPEG sans métadonnées. Garde l'en-tête JFIF (APP0), les tables et l'image ; retire APP1-APP15 et COM.
    InvalidImage si ce n'est pas un JPEG valide, trop lourd ou trop grand."""
    if len(data) > MAX_BYTES:
        raise InvalidImage("Photo trop lourde (1 Mo au plus)")
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        raise InvalidImage("Seules les photos JPEG sont acceptées")
    out = bytearray(b"\xff\xd8")
    i, seen_frame = 2, False
    while i < len(data):
        if data[i] != 0xFF:
            raise InvalidImage("Photo abîmée (JPEG illisible)")
        while i < len(data) and data[i] == 0xFF:   # octets de remplissage
            i += 1
        if i >= len(data):
            raise InvalidImage("Photo abîmée (JPEG incomplet)")
        marker = data[i]
        i += 1
        if marker in _STANDALONE:
            out += bytes([0xFF, marker])
            continue
        if marker == 0xD9:   # fin d'image sans données d'image
            break
        if i + 2 > len(data):
            raise InvalidImage("Photo abîmée (JPEG incomplet)")
        length = int.from_bytes(data[i:i + 2], "big")
        if length < 2 or i + length > len(data):
            raise InvalidImage("Photo abîmée (segment invalide)")
        segment = data[i:i + length]
        if marker in (0xC0, 0xC1, 0xC2):   # dimensions de l'image
            h, w = int.from_bytes(segment[3:5], "big"), int.from_bytes(segment[5:7], "big")
            if not (0 < w <= MAX_SIDE and 0 < h <= MAX_SIDE):
                raise InvalidImage("Photo trop grande")
            seen_frame = True
        keep = not (0xE1 <= marker <= 0xEF or marker == 0xFE)
        if keep:
            out += bytes([0xFF, marker]) + segment
        i += length
        if marker == 0xDA:   # début des données de l'image : le reste est copié tel quel
            if not seen_frame:
                raise InvalidImage("Photo abîmée (dimensions absentes)")
            out += data[i:]
            return bytes(out)
    raise InvalidImage("Photo abîmée (pas de données d'image)")


class Storage:
    """Fichiers des photos. Aujourd'hui un dossier du disque ; même interface pour un stockage en ligne plus tard."""

    def __init__(self, root: str | None = None):
        self.root = Path(root or get_settings().media_dir)

    def save(self, kind: str, data: bytes) -> str:
        assert kind in KINDS
        name = f"{secrets.token_hex(16)}.jpg"
        folder = self.root / kind
        folder.mkdir(parents=True, exist_ok=True)
        (folder / name).write_bytes(clean_jpeg(data))
        return f"/api/v1/media/{kind}/{name}"

    def path(self, kind: str, name: str) -> Path | None:
        if kind not in KINDS or not NAME_RE.match(name):
            return None
        p = self.root / kind / name
        return p if p.is_file() else None

    def delete(self, url: str | None) -> None:
        """Supprime le fichier d'une adresse /api/v1/media/<sorte>/<nom> ; ignore toute autre adresse."""
        if not url:
            return
        m = re.match(r"^/api/v1/media/([a-z]+)/([0-9a-f]{32}\.jpg)$", url)
        if m and (p := self.path(m.group(1), m.group(2))):
            p.unlink(missing_ok=True)


def storage() -> Storage:
    return Storage()
