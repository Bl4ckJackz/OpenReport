# /relazione-estimate

Stima preventiva di token, costo (USD/EUR), e tempo per generare una relazione, prima di iniziare. Aiuta a decidere:

- Se attivare outline-first (Step 3.6)
- Quale modello usare (Haiku vs Sonnet vs Opus)
- Se vale Batch API (sync vs batch)
- Se conviene ridurre target di pagine

## Esecuzione

```bash
python scripts/workflow/estimate.py \
    --tipologia tesi \
    --pages 80 \
    --lingua italiano \
    --online --outline-first

# Modello specifico (default: confronta tutti)
python scripts/workflow/estimate.py --tipologia tecnica --pages 30 --model sonnet-4.6

# Output JSON per integrazione
python scripts/workflow/estimate.py --pages 50 --json
```

## Argomenti

| Flag | Default | Descrizione |
|---|---|---|
| `--tipologia` | `generica` | Cosmetico (appare nell'header) |
| `--pages` | (richiesto) | Pagine A4 attese |
| `--lingua` | `italiano` | Cosmetico |
| `--model` | `all` | `haiku-4.5`, `sonnet-4.6`, `opus-4.7`, o `all` |
| `--mode` | `all` | `sync`, `batch`, o `all` |
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

Model          Mode         EUR      USD  Time
------------------------------------------------------------
haiku-4.5      sync       0.316    0.344  120–240m
haiku-4.5      batch      0.158    0.172  10m–24h
sonnet-4.6     sync       0.948    1.030  120–240m
sonnet-4.6     batch      0.474    0.515  10m–24h
opus-4.7       sync       4.740    5.152  120–240m
opus-4.7       batch      2.370    2.576  10m–24h

Risparmio max scegliendo haiku-4.5 batch: €4.582
```

## Limiti / disclaimer

- **Stima ±30%**: l'uso reale dipende da quanto refinement chiede l'utente
- **Tasso EUR/USD** è hardcoded a 0.92 — aggiorna `USD_TO_EUR` nello script per cambi importanti
- **Pricing**: i numeri sono list price Anthropic gennaio 2026. Verifica su [anthropic.com/pricing](https://www.anthropic.com/pricing) prima di pianificare bulk
- **Time sync**: 1.5–3 min/pagina è una media generosa; setup veloce (<10 file scansionati) accorcia, codebase grandi allungano
- **Time batch**: target Anthropic <1h, ma SLA contrattuale 24h

## Behavior nello skill flow

A Step 1 (dopo che `pages` è risposto), se `pages >= 30`, considera invocare automaticamente questo script in modalità `--json` e mostrare costo/tempo all'utente come parte della conferma. Specialmente utile prima di Step 3.9 (token budget guard).
