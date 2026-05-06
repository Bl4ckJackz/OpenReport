# Changelog

## 2.4.1 — 2026-05-06

Pulizia: la skill resta 100% gratuita per chi usa Claude Code.

### Modifiche

- **`scripts/workflow/estimate.py`** — riscritto. Rimossi prezzi €/$, modelli specifici, modalità batch. L'output ora è: token (input/output/totale), pressione % sul context window, durata sessione interattiva, raccomandazioni automatiche (outline-first, pausa + `/clear`, `--draft-only`).
- **`steps/estimate.md`** — riallineato senza riferimenti a costi monetari o API a pagamento. Disclaimer esplicito: la skill gira in Claude Code, costo già incluso nell'abbonamento.
- **`docs/PERFORMANCE.md`** — rimosse sezioni "Model routing" e "Batch API". Soften delle menzioni Memory tool / context editing (rilevanti solo per integrazioni SDK avanzate). Focus rimesso su gestione context window, knowledge graph, outline-first, sub-agent policy.
- **`README.md`** — sezione Stima preventiva e Performance riallineate.

### Aggiunte

- **`tests/test_estimate.py`** — 5 smoke test: human output, JSON parse, invariante `input+output==total`, outline-first riduce output per pages ≥ 30, CLI rifiuta input mancante o non positivo.

### Nessuna breaking change

Lo schema `outline` introdotto in 2.4.0 resta. Tutti gli step e i path scripts sono invariati.

## 2.4.0 — 2026-05-06

Stima preventiva + workflow outline-first per documenti lunghi.

### Aggiunte

- **`/relazione-estimate`** — stima preventiva prima di partire. Implementazione: `scripts/workflow/estimate.py`. Documentazione: `steps/estimate.md`. *(Riscritto in 2.4.1 senza riferimenti a costi monetari.)*
- **Step 3.6 — Outline-first review** (opzionale, attivo per pages ≥ 30): genera prima la struttura (~2.5k token), la sottoponi all'utente per approvazione, poi Step 4 espande dall'outline approvato. Vantaggi: −30% token output, −40% iterazioni refinement. Documentazione: `steps/step-3.6-outline.md`.
- **Schema esteso**: `schemas/session-state.schema.json` ha ora il blocco `outline` (`approved`, `version`, `path`, `section_count`, `subsection_count`, `generated_at`, `approved_at`).

### Modifiche

- `SKILL.md` — aggiunto Step 3.6 al flow + `/relazione-estimate` al frontmatter `description` e alla sezione "When to Use".
- `README.md` — sezioni Stima preventiva e Outline-first.

### Note di migrazione

Nessuna breaking change. Sessioni esistenti restano valide; il nuovo campo `outline` è opzionale nello schema.

## 2.3.0 — 2026-05-06

Token efficiency pass + performance playbook.

### Aggiunte

- **`docs/PERFORMANCE.md`** — playbook completo con 10 raccomandazioni quantitative basate sulle linee guida ufficiali Anthropic (skills best practices, prompt caching, Memory tool, context management) e benchmark fine 2025.
- **`steps/red-flags.md`** — lista anti-pattern e regole bloccanti, caricabile on-demand.
- **`steps/step-0-resume.md`** — dettaglio completo del menu di selezione e ripresa, prima inline in SKILL.md.
- **`steps/step-1-questions.md`** — dettaglio completo delle 10–11 domande, opzioni, default per tipologia, regole mock/online.
- **`steps/code-snippets.md`** — regole code snippet handling per Step 4, prima inline.
- **Sezione "Sub-agent delegation policy"** in SKILL.md — quando delegare e quando no, con riferimento al playbook.

### Modifiche

- **`SKILL.md` da ~9.8k a ~7.3k token** (-25%) tramite progressive disclosure:
  - Step 0 (resume check): 70 righe → 12 righe (dettaglio in `steps/step-0-resume.md`)
  - Step 1 (questions): 65 righe → 20 righe (dettaglio in `steps/step-1-questions.md`)
  - Step 4 (code snippet handling): 16 righe → 1 riga (dettaglio in `steps/code-snippets.md`)
  - Red Flags: 30 righe → 3 righe (dettaglio in `steps/red-flags.md`)
- **`README.md`** — sezione Performance con numeri chiave e link al playbook.

### Note di migrazione

Nessuna breaking change. Le sessioni esistenti continuano a funzionare. Step file nuovi vengono caricati on-demand dalla skill quando servono.

