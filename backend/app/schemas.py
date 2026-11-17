from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from .models import Shop

DTC_PATTERN = r"^[PCBUpcbu][0-3][0-9A-Fa-f]{3}$"


class DiagnosisRequest(BaseModel):
    text: str = Field("", max_length=2000)
    variant_id: int | None = None
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
    sale_mode: str | None = None
    brand_ids: list[int] | None = None
    category_ids: list[int] | None = None


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


class MePatch(BaseModel):
    name: str | None = None
    role: str | None = Field(None, pattern="^(driver|mechanic|shop_owner)$")
    consent: bool | None = None


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
        "status": shop.status, "is_demo": shop.is_demo,
    }
    if full:
        d.update({
            "parts_origin": shop.parts_origin, "sale_mode": shop.sale_mode, "source": shop.source,
            "photo_url": shop.photo_url,
            "verified_at": _iso(shop.verified_at), "visited_at": _iso(shop.visited_at), "updated_at": _iso(shop.updated_at),
            "brands": [{"brand_id": b.brand_id, "source": b.source, "confirmed_at": _iso(b.confirmed_at)} for b in shop.brands],
            "categories": [{"category_id": c.category_id, "source": c.source, "confirmed_at": _iso(c.confirmed_at)} for c in shop.categories],
            "owner_user_id": shop.owner_user_id,
        })
    return d


def _iso(d: datetime | None) -> str | None:
    return d.isoformat() if d else None
