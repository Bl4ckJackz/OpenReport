# /relazione-doctor

Diagnostica dell'ambiente. Verifica che tutte le dipendenze necessarie siano installate e segnala quelle opzionali mancanti.

## Quando usarlo

- All'installazione, per capire se serve installare qualcosa di aggiuntivo
- Prima di un'esportazione PDF complessa, per evitare di scoprire a metà che manca XeLaTeX
- In CI per validare l'ambiente di build (`--json` per output parsabile)

## Esecuzione

```bash
python scripts/workflow/doctor.py            # report leggibile
python scripts/workflow/doctor.py --json     # JSON per CI
```

## Output

Tre livelli di severità:

| Livello | Significato | Esempio |
|---|---|---|
| **REQ** (required) | senza questo nulla funziona — exit non-zero | Python ≥ 3.10, `pyyaml`, `jsonschema` |
| **REC** (recommended) | manca → degradazione importante | Pandoc, `python-docx`, Git |
| **OPT** (optional) | manca → funzionalità avanzate disabilitate | XeLaTeX, ffmpeg, hunspell, LanguageTool |

## Behavior nello skill flow

- **Step 0 (resume check)** — se nessuna sessione attiva e nessun `.brand-profile.json`, suggerisci `/relazione-setup` invece di doctor.
- **Step 7 (export)** — se l'utente sceglie un formato che richiede tool mancanti, il doctor viene invocato automaticamente in modo silenzioso e produce solo l'errore mirato.

## Esempio output

```
relazione-doctor — environment check

== CORE ==
  OK  [REQ] Python >= 3.10 (3.12.3)
  OK  [REC] git (2.45.1)
  OK  [REQ] python:yaml (6.0.1)
  --  [REQ] python:jsonschema
        hint: pip install jsonschema

OK — all required tools available.
```

Exit code:

- `0` — tutto richiesto presente (anche se REC/OPT mancano)
- `1` — almeno un REQ manca