## 2.2.0 — 2026-05-06

Riorganizzazione architetturale + onboarding migliorato + test automatici.

### Aggiunte

- **`/relazione-doctor`** — slash command per diagnostica ambiente. Implementazione: `scripts/workflow/doctor.py`. Documentazione: `steps/doctor.md`.
- **`/relazione-setup`** — wizard al primo utilizzo (doctor + brand profile + Eisvogel). Implementazione: `scripts/workflow/setup.py`. Documentazione: `steps/setup.md`.
- **`tests/`** — smoke test pytest:
  - `test_doctor.py` — validazione output doctor (human + JSON)
  - `test_schemas.py` — caricabilità di tutti i JSON Schema
  - `test_scripts_importable.py` — tutti i Python script hanno shebang e parsano senza errori
- **`.github/workflows/test.yml`** — CI su Linux/macOS/Windows × Python 3.10/3.11/3.12.
- **`pytest.ini`** — configurazione test runner.

### Modifiche

- **Riorganizzazione `scripts/`** in 7 sottocartelle tematiche:
  - `quality/` (17 script) — self-check, readability, tone, citations, layout, grammar, spell, plagio, accessibility, fact-check, cross-ref-lint, temporal, clarity, reviewer-simulator, voice-lock
  - `security/` (7 script) — PII redact, secret scan, watermark utente, GPG sign, PDF redact/protect, integrity hash
  - `export/` (14 script) — PDF/DOCX/EPUB/Typst/Quarto/HTML, slides, audiobook, dyslexia variant
  - `intel/` (12 script) — citations, papers (arXiv/Semantic Scholar/Zotero), knowledge graph, schema-to-diagram, glossary
  - `generators/` (12 script) — abstract, TOC, table-from-data, auto-diagram, RACI, RTM, Gantt, KPI, risk register, stakeholder map, defense simulator, bilingual generator
  - `workflow/` (15 script) — state, brand, setup, doctor, auto-save, live-preview, progress, search, tags, audit trail, resolve variables, section regen
  - `integrations/` (8 script, già esistente) — Jira, Linear, Confluence, Notion, SharePoint, Slack, Teams, Git
- **Tutti i riferimenti aggiornati** in `SKILL.md`, `steps/*.md`, `presets/*.yaml`, `pdf-templates/README.md`, `docs/SKILL-GUIDE.md`, scripts che invocano altri scripts.
- **`SKILL.md`** frontmatter esteso: aggiunti `/relazione-doctor` e `/relazione-setup` alla `description`.
- **`README.md`** — sezione Test, sezione Diagnostica, struttura cartelle aggiornata.

### Note di migrazione

- **Path scripts cambiati**: ogni invocazione di `scripts/<X>` deve ora puntare alla sottocartella. Esempi:
  - `scripts/self-check.sh` → `scripts/quality/self-check.sh`
  - `scripts/pii-redact.py` → `scripts/security/pii-redact.py`
  - `scripts/parallel-export.sh` → `scripts/export/parallel-export.sh`
- Sessioni esistenti continuano a funzionare se la skill è aggiornata; preset salvati con path vecchi vanno rigenerati o aggiornati a mano.
- Plugin esterni che chiamavano `scripts/<X>` direttamente: aggiornare il path.

## 2.1.01 — 2026-05-06

Pulizia per pubblicazione open-source su `Bl4ckJackz/OpenReport`.

### Aggiunte

- **`README.md`** pubblico con quickstart, comandi, dipendenze e struttura del repo.
- **`LICENSE`** MIT.
- **`.gitattributes`** per normalizzare line endings (LF) cross-platform.
- **`scripts/workflow/doctor.py`** — diagnostica delle dipendenze (required/recommended/optional). Supporta `--json` per integrazioni CI.
- **`examples/`** — due esempi reali (status report, estratto tesi) come showcase e benchmark visivo.

### Modifiche

- **`SKILL.md`** snellito: rimosse le sezioni "What's new" duplicate (vivono in `CHANGELOG.md`). Risparmio token per invocazione ~15%.
- **Preset rinominati** da `mindsmart-*` a `example-brand-*`: `presets/mindsmart-tecnica.yaml` → `presets/example-brand-tecnica.yaml`, `pdf-templates/eisvogel-mindsmart.yaml` → `pdf-templates/eisvogel-example-brand.yaml`. Aggiornati tutti i riferimenti.
- **`scripts/intel/citation-enrich.py`** — User-Agent generico (`noreply@example.com`) al posto di indirizzo aziendale.

