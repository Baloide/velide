import re

# Codice Fiscale Italiano (16 caratteri con possibile omocodia)
REGEX_TAX_CODE = re.compile(
    r"\b[A-Z]{6}[0-9LMNPQRSTUV]{2}[A-EHLMPR-T][0-9LMNPQRSTUV]{2}[A-Z][0-9LMNPQRSTUV]{3}[A-Z]\b",
    re.IGNORECASE,
)

# Email
REGEX_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

# Telefoni e Cellulari (italiani e formati comuni con prefisso +39)
REGEX_PHONE = re.compile(
    r"(?:(?:\+|00)39[\s\.\-]?)?(?:(?:3[1-9]\d{1}[\s\.\-]?\d{6,7})|(?:0\d{1,4}[\s\.\-]?\d{5,8}))\b"
)

# Date in formato numerico (es. 12/05/1980, 12-05-1980, 12.05.80)
REGEX_DATE_NUMERIC = re.compile(
    r"\b(?:0?[1-9]|[12][0-9]|3[01])[\/\-\.](?:0?[1-9]|1[012])[\/\-\.](?:19\d{2}|20\d{2}|\d{2})\b"
)

# Date in formato testuale italiano (es. 14 ottobre 1985, 2 marzo 2024)
MONTHS_IT = (
    r"(?:gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre|"
    r"gen|feb|mar|apr|mag|giu|lug|ago|set|ott|nov|dic)"
)
REGEX_DATE_TEXT = re.compile(
    rf"\b(?:0?[1-9]|[12][0-9]|3[01])\s+{MONTHS_IT}\s+(?:19\d{2}|20\d{2})\b",
    re.IGNORECASE,
)

# Nomi preceduti da qualifiche o etichette cliniche
PREFIXES_CLINICAL = (
    r"(?:Paziente|Paz\.|Sig\.|Sig\.ra|Signor|Signora|Dott\.|Dott\.ssa|Dr\.|Dr\.ssa|Prof\.|Prof\.ssa|"
    r"Assistito|Assistita|Nome e Cognome|Nome|Cognome|Intestatario|Nato il|Nata il)"
)
REGEX_CLINICAL_NAME = re.compile(
    rf"(?P<prefix>{PREFIXES_CLINICAL})[:\s]+(?P<name>[A-ZÀ-Ú][a-zà-ú']+(?:\s+[A-ZÀ-Ú][a-zà-ú']+){{1,3}})",
    re.UNICODE,
)

# Identificativi sanitari: Cartella Clinica, ID Referto, Tessera Sanitaria
REGEX_CLINICAL_ID = re.compile(
    r"\b(?:Cartella(?:\s+Clinica)?|C\.C\.|ID(?:\s+Referto)?|N\.\s*Cartella|Tessera\s+Sanitaria|Codice\s+Sanitario|Protocollo|Fascicolo)\s*[:#\s]*([A-Z0-9\-\/]{4,20})\b",
    re.IGNORECASE,
)

# Ospedali e strutture sanitarie
REGEX_HOSPITAL = re.compile(
    r"\b(?:Ospedale|Policlinico|Presidio\s+Ospedaliero|Azienda\s+Ospedaliera|A\.?O\.?U\.?|ASL|A\.?S\.?L\.?|Casa\s+di\s+Cura|IRCCS|Clinica)\s+([A-ZÀ-Ú][a-zà-úA-ZÀ-Ú'\-\s]+?)(?=\b(?:,|\.|\n|–|-|di|in|$))",
    re.UNICODE,
)

# Indirizzi italiani comuni
REGEX_ADDRESS = re.compile(
    r"\b(?:Via|Viale|Corso|Piazza|Piazzale|Largo|Vicolo|Contrada|Strada)\s+([A-ZÀ-Ú][a-zà-úA-ZÀ-Ú'\s]+(?:\d{1,4}[A-Za-z]?)?)",
    re.UNICODE,
)
