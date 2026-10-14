import re
import time

from app.schemas.redact import EntityDetection, MaskMode, RedactOptions, RedactResponse
from app.services.languages import RULES, labels
from app.services.patterns import REGEX_EMAIL, REGEX_TAX_CODE
from app.services.person_context import detect_contextual_people
from app.services.profile_context import CITY_COUNTRY, detect_profile_people, detect_urls

DATE_NUMERIC = re.compile(
    r"\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[/.-]\d{1,2}[/.-](?:\d{4}|\d{2}))\b"
)
PHONE = re.compile(
    r"(?<![\w])(?:\+|00)\d{1,3}(?:[ .()\-]*\d){6,13}(?!\w)|\b(?:\d[ .()\-]*){8,14}\b"
)
# Extra national IDs require explicit context to avoid treating clinical measurements as IDs.
NATIONAL_ID = re.compile(
    r"\b(?:NIF|NIE|DNI|CPF|Steuer-ID|Tax ID|NHS number|NIR|numéro de sécurité sociale)\s*:\s*[A-Z0-9][A-Z0-9 .\-/]{5,24}",
    re.I,
)


class RedactionEngine:
    """Deterministic local rules; review the result before sharing it."""

    def redact(self, text: str, options: RedactOptions) -> RedactResponse:
        """Detect and replace selected identifiers without modifying the input.

        Args:
            text: Original Unicode text; API callers enforce the size limit.
            options: Language, enabled categories, masking mode, custom terms.
        Returns:
            Output text and detections with original-text, exclusive-end offsets.

        Overlapping spans are merged. Pseudonyms are consistent only within this
        request; no registry persists. Confidence values are conventional scores,
        not measured probabilities or an anonymity guarantee.
        """
        started = time.perf_counter()
        rules = RULES[options.language]
        matches = []
        contextual_names, contextual_ids = detect_contextual_people(text, options.language)
        urls = detect_urls(text)
        contextual_names.extend(detect_profile_people(text, urls))

        def add(regex, kind):
            for m in regex.finditer(text):
                matches.append((m.start(), m.end(), kind))

        if options.redact_tax_codes:
            add(REGEX_TAX_CODE, "TAX_CODE")
            add(NATIONAL_ID, "TAX_CODE")
        if options.redact_dates:
            add(DATE_NUMERIC, "DATE")
            add(rules["date"], "DATE")
        if options.redact_contacts:
            add(REGEX_EMAIL, "EMAIL")
            matches.extend((start, end, "URL") for start, end in urls)
            # Date-looking strings must never win against dates, even when date masking is disabled.
            dates = [(m.start(), m.end()) for m in DATE_NUMERIC.finditer(text)]
            for m in PHONE.finditer(text):
                if not any(
                    m.start() < end and m.end() > start
                    for start, end in dates + urls + [(s, e) for s, e, _ in contextual_ids]
                ):
                    matches.append((m.start(), m.end(), "PHONE"))
        if options.redact_names:
            discovered_names = list(contextual_names)
            for m in rules["name"].finditer(text):
                kind = (
                    "DOCTOR"
                    if re.search(
                        r"dott|dr|doctor|doutor|prof|docteur|pr\.|dokter|lekarz|lekarka|doktor|врач|доктор|д-р",
                        m["prefix"],
                        re.I,
                    )
                    else "NAME"
                )
                discovered_names.append((m.start("name"), m.end("name"), kind))
            # Reuse contextual evidence throughout the document, allowing spacing changes.
            seen_names = set()
            for start, end, kind in discovered_names:
                words = text[start:end].split()
                key = (" ".join(words).casefold(), kind)
                if key in seen_names:
                    continue
                seen_names.add(key)
                pattern = r"(?<!\w)" + r"[ \t]+".join(re.escape(word) for word in words) + r"(?!\w)"
                for repeat in re.finditer(pattern, text, re.I):
                    matches.append((repeat.start(), repeat.end(), kind))
        if options.redact_locations:
            add(CITY_COUNTRY, "LOCATION")
            add(rules["hospital"], "HOSPITAL")
            add(rules["address"], "LOCATION")
            add(rules["location"], "LOCATION")
            if options.language == "en":
                add(
                    re.compile(r"\b\d{1,5}[ \t]+[^\n,;]+[ \t]+(?:Street|Road|Avenue|Lane)\b"),
                    "LOCATION",
                )
            elif options.language == "de":
                add(
                    re.compile(r"\b[A-ZÄÖÜ][\wäöüß]*(?:straße|strasse|weg|platz)[ \t]+\d{1,5}\b"),
                    "LOCATION",
                )
        if options.redact_ids:
            matches.extend(contextual_ids)
            add(rules["id"], "ID")
        for keyword in options.custom_keywords:
            if keyword.strip():
                add(re.compile(re.escape(keyword.strip()), re.I), "CUSTOM")
        # Merge intersecting spans to avoid exposing a tail of an overlapping detection.
        merged = []
        for start, end, kind in sorted(matches, key=lambda m: (m[0], -(m[1] - m[0]))):
            if merged and start < merged[-1][1]:
                old_start, old_end, old_kind = merged[-1]
                merged[-1] = (old_start, max(old_end, end), old_kind)
            else:
                merged.append((start, end, kind))
        localized = labels(options.language)
        registry, counts, pieces, entities = {}, {}, [], []
        cursor = 0
        for start, end, kind in merged:
            original = text[start:end]
            label = localized[kind]
            if options.mask_mode == MaskMode.BLOCK:
                replacement = "█" * max(4, min(len(original), 12))
            elif options.mask_mode == MaskMode.ASTERISK:
                replacement = "*" * max(4, min(len(original), 10))
            elif options.mask_mode == MaskMode.PSEUDONYM:
                key = (kind, " ".join(original.split()).casefold())
                if key not in registry:
                    counts[kind] = counts.get(kind, 0) + 1
                    registry[key] = f"{label}_{counts[kind]}"
                replacement = registry[key]
            else:
                replacement = f"[{label}]"
            pieces.extend((text[cursor:start], replacement))
            entities.append(
                EntityDetection(
                    entity_type=kind,
                    original=original,
                    replacement=replacement,
                    start=start,
                    end=end,
                    confidence=0.95,
                )
            )
            cursor = end
        pieces.append(text[cursor:])
        return RedactResponse(
            redacted_text="".join(pieces),
            entities_found=len(entities),
            entities=entities,
            execution_ms=round((time.perf_counter() - started) * 1000, 2),
        )
