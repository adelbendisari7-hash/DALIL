from __future__ import annotations

import re
from datetime import date, datetime, timedelta

from pydantic import BaseModel, Field, field_validator

from .models import Shop

DTC_PATTERN = r"^[PCBUpcbu][0-3][0-9A-Fa-f]{3}$"


class DiagnosisRequest(BaseModel):
    text: str = Field("", max_length=2000)
    variant_id: int | None = None
    user_vehicle_id: int | None = None   # voiture du compte client (remplace variant_id si elle en a un)
    dtc_codes: list[str] = Field(default_factory=list, max_length=10)
    mode: str = Field("full", pattern="^(full|classifier|retrieval)$")
    # True : répondre tout de suite avec le classifieur (`llm: "pending"`) ; le modèle de langage affine en
    # arrière-plan et le résultat se relit par GET /diagnosis/{id} jusqu'à `llm` != "pending".
    defer_llm: bool = False

    @field_validator("dtc_codes")
    @classmethod
    def _codes(cls, v: list[str]) -> list[str]:
        import re

        out = []
        for c in v:
            c = c.strip().upper().replace(" ", "")
            if c and not re.match(DTC_PATTERN, c):
                raise ValueError(f"Code OBD-II invalide : {c}. Un code commence par P, C, B ou U, puis 4 caractères "
                                 f"dont le premier va de 0 à 3 (exemple : P0420). Vérifiez la lecture de la valise.")
            if c:
                out.append(c)
        return out


class AnswersRequest(BaseModel):
    answers: dict[str, int]
    defer_llm: bool = False


