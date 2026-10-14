import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.main import app
from app.schemas.redact import MaskMode, RedactOptions
from app.services.languages import SAMPLES, labels
from app.services.redaction_engine import RedactionEngine
from fastapi.testclient import TestClient


class RedactionTests(unittest.TestCase):
    def setUp(self):
        self.engine = RedactionEngine()

    def test_ten_languages(self):
        sensitive = {
            "it": [
                "Mario Rossi",
                "Antonio Bianchi",
                "mario.rossi@example.com",
                "339 1234567",
                "Via Toledo",
                "San Giovanni",
                "CC-2026-1042",
                "14 ottobre 2026",
                "RSSMRA78E12F839K",
            ],
            "en": [
                "James Smith",
                "Emma Wilson",
                "james.smith@example.com",
                "7700 900123",
                "Oak Street",
                "Saint Mary",
                "MR-2026-1042",
                "October 14, 2026",
            ],
            "es": [
                "Carlos García",
                "Elena López",
                "carlos.garcia@example.com",
                "612 345 678",
                "Calle Mayor",
                "San Miguel",
                "HC-2026-1042",
                "14 de octubre de 2026",
            ],
            "de": [
                "Thomas Müller",
                "Anna Schmidt",
                "thomas.mueller@example.com",
                "151 23456789",
                "Hauptstraße",
                "Sankt Martin",
                "PA-2026-1042",
                "14. Oktober 2026",
            ],
            "fr": [
                "Pierre Martin",
                "Sophie Bernard",
                "pierre.martin@example.com",
                "6 12 34 56 78",
                "Victor Hugo",
                "Saint Pierre",
                "DM-2026-1042",
                "14 octobre 2026",
            ],
            "pt": [
                "João Silva",
                "Ana Costa",
                "joao.silva@example.com",
                "912 345 678",
                "Rua das Flores",
                "São Miguel",
                "PC-2026-1042",
                "14 de outubro de 2026",
            ],
            "nl": [
                "Jan de Vries",
                "Emma Bakker",
                "jan.devries@example.com",
                "6 12345678",
                "Kerkstraat",
                "Sint Lucas",
                "PD-2026-1042",
                "14 oktober 2026",
            ],
            "pl": [
                "Łukasz Wiśniewski",
                "Anna Kowalska",
                "lukasz.wisniewski@example.com",
                "512 345 678",
                "Długa",
                "Świętego Łukasza",
                "HC-2026-1042",
                "14 października 2026",
            ],
            "tr": [
                "İlker Yılmaz",
                "Ayşe Demir",
                "ilker.yilmaz@example.com",
                "532 123 4567",
                "Çiçek Sokak",
                "Şehir Sağlık",
                "HD-2026-1042",
                "14 Ekim 2026",
            ],
            "ru": [
                "Иван Петров",
                "Анна Иванова",
                "ivan.petrov@example.com",
                "912 345 6789",
                "Садовая",
                "Святого Луки",
                "MK-2026-1042",
                "14 октября 2026 г.",
            ],
        }
        for lang, text in SAMPLES.items():
            with self.subTest(language=lang):
                result = self.engine.redact(text, RedactOptions(language=lang))
                for value in sensitive[lang] + [
                    "12.05.1978"
                    if lang in ["de", "pl", "tr", "ru"]
                    else ("05/12/1978" if lang == "en" else "12/05/1978")
                ]:
                    self.assertNotIn(value, result.redacted_text)
                self.assertIn("135/85 mmHg", result.redacted_text)
                self.assertIn("88 bpm", result.redacted_text)
                self.assertIn("30", result.redacted_text)
                if lang == "it":
                    self.assertIn("RELAZIONE CLINICA · ESEMPIO FITTIZIO", result.redacted_text)
                self.assertIn(f"[{labels(lang)['NAME']}]", result.redacted_text)
                for entity in result.entities:
                    self.assertEqual(text[entity.start : entity.end], entity.original)

    def test_consistent_names_and_modes(self):
        text = "Patient: James Smith\nJames Smith returned."
        for mode in MaskMode:
            result = self.engine.redact(text, RedactOptions(language="en", mask_mode=mode))
            self.assertNotIn("James Smith", result.redacted_text)
            self.assertEqual(result.entities[0].replacement, result.entities[1].replacement)
        result = self.engine.redact(text, RedactOptions(language="en", mask_mode="PSEUDONYM"))
        self.assertEqual(result.entities[0].replacement, "PATIENT_NAME_1")

    def test_disabled_categories_and_custom_unicode_offsets(self):
        options = RedactOptions(
            language="en",
            redact_names=False,
            redact_tax_codes=False,
            redact_dates=False,
            redact_contacts=False,
            redact_locations=False,
            redact_ids=False,
            custom_keywords=["istanbul", "secret"],
        )
        text = "İstanbul SECRET Patient: James Smith 12/05/1978"
        result = self.engine.redact(text, options)
        self.assertNotIn("İstanbul", result.redacted_text)
        self.assertNotIn("SECRET", result.redacted_text)
        self.assertIn("James Smith", result.redacted_text)
        self.assertIn("12/05/1978", result.redacted_text)
        for entity in result.entities:
            self.assertEqual(text[entity.start : entity.end], entity.original)

    def test_overlap_masks_whole_span(self):
        result = self.engine.redact(
            "secret phrase tail",
            RedactOptions(language="it", custom_keywords=["secret phrase", "phrase tail"]),
        )
        self.assertEqual(result.redacted_text, "[DATO_RISERVATO]")

    def test_dates_not_phones(self):
        result = self.engine.redact(
            "Visit 12.05.1978; BP 135/85; HR 88.", RedactOptions(language="en", redact_dates=False)
        )
        self.assertEqual(result.entities_found, 0)

    def test_unlabelled_addresses_and_ids(self):
        for language, text, value in [
            ("en", "Address is 142 Oak Street.", "142 Oak Street"),
            ("de", "Wohnt Hauptstraße 142.", "Hauptstraße 142"),
            ("es", "DNI: 12345678Z", "12345678Z"),
            ("pt", "CPF: 123.456.789-00", "123.456.789-00"),
        ]:
            with self.subTest(language=language):
                result = self.engine.redact(text, RedactOptions(language=language))
                self.assertNotIn(value, result.redacted_text)

    def test_names_and_registration_numbers_in_project_document(self):
        text = """Università degli Studi di Salerno
GreenSpot
Problem Statement
Coordinatore del progetto:
Nome\tMatricola
La Magna Davide\t0512121375
Partecipanti:
Nome\tMatricola
Ciccarelli Raffaele\t0512121405
La Magna Davide\t0512121375
Manzolillo Matteo\t0512121666
Nota: verificare i partecipanti.
Scritto da: Ciccarelli Raffaele, La Magna Davide, Manzolillo Matteo
Revision History
Data\tVersione\tDescrizione\tAutore
12/10/2026\t1.0\tPrima bozza\tTeam GreenSpot
"""
        result = self.engine.redact(text, RedactOptions(language="it"))
        for name in ["La Magna Davide", "Ciccarelli Raffaele", "Manzolillo Matteo"]:
            self.assertNotIn(name, result.redacted_text)
        for identifier in ["0512121375", "0512121405", "0512121666"]:
            self.assertNotIn(identifier, result.redacted_text)
            self.assertTrue(
                all(e.entity_type == "ID" for e in result.entities if e.original == identifier)
            )
        for untouched in [
            "Università degli Studi di Salerno",
            "GreenSpot",
            "Problem Statement",
            "Revision History",
            "Team GreenSpot",
        ]:
            self.assertIn(untouched, result.redacted_text)
        self.assertEqual(len([e for e in result.entities if e.entity_type == "NAME"]), 7)
        pseudonyms = self.engine.redact(text, RedactOptions(language="it", mask_mode="PSEUDONYM"))
        substitutions = [
            e.replacement for e in pseudonyms.entities if e.original == "La Magna Davide"
        ]
        self.assertEqual(len(set(substitutions)), 1)
        for entity in result.entities:
            self.assertEqual(text[entity.start : entity.end], entity.original)

    def test_contextual_names_flattened_tables_and_capitals(self):
        for text in [
            "Nome Matricola\nLA MAGNA DAVIDE 0512121375",
            "Nome  Matricola\nLa Magna Davide  0512121375",
            "Scritto da: Ciccarelli Raffaele, La Magna Davide",
            "Nome\nLa Magna Davide\nDescrizione del documento",
        ]:
            result = self.engine.redact(text, RedactOptions(language="it"))
            self.assertNotIn("La Magna Davide", result.redacted_text)
            self.assertNotIn("LA MAGNA DAVIDE", result.redacted_text)
            self.assertNotIn("Ciccarelli Raffaele", result.redacted_text)
        text = "Nome\tCognome\nMario\tRossi\nFirma di Mario Rossi"
        result = self.engine.redact(text, RedactOptions(language="it"))
        self.assertNotIn("Mario", result.redacted_text)
        self.assertNotIn("Rossi", result.redacted_text)

    def test_contextual_filters_and_no_generic_capitalized_phrases(self):
        text = "Nome\tMatricola\nLa Magna Davide\t0512121375"
        result = self.engine.redact(
            text, RedactOptions(language="it", redact_names=False, redact_ids=False)
        )
        self.assertEqual(result.redacted_text, text)
        result = self.engine.redact(text, RedactOptions(language="it", redact_contacts=False))
        self.assertNotIn("0512121375", result.redacted_text)
        text = "Problem Statement\nRevision History\nMedicina Interna\nNome\tMatricola\nTeam GreenSpot\t2026000011"
        result = self.engine.redact(text, RedactOptions(language="it", redact_contacts=False))
        self.assertEqual(result.redacted_text, text)

    def test_contextual_people_in_other_languages(self):
        examples = [
            (
                "en",
                "Name\tStudent ID\nJames Smith\tST-20260001\nWritten by: James Smith",
                "James Smith",
            ),
            (
                "ru",
                "ФИО\tНомер студента\nИван Петров\tST-20260001\nАвтор: Иван Петров",
                "Иван Петров",
            ),
            (
                "pl",
                "Imię i nazwisko\tNumer indeksu\nŁukasz Wiśniewski\tST-20260001",
                "Łukasz Wiśniewski",
            ),
        ]
        for language, text, name in examples:
            result = self.engine.redact(text, RedactOptions(language=language))
            self.assertNotIn(name, result.redacted_text)
            self.assertNotIn("ST-20260001", result.redacted_text)

    def test_cv_profile_link_person_location_and_course(self):
        text = """Contatta
www.linkedin.com/in/giampiero-
bartolomei-314046224 (LinkedIn)
Competenze principali
Prototipazione rapida
Elettronica
Dispositivi Medici
Certifications
MATLAB Fundamentals
Machine Learning with MATLAB
English Certificate Council of Europe
Level B1
Corso di Formazione Generale e
Specifica per Lavoratori
Giampiero Bartolomei
BioEngineer Specialist & Researcher at Math Biology
Roma, Lazio, Italia
Riepilogo
Giampiero Bartolomei lavora nel settore.
"""
        result = self.engine.redact(text, RedactOptions(language="it"))
        self.assertNotIn("linkedin.com", result.redacted_text)
        self.assertNotIn("bartolomei-314046224", result.redacted_text)
        self.assertNotIn("Giampiero Bartolomei", result.redacted_text)
        self.assertNotIn("Roma, Lazio, Italia", result.redacted_text)
        self.assertNotIn("[TELEFONO]", result.redacted_text)
        self.assertIn(
            "Corso di Formazione Generale e\nSpecifica per Lavoratori", result.redacted_text
        )
        for value in [
            "MATLAB Fundamentals",
            "Machine Learning with MATLAB",
            "Dispositivi Medici",
            "English Certificate Council of Europe",
            "BioEngineer Specialist & Researcher at Math Biology",
        ]:
            self.assertIn(value, result.redacted_text)
        self.assertEqual(
            [e.entity_type for e in result.entities], ["URL", "NAME", "LOCATION", "NAME"]
        )
        for entity in result.entities:
            self.assertEqual(text[entity.start : entity.end], entity.original)

    def test_contact_urls_phone_disambiguation_and_flags(self):
        text = "www.linkedin.com/in/mario-rossi-314046224\nMario Rossi\nEmail: mario@example.com\nTelefono: +39 339 1234567"
        result = self.engine.redact(text, RedactOptions(language="it", redact_contacts=False))
        self.assertIn("www.linkedin.com/in/mario-rossi-314046224", result.redacted_text)
        self.assertIn("mario@example.com", result.redacted_text)
        self.assertIn("+39 339 1234567", result.redacted_text)
        self.assertNotIn("\nMario Rossi", result.redacted_text)
        result = self.engine.redact(text, RedactOptions(language="it", redact_names=False))
        self.assertIn("\nMario Rossi", result.redacted_text)
        self.assertNotIn("linkedin.com", result.redacted_text)
        self.assertEqual(len([e for e in result.entities if e.entity_type == "PHONE"]), 1)
        result = self.engine.redact(
            "https://example.org/314046224\nCompetenze principali", RedactOptions(language="it")
        )
        self.assertIn("Competenze principali", result.redacted_text)
        self.assertEqual(result.entities[0].entity_type, "URL")

    def test_malformed_profile_url_does_not_interrupt_redaction(self):
        text = "https://www.linkedin.com:invalid-port/in/james-smith\nhttp://[invalid\nPatient: James Smith\nEmail: james@example.com"
        result = self.engine.redact(text, RedactOptions(language="en"))
        self.assertNotIn("james@example.com", result.redacted_text)
        self.assertNotIn("Patient: James Smith", result.redacted_text)
        self.assertEqual(len([e for e in result.entities if e.entity_type == "URL"]), 2)

    def test_real_street_vs_training_course(self):
        for course in [
            "Corso di Formazione Generale",
            "Corso di laurea in Ingegneria",
            "Corso MATLAB",
            "Corso di aggiornamento",
        ]:
            self.assertEqual(
                self.engine.redact(course, RedactOptions(language="it")).redacted_text, course
            )
        for address in [
            "Corso di Francia 142, Roma",
            "Corso Vittorio Emanuele 10",
            "Via Toledo 142, Napoli",
        ]:
            self.assertNotEqual(
                self.engine.redact(address, RedactOptions(language="it")).redacted_text, address
            )

    def test_professional_header_without_guessing_capitalized_skills(self):
        text = "Curriculum Vitae\nGiampiero Bartolomei\nBioEngineer Specialist & Researcher\nMachine Learning\nEngineer\nRoma, Italia"
        result = self.engine.redact(text, RedactOptions(language="it", redact_locations=False))
        self.assertNotIn("Giampiero Bartolomei", result.redacted_text)
        self.assertIn("Machine Learning", result.redacted_text)
        self.assertIn("Roma, Italia", result.redacted_text)
        clinical = "Follow Up\nMedico responsabile del reparto"
        self.assertEqual(
            self.engine.redact(clinical, RedactOptions(language="it")).redacted_text, clinical
        )


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_default_language_is_english(self):
        response = self.client.post("/api/redact/text", json={"text": "Patient: James Smith"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("[PATIENT_NAME]", response.json()["redacted_text"])
        self.assertNotIn("James Smith", response.json()["redacted_text"])
        self.assertEqual(self.client.get("/api/sample").json()["sample"], SAMPLES["en"])

    def test_contract_and_local_resources(self):
        for language in SAMPLES:
            sample = self.client.get("/api/sample", params={"language": language})
            self.assertEqual(sample.status_code, 200)
            response = self.client.post(
                "/api/redact/text",
                json={"text": sample.json()["sample"], "options": {"language": language}},
            )
            self.assertEqual(response.status_code, 200)
            self.assertGreater(response.json()["entities_found"], 0)
            self.assertEqual(response.headers["cache-control"], "no-store")
        for path in [
            "/",
            "/static/styles.css",
            "/static/app.js",
            "/static/i18n.js",
            "/static/icon.svg",
            "/static/theme.js",
            "/api/health",
            "/openapi.json",
        ]:
            self.assertEqual(self.client.get(path).status_code, 200)
        self.assertNotIn("https://", self.client.get("/").text)

    def test_validation_and_hosts(self):
        for payload in [
            {"text": ""},
            {"text": "x" * 200001},
            {"text": "x", "options": {"language": "xx"}},
            {"text": "x", "options": {"mask_mode": "INVALID"}},
        ]:
            self.assertEqual(self.client.post("/api/redact/text", json=payload).status_code, 422)
        self.assertEqual(self.client.get("/api/sample?language=xx").status_code, 422)
        self.assertEqual(
            self.client.get("/api/health", headers={"Host": "evil.example"}).status_code, 400
        )
        self.assertNotEqual(
            self.client.get("/api/health", headers={"Origin": "https://evil.example"}).headers.get(
                "access-control-allow-origin"
            ),
            "*",
        )

    def test_download_availability(self):
        data = self.client.get("/api/downloads").json()
        response = self.client.get("/download/windows")
        self.assertEqual(response.status_code, 200 if data["windows"] else 404)


if __name__ == "__main__":
    unittest.main()
