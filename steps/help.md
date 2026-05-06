# /relazione-help

Mostra il welcome message della skill (uguale a quello che vede chi invoca `/relazione` per la prima volta), con cosa fa la skill e la sequenza tipica di comandi per usarla al 100%.

## Esecuzione

L'utente lancia `/relazione-help`. La skill stampa:

```
/relazione — generatore di relazioni formali in italiano e inglese.

Cosa fa: scansiona la cwd, ti fa qualche domanda, genera la bozza, esegue
13+ controlli qualità (forbidden terms, PII/secret, layout, citazioni,
leggibilità), esporta DOCX/PDF/EPUB, gestisce un workflow di approvazione.

Sequenza tipica per uso 100%:
  1.  /relazione-doctor       (opzionale — verifica dipendenze)
  2.  /relazione-setup        (solo prima volta — brand profile + Eisvogel)
  3.  /relazione-estimate     (opzionale — preview token e tempo)
  4.  /relazione              (questo flow — Step 1..8)
  5.  /relazione-review       (promuove a 'in-review' con watermark)
  6.  /relazione-import-feedback  (se ricevi commenti DOCX dal revisore)
  7.  /relazione-approve      (Step 9 — finalizza, archivia, audit log)

Anytime:
  /relazione-continua    riprende sessione interrotta
  /relazione-stats       dashboard sessioni
  /relazione-diff        confronta due iterazioni
  /relazione-rollback    ripristina backup
  /relazione-help        mostra di nuovo questo riepilogo

Per uso avanzato:
  /relazione-quick           skip questions, default smart
  /relazione-brand           configura brand aziendale
  /relazione-ricorrente      report ricorrenti (status weekly, ecc.)
  /relazione-workspace       workspace multi-sessione
  /relazione-preset-import   importa preset da URL
```

## Implementazione

Non richiede script — è solo un messaggio testuale. Quando Claude vede `/relazione-help`, stampa il blocco sopra e termina il turno (nessuna `AskUserQuestion`, nessuna azione successiva).

## Variante prima invocazione

Quando `/relazione` viene chiamato senza sessione esistente (Step 0 con 0 cartelle `relazioni*/`), il welcome è mostrato automaticamente prima di Step 1, con la riga finale «Procediamo? Step 1 ti fa 9-11 domande iniziali...» e attende ack.

Se `--no-intro` è passato, oppure `.user-profile.json` ha `seen_intro: true`, salta il welcome e va direttamente a Step 1.
