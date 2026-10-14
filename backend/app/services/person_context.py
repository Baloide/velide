"""Find people in explicitly labelled lists and tables, without guessing from capitals alone."""

import re

from app.services.languages import DATA

CONTEXT = {
    "it": (
        "Nome|Nome e Cognome|Nominativo|Cognome",
        "Matricola|Identificativo|Codice|ID",
        "Scritto da|Redatto da|Firmato da|Autore|Autori|Responsabile|Coordinatore(?: del progetto)?|Partecipanti",
    ),
    "en": (
        "Name|Full name|First name|Last name|Surname",
        "Student ID|Registration number|Identifier|ID",
        "Written by|Prepared by|Signed by|Author|Authors|Coordinator|Participants",
    ),
    "es": (
        "Nombre|Nombre completo|Apellidos",
        "Matrícula|Identificador|Código|ID",
        "Escrito por|Redactado por|Firmado por|Autor|Autores|Coordinador|Participantes",
    ),
    "de": (
        "Name|Vorname|Nachname",
        "Matrikelnummer|Kennung|ID",
        "Verfasst von|Geschrieben von|Autor|Autoren|Koordinator|Teilnehmer",
    ),
    "fr": (
        "Nom|Nom complet|Prénom",
        "Matricule|Identifiant|ID",
        "Rédigé par|Écrit par|Signé par|Auteur|Auteurs|Coordinateur|Participants",
    ),
    "pt": (
        "Nome|Nome completo|Apelido|Sobrenome",
        "Matrícula|Identificador|Código|ID",
        "Escrito por|Redigido por|Assinado por|Autor|Autores|Coordenador|Participantes",
    ),
    "nl": (
        "Naam|Voornaam|Achternaam",
        "Studentnummer|Registratienummer|ID",
        "Geschreven door|Auteur|Auteurs|Coördinator|Deelnemers",
    ),
    "pl": (
        "Imię i nazwisko|Imię|Nazwisko",
        "Numer indeksu|Identyfikator|ID",
        "Napisane przez|Autor|Autorzy|Koordynator|Uczestnicy",
    ),
    "tr": (
        "Ad Soyad|Ad|Soyad",
        "Öğrenci numarası|Kimlik|ID",
        "Yazan|Hazırlayan|Yazar|Yazarlar|Koordinatör|Katılımcılar",
    ),
    "ru": (
        "ФИО|Имя|Фамилия",
        "Номер студента|Идентификатор|ID",
        "Автор|Авторы|Подготовил|Подписал|Координатор|Участники",
    ),
}
PARTICLES = {
    "la",
    "lo",
    "le",
    "di",
    "de",
    "del",
    "della",
    "da",
    "do",
    "dos",
    "das",
    "du",
    "van",
    "von",
    "der",
    "den",
    "al",
    "el",
}
NON_NAMES = {
    "nome",
    "cognome",
    "matricola",
    "name",
    "surname",
    "identifier",
    "id",
    "data",
    "versione",
    "descrizione",
    "autore",
    "autori",
    "revision",
    "history",
    "team",
    "progetto",
    "problem",
    "statement",
    "clinical",
    "note",
    "medicina",
    "interna",
    "università",
    "universita",
    "studi",
    "informazioni",
    "documento",
    "partecipanti",
    "coordinatore",
    "requisiti",
    "funzionali",
}
NON_NAMES.update(
    {
        "corso",
        "formazione",
        "generale",
        "specifica",
        "lavoratori",
        "competenze",
        "principali",
        "certifications",
        "certificazioni",
        "matlab",
        "machine",
        "learning",
        "english",
        "certificate",
        "council",
        "europe",
        "level",
        "bioengineer",
        "bioengineering",
        "specialist",
        "researcher",
        "engineer",
        "engineering",
        "dispositivi",
        "medici",
        "prototipazione",
        "elettronica",
    }
)
TOKEN = re.compile(r"[^\W\d_]+(?:['’\-][^\W\d_]+)*\.?", re.UNICODE)
IDENTIFIER = re.compile(r"[A-Z0-9][A-Z0-9/\-]{3,30}", re.I)


def is_person(value, single=False):
    """Check a contextual name candidate, including particles and initials.

    Args:
        value: Candidate cell or field value, not arbitrary prose.
        single: Permit one component in separate first/last-name columns.
    Returns:
        Whether the token rules accept it; this is not calibrated confidence.
    """
    tokens = value.split()
    if not (1 if single else 2) <= len(tokens) <= 6:
        return False
    meaningful = 0
    for token in tokens:
        if not TOKEN.fullmatch(token) or token.casefold().rstrip(".") in NON_NAMES:
            return False
        if token.casefold() in PARTICLES:
            continue
        if not token[0].isupper():
            return False
        meaningful += 1
    return meaningful >= (1 if single else 2)


