# OpenReport — `relazione` skill

Skill modulare per **Claude Code** (compatibile Copilot CLI / Gemini CLI) che genera **relazioni formali in italiano e inglese** — accademiche (tesi, ricerca, stage, lab, progetto) ed enterprise (proposta, RFP response, SOW, business case, spec funzionale/tecnica, incident post-mortem, status report, whitepaper, case study, handover, runbook, audit, compliance).

Scansiona la cartella corrente, raccoglie i requisiti tramite domande mirate (o preset), genera la bozza, esegue 13+ controlli di qualità, esporta in DOCX/PDF/EPUB e gestisce un workflow di approvazione con audit trail.

Versione corrente: vedi [`VERSION`](./VERSION) — changelog completo in [`CHANGELOG.md`](./CHANGELOG.md).

---

## Caratteristiche principali

- **34 tipologie** di documento (accademiche + enterprise) con template dedicati in [`templates.md`](./templates.md)
- **Brand profile** + **user voice profile** — la relazione "suona" come scritta dall'utente, non da un'AI
- **Self-check bloccante** — forbidden terms (AI tells), fact-check vs ricerca, cross-ref lint, temporal consistency, citazioni, leggibilità (Gulpease/Flesch), tone drift, PII/secret scan, accessibility, layout coherence
- **Export dual-style** — DOCX + PDF moderno + (opzionale) PDF accademico LaTeX/Eisvogel
- **Knowledge graph leggero** — embedding hash-based 128-dim per ridurre il consumo di token del 60–80% sulle sessioni lunghe
- **Approval workflow** — `in-progress → ready-for-approval → approved → completed` con audit trail append-only e watermark dinamici (DRAFT / FOR REVIEW / CONFIDENTIAL)
- **Ricorrenze** — status report settimanali/mensili con diff automatico dal periodo precedente
- **Multi-lingua parallelo** — IT + EN allineati capitolo per capitolo (+ ES/FR/DE/PT)
- **Persistenza** — la sessione sopravvive a context reset (`/relazione-continua`)
- **Integrazioni** — Jira, Linear, Confluence, Notion, SharePoint, Slack, Teams, Git, Zotero, arXiv, Semantic Scholar, CrossRef
- **Defense simulator** — pacchetto domande/risposte per discussione tesi
- **Template università italiane** — Bocconi, Federico II, PoliMi, PoliTo, Sapienza, UniBo, UniMi, UniNa, UniPd, UniPi

## Comandi

| Comando | Cosa fa |
|---|---|
| `/relazione` | Workflow completo guidato (9 domande + iterazioni) |
| `/relazione-quick` | Default intelligenti, salta le domande (auto-detect tipologia da nome cartella) |
| `/relazione-continua` | Riprende sessione interrotta (legge `.session/session-state.json`) |
| `/relazione-rollback` | Ripristina versione precedente da backup |
| `/relazione-stats` | Statistiche e diagnostica delle sessioni |
| `/relazione-diff` | Confronta due iterazioni (utile per revisione cliente/docente) |
| `/relazione-brand` | Configura brand profile aziendale |
| `/relazione-review` | Promuove a status `in-review`, aggiunge watermark |
| `/relazione-approve` | Approva, timbra data, archivia versione |
| `/relazione-import-feedback` | Importa track-changes da DOCX revisionato |
| `/relazione-ricorrente` | Crea/esegue report ricorrenti con diff |
| `/relazione-workspace` | Workspace multi-sessione |
| `/relazione-condividi` | Comprime e condivide una sessione |
| `/relazione-preset-import` | Importa preset da URL (gist/GitHub) |

## Installazione

### Claude Code

```bash
# Clona nella cartella skills di Claude Code
git clone https://github.com/Bl4ckJackz/OpenReport.git ~/.claude/skills/relazione
```

Su **Windows (PowerShell)**:

```powershell
git clone https://github.com/Bl4ckJackz/OpenReport.git "$env:USERPROFILE\.claude\skills\relazione"
```

