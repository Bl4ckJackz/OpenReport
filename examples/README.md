# Examples

Esempi di output reale prodotto dalla skill, anonimizzati. Servono come:

- **Showcase** — vedere il livello di qualità prima di installare
- **Benchmark visivo** — regressioni di stile/layout sono evidenti rispetto a un baseline
- **Onboarding** — un nuovo utente capisce in 30 secondi cosa aspettarsi

## Indice

| File | Tipologia | Lingua | Pagine | Note |
|---|---|---|---|---|
| [`status-report-weekly.md`](./status-report-weekly.md) | enterprise / status-report | IT | 3 | Diff dal periodo precedente, KPI table |
| [`tesi-magistrale-excerpt.md`](./tesi-magistrale-excerpt.md) | accademica / tesi | IT | 5 (estratto) | Frontespizio + abstract + capitolo 1 |

## Generare i propri esempi

Da una cartella di lavoro:

```bash
/relazione-quick
# oppure
/relazione --profile=status-report-weekly
```

Per condividere un esempio anonimizzato:

```bash
python scripts/security/pii-redact.py RELAZIONE.md > examples/mio-esempio.md
```
