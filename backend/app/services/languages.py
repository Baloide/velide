"""Language-specific, conservative rules. These are heuristics, not an NER model."""

import re

LANGUAGES = ("it", "en", "es", "de", "fr", "pt", "nl", "pl", "tr", "ru")
DATA = {
    "it": dict(
        names=r"Paziente|Paz\.|Sig\.ra|Sig\.|Signor|Signora|Dott\.ssa|Dott\.|Dr\.|Prof\.|Assistito|Assistita|Nome e Cognome|Nome|Cognome",
        hospitals=r"Presidio Ospedaliero|Ospedale|Policlinico|Clinica|Casa di Cura|ASL|IRCCS",
        addresses=r"Via|Viale|Corso|Piazza|Largo|Vicolo|Strada",
        locations=r"Residenza|Domicilio|Luogo di nascita|Città",
        ids=r"Cartella Clinica|Cartella|ID Referto|Tessera Sanitaria|Codice Sanitario|Protocollo|Fascicolo|Matr\. Ospedale",
        months="gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre",
        labels="NOME_PAZIENTE MEDICO CODICE_FISCALE TELEFONO EMAIL INDIRIZZO STRUTTURA_SANITARIA ID_CARTELLA DATA DATO_RISERVATO",
    ),
    "en": dict(
        names=r"Patient|Mr\.|Mrs\.|Ms\.|Dr\.|Doctor|Prof\.|Full name|Name",
        hospitals=r"Hospital|Clinic|Medical Center|Medical Centre|University Hospital",
        addresses=r"Street|Road|Avenue|Lane|Address",
        locations=r"Residence|City|Place of birth",
        ids=r"Medical Record|Record ID|Patient ID|Health ID|Case number",
        months="January February March April May June July August September October November December",
        labels="PATIENT_NAME DOCTOR TAX_ID PHONE EMAIL ADDRESS HEALTHCARE_FACILITY RECORD_ID DATE PRIVATE_DATA",
    ),
    "es": dict(
        names=r"Paciente|Sr\.|Sra\.|Dra\.|Dr\.|Doctor|Doctora|Nombre completo|Nombre",
        hospitals=r"Hospital|Clínica|Centro de Salud|Centro Médico",
        addresses=r"Calle|Avenida|Plaza|Paseo|Dirección",
        locations=r"Residencia|Domicilio|Ciudad|Lugar de nacimiento",
        ids=r"Historia Clínica|Historia clínica|ID Paciente|Número de historia|Tarjeta Sanitaria",
        months="enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre",
        labels="NOMBRE_PACIENTE MÉDICO ID_FISCAL TELÉFONO EMAIL DIRECCIÓN CENTRO_SANITARIO ID_HISTORIA FECHA DATO_PRIVADO",
    ),
    "de": dict(
        names=r"Patientin|Patient|Herr|Frau|Dr\.|Prof\.|Name",
        hospitals=r"Krankenhaus|Klinik|Klinikum|Universitätsklinikum",
        addresses=r"Straße|Strasse|Adresse|Anschrift",
        locations=r"Wohnort|Geburtsort|Stadt",
        ids=r"Patientenakte|Aktennummer|Patienten-ID|Versichertennummer",
        months="Januar Februar März April Mai Juni Juli August September Oktober November Dezember",
        labels="PATIENTENNAME ARZT STEUER_ID TELEFON EMAIL ADRESSE EINRICHTUNG AKTEN_ID DATUM PRIVATE_DATEN",
    ),
    "fr": dict(
        names=r"Patiente|Patient|Mme\.|M\.|Dr\.|Docteur|Pr\.|Nom complet|Nom",
        hospitals=r"Hôpital|Clinique|Centre Hospitalier|Centre hospitalier|CHU",
        addresses=r"Rue|Avenue|Boulevard|Place|Adresse",
        locations=r"Résidence|Domicile|Ville|Lieu de naissance",
        ids=r"Dossier Médical|Dossier médical|Dossier|Identifiant patient|Numéro de dossier",
        months="janvier février mars avril mai juin juillet août septembre octobre novembre décembre",
        labels="NOM_PATIENT MÉDECIN ID_FISCAL TÉLÉPHONE EMAIL ADRESSE ÉTABLISSEMENT ID_DOSSIER DATE DONNÉE_PRIVÉE",
    ),
    "pt": dict(
        names=r"Paciente|Sr\.|Sra\.|Dra\.|Dr\.|Doutor|Doutora|Nome completo|Nome",
        hospitals=r"Hospital|Clínica|Centro de Saúde|Centro Médico",
        addresses=r"Rua|Avenida|Praça|Travessa|Endereço|Morada",
        locations=r"Residência|Domicílio|Cidade|Local de nascimento",
        ids=r"Prontuário|Processo Clínico|Processo clínico|ID Paciente|Número de processo|Cartão de Saúde",
        months="janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro",
        labels="NOME_PACIENTE MÉDICO ID_FISCAL TELEFONE EMAIL ENDEREÇO UNIDADE_SAÚDE ID_PROCESSO DATA DADO_PRIVADO",
    ),
    "nl": dict(
        names=r"Patiënt|Patiënte|Dhr\.|Mevr\.|Dr\.|Dokter|Prof\.|Naam",
        hospitals=r"Ziekenhuis|Kliniek|Medisch Centrum",
        addresses=r"Adres|Straat|Laan",
        locations=r"Woonplaats|Geboorteplaats|Stad",
        ids=r"Patiëntendossier|Dossiernummer|Patiëntnummer",
        months="januari februari maart april mei juni juli augustus september oktober november december",
        labels="PATIËNTNAAM ARTS BELASTINGNUMMER TELEFOON EMAIL ADRES ZORGINSTELLING DOSSIER_ID DATUM PRIVÉGEGEVENS",
    ),
    "pl": dict(
        names=r"Pacjentka|Pacjent|Pan|Pani|Dr\.|Lekarz|Lekarka|Prof\.|Imię i nazwisko",
        hospitals=r"Szpital|Klinika|Centrum Medyczne",
        addresses=r"Adres|Ulica|Ul\.|Aleja|Plac",
        locations=r"Miejsce zamieszkania|Miejsce urodzenia|Miasto",
        ids=r"Historia choroby|Numer dokumentacji|ID pacjenta",
        months="stycznia lutego marca kwietnia maja czerwca lipca sierpnia września października listopada grudnia",
        labels="NAZWISKO_PACJENTA LEKARZ ID_PODATKOWY TELEFON EMAIL ADRES PLACÓWKA ID_DOKUMENTACJI DATA DANE_PRYWATNE",
        word=r"[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+(?:['’\-][A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż]+)*",
    ),
    "tr": dict(
        names=r"Hasta|Bay|Bayan|Dr\.|Doktor|Prof\.|Ad Soyad",
        hospitals=r"Hastane|Hastanesi|Klinik|Sağlık Merkezi",
        addresses=r"Adres|Sokak|Cadde|Mahalle",
        locations=r"İkamet|Doğum yeri|Şehir",
        ids=r"Hasta dosyası|Dosya numarası|Hasta No",
        months="Ocak Şubat Mart Nisan Mayıs Haziran Temmuz Ağustos Eylül Ekim Kasım Aralık",
        labels="HASTA_ADI DOKTOR VERGİ_NO TELEFON EMAIL ADRES SAĞLIK_KURULUŞU DOSYA_NO TARİH ÖZEL_VERİ",
        word=r"[A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:['’\-][A-ZÇĞİÖŞÜa-zçğıöşü]+)*",
    ),
    "ru": dict(
        names=r"Пациентка|Пациент|Врач|Доктор|Д-р|ФИО",
        hospitals=r"Больница|Клиника|Медицинский центр",
        addresses=r"Адрес|Улица|Ул\.|Проспект",
        locations=r"Место жительства|Место рождения|Город",
        ids=r"Медицинская карта|Номер карты|ID пациента",
        months="января февраля марта апреля мая июня июля августа сентября октября ноября декабря",
        labels="ИМЯ_ПАЦИЕНТА ВРАЧ НАЛОГОВЫЙ_НОМЕР ТЕЛЕФОН EMAIL АДРЕС МЕДУЧРЕЖДЕНИЕ НОМЕР_КАРТЫ ДАТА ЛИЧНЫЕ_ДАННЫЕ",
        word=r"[А-ЯЁ][а-яё]+(?:['’\-][А-ЯЁа-яё]+)*",
    ),
}
ENTITY_TYPES = (
    "NAME",
    "DOCTOR",
    "TAX_CODE",
    "PHONE",
    "EMAIL",
    "LOCATION",
    "HOSPITAL",
    "ID",
    "DATE",
    "CUSTOM",
)
# A capitalized word with accents, apostrophes or hyphens; no newline consumption.
WORD = r"[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ]+(?:['’\-][A-ZÀ-ÖØ-Þa-zà-öø-ÿ]+)*"
NAME = rf"{WORD}(?:[ \t]+(?:(?:de|da|do|dos|del|della|van|von|du|le)[ \t]+)?{WORD}){{1,3}}"