Riavvia Claude Code e scrivi `/relazione` per attivarla.

### Copilot CLI / Gemini CLI

Il file `SKILL.md` è compatibile con il formato Anthropic Skills. Per Gemini CLI la skill viene attivata via `activate_skill`. Vedi [`docs/SKILL-GUIDE.md`](./docs/SKILL-GUIDE.md) per i dettagli.

## Dipendenze

La skill funziona "a livelli" — il workflow base richiede solo Python. Le funzionalità avanzate sono opzionali e degradano in modo elegante se mancano i tool.

| Funzionalità | Tool richiesto | Note |
|---|---|---|
| Workflow base, self-check, redact, schemi | **Python ≥ 3.10** | obbligatorio |
| Export DOCX | **Pandoc ≥ 3.0** | consigliato |
| Export PDF moderno | **Pandoc + wkhtmltopdf** o **weasyprint** | uno dei due |
| Export PDF accademico (LaTeX) | **TeX Live** + template **Eisvogel** | opzionale |
| Diagrammi Mermaid | **mermaid-filter** (npm) | opzionale |
| EPUB con audio | **pandoc**, **ffmpeg** | opzionale |
| Grammar check | **LanguageTool** (server o CLI) | opzionale |
| Spell check | **hunspell** + dizionari it/en | opzionale |
| Integrazioni | API key del servizio (Jira, Linear, ecc.) | opzionale |

Pacchetti Python (installa solo ciò che usi):

```bash
pip install pyyaml jsonschema rich requests beautifulsoup4 lxml \
            python-docx pypdf reportlab \
            sentence-transformers numpy   # solo per knowledge-graph avanzato
```

## Struttura del repo

```
SKILL.md            # orchestratore principale (caricato da Claude)
VERSION             # semver corrente
CHANGELOG.md        # storico versioni
templates.md        # struttura per ogni tipologia
docs/               # guida utente estesa
steps/              # istruzioni per ogni step (caricati on-demand)
scripts/            # 70+ automazioni Python/Bash (self-check, export, redact, …)
presets/            # risposte preconfigurate per pattern ricorrenti
pdf-templates/      # YAML Pandoc/Eisvogel + template università
schemas/            # JSON Schema per validazione (session-state, brand, user)
```

## Esempio di utilizzo

```
$ cd ~/progetti/tesi-magistrale/
$ claude
> /relazione

[la skill scansiona la cwd, fa 9 domande, propone preset "tesi-magistrale"]

> /relazione-review
[promuove a in-review, watermarka il PDF "FOR REVIEW"]

> /relazione-import-feedback revisione-prof.docx
[importa i commenti del docente, propone fix per ciascuno]

> /relazione-approve
[stampa data approvazione, archivia versione finale]
```

## Privacy & sicurezza

- **Forbidden terms check** — la relazione non contiene mai riferimenti a Claude/Anthropic/AI o disclaimer "generato da intelligenza artificiale". Il testo è dell'utente.
- **PII redact** — email, IP, path locali, codici fiscali, numeri di telefono vengono identificati prima dell'export.
- **Secret scan** — token, API key, password vengono bloccati in fase di pre-export.
- **PDF redact permanente** — disponibile in `scripts/pdf-redact.py`.
- **GPG sign** — firma del PDF finale per integrità (`scripts/gpg-sign.sh`).

## Licenza

TBD — il progetto è pubblicato come riferimento; specificare licenza prima dell'adozione in produzione.

## Contribuire

Pull request benvenute. Ogni nuovo `script/*` deve:

1. Avere un'intestazione `#!/usr/bin/env python3` o `#!/usr/bin/env bash` e essere eseguibile
2. Esporre `--help` con descrizione + esempio
3. Degradare con messaggio chiaro se mancano dipendenze opzionali
4. Essere referenziato in `SKILL.md` (tabella tool registry) e nello `steps/*.md` pertinente
5. Avere voce in `CHANGELOG.md`
