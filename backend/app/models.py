"""Modèle de données (section 8 du cahier des charges).

Choix de portabilité : le même code tourne sur PostgreSQL (cible) et SQLite (repli local).
- Positions : colonnes `lat`/`lng` ; sur PostgreSQL, la migration ajoute une colonne PostGIS
  `geom` générée à partir d'elles, avec un index GIST.
- Vecteurs : type `Embedding` = pgvector sur PostgreSQL, JSON ailleurs.
- Tableaux (`synonyms[]`, `dtc_codes[]`) : JSON.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from .db import Base

EMBEDDING_DIM = 1024  # Qwen3-Embedding-0.6B


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Embedding(TypeDecorator):
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from pgvector.sqlalchemy import Vector

            return dialect.type_descriptor(Vector(EMBEDDING_DIM))
        return dialect.type_descriptor(JSON())


# --- Géographie -----------------------------------------------------------

class Wilaya(Base):
    __tablename__ = "wilayas"
    code: Mapped[str] = mapped_column(String(4), primary_key=True)
    nom_fr: Mapped[str] = mapped_column(String(100))
    nom_ar: Mapped[str | None] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(Boolean, default=False)  # F23 : activation par configuration


class Commune(Base):
    __tablename__ = "communes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(8), unique=True)
    wilaya_code: Mapped[str] = mapped_column(ForeignKey("wilayas.code"))
    nom_fr: Mapped[str] = mapped_column(String(100))
    nom_ar: Mapped[str | None] = mapped_column(String(100))
    lat: Mapped[float | None] = mapped_column(Float)
    lng: Mapped[float | None] = mapped_column(Float)


# --- Comptes --------------------------------------------------------------

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    # Connexion par mot de passe (27/11/2026, SMS payants) : scrypt salé, jamais le mot de passe lui-même
    password_hash: Mapped[str | None] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(20), default="driver")  # driver|mechanic|shop_owner|admin
    name: Mapped[str | None] = mapped_column(String(120))   # « Prénom Nom », gardé pour l'affichage et les magasins
    # Compte client (27/11/2026) : prénom, nom et téléphone obligatoires pour un compte complet ; le reste facultatif
    first_name: Mapped[str | None] = mapped_column(String(60))
    last_name: Mapped[str | None] = mapped_column(String(60))
    email: Mapped[str | None] = mapped_column(String(160))
    commune_id: Mapped[int | None] = mapped_column(ForeignKey("communes.id"))
    birth_date: Mapped[date | None] = mapped_column(Date)
    lang: Mapped[str] = mapped_column(String(5), default="fr")
    consent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class UserVehicle(Base):
    """Voiture d'un client. Le matricule (normalisé : chiffres seuls) est unique dans toute la base : un matricule
    déjà pris se signale (PlateReport) et l'administrateur le libère, par exemple après une revente."""
    __tablename__ = "user_vehicles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    plate: Mapped[str] = mapped_column(String(16), unique=True)
    variant_id: Mapped[int | None] = mapped_column(ForeignKey("vehicle_variants.id"))
    year: Mapped[int | None] = mapped_column(Integer)
    label: Mapped[str | None] = mapped_column(String(120))   # voiture absente du référentiel : marque et modèle saisis
    nickname: Mapped[str | None] = mapped_column(String(60))
    mileage_km: Mapped[int | None] = mapped_column(Integer)
    vin: Mapped[str | None] = mapped_column(String(17))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    variant: Mapped[VehicleVariant | None] = relationship()


class PlateReport(Base):
    """Signalement « ce matricule est le mien mais il est déjà enregistré » ; traité par l'administrateur."""
    __tablename__ = "plate_reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plate: Mapped[str] = mapped_column(String(16), index=True)
    reporter_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    message: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="open")   # open|released|rejected
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class OtpCode(Base):
    __tablename__ = "otp_codes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone: Mapped[str] = mapped_column(String(20), index=True)
    code_hash: Mapped[str] = mapped_column(String(128))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    used: Mapped[bool] = mapped_column(Boolean, default=False)


class AdminAction(Base):
    """Journal des actions administrateur (section 10, sécurité)."""
    __tablename__ = "admin_actions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(60))
    target: Mapped[str | None] = mapped_column(String(120))
    details: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


# --- Véhicules ------------------------------------------------------------