def compile_rules(language):
    """Compile one language's detection rules from DATA without normalizing text.

    Raises:
        KeyError: Language metadata is missing.
        re.error: A configured expression is invalid.
    """
    d = DATA[language]
    months = "|".join(d["months"].split())
    word = d.get("word", WORD)
    name = rf"{word}(?:[ \t]+(?:(?:de|da|do|dos|del|della|van|von|du|le)[ \t]+)?{word}){{1,3}}"
    addresses = d["addresses"]
    if language == "it":
        # "Corso di formazione" is training, whereas "Corso di Francia" is a street.
        addresses = addresses.replace(
            "Corso",
            r"Corso(?![ \t]+(?:(?:di|in|per)[ \t]+)?(?:formazione|aggiornamento|laurea|studi|specializzazione|perfezionamento|abilitazione|lingua|inglese|italiano|matlab)\b)",
        )
    return {
        "name": re.compile(rf"\b(?P<prefix>(?i:{d['names']}))[ \t]*:?[ \t]+(?P<name>{name})"),
        "hospital": re.compile(
            rf"\b(?i:{d['hospitals']})[ \t]+[A-ZÀ-ÖØ-ÞĄĆĘŁŃŚŹŻÇĞİŞÜА-ЯЁ0-9][^\n,;.!]+"
        ),
        "address": re.compile(rf"\b(?i:{addresses})[ \t]*:?[ \t]+[^\n;]+"),
        "location": re.compile(rf"\b(?i:{d['locations']})[ \t]*:[ \t]*[^\n;]+"),
        "id": re.compile(rf"\b(?:{d['ids']})[ \t]*[:#]?[ \t]+[A-Z0-9][A-Z0-9/\-]{{3,30}}\b", re.I),
        "date": re.compile(
            rf"\b(?:\d{{1,2}}\.?[ \t]+(?:de[ \t]+)?(?:{months})[ \t]+(?:de[ \t]+)?\d{{4}}(?:[ \t]+г\.)?|(?:{months})[ \t]+\d{{1,2}},?[ \t]+\d{{4}})\b",
            re.I,
        ),
    }


