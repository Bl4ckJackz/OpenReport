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
| `/relazione-doctor` | Diagnostica ambiente (dipendenze required/recommended/optional) |
| `/relazione-setup` | Wizard al primo utilizzo (brand profile + Eisvogel + doctor) |
| `/relazione-estimate` | Stima preventiva di token, pressione context-window e tempo prima di iniziare |
| `/relazione-help` | Mostra il welcome con cosa fa la skill e la sequenza di comandi per usarla al 100% |
| `/relazione-exit` | Uscita pulita: forza save, crea backup snapshot, stampa summary + comando di resume |

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

Riavvia Claude Code e — al primo utilizzo — esegui:

```bash
python ~/.claude/skills/relazione/scripts/workflow/setup.py
```

Poi scrivi `/relazione` per attivarla.

### Copilot CLI / Gemini CLI

Il file `SKILL.md` è compatibile con il formato Anthropic Skills. Per Gemini CLI la skill viene attivata via `activate_skill`. Vedi [`docs/SKILL-GUIDE.md`](./docs/SKILL-GUIDE.md) per i dettagli.

## Stima preventiva

Prima di iniziare una relazione lunga puoi stimare token attesi, pressione sul context window e durata:

```bash
python scripts/workflow/estimate.py --tipologia tesi --pages 80 --online --outline-first
```

Output: token input/output/totali, percentuale di context window utilizzato al picco, raccomandazioni automatiche (attiva outline-first, pianifica pausa, considera `--draft-only`). Stima ±30%. Vedi [`steps/estimate.md`](./steps/estimate.md).

## Outline-first (per documenti ≥ 30 pagine)

Per documenti lunghi, la skill genera **prima** l'indice + 1 frase per sezione (~2.5k token), te lo sottopone, lo approvi/modifichi, e **poi** Step 4 espande sezione per sezione. Vantaggi:

- −30% token sull'output finale (catturi rifusioni strutturali prima di pagare l'espansione)
- −40% iterazioni di refinement (problemi di scope visti subito)
- L'utente co-crea invece di ricevere

Trigger automatico per `pages >= 60`, opzionale per 30-60. Vedi [`steps/step-3.6-outline.md`](./steps/step-3.6-outline.md).

## Diagnostica

Verifica l'ambiente in 1 comando:

```bash
python scripts/workflow/doctor.py            # report leggibile
python scripts/workflow/doctor.py --json     # output machine-readable per CI
```

Esce con codice ≠ 0 se manca uno strumento **required**. Strumenti `recommended` e `optional` sono segnalati ma non bloccanti.

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
scripts/
  quality/        # self-check, readability, tone, citations, layout, grammar
  security/       # PII redact, secret scan, watermark, GPG sign
  export/         # PDF/DOCX/EPUB/Typst/Quarto/HTML, slides, audiobook
  intel/          # citations, papers, knowledge graph, schema diagrams
  generators/     # abstract, TOC, RACI, RTM, Gantt, KPI, risk register
  workflow/       # state, brand, setup, doctor, save, search, tags
  integrations/   # Jira, Linear, Confluence, Notion, SharePoint, Slack, Teams
tests/              # smoke tests (pytest)
presets/            # risposte preconfigurate per pattern ricorrenti
pdf-templates/      # YAML Pandoc/Eisvogel + template università
schemas/            # JSON Schema per validazione (session-state, brand, user)
```

## Esempio di utilizzo

Alla prima invocazione la skill ti mostra cosa fa e la sequenza di comandi consigliata. Tra una fase e l'altra ti dice esplicitamente quale comando lanciare poi (pattern `→ Next:`).

```
$ cd ~/progetti/tesi-magistrale/
$ claude
> /relazione

[Welcome con la sequenza tipica + 9-11 domande iniziali]
[Scan, knowledge graph, draft, self-check, layout-check, export]
→ Next: artifact pronti. Step 8 ti chiede quali companion vuoi.

> /relazione-review
[promuove a 'in-review', watermarka il PDF "FOR REVIEW"]
→ Next: condividi il PDF. Quando ricevi feedback DOCX: /relazione-import-feedback <file>

> /relazione-import-feedback revisione-prof.docx
[importa i commenti del docente, propone fix per ciascuno]
→ Next: ho applicato N suggerimenti. /relazione per riaprire e continuare.

> /relazione-approve
[stampa data approvazione, archivia versione finale, audit log]
→ Next: relazione approvata e archiviata. Versione finale in archive/v1.0/.
```

## Privacy & sicurezza

- **Forbidden terms check** — la relazione non contiene mai riferimenti a Claude/Anthropic/AI o disclaimer "generato da intelligenza artificiale". Il testo è dell'utente.
- **PII redact** — email, IP, path locali, codici fiscali, numeri di telefono vengono identificati prima dell'export.
- **Secret scan** — token, API key, password vengono bloccati in fase di pre-export.
- **PDF redact permanente** — disponibile in `scripts/security/pdf-redact.py`.
- **GPG sign** — firma del PDF finale per integrità (`scripts/security/gpg-sign.sh`).

## Esempi

Vedi [`examples/`](./examples/) — output reali della skill (anonimizzati) per uno status report settimanale e un estratto di tesi magistrale.

## Licenza

[MIT](./LICENSE) — Copyright (c) 2026 Dominik Duda.

## Performance

Vedi [`docs/PERFORMANCE.md`](./docs/PERFORMANCE.md) — playbook su gestione context window, knowledge graph come single source of truth, outline-first per documenti lunghi, sub-agent policy, modalità `--draft-only`.

Numeri chiave:

- `SKILL.md` body: ~556 righe (~7.5k token caricati per turno)
- Knowledge graph hash-128 in `.session/knowledge/` riduce re-read del 60–80%
- Sub-agent solo per output verboso (>5k righe) o parallelizzazione genuina (4+ task indipendenti) — costo startup ~20k token
- Outline-first risparmia ~30% output su documenti ≥ 30 pp

## Test

```bash
pip install pytest jsonschema pyyaml
pytest
```

CI su Linux/macOS/Windows × Python 3.10/3.11/3.12 — vedi `.github/workflows/test.yml`.

## Contribuire

Pull request benvenute. Ogni nuovo `script/*` deve:

1. Stare nella sottocartella appropriata (`quality/`, `security/`, `export/`, `intel/`, `generators/`, `workflow/`, `integrations/`)
2. Avere un'intestazione `#!/usr/bin/env python3` o `#!/usr/bin/env bash` e essere eseguibile
3. Esporre `--help` con descrizione + esempio
4. Degradare con messaggio chiaro se mancano dipendenze opzionali
5. Essere referenziato in `SKILL.md` (tabella tool registry) e nello `steps/*.md` pertinente
6. Avere voce in `CHANGELOG.md`
7. Far passare `pytest` (almeno gli smoke test esistenti)
