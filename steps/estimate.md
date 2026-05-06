# /relazione-estimate

Stima preventiva di **token, pressione sul context window, e tempo** per generare una relazione, prima di iniziare. Aiuta a decidere:

- Se attivare outline-first (Step 3.6)
- Se pianificare una pausa + `/clear` per liberare context
- Se conviene la modalità `--draft-only`
- Quanto durerà la sessione interattiva

> La skill gira dentro Claude Code: il costo è già incluso nell'abbonamento. Questo strumento riguarda **gestione del context**, non costi monetari.

## Esecuzione

```bash
python scripts/workflow/estimate.py \
    --tipologia tesi \
    --pages 80 \
    --lingua italiano \
    --online --outline-first

# Output JSON per integrazione
python scripts/workflow/estimate.py --pages 50 --json
```

## Argomenti

| Flag | Default | Descrizione |
|---|---|---|
| `--tipologia` | `generica` | Cosmetico (appare nell'header) |
| `--pages` | (richiesto) | Pagine A4 attese |
| `--lingua` | `italiano` | Cosmetico |
| `--online` | off | Conta ricerca online (input +N×150, max +8k) |
| `--mock` | off | Conta tracking mock data |
| `--outline-first` | off | Conta sconto Step 3.6 (~−30% output se pages >= 30) |
| `--json` | off | Output JSON invece che human |

## Output

```
relazione-estimate — tesi · 80 pp · italiano

Token usage (heuristic, ±30%):
  Input:    24,000 tokens
  Output:   63,900 tokens
  Total:    87,900 tokens

Context-window pressure: 44% di 200,000
  -> moderate

Tempo sessione interattiva (Step 1 -> Step 9): 120-240 minuti
  (1.5-3 min/pagina; setup veloce o codebase piccolo accorcia)

Modificatori applicati: ricerca online (+input fino a 8,000).

Raccomandazioni:
  - Attiva --outline-first: per pages >= 60 risparmia ~30% output ...
```

## Verdetti context pressure

| Peak % | Verdetto | Cosa fare |
|---|---|---|
| < 30% | `comfortable` | Procedi normalmente |
| 30–60% | `moderate` | OK, ma prepara checkpoint a Step 5 |
| 60–90% | `tight` | Pausa + `/clear` raccomandata a Step 5 |
| > 90% | `over budget` | Spezza in 2 sessioni o usa `--draft-only` |

## Limiti / disclaimer

- **Stima ±30%**: l'uso reale dipende da quanto refinement chiede l'utente
- **Time**: 1.5–3 min/pagina è una media; setup veloce (<10 file scansionati) accorcia, codebase grandi allungano
- **Context window**: il default 200k è prudente. Sonnet 4.6 in Claude Code supporta finestre più ampie; lo stimatore resta conservativo per evitare sorprese

## Behavior nello skill flow

A Step 1 (dopo che `pages` è risposto), se `pages >= 30`, considera invocare automaticamente questo script in modalità `--json` e mostrare i numeri all'utente come parte della conferma. Specialmente utile prima di Step 3.9 (token budget guard).
