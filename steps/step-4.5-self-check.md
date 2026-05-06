# Step 4.5 — Self-check pre-output

Eseguito **dopo Step 4 (draft) e prima di Step 5 (follow-up)**. Anche subito prima di Step 6 (write finale).

Lo script `scripts/self-check.sh <file>` esegue tutti i controlli e ritorna report strutturato.

## Controlli obbligatori

### 1. Word count vs target
```
words_actual = $(wc -w <file>)
words_target = answers.lunghezza_target_pagine * 400
deviation = abs(actual - target) / target

WARN if deviation > 0.20
FAIL if deviation > 0.40
```

### 2. Forbidden terms grep
Esegui `scripts/forbidden-check.sh` (vedi `steps/forbidden-terms.md`).
- Match → FAIL, lista occorrenze + numero riga.

### 3. AI tells (Italiano + Inglese)
Stessa lista di `steps/forbidden-terms.md` sezione 2-3.
- WARN se ≥ 3 occorrenze totali.

### 4. Mock inventory consistency
Per ogni `[MOCK]` nel testo, verifica esista entry corrispondente nella sezione "Nota metodologica".
- FAIL se mock non listati.

### 5. Citation completeness
Per ogni `\cite{key}` (LaTeX) o `[^N]` (markdown):
- Verifica `key` esista in `references.bib` o `[^N]` abbia entry corrispondente
- FAIL se citazione orfana

### 6. Citation density (per sezioni > 800 parole)
- Calcola N citazioni per sezione
- WARN se sezione > 800 parole ha < 2 citazioni (o < 1 per `bug`/`finale`/`esperienza`)

### 7. Image references
Per ogni `![](path)` o `\includegraphics{path}`:
- Verifica file esiste relativo al `.md`/`.tex`
- FAIL se path mancante

### 8. Readability score
- Italiano: indice **Gulpease** (0-100, target 50-70 per testo formale)
- Inglese: **Flesch-Kincaid** (target 30-50 per accademico, 50-70 per business)
- Per ogni sezione, mostra score
- WARN se sezione fuori range target del registro scelto

### 9. Tone drift detection
Per ogni sezione vs prima sezione (baseline):
- Confronta lunghezza media frase (delta > 30% → WARN)
- Confronta uso prima persona singolare vs plurale vs impersonale (cambio dominante → WARN)
- Confronta densità subordinate (delta > 40% → WARN)

### 10. Voice profile lock check
Se `session-state.json.voice_profile` è popolato (locked dopo prima sezione):
- Verifica ogni nuova sezione rientri nei marker locked
- WARN se drift significativo

## Output del self-check

```
=== SELF-CHECK RELAZIONE ===
File: RELAZIONE.md (3247 parole)
Target: ~3200 parole (8 pagine × 400) — OK (deviazione 1.5%)

[FAIL] Forbidden terms (2):
  - line 142: "Co-Authored-By: Claude"
  - line 891: "🤖 Generated with"

[WARN] AI tells (4):
  - line 23: "delve into"
  - line 67: "in conclusione"
  - line 234: "rappresenta una pietra miliare"
  - line 512: "navigare nel complesso panorama"

[OK] Mock inventory: 7 mock listati e tutti presenti in Nota metodologica
[OK] Citations: tutte le 18 chiavi `\cite{}` esistono in references.bib
[WARN] Citation density: sezione "Stato dell'arte" (1240 parole) ha solo 1 citazione
[FAIL] Missing image: line 445 → ./img/architecture.png non esiste
[OK] Readability: tutte le sezioni in range Gulpease 55-65
[WARN] Tone drift: sezione 7 ("Risultati") ha lunghezza frase media +45% vs baseline

=== AZIONE RICHIESTA ===
Risolvi 2 FAIL prima di procedere a Step 6.
4 WARN da valutare (puoi ignorare se motivati).
```

## Comportamento

- **FAIL > 0** → blocca write output. Mostra lista, chiedi rewrite, ri-esegui.
- **WARN > 0** → mostra ma non blocca. Chiedi conferma "procedi così o rivedo i WARN?".
- **All clean** → procedi a Step 5 (refinement) o Step 6 (write).

Salva risultati in `session-state.json.self_check_results`.
