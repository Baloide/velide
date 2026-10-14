from enum import Enum
from typing import List, Literal

from pydantic import BaseModel, Field


class MaskMode(str, Enum):
    TAG = "TAG"  # E.g., [NOME], [CODICE_FISCALE]
    BLOCK = "BLOCK"  # E.g., ██████
    PSEUDONYM = "PSEUDONYM"  # E.g., Paziente_1, Ospedale_A
    ASTERISK = "ASTERISK"  # E.g., ******


class RedactOptions(BaseModel):
    language: Literal["it", "en", "es", "de", "fr", "pt", "nl", "pl", "tr", "ru"] = "en"
    mask_mode: MaskMode = Field(
        default=MaskMode.TAG, description="Modalità di mascheramento dei dati sensibili"
    )
    redact_names: bool = Field(default=True, description="Riconosci e maschera nomi e cognomi")
    redact_tax_codes: bool = Field(
        default=True, description="Maschera Codici Fiscali (CF) italiani"
    )
    redact_dates: bool = Field(default=True, description="Maschera date di nascita e visite")
    redact_contacts: bool = Field(
        default=True, description="Maschera numeri di telefono, cellulari, email e link web"
    )
    redact_locations: bool = Field(
        default=True, description="Maschera indirizzi, città, CAP e strutture ospedaliere"
    )
    redact_ids: bool = Field(
        default=True, description="Maschera codici cartella, tessere sanitarie e ID referti"
    )
    custom_keywords: List[str] = Field(
        default_factory=list,
        description="Lista opzionale di parole o nominativi personalizzati da censurare",
    )


class EntityDetection(BaseModel):
    entity_type: str
    original: str
    replacement: str
    start: int
    end: int
    confidence: float = 1.0


class RedactRequest(BaseModel):
    text: str = Field(
        ..., min_length=1, max_length=200000, description="Testo clinico da de-identificare"
    )
    options: RedactOptions = Field(default_factory=RedactOptions)


class RedactResponse(BaseModel):
    redacted_text: str
    entities_found: int
    entities: List[EntityDetection]
    execution_ms: float