class Brand(Base):
    __tablename__ = "brands"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)
    country: Mapped[str | None] = mapped_column(String(40))
    priority: Mapped[int] = mapped_column(Integer, default=0)
    models: Mapped[list[Model]] = relationship(back_populates="brand")


class Model(Base):
    __tablename__ = "models"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    pilot: Mapped[bool] = mapped_column(Boolean, default=False)  # pilote de référence exacte (F14)
    # Ordre d'affichage : nombre d'annonces Ouedkniss du modèle (data/market/ouedkniss_modeles.json)
    priority: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    brand: Mapped[Brand] = relationship(back_populates="models")
    variants: Mapped[list[VehicleVariant]] = relationship(back_populates="model")
    __table_args__ = (UniqueConstraint("brand_id", "name"),)


class VehicleVariant(Base):
    __tablename__ = "vehicle_variants"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("models.id"), index=True)
    year_from: Mapped[int] = mapped_column(Integer)
    year_to: Mapped[int | None] = mapped_column(Integer)
    engine: Mapped[str] = mapped_column(String(60))
    fuel: Mapped[str] = mapped_column(String(20))  # essence|diesel|gpl|hybride|electrique
    model: Mapped[Model] = relationship(back_populates="variants")


# --- Pièces ---------------------------------------------------------------

class PartCategory(Base):
    __tablename__ = "part_categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("part_categories.id"), index=True)
    name_fr: Mapped[str] = mapped_column(String(120))
    name_ar: Mapped[str | None] = mapped_column(String(120))
    synonyms: Mapped[list] = mapped_column(JSON, default=list)
    pilot: Mapped[bool] = mapped_column(Boolean, default=False)


class PartReference(Base):
    """Références exactes (F14), toujours lues dans cette table, jamais générées."""
    __tablename__ = "part_references"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("part_categories.id"), index=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("vehicle_variants.id"), index=True)
    oem_ref: Mapped[str] = mapped_column(String(60), index=True)
    part_brand: Mapped[str | None] = mapped_column(String(60))
    source: Mapped[str] = mapped_column(String(40))  # magasin|catalogue|terrain
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


# --- Magasins -------------------------------------------------------------

class Shop(Base):
    __tablename__ = "shops"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    phone: Mapped[str | None] = mapped_column(String(20), index=True, unique=True)   # unique depuis le 27/11/2026
    whatsapp: Mapped[str | None] = mapped_column(String(20))
    commune_id: Mapped[int | None] = mapped_column(ForeignKey("communes.id"))
    lat: Mapped[float | None] = mapped_column(Float)
    lng: Mapped[float | None] = mapped_column(Float)
    address: Mapped[str | None] = mapped_column(String(255))
    landmark: Mapped[str | None] = mapped_column(String(200))   # repère : « en face de la mosquée El Feth »
    hours: Mapped[str | None] = mapped_column(String(255))     # texte affiché (tiré de `opening` s'il existe)
    # Horaires structurés : {"days": [5, 6, 0, 1, 2, 3], "from": "08:00", "to": "18:00", "break": ["12:00", "13:30"]}
    # (jours de la semaine de Python : lundi = 0 ... dimanche = 6), pour « ouvert maintenant »
    opening: Mapped[dict | None] = mapped_column(JSON)
    closed_until: Mapped[date | None] = mapped_column(Date)    # « fermé exceptionnellement » jusqu'à cette date incluse
    closed_note: Mapped[str | None] = mapped_column(String(120))
    reject_reason: Mapped[str | None] = mapped_column(String(255))
    shop_type: Mapped[str] = mapped_column(String(20), default="pieces")  # pieces|casse|pneus|garage
    parts_origin: Mapped[list] = mapped_column(JSON, default=list)  # origine|adaptable|occasion
    sale_mode: Mapped[str | None] = mapped_column(String(20))  # gros|detail|les_deux
    photo_url: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)  # draft|verified|claimed|rejected
    source: Mapped[str] = mapped_column(String(20), default="terrain")  # terrain|osm|declared
    osm_id: Mapped[str | None] = mapped_column(String(40), unique=True)
    surveyor: Mapped[str | None] = mapped_column(String(80))
    visited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    owner_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)  # données fictives clairement marquées
    survey: Mapped[dict | None] = mapped_column(JSON)  # réponses étude de marché (section 14)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    brands: Mapped[list[ShopBrand]] = relationship(cascade="all, delete-orphan")
    categories: Mapped[list[ShopCategory]] = relationship(cascade="all, delete-orphan")
    commune: Mapped[Commune | None] = relationship()


