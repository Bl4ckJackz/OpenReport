# Performance & Token Efficiency Playbook

Linee guida per chi modifica la skill e per chi la usa in sessioni lunghe (tesi, whitepaper, relazioni complesse) dove il context window può diventare il collo di bottiglia.

> La skill è pensata per girare dentro **Claude Code** — non richiede API a pagamento. Le ottimizzazioni qui sono di **gestione context** e di **architettura della skill**, non di billing.

## Obiettivi misurabili

| Metrica | Stato attuale | Target |
|---|---|---|
| `SKILL.md` body (righe) | ~556 | < 600 (consigliato 500) |
| `SKILL.md` token caricati per turno | ~7.5k | < 8k |
| Re-read di file sorgente in Step 4+ | tendenzialmente 0 (KG) | 0 |
| Pressione context per relazione media (15-40 pp) | 30–50% | sotto 60% |
| Pressione context per documento lungo (60+ pp) | rischio 70%+ | sotto 70% via outline-first |

## 1. Mantieni `SKILL.md` corto (alta priorità)

- Body sotto 600 righe — meglio 500. Tutto il resto va in `steps/*.md` caricati on-demand via Read.
- Ogni riga di `SKILL.md` è un costo ricorrente per turno.
- **Verifica**: `wc -l SKILL.md` prima di ogni release. Se cresce, sposta dettaglio in step file.

## 2. Progressive disclosure dei dettagli

Pattern adottato dalla skill:

- `SKILL.md` contiene **router e regole base**
- `steps/*.md` contengono **istruzioni dettagliate** caricate solo quando lo step pertinente è raggiunto
- `templates.md` è caricato solo quando la tipologia è scelta
- `presets/*.yaml` sono caricati solo se richiamati esplicitamente

## 3. Knowledge graph come single source of truth (alta priorità)

Step 2.6 costruisce `.session/knowledge/`. Da Step 4 in poi, **mai re-read di file sorgente** se il dato è recuperabile da `query.py`. Riduzione tipica: 60–80% dei token di re-read.

Auditare periodicamente che gli step successivi non bypassino il KG con Read diretti.

## 4. Outline-first per documenti ≥ 30 pp (alta priorità)

Step 3.6 genera prima la struttura (~2.5k token), la sottoponi all'utente, poi Step 4 espande sezione per sezione. Cattura problemi di scope **prima** di scrivere 60 pagine inutili.

Risparmio osservato: **−30% token output** + **−40% iterazioni Step 5**. Vedi `steps/step-3.6-outline.md`.

## 5. Sub-agent — quando sì, quando no

| Situazione | Delega | Motivo |
|---|---|---|
| Self-check completo (output 5k+ righe) | **Sì** | tieni il rumore fuori dal main context |
| Export PDF + DOCX + EPUB + LaTeX | **Sì** (parallelo) | 4 esportazioni indipendenti |
| Step 2 deep scan (4 facet) | **Sì** | già implementato in `steps/step-2-parallel.md` |
| Resolve `{{var}}` da file vars | **No** | costo > startup |
| Read di un singolo step file | **No** | usa il Read tool diretto |
| Lookup classificazione tipologia | **No** | regex inline |

Costo subagent fisso: ~20k token di startup. Soglia di break-even: l'output del subagent risparmia almeno 25k token al main context, OPPURE è una parallelizzazione genuina (4+ task indipendenti).

## 6. Sessioni cross-reset (`.session/session-state.json`)

Lo state machine permette `Pausa + /clear`. Sfruttalo:

- A Step 3.9 (token budget guard), se la stima è alta → pausa e riprendi
- A Step 5 (refinement) tra cicli su documenti lunghi
- A Step 7 prima dell'export pesante

L'utente fa `/clear`, riapre la skill, l'auto-resume rilegge il file (1.5k token) invece di tenere 60k in context attivo.

## 7. `/relazione-estimate` per pianificare

Prima di lanciare un documento lungo, esegui `python scripts/workflow/estimate.py --pages N` per vedere:

- Token attesi (input/output/totale)
- Pressione percentuale sul context window
- Raccomandazioni automatiche (attiva outline-first, pianifica pausa, considera `--draft-only`)

## 8. Audit `SKILL.md` per prosa duplicata da scripts

Il codice in `scripts/` esegue via Bash e consuma **zero token di context**. Ogni riga di SKILL.md che descrive cosa fa uno script è duplicazione costosa. Periodicamente:

```bash
grep -E "fa X|esegue|orchestratore che lancia" SKILL.md
```

Se la riga descrive comportamento di uno script, sostituiscila con un puntatore breve.

## 9. Embeddings — non aggiornare se non serve

Hash-128 attuale (in `scripts/intel/knowledge-graph.py`): zero dipendenze, recall sufficiente per la maggior parte dei casi.

**Aggiorna solo se** il KG produce miss frequenti su sezioni semanticamente vicine.

## 10. Modalità `--draft-only`

Per documenti molto lunghi (80+ pp) dove il context è quasi pieno solo a leggere il template + scan, considera la modalità `--draft-only` (vedi `steps/token-budget-guard.md`):

- Genera frontespizio compilato
- TOC completo
- Tutti i titoli/sottotitoli
- 1 paragrafo introduttivo per sezione
- `[DA ESPANDERE: <bullet>]` come placeholder

Costo ~1/5 del draft completo. L'utente espande sezione per sezione in sessioni successive (auto-resume).

## Quick-win order per maintainer

1. Mantieni `SKILL.md` < 600 righe (verifica ad ogni PR)
2. Aggiungi prosa nuova in `steps/*.md`, non in `SKILL.md`
3. Quando aggiungi uno script, NON descrivere cosa fa in `SKILL.md` — lascia il pointer
4. Periodicamente esegui `grep -c "scripts/" SKILL.md` e verifica che ogni riferimento sia un puntatore, non una spiegazione
5. Se aggiungi una fase che produce output verboso (lint, scan), pensa subito se può girare in subagent
