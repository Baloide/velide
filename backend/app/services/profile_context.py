"""Contact/profile context and disambiguation for text extracted from CVs and PDFs."""

import re
import unicodedata
from urllib.parse import unquote, urlsplit

from app.services.person_context import is_person

URL_START = re.compile(r"\b(?:https?://|www\.)[^\s<>()]+", re.I)
ROLE = re.compile(
    r"\b(?:bioengineer|engineer|engineering|specialist|researcher|developer|designer|consultant|psychologist|physician|nurse|student|manager|ingegnere|ricercator|medico|infermier|psicolog|consulent|studente|ingenieur|ingeniero|investigador|développeur|chercheur|инженер|исследователь|психолог)\w*\b",
    re.I,
)
PROFILE_HEADING = re.compile(
    r"^[ \t]*(?:Curriculum Vitae|CV|Résumé|Resume|Competenze principali|Esperienza professionale|Work experience|Skills|Berufserfahrung|Expérience professionnelle|Experiencia laboral|Experiência profissional|Werkervaring|Doświadczenie zawodowe|İş deneyimi|Опыт работы)[ \t]*$",
    re.I | re.M,
)
COUNTRIES = r"Italia|Italy|France|Francia|Frankreich|França|España|Spagna|Spain|Espagne|Spanien|Portugal|Portogallo|Deutschland|Germany|Germania|Allemagne|Alemanha|Nederland|Netherlands|Paesi Bassi|Polska|Poland|Polonia|Pologne|Polen|Türkiye|Turkey|Turchia|Turquie|Россия|Russia|Russie|United Kingdom|Regno Unito|United States|Stati Uniti|USA|UK"
CITY_COUNTRY = re.compile(
    rf"^[ \t]*[^\W\d_][^\n,;:]+(?:,[ \t]*[^\n,;:]+)?,[ \t]*(?:{COUNTRIES})[ \t]*$", re.I | re.M
)


def detect_urls(text):
    """Return original-text URL spans, including supported PDF line wraps.

    Args:
        text: Original Unicode text, without normalization.
    Returns:
        Start/end character offsets; the end offset is exclusive.
    """
    spans = []
    for match in URL_START.finditer(text):
        if spans and match.start() < spans[-1][1]:
            continue
        end = match.end()
        # PDF exports often wrap a long profile slug just after a hyphen.
        if text[end - 1] in "-/":
            continuation = re.match(r"\r?\n[ \t]*([a-z0-9][a-z0-9._~/%?=&+#\-]*)", text[end:])
            if continuation:
                end += continuation.end()
        while end > match.start() and text[end - 1] in ".,;:!?":
            end -= 1
        spans.append((match.start(), end))
    return spans


def _slug(value):
    value = unicodedata.normalize("NFKD", unquote(value).casefold())
    value = "".join(c for c in value if not unicodedata.combining(c))
    return "-".join(re.findall(r"[^\W\d_]+", value))


def detect_profile_people(text, url_spans):
    """Return name spans supported by profile URLs or a CV heading and role.

    Args:
        text: Original Unicode text.
        url_spans: URL start/end offsets already found in that text.
    Returns:
        (start, exclusive_end, entity_type) tuples. This is a heuristic, not NER.
    """
    slugs = []
    for start, end in url_spans:
        value = re.sub(r"\s+", "", text[start:end])
        try:
            parsed = urlsplit(value if "://" in value else "https://" + value)
            hostname = (parsed.hostname or "").lower()
        except ValueError:
            # A malformed host must not prevent redaction of the rest of a note.
            continue
        if hostname in ("linkedin.com", "www.linkedin.com") and parsed.path.startswith("/in/"):
            slug = _slug(parsed.path[4:].strip("/"))
            if slug:
                slugs.append(slug)
    lines = list(re.finditer(r"[^\n]+", text))
    profile_context = bool(slugs) or bool(PROFILE_HEADING.search(text))
    names = []
    for i, line in enumerate(lines):
        candidate = line.group().strip()
        if not is_person(candidate):
            continue
        candidate_slug = _slug(candidate)
        linked_identity = candidate_slug in slugs
        next_line = next(
            (other.group().strip() for other in lines[i + 1 : i + 4] if other.group().strip()), ""
        )
        if linked_identity or (profile_context and ROLE.search(next_line)):
            start = line.start() + len(line.group()) - len(line.group().lstrip())
            names.append((start, start + len(candidate), "NAME"))
    return names
