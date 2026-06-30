"""
models.py - Startup Intelligence Schema (Crunchbase-like)
"""

from __future__ import annotations

import re
import hashlib
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


# =========================
# UTILS
# =========================

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def make_id(nom: str, source: str = "") -> str:
    base = nom or source or "unknown"
    h = hashlib.sha1(base.lower().encode("utf-8")).hexdigest()[:8]
    return f"{slugify(base)}-{h}"


# =========================
# JOB OFFER
# =========================

class JobOffer(BaseModel):
    titre: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    date_publication: Optional[str] = None


# =========================
# FUNDING (IMPORTANT)
# =========================

class FundingRound(BaseModel):
    stage: Optional[str] = None          # Seed, Series A...
    montant: Optional[str] = None        # "250K USD"
    date: Optional[str] = None
    investisseurs: List[str] = Field(default_factory=list)


# =========================
# SOCIALS
# =========================

class Socials(BaseModel):
    website: Optional[str] = None
    linkedin: Optional[str] = None
    facebook: Optional[str] = None
    twitter: Optional[str] = None
    instagram: Optional[str] = None


# =========================
# CONTACT
# =========================

class Contact(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


# =========================
# BASE (SCRAPING RAW)
# =========================

class StartupBase(BaseModel):
    """
    Données brutes collectées (scraping multi-sources)
    """

    id: str = ""
    nom: str
    secteur: Optional[str] = None
    domaine: Optional[str] = None

    description: Optional[str] = None
    site_web: Optional[str] = None

    ville: Optional[str] = None
    pays: str = "Tunisia"

    source: str = ""
    source_url: str = ""

    date_collecte: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    @field_validator("site_web")
    @classmethod
    def normalize_url(cls, v):
        if not v:
            return v
        v = v.strip()
        if not re.match(r"^https?://", v):
            v = "https://" + v
        return v.rstrip("/")

    @field_validator("nom")
    @classmethod
    def clean_nom(cls, v):
        return " ".join(v.split()).strip()

    def model_post_init(self, __context__) -> None:
        if not self.id:
            self.id = make_id(self.nom, self.source)


# =========================
# ENRICHED (FINAL MODEL)
# =========================

class StartupEnriched(StartupBase):
    """
    Version enrichie avec LLM + APIs
    """

    # ---- STRUCTURED OBJECTS ----
    contact: Contact = Field(default_factory=Contact)
    socials: Socials = Field(default_factory=Socials)
    funding: FundingRound = Field(default_factory=FundingRound)

    # ---- PEOPLE ----
    fondateurs: List[str] = Field(default_factory=list)

    # ---- COMPANY INFO ----
    annee_creation: Optional[int] = None
    nb_employes_estime: Optional[str] = None
    stage: Optional[str] = None

    # ---- AI / ANALYTICS ----
    tags: List[str] = Field(default_factory=list)
    summary_llm: Optional[str] = None

    # ---- JOBS ----
    offres_emploi: List[JobOffer] = Field(default_factory=list)

    # ---- METADATA ----
    sources_enrichissement: List[str] = Field(default_factory=list)
    date_enrichissement: Optional[str] = None

    # =========================
    # METHODS
    # =========================

    def mark_enriched(self):
        self.date_enrichissement = datetime.utcnow().isoformat()