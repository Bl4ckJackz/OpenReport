# Code snippet handling

Comportamento del Draft (Step 4) in base ad `answers.code_snippets`.

## Per modalità

### `no`
Nessun code block nel draft. Descrivi i moduli solo a parole.

### `sì-mirato`
Estrai 4–6 snippet brevi (10–30 righe ciascuno) dai file più rappresentativi della tipologia. Inseriscili in fenced code block con language hint, alla fine della sotto-sezione di pertinenza.

Privilegia:

- Pure functions testabili
- Formule matematiche
- Pattern di sicurezza (CSP, JWT)
- Funzioni di calcolo
- Indici DB unici parziali
- SQL migration significative

### `sì-estensivo`
10+ snippet distribuiti su tutte le sotto-sezioni rilevanti dell'implementazione (§7.2 in tipologia `progetto`, equivalente in altre), più Appendice "Firme di interfaccia" carica con firme TypeScript/Python/Dart dei moduli chiave. Mantieni gli snippet sotto le 60 righe ciascuno.

### `solo-appendice`
Corpo testo §implementazione neutro (descrizioni a parole, senza code block), Appendice dedicata carica con firme + 1-2 snippet di riferimento per modulo chiave.

## Regole comuni (sì-*  e solo-appendice)

1. Estrai esclusivamente da file realmente esistenti nella cwd (verifica con Read). **MAI inventare codice che non esiste.**
2. Specifica sempre il path di provenienza prima del code block: «L'estratto seguente, dal modulo `<path>`, mostra/illustra ...»
3. Riduci il codice estratto eliminando dettagli accessori (commenti verbosi, edge case minori), ma preserva la struttura essenziale e l'attribuzione.
4. Mai includere secret/API key/IP esposti — applica masking se necessario (verifica finale: `scripts/security/secret-scan.sh` in Step 6.5).
5. Language hint corretto (`typescript`, `python`, `dart`, `sql`, `rust`, `go`, ecc.) per abilitare syntax highlight nel PDF (eisvogel + listings).
6. Preferisci snippet che illustrano una **decisione** (perché X), un **pattern non banale**, o una **formula** citata in §3 stato dell'arte.
7. Aggiungi gli snippet a `files_written[]` solo se vivono in file separati; altrimenti restano inline nel `RELAZIONE.md`.