### Note di migrazione

Sessioni con `pdf_template: "../pdf-templates/eisvogel-mindsmart.yaml"` continuano a funzionare se l'utente mantiene il vecchio file localmente. Per allinearsi: aggiornare manualmente `session-state.json` o lanciare `/relazione-continua` e riselezionare il preset.

## 2.0.03 — 2026-05-04

Domanda condizionale per inclusione di code snippet dai sorgenti della cwd.

### Aggiunte

**Step 1 — Initial Questions**
- Pre-flight detection: Glob per file sorgente (`.ts/.tsx/.js/.jsx/.mjs/.cjs/.py/.go/.rs/.dart/.java/.kt/.swift/.rb/.php/.c/.cpp/.cc/.h/.hpp/.scala/.clj/.ex/.exs/.vue/.svelte/.sql/.prisma`) eseguita prima di Batch 5
- Esclude `node_modules`, `.next`, `dist`, `build`, `.git`, `vendor`, `target`, `__pycache__`, `venv`, `.venv`, `coverage`
- Soglia: ≥ 5 file → `cwd_has_source_code = true` → abilita Batch 5
- **Batch 5 (1 domanda condizionale)**: Q11 "Snippet di codice nella relazione" — opzioni `no`, `sì-mirato (4-6)`, `sì-estensivo (10+ + Appendice B firme)`, `solo-appendice`
- Default per tipologia (proposto come "Recommended"):
  - `tecnica`/`codice`/`analisi-codice`/`bug`/`spec-tecnica`/`runbook`/`incident-postmortem` → `sì-estensivo`
  - `progetto`/`tesi`/`ricerca`/`stage`/`finale`/`whitepaper`/`case-study`/`handover` → `sì-mirato`
  - `esperienza`/`laboratorio`/`status-report` → `solo-appendice`
  - `proposta`/`rfp-response`/`sow`/`business-case`/`audit-report`/`compliance-report` → `no`
- Se `cwd_has_source_code = false` → skip silenzioso, `code_snippets: "no"` in `answers`

**Step 4 — Generate Draft**
- Nuova sezione "Code snippet handling" che descrive il comportamento per ogni valore di `answers.code_snippets`:
  - `no` → nessun code block, descrizione solo testuale
  - `sì-mirato` → 4-6 snippet brevi (10-30 righe) nelle sotto-sezioni più rilevanti
  - `sì-estensivo` → 10+ snippet su tutte le sotto-sezioni implementative + Appendice B con firme TS/Python/Dart
  - `solo-appendice` → corpo neutro, Appendice B carica
- Regole comuni:
  - Estrarre solo da file realmente esistenti (Read prima di citare)
  - Specificare path: «L'estratto seguente, dal modulo `<path>`, ...»
  - Mai includere secret/API key/IP esposti
  - Language hint corretto per syntax highlight (`typescript`, `python`, `dart`, `sql`, `rust`, `go`, ecc.)
  - Privilegiare snippet che illustrano una decisione, un pattern non banale, o una formula citata in stato dell'arte

**Schema**
- `schemas/session-state.schema.json`: aggiunta `answers.code_snippets` (enum `no`/`si-mirato`/`si-estensivo`/`solo-appendice`, default `no`)

### Note di migrazione

- Le sessioni con state `skill_version: 2.0.02` o precedenti caricate via `/relazione-continua` continuano a funzionare. Il campo `code_snippets` è opzionale nello schema; se assente è trattato come `"no"`.
- Per sessioni in corso che vogliono attivare i snippet a posteriori: aggiungere manualmente `"code_snippets": "si-mirato"` (o altro valore) in `.session/session-state.json` sotto `answers`, poi richiedere a Claude la rigenerazione delle sezioni interessate.

---

## 2.0.02 — 2026-04-17

Qualità contenuto + ricerca avanzata + quality gates + export estesi + security + collaboration + lingue + AI coach + accessibility premium.

### Aggiunte

**Qualità contenuto**
- `auto-diagram.py` — Mermaid/PlantUML (flowchart/sequence/class/state/gantt) da descrizione testuale
- `table-from-data.py` — CSV/XLSX/JSON → tabelle md/tex con locale-aware formatting
- `abstract-generator.py` — abstract candidato da doc completo, con keywords extraction
- `toc-regen.py` — TOC rigenerato + numerazione heading sequenziale
- `steps/auto-diagram.md` — docs

