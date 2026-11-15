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


def rerank_with_llm(text: str, vehicle: str, passages: list[str], candidates: dict[str, str]) -> list[dict] | None:
    """Renvoie un classement validé, ou None (pas de fournisseur, budget épuisé, réponse invalide)."""
    llm = get_llm()
    if llm.name == "none" or not candidates or not budget.allow():
        return None
    user = build_user_message(text, vehicle, passages, candidates)
    try:
        data = llm.complete_json(SYSTEM_PROMPT, user)
    except Exception as e:  # réseau, quota : la chaîne continue sans modèle de langage
        log.warning("Appel au modèle de langage en échec : %s", e)
        return None
    if not isinstance(data, dict) or not isinstance(data.get("ranking"), list):
        return None
    out = []
    for item in data["ranking"][:3]:
        if isinstance(item, dict) and item.get("fault") in candidates:
            try:
                conf = min(max(float(item.get("confidence", 0)), 0.0), 1.0)
            except (TypeError, ValueError):
                conf = 0.0
            out.append({"fault": item["fault"], "confidence": conf, "explanation": str(item.get("explanation", ""))[:300]})
    return out or None
