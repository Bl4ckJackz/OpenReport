# Red Flags — STOP immediato

Carica questo file SOLO se Claude ha dubbi su uno specifico anti-pattern. Le regole bloccanti più critiche sono già in `SKILL.md` §NON-NEGOTIABLE RULES.

## Workflow / discipline

- Scrivere bozza prima di completare TUTTE le domande Step 1 (incluso scope online)
- WebSearch/WebFetch quando l'utente ha scelto `solo-locale`
- Saltare Step 4.5 self-check prima del write finale
- Saltare Step 6.5 quando il codice incluso può contenere secret
- Saltare Step 6.7 layout-coherence (BLOCCANTE)
- Procedere a Step 7 con `layout_check.fail_count > 0`
- Procedere senza salvare backup pre-rigenerazione
- Saltare Step 2.6 knowledge graph build
- Re-read di file sorgente quando il dato è già in `.session/knowledge/nodes.jsonl`
- Editare manualmente `session-state.json.status` saltando passaggi (transizione proibita)
- Step 8 che setta `status: "completed"` — VIETATO. Step 8 termina in `ready-for-approval`.

## Output / formato

- Produrre due PDF visivamente identici (formato `both` richiede stili differenziati)
- Saltare DOCX (è SEMPRE prodotto, mai opzionale)
- Sovrascrivere `RELAZIONE.pdf` da md con `RELAZIONE.pdf` da tex (rinomina sempre `-tex.pdf`)
- Scrivere file di output direttamente in cwd invece che in sottocartella
- Non verificare con Glob se `relazioni/` esiste già — porta a sovrascritture
- Path immagini inesistenti
- `\cite{key}` per chiavi non in `.bib`
- Mescolare sintassi md in `.tex` o viceversa
- Leggere `node_modules` o altre escluse

## Contenuto / integrità

- Includere riferimenti AI/Claude/Anthropic anche in commenti LaTeX
- Claimare docx/pdf/LaTeX compilato senza eseguire e verificare exit-code
- Installare tool senza chiedere
- Producing report molto sotto target di pagine
- Ripetere contenuto per gonfiare lunghezza
- `[MOCK]` non listati in Nota metodologica
- Mockare nomi persone / bibliografia / DOI / dati fiscali (anche con sì-mock)
- Inventare URL/DOI/autori — cita solo recuperati via WebSearch
- Saltare ricerca online per `tesi`/`ricerca`/`progetto`
