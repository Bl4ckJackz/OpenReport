# Step — Integrazioni esterne (opt-in)

Le integrazioni permettono alla skill di importare dati da sistemi esterni (Jira, Linear, Git) e pubblicare output su piattaforme aziendali (Confluence, Notion, SharePoint, Slack, Teams).

## Setup credenziali

Tutte le credenziali vanno in `~/.claude/.env` (mai committare, mai nel brand profile):

```bash
# Jira
export JIRA_BASE_URL=https://your.atlassian.net
export JIRA_EMAIL=user@example.com
export JIRA_API_TOKEN=...

# Linear
export LINEAR_API_KEY=lin_api_xxx

# Confluence
export CONFLUENCE_BASE_URL=https://your.atlassian.net/wiki
export CONFLUENCE_EMAIL=user@example.com
export CONFLUENCE_API_TOKEN=...

# Notion
export NOTION_API_KEY=secret_xxx
export NOTION_PARENT_DB=database_or_page_id

# SharePoint (Microsoft Graph)
export MSGRAPH_TENANT=tenant.onmicrosoft.com
export MSGRAPH_CLIENT_ID=...
export MSGRAPH_CLIENT_SECRET=...
export MSGRAPH_SITE_ID=...

# Slack
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Teams
export TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
```

Per caricarle automaticamente: `source ~/.claude/.env` oppure usa un hook shell.

## Uso nelle tipologie

| Tipologia | Integrazione raccomandata |
|---|---|
| `status-report` | Jira/Linear import issue + git-activity-extended |
| `proposta` | Confluence/SharePoint export per condivisione cliente |
| `case-study` | Notion publish per knowledge base aziendale |
| `handover` | Confluence wiki |
| `incident-postmortem` | Slack/Teams notify team |
| `sow` | SharePoint upload + Teams notify |
| `audit-report` | SharePoint (classificazione confidential) |

## Workflow Step 2/5 integrato

Durante **Step 2 scan** o **Step 5 refinement**, se `state.integrations.jira_project` impostato:

```bash
python3 scripts/integrations/jira-import.py --project $PRJ --jql "resolved >= -7d" --md > .session/jira-activity.md
```

Il contenuto viene incluso in Step 5 per generare sezioni `Risultati del periodo` con dati reali, non stimati.

## Workflow Step 7/8 pubblicazione

Dopo approval (`/relazione-approve`), il preset può includere post-action:

```yaml
post_actions:
  - bundle
  - confluence_export: {space: KEY, parent: "12345"}
  - slack_notify: {channel: "#sales"}
```

## Sicurezza

1. **Mai inline secret** nei file della skill
2. **Rate limit**: rispetta limiti API (Jira ~10 req/s, Notion ~3 req/s)
3. **Scope minimo**: usa API token con permessi solo necessari
4. **Audit**: ogni invio esterno registrato in `audit-trail.jsonl`
