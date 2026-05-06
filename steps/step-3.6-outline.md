# Step 3.6 — Outline-first review (opzionale)

Genera **prima** la struttura della relazione (indice + 1 frase per sezione), la sottoponi all'utente per approvazione/modifica, e **poi** Step 4 espande sezione per sezione partendo dall'outline approvato.

## Quando attivarlo

| Trigger | Comportamento |
|---|---|
| `pages >= 30` | Proponi attivazione con `AskUserQuestion` |
| `pages >= 60` | Attiva di default (utente può rifiutare) |
| `--outline-first` flag esplicito | Forza attivazione |
| `tipologia == "custom"` | Sempre raccomandato |
| Tipologia con struttura libera (`esperienza`, `whitepaper`) | Proponi |

Per documenti < 30 pp il costo del round-trip outline supera il guadagno: salta.

## Vantaggi misurabili

- **−30% token output** sul draft completo (catturi rifusioni strutturali prima di pagare l'espansione)
- **−40% iterazioni Step 5** (problemi di scope catturati a Step 3.6 invece che dopo aver scritto 60 pagine)
- L'utente sente di **co-creare** invece di ricevere

## Procedura

### 1. Generare l'outline

Carica `templates.md` per la tipologia scelta. Genera **solo**:

```markdown
# <Titolo proposto>

## 1. <Sezione obbligatoria 1>
*<Una frase: di cosa parla, ~20 parole>*

## 2. <Sezione obbligatoria 2>
*<Una frase>*

### 2.1 <Sotto-sezione, se richiesta dalla tipologia>
*<Una frase>*

[...]

## N. <Sezione finale (Conclusioni / Bibliografia)>
*<Una frase>*

---

**Stima**: ~<N> pagine totali · <X> sezioni di primo livello · <Y> sotto-sezioni
**Decisioni di scope rilevanti** (proposte):
- <Cosa si include>
- <Cosa si esclude>
- <Profondità di trattazione, es. "stato dell'arte breve, focus su implementazione">
```

Costo tipico: **~2.500 token output** (vs ~40k–80k del draft completo).

### 2. Scrivere l'outline su disco

```
<output_folder>/.session/outline.md
<output_folder>/.session/outline-v1.md   # backup snapshot
```

Aggiorna state:

```json
{
  "current_step": "step-3.6-outline-review",
  "outline": {
    "approved": false,
    "version": 1,
    "path": ".session/outline.md",
    "section_count": 12,
    "subsection_count": 24,
    "generated_at": "2026-05-06T10:30:00Z"
  }
}
```

### 3. Sottoporre all'utente

Presenta il file. Poi `AskUserQuestion`:

```
Ho generato l'outline (12 sezioni, 24 sotto-sezioni). Cosa vuoi fare?

- Approvo, procedi a Step 4 espansione completa
- Voglio modificare alcune sezioni (apri editor)
- Aggiungi/rimuovi sezioni (AskUserQuestion strutturato)
- Cambio scope: ridiscutiamo le risposte Step 1
- Rigenerala con focus diverso (chiedo io)
```

### 4. Iterare se richiesto

- **Modifica manuale**: l'utente edita `.session/outline.md`. Tu fai Read e procedi.
- **Aggiungi/rimuovi**: presenta lista sezioni, multiSelect per rimuovere, prompt per aggiungere.
- **Cambio scope**: salta indietro a Step 1, ri-fai le domande pertinenti, rigenera outline (incrementi `version` e salvi nuovo `outline-v2.md`).
- **Rigenera con focus**: prompt aperto «Cosa vuoi enfatizzare di più?», assorbi, rigenera.

Loop finché l'utente approva.

### 5. Approvazione

Setta `outline.approved: true`, `outline.approved_at: <ISO>`. Procedi a Step 3.9 (token budget guard) — l'outline approvato riduce la stima.

## Behavior in Step 4 (draft)

Quando `outline.approved == true`:

1. Read `.session/outline.md`
2. **Espandi sezione per sezione** rispettando l'outline:
   - Mantieni titoli e numerazione esatti
   - La frase guida diventa la tesi della sezione (1° paragrafo)
   - Lunghezza per sezione = `pages / section_count` (può variare ±50% per sezioni ovviamente più dense)
3. **Non aggiungere sezioni nuove** — se durante l'espansione emerge bisogno di sezione mancante, **fermati** e chiedi all'utente: "Manca una sezione su X. Vuoi aggiungerla all'outline?"
4. **Non rinominare titoli** dell'outline approvato senza chiedere

## Voice profile + outline

Se `voice_profile` esiste già (utente con `.user-profile.json` settato), applicalo già nelle frasi-guida dell'outline. Coerenza voice da subito.

## Backout

Se l'utente a Step 5 si rende conto che l'outline era sbagliato:

```
AskUserQuestion:
- Riscrivi singola sezione (resta nell'outline)
- Modifica outline e ri-espandi (torna a Step 3.6, marca outline come v2)
- Abbandona outline e modalità libera (setta outline.approved=false, perdi guarantee)
```

## Skip

Se l'utente non vuole outline-first ma vuole comunque struttura validata, propone Step 4 modalità `--draft-only` (vedi `steps/token-budget-guard.md` § Modalità --draft-only) che è simile ma più leggero.
