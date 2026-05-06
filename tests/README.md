# Tests

Smoke test per gli script bloccanti della pipeline (quelli che, se si rompono, possono mandare in produzione una relazione difettosa senza errori visibili).

## Esecuzione

```bash
pip install pytest jsonschema pyyaml
pytest                          # tutti i test
pytest tests/test_doctor.py -v  # un singolo file
```

## Cosa è coperto

| File | Script testato | Cosa verifica |
|---|---|---|
| `test_doctor.py` | `scripts/workflow/doctor.py` | Esegue il doctor in modalità `--json`, parse del payload, presenza chiavi attese |
| `test_resolve_variables.py` | `scripts/workflow/resolve-variables.py` | Sostituzione `{{placeholder}}` con valori da file vars |
| `test_layout_coherence.py` | `scripts/quality/layout-coherence.py` | Documento valido passa, frontespizio fuori posto fallisce |
| `test_pii_redact.py` | `scripts/security/pii-redact.py` | Email, IP, codici fiscali vengono mascherati |
| `test_schemas.py` | `schemas/*.json` | Tutti i JSON Schema sono caricabili e validi |

## Filosofia

Questi sono **smoke test**, non test esaustivi. L'obiettivo è verificare che:

1. Lo script si avvia senza crash di import
2. Il contratto di input/output (CLI args, schema JSON) regge
3. I path di rinomina/spostamento non hanno rotto le invocazioni interne

Per coverage approfondito di logica complessa, aggiungere test mirati nello stesso file.

## CI

Lo workflow GitHub Actions in `.github/workflows/test.yml` esegue questi test su Linux/macOS/Windows con Python 3.10, 3.11, 3.12.
