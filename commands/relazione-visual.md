---
description: Hub visuale per /relazione — apre nel browser gallery LAYOUTS, dashboard sessione, live preview del draft, flowchart del workflow
argument-hint: "[layouts|dashboard|live|flow|all]"
---

# /relazione-visual — Companion grafico

Genera artefatti HTML/SVG e li apre nel browser. Utile per:
- **Onboarding**: capire il workflow con un flowchart cliccabile
- **Selezione layout**: confrontare i 6 schemi prima di avviare `/relazione`
- **Monitoraggio sessione**: dashboard con progress ring, sezioni, metriche
- **Live editing**: vedere il documento auto-aggiornato mentre Step 4 riempie lo skeleton

## Sub-comandi

| Sub-comando | Cosa fa |
|---|---|
| `layouts` | Genera e apre `layouts-gallery.html` — i 6 schemi LAYOUTS come box visivi navigabili |
| `dashboard` | Trova la sessione attiva e genera `dashboard.html` — progress ring SVG, lista sezioni, metriche, quick actions |
| `live` | Avvia server HTTP locale (porta 8766) con live-preview del draft + badge per sezione + auto-open. **Loop bloccante** (Ctrl+C per uscire) |
| `flow` | Genera e apre `workflow.html` — il flowchart del workflow `/relazione` (Mermaid in-browser, con fallback graphviz se installato) |
| `all` *(default)* | Genera tutti gli artefatti e apre un `index.html` con 4 card linkate |

## Esecuzione

### `layouts`

```bash
python3 ~/.claude/skills/relazione/scripts/render-layouts-gallery.py --open
```

Output: `~/.claude/skills/relazione/.cache/layouts-gallery.html`

Mostra i 6 layout (ACCADEMICO, AZIENDALE, TECNICO, POSTMORTEM, NARRATIVO, STATUS) con:
- Tabs in alto per navigare tra categorie
- Box visivi per ogni sezione (REQUIRED in colore primario, OPTIONAL grigio tratteggiato)
- Regole bloccanti, scaling per pagine, varianti per tipologia (pieghevoli)
- Hover su sezione → mostra descrizione del ruolo (se presente nello schema)

### `dashboard`

```bash
python3 ~/.claude/skills/relazione/scripts/render-stats-dashboard.py --open
```

Default: trova la sessione più recente in cwd (incluso `relazioni-workspaces/*/*/` e `relazioni-ricorrenti/*/*/`).

Per una sessione specifica:
```bash
python3 ~/.claude/skills/relazione/scripts/render-stats-dashboard.py --session relazioni-2026-04-16/ --open
```

Output: `<session>/.session/dashboard.html`

Mostra:
- Anello SVG progress (sezioni done / totali nello skeleton)
- Lista sezioni con icone (✓ done · ⟳ writing · ☐ pending)
- Metriche: parole, pagine stimate, [MOCK], [DA RIEMPIRE]
- Bar token budget con soglie colorate
- Quick actions: apri sorgente, apri PDF/DOCX, copia comando resume
- Tabella dipendenze sistema (pandoc, xelatex, biber, dot, python3)

### `live`

```bash
bash ~/.claude/skills/relazione/scripts/live-preview-draft.sh <session-folder>
```

Esempio: `bash scripts/live-preview-draft.sh ./relazioni/`

Comportamento:
- Avvia http.server su porta 8766
- Pre-elabora il draft `.md` per iniettare badge `[done|writing|pending]` per ogni `<!-- SECTION: ... -->`
- Genera HTML via pandoc con CSS che evidenzia `[DA RIEMPIRE]` (rosso) e `[MOCK]` (arancio)
- Auto-apre il browser (cross-OS via `_browser-open.sh`)
- Polling 2s sul file draft, re-render automatico ad ogni save
- **Loop bloccante** — Ctrl+C per fermare

**NB:** se `/relazione` Step 4 sta girando in un'altra shell Claude Code, la live preview si aggiorna mentre Claude scrive. Tipico setup: Claude in shell #1, `/relazione-visual live` in shell #2.

### `flow`

```bash
python3 ~/.claude/skills/relazione/scripts/render-flowchart.py --open
```

