# Token budget guard

Stima i token che la sessione consumerà e avvisa proattivamente per evitare context exhaustion.

## Stima a inizio Step 4 (draft)

Formula heuristic:

```
base_tokens = 5000  # overhead skill + scan
draft_tokens = pages_target * 600  # ~600 token/pagina di draft generato
research_tokens = is_online ? min(pages_target * 200, 15000) : 0
mock_tokens = is_si_mock ? pages_target * 100 : 0
refinement_tokens = pages_target * 300  # iterazioni Step 5

total_estimate = base + draft + research + mock + refinement
```

Esempio target 50 pagine + online + sì-mock:
```
5000 + 30000 + 10000 + 5000 + 15000 = 65000 token
```

Salva in `session-state.json.token_budget.estimated_tokens`.

## Soglie

| Estimate | Azione |
|---|---|
| < 30k | Procedi senza avviso |
| 30k–60k | Mostra stima, chiedi conferma |
| 60k–100k | Forte raccomandazione: usa Step 4.6 two-pass writing + checkpoint frequenti |
| > 100k | BLOCCA, proponi: spezzare in 2 sessioni, abbassare target, modalità `--draft-only` |

## AskUserQuestion al gate

```
"Stima token sessione: ~65k. Con 200k context window ne resta poco per refinement.
Come preferisci procedere?"

- Procedi normalmente (rischio context tight su refinement)
- Attiva two-pass + checkpoint dopo Pass 1 (consigliato)
- Riduci target pagine (chiedo nuovo target)
- Modalità --draft-only (solo scheletro, espandi tu manualmente)
```

## Tracking durante esecuzione

Aggiorna `session-state.json.token_budget.actual_tokens_used` periodicamente.

A 70% del context window usato:
- Salva backup
- Suggerisci `/clear` + `/relazione-continua`
- Setta `current_step` corretto per riprendere

A 90%:
- Forzato checkpoint
- Salva tutto
- Termina con istruzioni per riprendere

## Modalità --draft-only

Genera solo:
- Frontespizio compilato
- TOC completo
- Tutti i titoli/sottotitoli
- 1 paragrafo introduttivo per ogni sezione (non espansione completa)
- `[DA ESPANDERE: <punto bullet>]` come placeholder per il contenuto

Costo: ~1/5 dei token rispetto a draft completo.

Permette validare struttura prima di spendere token sul contenuto.
