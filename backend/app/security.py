"""Connexion par code SMS à usage unique, jetons JWT, contrôle des rôles, limitation de débit."""
from __future__ import annotations

import hashlib
import hmac
import logging
import re
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .config import get_settings
from .db import get_db
from .models import AdminAction, User

log = logging.getLogger("dalil.auth")
bearer = HTTPBearer(auto_error=False)

PHONE_RE = re.compile(r"^(?:\+213|0)(5|6|7)\d{8}$")


def normalize_phone(raw: str) -> str:
    """Normalise un numéro mobile algérien au format +213XXXXXXXXX."""
    p = re.sub(r"[\s.\-()]", "", raw or "")
    if p.startswith("00213"):
        p = "+" + p[2:]
    if not PHONE_RE.match(p):
        raise HTTPException(422, "Numéro de mobile algérien invalide (ex. 0550 12 34 56)")
    return "+213" + p[-9:]


def hash_code(phone: str, code: str) -> str:
    key = get_settings().jwt_secret.encode()
    return hmac.new(key, f"{phone}:{code}".encode(), hashlib.sha256).hexdigest()


def new_otp() -> str:
    """Code à 6 chiffres. `otp_test_code` (tests de bout en bout dans un navigateur, qui ne lit pas la console)
    n'est honoré qu'avec le fournisseur SMS « console » : jamais avec un vrai envoi de SMS."""
    s = get_settings()
    if s.otp_test_code:
        if s.sms_provider == "console":
            return s.otp_test_code
        log.error("DALIL_OTP_TEST_CODE ignoré : réservé au fournisseur SMS « console »")
    return f"{secrets.randbelow(10**6):06d}"


class SmsSender:
    """Interface d'envoi SMS ; le fournisseur réel est choisi à la mise en ligne."""

    def send(self, phone: str, text: str) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class ConsoleSms(SmsSender):
    last: dict[str, str] = {}

    def send(self, phone: str, text: str) -> None:
        ConsoleSms.last[phone] = text
        log.warning("[SMS console] %s : %s", phone, text)


def get_sms_sender() -> SmsSender:
    return ConsoleSms()


def create_token(user: User) -> str:
    s = get_settings()
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=s.jwt_ttl_hours),
    }
    return jwt.encode(payload, s.jwt_secret, algorithm="HS256")


def current_user_optional(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)
) -> User | None:
    if not creds:
        return None
    try:
        payload = jwt.decode(creds.credentials, get_settings().jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Jeton invalide ou expiré")
    return db.get(User, int(payload["sub"]))


def current_user(user: User | None = Depends(current_user_optional)) -> User:
    if user is None:
        raise HTTPException(401, "Connexion requise")
    return user


def require_role(*roles: str):
    def dep(user: User = Depends(current_user)) -> User:
        if user.role not in roles and user.role != "admin":
            raise HTTPException(403, "Accès refusé")
        return user

    return dep


require_admin = require_role("admin")


def log_admin(db: Session, user: User, action: str, target: str | None = None, details: dict | None = None):
    db.add(AdminAction(user_id=user.id, action=action, target=target, details=details))


class RateLimiter:
    """Limiteur simple à fenêtre glissante, en mémoire (suffisant pour un seul processus)."""

    def __init__(self, per_minute: int):
        self.per_minute = per_minute
        self.hits: dict[str, deque] = defaultdict(deque)

    def __call__(self, request: Request) -> None:
        key = request.client.host if request.client else "anon"
        now = time.monotonic()
        q = self.hits[key]
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= self.per_minute:
            raise HTTPException(429, "Trop de demandes, réessayez dans une minute")
        q.append(now)


diagnosis_limiter = RateLimiter(get_settings().diagnosis_rate_per_minute)
feedback_limiter = RateLimiter(get_settings().feedback_rate_per_minute)


def client_hash(request: Request) -> str:
    """Empreinte courte et non réversible du client (HMAC de l'adresse IP avec la clé du serveur) : sert à compter
    les retours par client sans conserver d'adresse IP (collecte minimale, section 10)."""
    ip = request.client.host if request.client else "anon"
    return hmac.new(get_settings().jwt_secret.encode(), f"client:{ip}".encode(), hashlib.sha256).hexdigest()[:16]
otp_limiter = RateLimiter(get_settings().otp_rate_per_minute)