class ShopClaim(Base):
    """Revendication d'une fiche créée par l'équipe par un compte dont le numéro n'est pas celui de la fiche :
    l'administrateur appelle le magasin avant de l'accepter (sinon n'importe qui pourrait prendre une fiche)."""
    __tablename__ = "shop_claims"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20), default="pending")   # pending|accepted|rejected
    reason: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ShopMember(Base):
    """Employé d'un magasin (plan côté magasin, phase 3). Le gérant est `shops.owner_user_id` ; lui seul ajoute,
    règle les accès (`permissions`), suspend ou retire un employé. L'équipe DALIL n'a aucun écran pour cela."""
    __tablename__ = "shop_members"
    __table_args__ = (UniqueConstraint("shop_id", "user_id", name="uq_shop_members"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    permissions: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(20), default="active")   # active|suspended
    added_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ShopActivity(Base):
    """Journal du magasin, lu par le gérant : qui a répondu à une demande, modifié un prix, ajouté un produit..."""
    __tablename__ = "shop_activity"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(40))
    target: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class ShopEvent(Base):
    """Statistiques du magasin (phase 4) : apparition dans un classement, fiche ouverte. Sans donnée personnelle :
    l'empreinte du client (HMAC de l'adresse IP) sert seulement à compter une fois par client et par jour."""
    __tablename__ = "shop_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(20))   # impression|view
    client_hash: Mapped[str | None] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class SearchEvent(Base):
    """Pièce cherchée par un client (« ce que cherchent les clients près de chez vous ») : famille, marque du
    véhicule, position arrondie à 0,01 degré (environ 1 km) si le client l'a donnée. Rien d'autre."""
    __tablename__ = "search_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("part_categories.id"), index=True)
    brand_id: Mapped[int | None] = mapped_column(ForeignKey("brands.id"))
    lat: Mapped[float | None] = mapped_column(Float)
    lng: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class ShopBrand(Base):
    __tablename__ = "shop_brands"
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.id", ondelete="CASCADE"), primary_key=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"), primary_key=True)
    source: Mapped[str] = mapped_column(String(20), default="declared")  # terrain|declared|observed
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=utcnow)


class ShopCategory(Base):
    __tablename__ = "shop_categories"
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.id", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("part_categories.id"), primary_key=True)
    source: Mapped[str] = mapped_column(String(20), default="declared")
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=utcnow)


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.id", ondelete="CASCADE"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("part_categories.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    oem_ref: Mapped[str | None] = mapped_column(String(60), index=True)
    part_brand: Mapped[str | None] = mapped_column(String(60))
    condition: Mapped[str] = mapped_column(String(20), default="neuf")  # neuf|adaptable|occasion
    price: Mapped[float | None] = mapped_column(Float)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    photo_url: Mapped[str | None] = mapped_column(String(255))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    # Dernière fois que le magasin a confirmé le prix et le stock (« prix confirmé il y a N jours »)
    price_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=utcnow)
    fitments: Mapped[list[ProductFitment]] = relationship(cascade="all, delete-orphan")


class ProductFitment(Base):
    __tablename__ = "product_fitments"
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("vehicle_variants.id"), primary_key=True)


# --- Connaissances de diagnostic -----------------------------------------

class Fault(Base):
    __tablename__ = "faults"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    name_fr: Mapped[str] = mapped_column(String(160))
    system: Mapped[str] = mapped_column(String(40))  # freinage|moteur|allumage|...
    severity: Mapped[str] = mapped_column(String(20))  # faible|moyenne|haute|critique
    description: Mapped[str | None] = mapped_column(Text)
    do_not_drive: Mapped[bool] = mapped_column(Boolean, default=False)
    fuel: Mapped[str | None] = mapped_column(String(20))  # restreint la panne à un carburant
    parts: Mapped[list[FaultPart]] = relationship(cascade="all, delete-orphan")


