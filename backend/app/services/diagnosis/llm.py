"""Étape 4 : synthèse par un modèle de langage, derrière une interface unique.

Fournisseurs :
- none           : pas d'appel ; la synthèse est déterministe (classifieur + recherche).
- openai_compat  : serveur compatible OpenAI (llama.cpp, Ollama, vLLM) servant le modèle
                   affiné par l'équipe (Qwen3 / Gemma 3 + LoRA). C'est la cible du PFE.
- anthropic      : modèle payant, utilisé comme point de comparaison sur le jeu de test.

Le modèle ne peut que reclasser des pannes candidates fournies par la chaîne ; toute panne
hors de la liste est rejetée, et aucune référence de pièce n'est jamais demandée au modèle.
"""
from __future__ import annotations

import json
import logging
import re
import threading
import time
from collections import OrderedDict
from datetime import datetime, timezone

import httpx

from ...config import get_settings

log = logging.getLogger("dalil.llm")

SYSTEM_PROMPT = (
    "Tu es l'assistant de diagnostic automobile DALIL, à Oran. Tu reçois la description d'une panne, "
    "le véhicule, des passages de la base de connaissances et une liste de pannes candidates. "
    "Réponds UNIQUEMENT par un objet JSON : "
    '{"ranking":[{"fault":"<slug candidat>","confidence":0..1,"explanation":"<1 phrase en français>"}]} '
    "avec au plus 3 éléments, choisis exclusivement parmi les slugs candidats. "
    "N'invente jamais de référence de pièce, de prix ni de magasin."
)


class LLMProvider:
    name = "none"

    def complete_json(self, system: str, user: str) -> dict | None:
        return None


class _CallBudget:
    """Plafond mensuel d'appels (section 10, coût)."""

    def __init__(self):
        self.month, self.count = None, 0

    def allow(self) -> bool:
        m = datetime.now(timezone.utc).strftime("%Y-%m")
        if m != self.month:
            self.month, self.count = m, 0
        if self.count >= get_settings().llm_monthly_call_cap:
            return False
        self.count += 1
        return True


budget = _CallBudget()


def _parse_json(text: str) -> dict | None:
    m = re.search(r"\{.*\}", text or "", re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def complete_json(self, system: str, user: str) -> dict | None:
        s = get_settings()
        r = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": s.llm_api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": s.llm_model, "max_tokens": 800, "system": system,
                  "messages": [{"role": "user", "content": user}]},
            timeout=30,
        )
        r.raise_for_status()
        text = "".join(b.get("text", "") for b in r.json().get("content", []) if b.get("type") == "text")
        return _parse_json(text)


class OpenAICompatProvider(LLMProvider):
    name = "openai_compat"

    def complete_json(self, system: str, user: str) -> dict | None:
        s = get_settings()
        r = httpx.post(
            s.llm_base_url.rstrip("/") + "/chat/completions",
            headers={"Authorization": f"Bearer {s.llm_api_key or 'local'}"},
            json={"model": s.llm_model, "temperature": 0, "max_tokens": 800,
                  "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]},
            timeout=s.llm_timeout,
        )
        r.raise_for_status()
        return _parse_json(r.json()["choices"][0]["message"]["content"])


def get_llm() -> LLMProvider:
    p = get_settings().llm_provider
    if p == "anthropic":
        return AnthropicProvider()
    if p == "openai_compat":
        return OpenAICompatProvider()
    return LLMProvider()


def build_user_message(text: str, vehicle: str, passages: list[str], candidates: dict[str, str]) -> str:
    """Message envoyé au modèle. Utilisé aussi par ml/build_llm_dataset.py : le modèle affiné
    apprend exactement le format qu'il recevra en production."""
    return json.dumps({
        "description": text, "vehicule": vehicle,
        "passages": [p[:600] for p in passages[:5]],
        "candidats": [{"slug": k, "nom": v} for k, v in candidates.items()],
    }, ensure_ascii=False)


class _ResponseCache:
    """Cache en mémoire des classements validés (section 10, coût : codes OBD et questions fréquentes).

    Clé : fournisseur, modèle et message complet (texte, véhicule, passages, candidats). Une même question
    posée deux fois ne coûte qu'un appel ; changer de modèle ou de passages change la clé. Vidé au
    redémarrage du serveur (pas de table : le gain d'un cache persistant ne justifie pas une migration)."""

    def __init__(self, size: int = 512):
        self.size = size
        self.data: OrderedDict[str, tuple[float, list[dict]]] = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key: str) -> list[dict] | None:
        with self.lock:
            hit = self.data.get(key)
            if hit is None:
                return None
            if time.monotonic() - hit[0] > get_settings().llm_cache_ttl:
                del self.data[key]
                return None
            self.data.move_to_end(key)
            return hit[1]

    def put(self, key: str, value: list[dict]) -> None:
        with self.lock:
            self.data[key] = (time.monotonic(), value)
            self.data.move_to_end(key)
            while len(self.data) > self.size:
                self.data.popitem(last=False)


cache = _ResponseCache()

# États rendus avec le classement, recopiés dans le résultat du diagnostic (champ « llm ») :
#   off      pas de modèle de langage configuré, ou rien à classer
#   used     le modèle a répondu et sa réponse a été retenue
#   cached   même question déjà posée : réponse du cache
#   fallback le modèle n'a pas répondu à temps, a échoué, ou sa réponse a été rejetée : classement du classifieur


def rerank_with_llm(text: str, vehicle: str, passages: list[str], candidates: dict[str, str]) -> tuple[list[dict] | None, str]:
    """Renvoie (classement validé ou None, état). Dans tous les cas d'échec la chaîne garde le classement
    du classifieur : l'utilisateur reçoit un diagnostic, jamais une erreur."""
    llm = get_llm()
    if llm.name == "none" or not candidates:
        return None, "off"
    user = build_user_message(text, vehicle, passages, candidates)
    key = f"{llm.name}|{get_settings().llm_model}|{user}"
    cached = cache.get(key)
    if cached is not None:
        return cached, "cached"
    if not budget.allow():
        return None, "fallback"
    try:
        data = llm.complete_json(SYSTEM_PROMPT, user)
    except Exception as e:  # réseau, délai dépassé, quota : la chaîne continue sans modèle de langage
        log.warning("Appel au modèle de langage en échec : %s", e)
        return None, "fallback"
    if not isinstance(data, dict) or not isinstance(data.get("ranking"), list):
        return None, "fallback"
    out = []
    for item in data["ranking"][:3]:
        if isinstance(item, dict) and item.get("fault") in candidates:
            try:
                conf = min(max(float(item.get("confidence", 0)), 0.0), 1.0)
            except (TypeError, ValueError):
                conf = 0.0
            out.append({"fault": item["fault"], "confidence": conf, "explanation": str(item.get("explanation", ""))[:300]})
    if not out:  # réponse valide mais aucune panne parmi les candidats : rejetée
        return None, "fallback"
    cache.put(key, out)
    return out, "used"
