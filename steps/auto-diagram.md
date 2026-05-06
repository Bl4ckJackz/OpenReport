# Step — Auto-diagrammi da descrizione testuale

`scripts/auto-diagram.py` converte descrizioni strutturate in Mermaid/PlantUML pronti da incollare nel draft.

## Tipi supportati

| Tipo | Quando usarlo | Engine |
|---|---|---|
| `flowchart` | processi, user journey, business flow | Mermaid + PlantUML |
| `sequence` | interazioni attori (API call, UX flow) | Mermaid |
| `class` | modello dati UML, architettura componenti | Mermaid |
| `state` | ciclo vita documento/entità | Mermaid |
| `gantt` | timeline progetto | Mermaid |

## Workflow Step 5 refinement

1. Se l'utente dice "aggiungi un diagramma che spiega X", chiedi tipo:
   - `AskUserQuestion` con 5 opzioni tipi sopra
2. Genera skeleton:
   ```bash
   python3 scripts/auto-diagram.py --template flowchart > /tmp/diag.txt
   ```
3. Mostra template, chiedi all'utente di riempirlo (nodi, edges, actor, ecc.)
4. Converti:
   ```bash
   python3 scripts/auto-diagram.py /tmp/diag.txt --engine mermaid -o /tmp/diag.md
   ```
5. Inserisci il blocco Mermaid nel draft via Edit

## Esempio completo

Input (`/tmp/arch.txt`):
```
TYPE: class
TITLE: Dominio e-commerce
CLASSES:
  User:
    - id: UUID
    - email: string
    + authenticate(): bool
  Cart:
    - user_id: UUID
    - items: List[Item]
    + addItem(i): void
    + total(): decimal
  Order:
    - cart_id: UUID
    - status: string
    + confirm(): void
RELATIONS:
  User ||--o{ Cart : owns
  Cart ||--|| Order : generates
```

Esecuzione:
```bash
python3 scripts/auto-diagram.py /tmp/arch.txt --engine mermaid
```

Output:
```
`\`\`mermaid
classDiagram
    %% Dominio e-commerce
    class User {
        - id: UUID
        - email: string
        + authenticate(): bool
    }
    class Cart { ... }
    User ||--o{ Cart : owns
    Cart ||--|| Order : generates
`\`\`
```

## Quando usarlo

- Tipologie con `elementi_visivi` che includono `schemi`
- Tesi/ricerca (architetture, modelli dati, metodologia)
- Spec tecnica (C4 diagrams, sequenze API, state machine)
- Business case (organigramma, flow decisionali)
- Runbook (procedure step-by-step visualizzate)

## Red flags

- **Non inventare rami/nodi** mancanti: chiedi all'utente se il flusso ha un ramo che la descrizione non menziona
- **Non forzare complessità**: 30+ nodi in un flowchart è illeggibile, split in sotto-diagrammi
- **Coerenza con il doc**: i nomi nei diagrammi devono matchare quelli nel testo circostante
- **PlantUML fallback**: se Mermaid non supporta un tipo, genera PlantUML equivalente (richiede rendering server-side in Step 7)
