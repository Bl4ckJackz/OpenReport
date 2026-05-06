# Backup automatico & skill versioning

## Backup incrementale

Trigger: prima di ogni rigenerazione/refinement pesante (Step 4, Step 4.6 sezione, Step 5 refine, Step 6 write).

Path: `<output>/.session/backups/{ISO-timestamp}-{step}/`

Contenuto:
- Snapshot di `RELAZIONE.md` / `RELAZIONE.tex` corrente
- Snapshot di `references.bib` corrente
- Snapshot di `session-state.json` corrente

Aggiorna `session-state.json.backups[]` con metadata.

Retention: ultimi 10 backup. Più vecchi → cancella automatico.

## Rollback

Comando: `/relazione-rollback`

Lista backup disponibili (timestamp + step + size). Utente sceglie. Il rollback:
1. Sposta file correnti in `<output>/.session/backups/_pre-rollback-{ISO}/`
2. Ripristina file dal backup scelto
3. Aggiorna `session-state.json.current_step`
4. Conferma all'utente

## Skill versioning

`session-state.json.skill_version` registra la versione della skill che ha creato lo state.

`<skill_dir>/VERSION` contiene la versione corrente (semver).

### Migrazione automatica

Quando `/relazione-continua` carica uno state:
1. Confronta `state.skill_version` con `<skill_dir>/VERSION`
2. Se uguali: procedi normalmente
3. Se state è VECCHIA major (es. state 1.x, skill 2.x): mostra warning + chiedi
   - `Migra automaticamente` (esegui migration script in `scripts/migrate-{from}-to-{to}.py`)
   - `Apri come read-only` (l'utente può leggere ma non può continuare)
   - `Annulla`
4. Se state è NUOVA (skill è stata rollback): blocca con errore. Update skill prima.

### Migration scripts

`scripts/migrate-1.x-to-2.0.py` — esempio:
- Aggiunge campo `skill_version`
- Converte `current_step` enum vecchio → nuovo
- Aggiunge `voice_profile`, `mock_inventory`, `self_check_results` con default null/[]
- Aggiunge `backups[]` vuoto
- Aggiunge `token_budget` con default

Tieni le migrazioni cumulative: 1.0 → 1.5 → 2.0 sequenziali se serve.

## Schema validation

A ogni load di `session-state.json`:
1. Carica schema da `schemas/session-state.schema.json`
2. Valida con `jsonschema` (Python) o tool equivalente
3. Se invalid: mostra errore esatto, chiedi se riparare manualmente o scartare

A ogni save:
1. Valida prima di scrivere
2. Se invalid: blocca, mostra errore (è bug della skill, non dell'utente — salva log)

## Comando manuale

`/relazione-stats` mostra:
- Versione skill
- Versione state corrente (se sessione attiva)
- N backup disponibili
- Età dello state
- Token usage stimato vs cap
