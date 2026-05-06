# Step 6.7 — Layout coherence check (BLOCCANTE)

Eseguito **dopo Step 6.5 (PII/secret) e prima di Step 7 (export)**. Verifica che l'ordine degli elementi del documento sia coerente con `pdf_style` e con la tipologia. **Mai produrre PDF/DOCX se questo step fallisce.**

## Obiettivo

Impedire artefatti come:
- Indice (TOC) **prima** del frontespizio
- Document Control sheet messo in fondo
- Bibliografia in mezzo al corpo
- Appendici prima della bibliografia (per stili che lo vietano)
- `\listoffigures` / `\listoftables` prima del TOC in stile accademico

## Comando

```bash
python3 scripts/layout-coherence.py <output>/RELAZIONE.md \
  --style=<accademico|moderno|brand> \
  --tipologia=<tipologia> \
  [--strict]
```

Per formato `latex` o `both`, esegui anche su `RELAZIONE.tex`.

Per formato `both`, esegui SU ENTRAMBI e verifica che entrambi siano OK prima di compilare.

## Regole verificate

| Regola | Severità | Quando |
|---|---|---|
| `frontespizio-first` | FAIL | Sempre (eccetto `bug`/`codice`) |
| `frontespizio-missing` | WARN | Sempre |
| `toc-after-frontespizio` | FAIL | Se TOC presente |
| `toc-after-control` | FAIL | Se enterprise + TOC presente |
| `missing-control-sheet` | WARN | Tipologia enterprise |
| `control-after-frontespizio` | FAIL | Se control sheet presente |
| `appendix-after-biblio` | WARN | Se entrambe presenti |
| `section-after-biblio` | FAIL | Sezioni di corpo dopo bibliografia |
| `lof-after-toc` | FAIL | Solo `accademico` |
| `missing-abstract` | WARN | Solo `accademico` + tipologia accademica |
| `style-mismatch` | WARN | `moderno` su tipologia accademica |
| `brand-no-control` | FAIL | `brand` su tipologia enterprise |

## Output

Il tool stampa per ogni finding:
```
[FAIL] toc-after-frontespizio line 42: Indice (riga 42) appare PRIMA del frontespizio (riga 87).
```

Se `--json` viene passato, output strutturato:

```json
{
  "summary": {"fail": 1, "warn": 2, "ok": false},
  "findings": [{"sev":"FAIL","rule":"toc-after-frontespizio","line":42,"msg":"..."}]
}
```

## Comportamento orchestratore

1. **FAIL > 0** → BLOCCA. Mostra report all'utente con `AskUserQuestion`:
   - `Riordina automaticamente` → tenta fix programmatico (sposta blocchi)
   - `Apri il file e correggi manualmente` → pausa, salva state, l'utente riapre quando ha sistemato
   - `Forza export (sconsigliato)` → solo dopo conferma esplicita, NON si può procedere ad approvazione successiva
2. **WARN > 0** → mostra, chiedi `procedo / rivedo`. Default `procedo`.
3. **OK** → procedi a Step 7.

## Auto-fix programmatico (opzionale)

Se utente sceglie "Riordina automaticamente":
1. Parsa il file in blocchi (regex su `^# `, `^## `, `\section{}`, ecc.)
2. Riordina secondo l'array `EXPECTED_ORDER` definito in `layout-coherence.py`
3. Backup pre-fix in `.session/backups/{ISO}-pre-layout-fix/`
4. Riscrive il file
5. Re-run `layout-coherence.py` per verificare; se ancora FAIL, escala a manuale

## Stato

In `session-state.json`:

```json
"layout_check": {
  "executed_at": "<ISO>",
  "style": "<style>",
  "fail_count": 0,
  "warn_count": 1,
  "auto_fix_applied": false,
  "force_overridden": false
}
```

`force_overridden: true` blocca successivamente `/relazione-approve` (non si può approvare un layout incoerente forzato).

## Red flags

- Saltare questo step perché "ho già controllato a occhio"
- Eseguire solo su uno dei due file in formato `both` (deve girare su entrambi)
- Procedere a Step 7 con FAIL > 0
- Approvare con `force_overridden: true` (BLOCCATO da Step 9)
