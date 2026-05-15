---
description: Crea, esegue e gestisce relazioni ricorrenti (status report weekly/monthly) con diff da periodo precedente
argument-hint: "<setup|run|list|remove> [nome]"
---

# /relazione-ricorrente — Report ricorrenti

Gestisce sessioni di relazione ricorrenti (tipicamente `status-report`). Ogni esecuzione rigenera il report per il nuovo periodo attingendo dati automaticamente da Jira/Linear/Git e calcolando diff dal periodo precedente.

## Sub-comandi

### `/relazione-ricorrente setup <nome>`

Crea config in `relazioni-ricorrenti/<nome>/config.yaml`. Wizard:

1. `AskUserQuestion`: cadenza (`daily`, `weekly`, `biweekly`, `monthly`, `quarterly`)
2. `AskUserQuestion`: tipologia base (`status-report`, `kpi-dashboard`, `incident-postmortem`)
3. Chiedi sorgenti dati:
   - Jira project key? (vuoto = skip)
   - Linear team? (vuoto = skip)
   - Git repo path? (vuoto = cwd)
   - Calendar / meetings? (vuoto = skip)
4. Chiedi destinatari:
   - Slack channel (opzionale)
   - Teams webhook (opzionale)
   - Email (opzionale)
5. Scrivi `relazioni-ricorrenti/<nome>/config.yaml`:

```yaml
name: "ACME Weekly Status"
cadenza: "weekly"
tipologia: "status-report"
preset: "status-report-weekly"
sources:
  jira_project: "ACME"
  linear_team: null
  git_repo: "/path/to/repo"
destinatari:
  slack_channel: "#acme-status"
  teams_webhook: null
last_run: null
next_run: "2026-04-21"
periodi_generati: []
```

### `/relazione-ricorrente run <nome>`

Esegue un ciclo:

1. Leggi `config.yaml`, determina `periodo` (es. `2026-W16`)
2. Crea cartella `relazioni-ricorrenti/<nome>/<periodo>/`
3. Importa dati da sorgenti configurate:
   ```bash
   python3 ~/.claude/skills/relazione/scripts/integrations/jira-import.py \
     --project "$JIRA" --since "<last_run>" --md > .session/jira-data.md
   python3 ~/.claude/skills/relazione/scripts/integrations/git-activity-extended.sh \
     --since "<last_run>" > .session/git-data.md
   ```
4. Genera relazione usando `preset` + tipologia (come `/relazione-quick --profile=status-report-weekly`)
5. Calcola diff da periodo precedente:
   ```bash
   python3 ~/.claude/skills/relazione/scripts/diff-summary.py \
     <periodo_prec>/RELAZIONE.md <periodo_corr>/RELAZIONE.md > .session/diff.md
   ```
   Appendi sezione "Variazioni dal periodo precedente" al report
6. Self-check + export PDF
7. Notifica se configurata:
   ```bash
   bash ~/.claude/skills/relazione/scripts/integrations/slack-notify.sh \
     "Status report <periodo> pronto: <link>"
   ```
8. Aggiorna `config.yaml`: `last_run`, `next_run`, append `<periodo>` a `periodi_generati`

### `/relazione-ricorrente list`

Elenca tutti i report ricorrenti configurati:
```bash
for f in relazioni-ricorrenti/*/config.yaml; do
  python3 -c "import yaml; c=yaml.safe_load(open('$f')); print(f\"{c['name']:30} cadenza={c['cadenza']:10} ultimo={c.get('last_run','mai')} prossimo={c.get('next_run')}\")"
done
```

### `/relazione-ricorrente remove <nome>`

Dopo conferma (`AskUserQuestion`): rimuovi `relazioni-ricorrenti/<nome>/` (chiedi se archiviare prima).

## Integrazione con scheduling

Una volta setup, puoi automatizzare con la skill `schedule` (cron remoto) oppure `loop`:

```bash
/schedule add "relazione-weekly" "0 9 * * 1" "/relazione-ricorrente run acme-weekly"
```

Oppure manualmente ogni lunedì: `/relazione-ricorrente run acme-weekly`.

## Red flags

- **Non sovrascrivere periodi già generati** — ogni periodo ha propria cartella immutabile
- **Diff richiede periodo precedente esistente** — primo run salta diff section
- **Credenziali integrazioni in ~/.claude/.env**, mai nel config.yaml
- **Periodo identifier**: `YYYY-Www` per weekly, `YYYY-MM` per monthly, `YYYY-Qq` per quarterly
- **Skipping missing data**: se Jira/Linear non raggiungibili, warn ma prosegui (report parziale > nessun report)