def detect_contextual_people(text, language):
    """Find names and identifiers in labelled tables, fields, and author lists.

    Args:
        text: Original Unicode document text.
        language: Supported language key with configured context labels.
    Returns:
        Two lists of (start, exclusive_end, entity_type) tuples: names and IDs.
    Raises:
        KeyError: An unsupported language reaches this internal helper.

    Offsets always refer to the input, including whitespace. The caller decides
    which categories to mask and expands known names to repeated occurrences.
    """
    name_labels, id_labels, authors = CONTEXT[language]
    names, identifiers = [], []
    name_header = re.compile(rf"(?:{name_labels})", re.I)
    id_header = re.compile(rf"(?:{id_labels})", re.I)
    lines = list(re.finditer(r"[^\n]+", text))
    columns = None
    for line in lines:
        value = line.group().strip("\r")
        cells = (
            list(re.finditer(r"[^\t]+", value))
            if "\t" in value
            else list(re.finditer(r"\S(?:.*?\S)?(?= {2,}|$)", value))
        )
        headers = [cell.group().strip() for cell in cells]
        name_columns = [i for i, header in enumerate(headers) if name_header.fullmatch(header)]
        id_columns = [i for i, header in enumerate(headers) if id_header.fullmatch(header)]
        if name_columns and all(i in name_columns or i in id_columns for i in range(len(headers))):
            columns = (name_columns, id_columns, len(headers))
            continue
        # Also handle flattened "Nome Matricola" headers with single spaces.
        if re.fullmatch(rf"[ \t]*(?:{name_labels})[ \t]+(?:{id_labels})[ \t]*", value, re.I):
            columns = ([0], [1], 2)
            continue
        if columns is not None:
            name_columns, id_columns, count = columns
            if len(cells) == 1 and count == 2 and name_columns == [0] and id_columns == [1]:
                row = re.fullmatch(
                    r"(?P<person>.+?)[ \t]+(?P<id>[A-Z0-9][A-Z0-9/\-]{3,30})[ \t]*", value, re.I
                )
                cells = [row, row] if row else []
                spans = (
                    [(row.start("person"), row.end("person")), (row.start("id"), row.end("id"))]
                    if row
                    else []
                )
            else:
                spans = [(cell.start(), cell.end()) for cell in cells]
            if len(spans) == count:
                values = [value[start:end].strip() for start, end in spans]
                if all(
                    is_person(values[i], single=len(name_columns) > 1) for i in name_columns
                ) and all(IDENTIFIER.fullmatch(values[i]) for i in id_columns):
                    for i in name_columns:
                        start, end = spans[i]
                        trimmed = value[start:end].lstrip()
                        offset = end - len(trimmed)
                        names.append(
                            (line.start() + offset, line.start() + offset + len(values[i]), "NAME")
                        )
                    for i in id_columns:
                        start, end = spans[i]
                        offset = end - len(value[start:end].lstrip())
                        identifiers.append(
                            (line.start() + offset, line.start() + offset + len(values[i]), "ID")
                        )
                    continue
            columns = None
    # Field/list labels can be followed by a name on the next line as well.
    field = re.compile(
        rf"\b(?P<prefix>(?:{authors}|{DATA[language]['names']}))[ \t]*:[ \t]*(?:\r?\n[ \t]*)?(?P<value>[^\n]+)",
        re.I,
    )
    for match in field.finditer(text):
        kind = (
            "DOCTOR"
            if re.search(
                r"dott|dr|doctor|doutor|prof|docteur|dokter|lekarz|doktor|врач|доктор",
                match["prefix"],
                re.I,
            )
            else "NAME"
        )
        for item in re.finditer(r"[^,;]+", match["value"]):
            candidate = item.group().strip().rstrip(".")
            if is_person(candidate):
                start = (
                    match.start("value")
                    + item.start()
                    + len(item.group())
                    - len(item.group().lstrip())
                )
                names.append((start, start + len(candidate), kind))
    direct_id = re.compile(
        rf"\b(?:{id_labels})[ \t]*[:#][ \t]*(?P<id>[A-Z0-9][A-Z0-9/\-]{{3,30}})\b", re.I
    )
    for match in direct_id.finditer(text):
        identifiers.append((match.start("id"), match.end("id"), "ID"))
    return names, identifiers