class ShopIn(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    phone: str | None = None
    whatsapp: str | None = None
    commune_id: int | None = None
    lat: float | None = Field(None, ge=-90, le=90)
    lng: float | None = Field(None, ge=-180, le=180)
    address: str | None = None
    hours: str | None = None
    shop_type: str = Field("pieces", pattern="^(pieces|casse|pneus|garage)$")
    parts_origin: list[str] = Field(default_factory=list)
    sale_mode: str | None = Field(None, pattern="^(gros|detail|les_deux)$")
    brand_ids: list[int] = Field(default_factory=list)
    category_ids: list[int] = Field(default_factory=list)
    photo_url: str | None = None
    surveyor: str | None = None
    survey: dict | None = None  # questions d'étude de marché (section 14)
    landmark: str | None = Field(None, max_length=200)
    opening: dict | None = None   # horaires structurés, voir services/shop_onboarding.check_opening

    @field_validator("opening")
    @classmethod
    def _opening(cls, v):
        from .services.shop_onboarding import check_opening
        return check_opening(v)


class ShopPatch(BaseModel):
    name: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    commune_id: int | None = None
    lat: float | None = None
    lng: float | None = None
    address: str | None = None
    hours: str | None = None
    parts_origin: list[str] | None = None
    sale_mode: str | None = Field(None, pattern="^(gros|detail|les_deux)$")
    brand_ids: list[int] | None = None
    category_ids: list[int] | None = None
    landmark: str | None = Field(None, max_length=200)
    opening: dict | None = None
    # « Fermé exceptionnellement » jusqu'à cette date (incluse) ; null efface la fermeture
    closed_until: date | None = None
    closed_note: str | None = Field(None, max_length=120)

    @field_validator("opening")
    @classmethod
    def _opening(cls, v):
        from .services.shop_onboarding import check_opening
        return check_opening(v)

    @field_validator("closed_until")
    @classmethod
    def _closed(cls, v):
        if v is not None and not date.today() - timedelta(days=1) <= v <= date.today() + timedelta(days=90):
            raise ValueError("Fermeture exceptionnelle : une date dans les 90 prochains jours")
        return v


class ShopRejectIn(BaseModel):
    reason: str = Field(..., min_length=3, max_length=255)


class ShopVerifyIn(BaseModel):
    """Liste de contrôle de l'appel de vérification : les trois cases doivent être cochées."""
    phone_ok: bool = False
    address_ok: bool = False
    activity_ok: bool = False


class ProductIn(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    category_id: int
    oem_ref: str | None = None
    part_brand: str | None = None
    condition: str = Field("neuf", pattern="^(neuf|origine|adaptable|occasion)$")
    price: float | None = Field(None, ge=0)
    in_stock: bool = True
    variant_ids: list[int] = Field(default_factory=list)


class ContactEventIn(BaseModel):
    shop_id: int
    channel: str = Field(pattern="^(call|whatsapp)$")
    session_id: int | None = None
    category_id: int | None = None
    variant_id: int | None = None


class FeedbackIn(BaseModel):
    shop_id: int | None = None
    session_id: int | None = None
    category_id: int | None = None
    part_found: bool | None = None
    diagnosis_correct: bool | None = None
    comment: str | None = Field(None, max_length=1000)


class OtpRequest(BaseModel):
    phone: str


class OtpVerify(BaseModel):
    phone: str
    code: str = Field(min_length=6, max_length=6)


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")
NAME_RE = re.compile(r"^[^\d@<>{}\[\]\/|]{1,60}$")   # lettres de toutes langues, espaces, tirets, apostrophes


def _clean_name(v: str | None) -> str | None:
    if v is None:
        return None
    v = " ".join(v.split())
    if not v:
        raise ValueError("ne peut pas être vide")
    if not NAME_RE.match(v):
        raise ValueError("ne doit contenir que des lettres")
    return v


class MePatch(BaseModel):
    name: str | None = None
    role: str | None = Field(None, pattern="^(driver|mechanic|shop_owner)$")
    consent: bool | None = None
    # Compte client : envoyer "" pour effacer un champ facultatif (e-mail, commune, date de naissance)
    first_name: str | None = Field(None, max_length=60)
    last_name: str | None = Field(None, max_length=60)
    email: str | None = Field(None, max_length=160)
    commune_id: int | None = None
    birth_date: date | None = None
    lang: str | None = Field(None, pattern="^(fr|ar)$")
    clear: list[str] = Field(default_factory=list)   # champs facultatifs à effacer : email, commune_id, birth_date

    @field_validator("first_name", "last_name")
    @classmethod
    def _names(cls, v):
        try:
            return _clean_name(v)
        except ValueError as e:
            raise ValueError(f"Prénom ou nom : {e}") from None

    @field_validator("email")
    @classmethod
    def _email(cls, v):
        if v is None or not v.strip():
            return None
        v = v.strip().lower()
        if not EMAIL_RE.match(v):
            raise ValueError("Adresse e-mail invalide")
        return v

    @field_validator("birth_date")
    @classmethod
    def _birth(cls, v):
        if v is None:
            return v
        age = (date.today() - v).days / 365.25
        if not 16 <= age <= 110:
            raise ValueError("Date de naissance invalide (16 ans au moins)")
        return v

    @field_validator("clear")
    @classmethod
    def _clear(cls, v):
        bad = set(v) - {"email", "commune_id", "birth_date"}
        if bad:
            raise ValueError(f"Champ impossible à effacer : {', '.join(sorted(bad))}")
        return v


def check_password(v: str) -> str:
    if len(v) < 8:
        raise ValueError("Mot de passe trop court : 8 caractères au moins")
    if v.strip() != v or not v.strip():
        raise ValueError("Mot de passe : pas d'espace au début ni à la fin")
    return v


class RegisterIn(BaseModel):
    """Inscription : prénom, nom, téléphone, mot de passe obligatoires ; e-mail facultatif ; consentement exigé."""
    first_name: str = Field(..., max_length=60)
    last_name: str = Field(..., max_length=60)
    phone: str = Field(..., max_length=24)
    password: str = Field(..., max_length=128)
    email: str | None = Field(None, max_length=160)
    consent: bool = Field(False, validate_default=True)   # validé même absent : pas de compte sans consentement

    @field_validator("password")
    @classmethod
    def _password(cls, v):
        return check_password(v)

    _names = field_validator("first_name", "last_name")(MePatch._names.__func__)
    _email = field_validator("email")(MePatch._email.__func__)

    @field_validator("consent")
    @classmethod
    def _consent(cls, v):
        if not v:
            raise ValueError("Acceptez la conservation de vos informations pour créer un compte")
        return v


class LoginIn(BaseModel):
    phone: str = Field(..., max_length=24)
    password: str = Field(..., max_length=128)


class PasswordChange(BaseModel):
    current: str = Field(..., max_length=128)
    new: str = Field(..., max_length=128)

    @field_validator("new")
    @classmethod
    def _password(cls, v):
        return check_password(v)


class PasswordResetIn(BaseModel):
    phone: str = Field(..., max_length=24)


VIN_RE = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")   # 17 caractères, sans I, O ni Q (norme ISO 3779)


def normalize_plate(raw: str) -> str:
    """Matricule algérien -> chiffres seuls : numéro d'ordre (3 à 6 chiffres), catégorie et année (3), wilaya (2).
    « 12345 115 31 », « 12345-115-31 » et « 12345.115.31 » donnent tous « 1234511531 »."""
    digits = re.sub(r"[\s\-./_]", "", raw or "")
    if not digits.isdigit() or not 8 <= len(digits) <= 11:
        raise ValueError("Matricule invalide : 8 à 11 chiffres, par exemple 12345-115-31")
    if digits[-2:] == "00":
        raise ValueError("Matricule invalide : les deux derniers chiffres sont le numéro de la wilaya")
    return digits


def format_plate(digits: str) -> str:
    return f"{digits[:-5]}-{digits[-5:-2]}-{digits[-2:]}"


class VehicleIn(BaseModel):
    plate: str = Field(..., max_length=24)
    variant_id: int | None = None
    year: int | None = Field(None, ge=1950, le=2100)
    label: str | None = Field(None, max_length=120)
    nickname: str | None = Field(None, max_length=60)
    mileage_km: int | None = Field(None, ge=0, le=2_000_000)
    vin: str | None = Field(None, max_length=24)

    @field_validator("plate")
    @classmethod
    def _plate(cls, v):
        return normalize_plate(v)

    @field_validator("vin")
    @classmethod
    def _vin(cls, v):
        if v is None or not v.strip():
            return None
        v = re.sub(r"[\s\-]", "", v).upper()
        if not VIN_RE.match(v):
            raise ValueError("Numéro de châssis invalide : 17 caractères, sans I, O ni Q")
        return v

    @field_validator("label", "nickname")
    @classmethod
    def _strip(cls, v):
        return " ".join(v.split()) or None if v is not None else None


class VehiclePatch(VehicleIn):
    plate: str | None = Field(None, max_length=24)   # tout est facultatif dans une modification

    @field_validator("plate")
    @classmethod
    def _plate(cls, v):
        return None if v is None else normalize_plate(v)


class PlateReportIn(BaseModel):
    plate: str = Field(..., max_length=24)
    message: str | None = Field(None, max_length=500)

    @field_validator("plate")
    @classmethod
    def _plate(cls, v):
        return normalize_plate(v)


class PartRequestIn(BaseModel):
    category_id: int
    variant_id: int | None = None
    session_id: int | None = None


class PartResponseIn(BaseModel):
    available: bool
    price: float | None = Field(None, ge=0)


def shop_out(shop: Shop, full: bool = True) -> dict:
    d = {
        "id": shop.id, "name": shop.name, "lat": shop.lat, "lng": shop.lng, "address": shop.address,
        "commune": shop.commune.nom_fr if shop.commune else None, "commune_id": shop.commune_id,
        "phone": shop.phone, "whatsapp": shop.whatsapp, "hours": shop.hours, "shop_type": shop.shop_type,
        "status": shop.status, "is_demo": shop.is_demo, "landmark": shop.landmark,
        "verified": shop.status in ("verified", "claimed") and shop.verified_at is not None,
        "verified_at": _iso(shop.verified_at), "open_status": _open_status(shop),
    }
    if full:
        d.update({
            "parts_origin": shop.parts_origin, "sale_mode": shop.sale_mode, "source": shop.source,
            "photo_url": shop.photo_url,
            "verified_at": _iso(shop.verified_at), "visited_at": _iso(shop.visited_at), "updated_at": _iso(shop.updated_at),
            "brands": [{"brand_id": b.brand_id, "source": b.source, "confirmed_at": _iso(b.confirmed_at)} for b in shop.brands],
            "categories": [{"category_id": c.category_id, "source": c.source, "confirmed_at": _iso(c.confirmed_at)} for c in shop.categories],
            "owner_user_id": shop.owner_user_id, "opening": shop.opening,
            "closed_until": shop.closed_until.isoformat() if shop.closed_until else None, "closed_note": shop.closed_note,
            "reject_reason": shop.reject_reason if shop.status == "rejected" else None,
        })
    return d


def _open_status(shop: Shop) -> dict | None:
    from .services.shop_onboarding import open_status
    return open_status(shop)


def _iso(d: datetime | None) -> str | None:
    return d.isoformat() if d else None


class VehicleRequestIn(BaseModel):
    brand: str = Field(min_length=1, max_length=60)
    model: str = Field(min_length=1, max_length=80)
    year: int | None = Field(None, ge=1950, le=2030)
    engine: str | None = Field(None, max_length=60)
