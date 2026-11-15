"""Registre des sources. Une source n'existe pour le pipeline que si elle est déclarée ici,
avec sa licence, et décrite dans data/sources/<id>.md (vérifié par les tests)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class SourceSpec:
    id: str
    name: str
    license: str
    license_url: str
    attribution: str
    lang: str
    module: str  # module de collecte dans pipeline.sources
    synthetic: bool = False
    notes: str = ""


@dataclass
class Context:
    limit: int | None = None
    refresh: bool = False
    options: dict = field(default_factory=dict)
    log: Callable[[str], None] = print


SOURCES: dict[str, SourceSpec] = {s.id: s for s in [
    SourceSpec(
        "nhtsa_complaints", "NHTSA – plaintes des propriétaires (ODI Complaints)",
        "Domaine public (gouvernement des États-Unis)", "https://www.usa.gov/government-copyright",
        "U.S. National Highway Traffic Safety Administration", "en", "nhtsa",
    ),
    SourceSpec(
        "nhtsa_recalls", "NHTSA – campagnes de rappel",
        "Domaine public (gouvernement des États-Unis)", "https://www.usa.gov/government-copyright",
        "U.S. National Highway Traffic Safety Administration", "en", "nhtsa",
    ),
    SourceSpec(
        "rappelconso", "RappelConso – rappels automobiles (DGCCRF)",
        "Licence Ouverte v2.0 (Etalab)", "https://www.etalab.gouv.fr/wp-content/uploads/2017/04/ETALAB-Licence-Ouverte-v2.0.pdf",
        "DGCCRF, RappelConso (data.economie.gouv.fr)", "fr", "rappelconso",
    ),
    SourceSpec(
        "mot_uk", "DVSA – contrôle technique britannique (MOT anonymisé)",
        "Open Government Licence v3.0", "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "Contains public sector information licensed under the Open Government Licence v3.0 (DVSA)", "en", "mot",
    ),
    SourceSpec(
        "stackexchange_mechanics", "Stack Exchange – Motor Vehicle Maintenance & Repair (export 2024-12-31)",
        "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/",
        "Auteurs de mechanics.stackexchange.com (lien et nom d'auteur par enregistrement)", "en", "stackexchange",
    ),
    SourceSpec(
        "cvffad", "Chinese Vehicle Fleet Fault Association Dataset (Mendeley Data, v1)",
        "CC BY 4.0", "http://creativecommons.org/licenses/by/4.0",
        "Zheng Y.-J., Chinese Vehicle Fleet Fault Association Dataset, Mendeley Data, v1, doi:10.17632/r98g7g6k5t.1",
        "zh", "cvffad", synthetic=True,
        notes="Textes générés à partir de gabarits (champ source = generated), flottes de camions et de cars anonymisées.",
    ),
]}