Default: estrae il blocco `dot` da `SKILL.md`, converte a Mermaid, renderizza in-browser (CDN jsdelivr).

Per fallback offline con graphviz:
```bash
python3 scripts/render-flowchart.py --prefer=dot --open
```

Se `dot` è installato (`choco install graphviz` su Windows, `brew install graphviz` su Mac), pre-renderizza `workflow.svg` e usa quello (fully offline).

Output: `~/.claude/skills/relazione/.cache/workflow.html` (+ `workflow.svg` con `--prefer=dot`).

### `all` (default)

Genera **tutti** gli artefatti in parallelo, poi apre un index page con 4 card linkate:

```bash
# Bash sequenziale (più sicuro che parallelo)
python3 ~/.claude/skills/relazione/scripts/render-layouts-gallery.py
python3 ~/.claude/skills/relazione/scripts/render-flowchart.py
python3 ~/.claude/skills/relazione/scripts/render-stats-dashboard.py 2>/dev/null || true
# Index page
cat > ~/.claude/skills/relazione/.cache/index.html <<'EOF'
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>/relazione — Visual hub</title>
<style>body{font-family:-apple-system,Inter,sans-serif;max-width:900px;margin:2em auto;padding:0 1em}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;margin-top:32px}
.card{padding:24px;border:1px solid #ddd;border-radius:12px;text-decoration:none;color:inherit;transition:transform .15s}
.card:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(0,0,0,.08);border-color:#1D3557}
.card h2{margin:0 0 8px;font-size:1.2em;color:#1D3557}
.card p{margin:0;color:#666;font-size:.9em}</style></head>
<body>
<h1>/relazione — Companion grafico</h1>
<p style="color:#666">Hub centrale degli artefatti visuali della skill.</p>
<div class="grid">
  <a class="card" href="layouts-gallery.html"><h2>📐 Gallery LAYOUTS</h2><p>I 6 schemi visivi per categoria di relazione, navigabili con tab.</p></a>
  <a class="card" href="workflow.html"><h2>🔀 Workflow flowchart</h2><p>Il diagramma di flusso della skill, da SKILL.md.</p></a>
  <a class="card" href="../../..">📊 Dashboard sessione<br><small style="color:#999">(in <code>&lt;sessione&gt;/.session/dashboard.html</code>)</small></a>
  <a class="card" href="#"><h2>👁 Live preview</h2><p>Da terminale: <code>/relazione-visual live</code></p></a>
</div>
</body></html>
EOF
bash ~/.claude/skills/relazione/scripts/_browser-open.sh ~/.claude/skills/relazione/.cache/index.html
```

## Cosa fare in base all'argomento

Parse `$ARGUMENTS`. Se vuoto o `all` → esegui il flow "all". Altrimenti esegui il sub-comando indicato.

Se l'utente passa un sub-comando non riconosciuto, mostra questa guida.

## Red flags

- **Sub-comando `live` è bloccante** — non avviarlo nella stessa shell di `/relazione`, useresti due loop concorrenti. Usa shell separata.
- **Mermaid richiede internet la prima volta** — se l'utente è offline, suggerisci `--prefer=dot` con graphviz installato.
- **`dashboard` richiede una sessione attiva** — se non trova `relazioni*/.session/session-state.json`, genera una pagina "nessuna sessione" invece di crashare.
- **`.cache/` non andrebbe versionato** — assicurati che sia in `.gitignore` se la skill è in un repo git.
- **Cross-OS**: lo script `_browser-open.sh` gestisce Windows/Mac/Linux/WSL — non chiamare `xdg-open`/`open`/`start` direttamente.

## Dipendenze

| Tool | Quando serve | Fallback se manca |
|---|---|---|
| `python3` | Sempre | Nessuno — bloccante |
| `pandoc` | Solo `live` | Errore con istruzione install |
| `bash` | Per `_browser-open.sh` | Su PowerShell, l'apertura del browser va fatta manualmente |
| `dot` (graphviz) | Solo con `flow --prefer=dot` | Fallback a Mermaid CDN |
| Internet | Solo Mermaid CDN al primo caricamento (poi cache browser) | `--prefer=dot` per offline puro |