class FaultPart(Base):
    __tablename__ = "fault_parts"
    fault_id: Mapped[int] = mapped_column(ForeignKey("faults.id", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("part_categories.id"), primary_key=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)


class DtcCode(Base):
    __tablename__ = "dtc_codes"
    code: Mapped[str] = mapped_column(String(8), primary_key=True)
    title_fr: Mapped[str] = mapped_column(String(255))
    title_en: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    causes: Mapped[list] = mapped_column(JSON, default=list)
    symptoms: Mapped[list] = mapped_column(JSON, default=list)
    source: Mapped[str] = mapped_column(String(40), default="dalil-seed")


class DtcPart(Base):
    __tablename__ = "dtc_parts"
    code: Mapped[str] = mapped_column(ForeignKey("dtc_codes.code", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("part_categories.id"), primary_key=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(60), index=True)
    lang: Mapped[str] = mapped_column(String(5), default="fr")
    text: Mapped[str] = mapped_column(Text)
    text_original: Mapped[str | None] = mapped_column(Text)
    embedding: Mapped[list | None] = mapped_column(Embedding)
    meta: Mapped[dict | None] = mapped_column("metadata", JSON)
    license: Mapped[str] = mapped_column(String(60), nullable=False)  # obligatoire (section 8)


# --- Traces d'usage -------------------------------------------------------

class DiagnosisSession(Base):
    __tablename__ = "diagnosis_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    variant_id: Mapped[int | None] = mapped_column(ForeignKey("vehicle_variants.id"))
    # Voiture du compte client concernée (historique par voiture) ; vidé si la voiture est retirée du compte
    user_vehicle_id: Mapped[int | None] = mapped_column(ForeignKey("user_vehicles.id", ondelete="SET NULL"))
    input_text: Mapped[str] = mapped_column(Text)
    lang: Mapped[str] = mapped_column(String(5), default="fr")
    dtc_codes: Mapped[list] = mapped_column(JSON, default=list)
    answers: Mapped[dict] = mapped_column(JSON, default=dict)
    result_json: Mapped[dict | None] = mapped_column(JSON)
    retrieved_chunk_ids: Mapped[list] = mapped_column(JSON, default=list)
    model_version: Mapped[str] = mapped_column(String(60))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class PartRequest(Base):
    __tablename__ = "part_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int | None] = mapped_column(ForeignKey("diagnosis_sessions.id"))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    variant_id: Mapped[int | None] = mapped_column(ForeignKey("vehicle_variants.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("part_categories.id"))
    status: Mapped[str] = mapped_column(String(20), default="open")  # open|answered|closed
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class RequestResponse(Base):
    __tablename__ = "request_responses"
    request_id: Mapped[int] = mapped_column(ForeignKey("part_requests.id", ondelete="CASCADE"), primary_key=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.id", ondelete="CASCADE"), primary_key=True)
    available: Mapped[bool | None] = mapped_column(Boolean)  # None = notifié, pas encore répondu
    price: Mapped[float | None] = mapped_column(Float)
    notified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ContactEvent(Base):
    __tablename__ = "contact_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int | None] = mapped_column(ForeignKey("diagnosis_sessions.id"))
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.id", ondelete="CASCADE"), index=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("part_categories.id"))
    variant_id: Mapped[int | None] = mapped_column(ForeignKey("vehicle_variants.id"))
    channel: Mapped[str] = mapped_column(String(20))  # call|whatsapp
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class VehicleRequest(Base):
    """« Mon véhicule n'est pas dans la liste » : ce que l'utilisateur a saisi, pour savoir quoi ajouter au référentiel."""
    __tablename__ = "vehicle_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brand: Mapped[str] = mapped_column(String(60))
    model: Mapped[str] = mapped_column(String(80))
    year: Mapped[int | None] = mapped_column(Integer)
    engine: Mapped[str | None] = mapped_column(String(60))
    client_hash: Mapped[str | None] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Feedback(Base):
    __tablename__ = "feedback"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int | None] = mapped_column(ForeignKey("diagnosis_sessions.id"))
    shop_id: Mapped[int | None] = mapped_column(ForeignKey("shops.id", ondelete="CASCADE"), index=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("part_categories.id"))
    part_found: Mapped[bool | None] = mapped_column(Boolean)
    diagnosis_correct: Mapped[bool | None] = mapped_column(Boolean)
    comment: Mapped[str | None] = mapped_column(Text)
    # Empreinte du client (HMAC de l'adresse IP, jamais l'adresse) : un « pièce trouvée » compte une fois par client
    # et par jour dans le score (section 6.4), pour qu'un magasin ne puisse pas gonfler le sien.
    client_hash: Mapped[str | None] = mapped_column(String(16), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
