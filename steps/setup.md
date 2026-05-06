# /relazione-setup

Wizard al primo utilizzo della skill. Risolve il problema dell'onboarding: configurazione di brand profile, verifica delle dipendenze e download del template LaTeX in un unico flusso guidato.

## Quando usarlo

- Subito dopo aver clonato la skill — eseguire una sola volta
- Se l'utente cambia macchina e vuole ricreare la configurazione
- Per generare un brand profile da template senza passare per `/relazione-brand`

## Cosa fa

```
[1/3] Diagnostica ambiente   → invoca scripts/workflow/doctor.py
[2/3] Brand profile          → prompt interattivo, scrive .brand-profile.json
[3/3] Eisvogel template      → opzionale, download da GitHub
```

## Esecuzione

```bash
python scripts/workflow/setup.py             # interattivo
python scripts/workflow/setup.py --no-input  # accetta default (CI / quickstart)
python scripts/workflow/setup.py --skip-doctor
```

## Idempotenza

- Se `.brand-profile.json` esiste già, **non viene sovrascritto** (per evitare di perdere customizzazioni). Per riscriverlo: rimuoverlo manualmente e rilanciare.
- Se `pdf-templates/eisvogel.latex` esiste già, viene saltato.

## Behavior nello skill flow

Quando l'utente invoca `/relazione` per la prima volta e:

- Manca `.brand-profile.json` **e**
- Manca `.session/` in qualsiasi `relazioni*/`

la skill propone di lanciare `/relazione-setup` prima di iniziare. L'utente può saltare con "no" (la skill chiederà i dati di brand al volo nel Step 1).
