from typing import Dict


class PseudonymRegistry:
    """Mantiene la coerenza delle sostituzioni all'interno dello stesso documento.

    Se 'Mario Rossi' viene sostituito con 'Paziente_1', ogni altra occorrenza
    di 'Mario Rossi' nello stesso testo riceverà lo stesso pseudonimo.
    """

    def __init__(self):
        self._registry: Dict[str, str] = {}
        self._counts: Dict[str, int] = {}

    def get_or_create(self, entity_type: str, original_val: str) -> str:
        key = f"{entity_type}:{original_val.strip().lower()}"
        if key in self._registry:
            return self._registry[key]

        current_count = self._counts.get(entity_type, 0) + 1
        self._counts[entity_type] = current_count

        pseudonym_map = {
            "NAME": f"Paziente_{chr(64 + current_count) if current_count <= 26 else current_count}",
            "DOCTOR": f"Medico_{current_count}",
            "TAX_CODE": f"CF_ANONIMO_{current_count:02d}",
            "PHONE": f"+39-XXX-XXXX{current_count:02d}",
            "EMAIL": f"paziente_{current_count}@example-anon.org",
            "LOCATION": f"Comune_{current_count}",
            "HOSPITAL": f"Struttura_Sanitaria_{current_count}",
            "ID": f"ID_REF_{current_count:04d}",
            "DATE": f"[DATA_{current_count}]",
        }

        pseudonym = pseudonym_map.get(entity_type, f"[{entity_type}_{current_count}]")
        self._registry[key] = pseudonym
        return pseudonym
