---
description: Mostra l'indice completo dei comandi /relazione-* con descrizione breve e quando usarli
---

# /relazione-help — Indice famiglia comandi

Stampa la tabella sotto. **Non leggere file, non lanciare comandi**: questo è un aiuto di navigazione.

## Comandi principali (workflow)

| Comando | Quando usarlo |
|---|---|
| `/relazione` | Avvio nuova relazione — 9 domande, scan cwd, draft, refine, export |
| `/relazione-quick [--profile=<nome>] [--tipologia=<x>]` | Skip domande, default smart dal nome cartella o preset |
| `/relazione-continua [--fresh]` | Riprendi sessione in pausa (auto-detect `relazioni*/`) |
| `/relazione-rollback [--last]` | Ripristina backup pre-modifica |
| `/relazione-diff [<f1> <f2>]` | Diff tra due iterazioni o tra corrente e ultimo backup |
| `/relazione-redline` | `~/.claude/commands/relazione-redline.md` | Mostra modifiche vs baseline in live preview + abilita track-changes negli export |
| `/relazione-stats [--current|--all]` | Dashboard sessioni + verifica dipendenze (pandoc, xelatex, biber, …) |

## Configurazione

| Comando | Quando usarlo |
|---|---|
| `/relazione-brand [list\|add\|edit\|activate\|show]` | Brand profile aziendale (logo, palette, font, banned/preferred words) |
| `/relazione-profile [show\|edit\|reset]` | User profile (voice, stile, preferenze output, banned/preferred personali) |
| `/relazione-preset-import <url\|gist\|path>` | Importa preset YAML da fonte esterna |
| `/relazione-preset-export <nome> [--public\|--private\|--stdout]` | Esporta preset locale come gist o stdout |

## Review & approvazione

| Comando | Quando usarlo |
|---|---|
| `/relazione-review --reviewers "Nome, Ruolo; …"` | Cambia `cover.status` a `in-review`, watermark, audit trail |
| `/relazione-approve --approver "Nome, Ruolo"` | Promuove `state.status` da `ready-for-approval` ad `approved` → archivio |
| `/relazione-import-feedback <feedback.docx>` | Applica commenti/track-changes docx una per una |

## Collaborazione & ricorrenza

| Comando | Quando usarlo |
|---|---|
| `/relazione-condividi [<cartella>]` | Comprime sessione (zip/tar.gz) e apre file manager per share |
| `/relazione-workspace [list\|create\|switch\|status\|archive\|stats] [nome]` | Multi-sessione raggruppate in workspace |
| `/relazione-ricorrente <setup\|run\|list\|remove> [nome]` | Report ricorrenti (weekly/monthly) con diff da periodo precedente |

## Companion grafico

| Comando | Quando usarlo |
|---|---|
| `/relazione-visual` | Hub HTML: gallery LAYOUTS, dashboard sessione, live preview, flowchart workflow |
| `/relazione-help --gallery` | Shortcut per `/relazione-visual layouts` |
| `/relazione-help --flow` | Shortcut per `/relazione-visual flow` |
| `/relazione-help --dashboard` | Shortcut per `/relazione-visual dashboard` |
| `/relazione-stats --html` | Shortcut per dashboard sessione corrente |

Se `$ARGUMENTS` contiene `--gallery`/`--flow`/`--dashboard`, NON stampare la tabella di indice — invece esegui:
```bash
# --gallery
python3 ~/.claude/skills/relazione/scripts/render-layouts-gallery.py --open
# --flow
python3 ~/.claude/skills/relazione/scripts/render-flowchart.py --open
# --dashboard
python3 ~/.claude/skills/relazione/scripts/render-stats-dashboard.py --open
```

## Approfondimenti

- Documentazione completa: `~/.claude/skills/relazione/SKILL.md` + `~/.claude/skills/relazione/docs/SKILL-GUIDE.md`
- Schemi layout visivi: `~/.claude/skills/relazione/LAYOUTS.md` (e gallery HTML con `/relazione-visual layouts`)
- Changelog: `~/.claude/skills/relazione/CHANGELOG.md`
- Preset disponibili: `~/.claude/skills/relazione/presets/*.yaml` (20+)
- Template LaTeX università: `~/.claude/skills/relazione/pdf-templates/universita/*.tex` (10 atenei)