**Ricerca avanzata**
- `arxiv-import.py` — fetch paper arXiv via API, export bibtex
- `semantic-scholar-import.py` — paper con TL;DR, citation count, open-access PDF
- `link-checker.sh` — verifica URL nel doc ancora raggiungibili, fallback Wayback
- `lit-review-assistant.py` — clusterizzazione tematica paper + proposta capitolo stato dell'arte

**Quality gates**
- `spell-check.sh` — hunspell con dictionary brand/user
- `grammar-check.py` — LanguageTool API (public o self-hosted)
- `citation-style-enforcer.py` — verifica APA/IEEE/Chicago/MLA/Vancouver su .bib
- `latex-sandbox-test.sh` — compile test in sandbox prima della consegna (3-pass + biber)

**Export aggiuntivi**
- `export-typst.sh` — alternativa moderna LaTeX (compile 10x più veloce)
- `export-quarto.sh` — Quarto per data-science (Python/R embedded)
- `export-html-standalone.sh` — HTML self-contained con dark-mode + responsive + print-friendly
- `pdf-protect.py` — password-protect PDF AES 256 + permessi granulari
- `qr-cover.py` — QR code per cover (URL/vCard/testo)
- `integrity-hash.sh` — SHA256 di tutti i deliverable per verifica integrità

**Security/compliance**
- `gpg-sign.sh` — firma GPG detached per authenticity proof
- `user-watermark.py` — watermark user-specific per tracking redistribuzione (batch support)
- `pdf-redact.py` — redaction permanente PII/secret da PDF (via PyMuPDF)

**Collaboration**
- `/relazione-workspace` — workspace multi-sessione (list/switch/create/archive/status/stats)
- `scripts/workflow/tag-manager.py` — tag system per sessioni (add/remove/search/tags)
- `scripts/workflow/full-text-search.sh` — ripgrep/grep full-text sulle sessioni passate
- `/relazione-preset-import` — marketplace preset da URL/gist/path

**Lingue aggiuntive**
- Schema `lingua` esteso: spagnolo, francese, tedesco, portoghese (oltre italiano, inglese, italiano+inglese)
- `forbidden-check.sh` esteso con AI-tells per ES/FR/DE/PT
- `scripts/workflow/locale-format.py` — date/numeri/valute/percentuali per 6 lingue

**AI writing coach**
- `clarity-score.py` — score chiarezza 0-100 per sezione (frasi lunghe, passive, vague, complex)
- `tone-adjust.py` — rileva frasi con tono disallineato al target (formale/semi-formale/tecnico/narrativo)
- `reviewer-simulator.py` — simula feedback reviewer severo (docente/cliente/commissione/peer)

**Accessibility premium**
- `epub3-audio.sh` — EPUB3 con TTS audio per paragrafo
- `audiobook-tts.sh` — MP3 audiobook con chapters (espeak/say/pico2wave → lame/ffmpeg)
- `dyslexia-variant.sh` — variante dyslexia-friendly (OpenDyslexic font, line-height 1.8, fondo crema)

### Modifiche

- `schemas/session-state.schema.json`: `lingua` estesa con spagnolo/francese/tedesco/portoghese
- `scripts/quality/forbidden-check.sh`: 4 nuove lingue per AI-tells

### Nuovi slash commands (+3)

- `/relazione-workspace`
- `/relazione-preset-import`

(Manteniamo `/relazione-brand`, `/relazione-review`, `/relazione-approve`, `/relazione-import-feedback`, `/relazione-ricorrente` da 2.0.01)

### Totale script nuovi in 2.0.02

+26 script (18 .py, 8 .sh) e +2 slash command.

### Retro-compatibilità

- State v2.0.0 e v2.0.01 continuano a funzionare
- Tutti gli script precedenti invariati
- Le nuove lingue sono opt-in

## 2.0.01 — 2026-04-17

Enterprise document production + università extension.

### Aggiunte

**Tipologie enterprise (14 nuove)**
- `proposta`, `rfp-response`, `sow`, `business-case`
- `spec-funzionale`, `spec-tecnica`, `incident-postmortem`
- `status-report`, `whitepaper`, `case-study`
- `handover`, `runbook`, `audit-report`, `compliance-report`

**Profili persistenti**
- `.user-profile.json` — voice stilistico cross-sessione
- `.brand-profile.json` — logo, palette, font, glossario, banned/preferred words, classification default
- Schema JSON validati (`schemas/user-profile.schema.json`, `schemas/brand-profile.schema.json`)

