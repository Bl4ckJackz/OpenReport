# Changelog

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
- `scripts/tag-manager.py` — tag system per sessioni (add/remove/search/tags)
- `scripts/full-text-search.sh` — ripgrep/grep full-text sulle sessioni passate
- `/relazione-preset-import` — marketplace preset da URL/gist/path

**Lingue aggiuntive**
- Schema `lingua` esteso: spagnolo, francese, tedesco, portoghese (oltre italiano, inglese, italiano+inglese)
- `forbidden-check.sh` esteso con AI-tells per ES/FR/DE/PT
- `scripts/locale-format.py` — date/numeri/valute/percentuali per 6 lingue

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
- `scripts/forbidden-check.sh`: 4 nuove lingue per AI-tells

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
