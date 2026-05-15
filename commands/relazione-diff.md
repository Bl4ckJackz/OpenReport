---
description: Confronta due iterazioni di una relazione evidenziando le differenze (utile per revisione con cliente/docente)
allowed-tools: Bash, Read, Glob
---

# /relazione-diff — Diff tra due versioni di una relazione

## Argomenti

`$ARGUMENTS` può essere:
- `<file1> <file2>` — diff esplicito tra due path
- `<file>` — diff tra `<file>` e l'ultimo backup in `.session/backups/`
- vuoto — auto-detect: trova ultima cartella `relazioni*/` e fai diff tra `RELAZIONE.md` corrente e ultimo backup

## Comportamento

1. **Localizza i due file:**
   - Se due path forniti, usa quelli
   - Se un path, cerca `<dir>/.session/backups/*-RELAZIONE.md` e usa il più recente
   - Se vuoto, Glob `relazioni*/.session/backups/*` per trovare backup recente

2. **Mostra diff in formato leggibile:**
   ```bash
   diff -u <vecchia> <nuova> | head -200
   ```
   Se diff è lungo (>500 righe), mostra solo statistiche:
   - Sezioni aggiunte/rimosse (titoli)
   - Word count delta
   - Righe modificate
   - Lista delle 5 modifiche più significative (per blocco contiguo modificato)

3. **Riassunto sezione per sezione:**
   Per ogni sezione (H1/H2):
   - Status: `unchanged | modified | added | removed`
   - Word count delta
   - Esempio prima riga modificata

4. **Suggerimento:**
   Se il delta è ampio (>20% parole modificate), proponi di salvare un nuovo backup pre-revisione e di fare commit logico (in `.session/backups/{timestamp}-pre-review.md`).

## Output formato

```
=== DIFF RELAZIONE ===
Vecchia: relazioni/.session/backups/2026-04-15T10-30-00-RELAZIONE.md (3120 parole)
Nuova:   relazioni/RELAZIONE.md (3247 parole, +127)

Sezioni:
  ✓ Introduzione        unchanged
  ⟳ Stato dell'arte     modified (+340 parole)
  ⟳ Metodologia         modified (+50 parole, +2 citazioni)
  + Risultati nuovi     added (340 parole)
  - Sezione vecchia     removed (180 parole)

Top modifiche:
  1. line 234: aggiunta sottosezione "Confronto con baseline"
  2. line 567: rimossa nota informale, sostituita con tabella
  3. line 891: chiarito calcolo metrica X
  ...

Per vedere il diff completo:
  diff -u <vecchia> <nuova> | less
```

## Note

Non modificare alcun file — solo lettura.
Salva eventuale snapshot in `.session/backups/` se l'utente lo conferma.