**Document control**
- Cover metadata estesa: `doc_id`, `protocollo`, `versione`, `classificazione` (public/internal/confidential/restricted), `status` (draft/in-review/approved/archived), `approvers[]`, `reviewers[]`, `stakeholders[]`
- Control sheet automatico per tipologie enterprise
- `steps/cover-control.md`

**Precisione (3 nuovi check in self-check.sh)**
- `fact-check.py` — URL/DOI/citazioni del draft verificate vs research-notes
- `cross-ref-lint.py` — \\ref/\\cite/anchor md/figure/tabelle/immagini
- `temporal-check.py` — date conflittuali, range invertiti, mismatch cover

**Prestazioni**
- `research-cache.py` — cache locale URL fetched, hit/miss stats
- `parallel-export.sh` — pdf+docx+epub concurrent
- `section-regen.py` — rigenerazione singola sezione senza riscrivere doc

**Usabilità**
- `live-preview.sh` — server HTML locale con auto-reload
- `progress-tracker.py` — %pagine, placeholder rimanenti, progress bar
- `auto-save.sh` — snapshot ogni N modifiche, retention 10

**Generatori strutturati**
- `raci-matrix.py` · `risk-register.py` · `rtm.py`
- `gantt-from-milestones.py` · `stakeholder-map.py` · `kpi-dashboard.py`

**Citation & accessibility**
- `citation-enrich.py` — CrossRef API per completare .bib
- `plagio-lite.py` — n-gram similarity vs research-notes
- `accessibility-pass.py` — alt-text, heading levels, link text, metadata lang

**Workflow approval**
- `watermark-pdf.py` — DRAFT/REVIEW/APPROVED via pypdf+reportlab o LaTeX fallback
- `audit-trail.py` — JSONL append-only con hash chain verifiabile
- `import-feedback.py` — estrae commenti e track-changes da docx
- Slash commands: `/relazione-review`, `/relazione-approve`, `/relazione-import-feedback`

**Multi-lingua parallelo**
- `bilingual-generator.py` — split-page (IT|EN) o sequential
- `steps/multilingua-parallel.md` — regole glossario, date, numeri, unità

**Integrazioni esterne** (opt-in, credenziali in ~/.claude/.env)
- `integrations/jira-import.py` · `linear-import.py`
- `integrations/confluence-export.py` · `notion-export.py` · `sharepoint-upload.py`
- `integrations/slack-notify.sh` · `teams-notify.sh`
- `integrations/git-activity-extended.sh` (PR/issue via gh CLI)
- `steps/integrations.md`

**Recurring reports**
- `/relazione-ricorrente` setup/run/list/remove
- `diff-summary.py` — variazioni dal periodo precedente

**Università (4 template aggiunti)**
- `universita/unipd-tesi.tex` (Padova)
- `universita/unipi-tesi.tex` (Pisa)
- `universita/unimi-tesi.tex` (Statale Milano)
- `universita/federico2-tesi.tex` (Federico II Napoli)
- `defense-simulator.py` — 20 Q&A simulate per discussione tesi

**Brand management**
- `brand-loader.py` — utility brand profile (list/info/apply-preferred-terms/banned-words/glossario)
- `brand-to-eisvogel.py` — genera YAML eisvogel da brand profile
- `resolve-variables.py` — sostituisce `{{client_name}}`, `{{project_code}}` etc.
- `/relazione-brand` setup wizard
- `steps/brand-profile.md`

### Modifiche

- `forbidden-check.sh` — accetta `--brand <nome>` e `--user-profile` per banned words extension
- `self-check.sh` — integra fact-check, cross-ref-lint, temporal-check. Flag `--research`, `--bib`, `--brand`.
- `session-state.schema.json` — 14 nuove tipologie, cover control estesa, `variables`, `progress`, `audit_trail_ref`, `research_cache_ref`, `integrations`, `recurring`, `lang_parallel`, 2 nuovi step enum (`step-9-approval`, `step-10-delivered`)
- `templates.md` — 14 sezioni nuove (circa +500 righe)

### Retro-compatibilità

- State v2.0.0 continuano a funzionare (nuovi campi opzionali)
- Tipologie esistenti invariate
- Tutti gli script precedenti compatibili

## 2.0.0 — release precedente

Vedi cronologia precedente del file.