RULES = {lang: compile_rules(lang) for lang in LANGUAGES}


def labels(language):
    result = dict(zip(ENTITY_TYPES, DATA[language]["labels"].split()))
    result["URL"] = {
        "it": "LINK",
        "en": "LINK",
        "es": "ENLACE",
        "de": "LINK",
        "fr": "LIEN",
        "pt": "LINK",
        "nl": "LINK",
        "pl": "LINK",
        "tr": "BAĞLANTI",
        "ru": "ССЫЛКА",
    }[language]
    return result


SAMPLES = {
    "it": "RELAZIONE CLINICA · ESEMPIO FITTIZIO\nOspedale San Giovanni\nCartella Clinica: CC-2026-1042\nPaziente: Mario Rossi\nData di nascita: 12/05/1978\nResidenza: Via Toledo 142, Napoli\nEmail: mario.rossi@example.com\nTelefono: +39 339 1234567\nCodice Fiscale: RSSMRA78E12F839K\nVisita: 14 ottobre 2026\nDott. Antonio Bianchi\n\nAstenia e tachicardia. PA 135/85 mmHg, FC 88 bpm.\nControllo tra 30 giorni. Mario Rossi prosegue il monitoraggio.",
    "en": "CLINICAL NOTE · FICTIONAL EXAMPLE\nHospital Saint Mary\nMedical Record: MR-2026-1042\nPatient: James Smith\nDate of birth: 05/12/1978\nAddress: 142 Oak Street, London\nEmail: james.smith@example.com\nPhone: +44 7700 900123\nVisit: October 14, 2026\nDr. Emma Wilson\n\nFatigue and tachycardia. BP 135/85 mmHg, HR 88 bpm.\nFollow-up in 30 days. James Smith continues monitoring.",
    "es": "INFORME CLÍNICO · EJEMPLO FICTICIO\nHospital San Miguel\nHistoria Clínica: HC-2026-1042\nPaciente: Carlos García\nFecha de nacimiento: 12/05/1978\nDirección: Calle Mayor 142, Madrid\nEmail: carlos.garcia@example.com\nTeléfono: +34 612 345 678\nConsulta: 14 de octubre de 2026\nDra. Elena López\n\nAstenia y taquicardia. PA 135/85 mmHg, FC 88 bpm.\nControl en 30 días. Carlos García continúa el seguimiento.",
    "de": "KLINISCHER BERICHT · FIKTIVES BEISPIEL\nKrankenhaus Sankt Martin\nPatientenakte: PA-2026-1042\nPatient: Thomas Müller\nGeburtsdatum: 12.05.1978\nAdresse: Hauptstraße 142, Berlin\nEmail: thomas.mueller@example.com\nTelefon: +49 151 23456789\nUntersuchung: 14. Oktober 2026\nDr. Anna Schmidt\n\nMüdigkeit und Tachykardie. RR 135/85 mmHg, HF 88 bpm.\nKontrolle in 30 Tagen. Thomas Müller setzt die Überwachung fort.",
    "fr": "COMPTE RENDU CLINIQUE · EXEMPLE FICTIF\nHôpital Saint Pierre\nDossier médical: DM-2026-1042\nPatient: Pierre Martin\nDate de naissance: 12/05/1978\nAdresse: Rue Victor Hugo 142, Paris\nEmail: pierre.martin@example.com\nTéléphone: +33 6 12 34 56 78\nConsultation: 14 octobre 2026\nDr. Sophie Bernard\n\nAsthénie et tachycardie. PA 135/85 mmHg, FC 88 bpm.\nContrôle dans 30 jours. Pierre Martin poursuit la surveillance.",
    "pt": "RELATÓRIO CLÍNICO · EXEMPLO FICTÍCIO\nHospital São Miguel\nProcesso clínico: PC-2026-1042\nPaciente: João Silva\nData de nascimento: 12/05/1978\nMorada: Rua das Flores 142, Lisboa\nEmail: joao.silva@example.com\nTelefone: +351 912 345 678\nConsulta: 14 de outubro de 2026\nDra. Ana Costa\n\nAstenia e taquicardia. PA 135/85 mmHg, FC 88 bpm.\nControlo em 30 dias. João Silva continua a monitorização.",
    "nl": "KLINISCH VERSLAG · FICTIEF VOORBEELD\nZiekenhuis Sint Lucas\nPatiëntendossier: PD-2026-1042\nPatiënt: Jan de Vries\nGeboortedatum: 12/05/1978\nAdres: Kerkstraat 142, Amsterdam\nEmail: jan.devries@example.com\nTelefoon: +31 6 12345678\nBezoek: 14 oktober 2026\nDr. Emma Bakker\n\nVermoeidheid en tachycardie. BP 135/85 mmHg, HR 88 bpm.\nControle over 30 dagen. Jan de Vries zet de monitoring voort.",
    "pl": "RAPORT KLINICZNY · PRZYKŁAD FIKCYJNY\nSzpital Świętego Łukasza\nHistoria choroby: HC-2026-1042\nPacjent: Łukasz Wiśniewski\nData urodzenia: 12.05.1978\nAdres: Ulica Długa 142, Warszawa\nEmail: lukasz.wisniewski@example.com\nTelefon: +48 512 345 678\nWizyta: 14 października 2026\nLekarz: Anna Kowalska\n\nOsłabienie i tachykardia. BP 135/85 mmHg, HR 88 bpm.\nKontrola za 30 dni. Łukasz Wiśniewski kontynuuje monitorowanie.",
    "tr": "KLİNİK RAPOR · KURGUSAL ÖRNEK\nHastane Şehir Sağlık\nHasta dosyası: HD-2026-1042\nHasta: İlker Yılmaz\nDoğum tarihi: 12.05.1978\nAdres: Çiçek Sokak 142, İstanbul\nEmail: ilker.yilmaz@example.com\nTelefon: +90 532 123 4567\nMuayene: 14 Ekim 2026\nDoktor: Ayşe Demir\n\nHalsizlik ve taşikardi. BP 135/85 mmHg, HR 88 bpm.\n30 gün sonra kontrol. İlker Yılmaz izleme devam ediyor.",
    "ru": "КЛИНИЧЕСКОЕ ЗАКЛЮЧЕНИЕ · ВЫМЫШЛЕННЫЙ ПРИМЕР\nБольница Святого Луки\nМедицинская карта: MK-2026-1042\nПациент: Иван Петров\nДата рождения: 12.05.1978\nАдрес: Улица Садовая 142, Москва\nEmail: ivan.petrov@example.com\nТелефон: +7 912 345 6789\nОсмотр: 14 октября 2026 г.\nВрач: Анна Иванова\n\nСлабость и тахикардия. BP 135/85 mmHg, HR 88 bpm.\nКонтроль через 30 дней. Иван Петров продолжает наблюдение.",
}
