# Performance & Token Efficiency Playbook

Linee guida per chi modifica la skill e per chi la usa in ambienti dove i token contano (sessioni lunghe, batch su molte relazioni, integrazioni CI). Aggiornato al gennaio 2026.

> Le raccomandazioni sono basate sulla documentazione ufficiale Anthropic ([Skills best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool), [context management](https://www.anthropic.com/news/context-management)) e benchmark comunitari di fine 2025.

## Obiettivi misurabili

| Metrica | Stato attuale | Target |
|---|---|---|
| `SKILL.md` body (righe) | ~530 | < 500 (consigliato 300) |
| `SKILL.md` token caricati per turno | ~7.3k | < 6k |
| Cache hit rate atteso (multi-turn ≥ 5 min) | n/a | > 80% |
| Token per relazione media (15-40 pp) | ~80–120k | -30% via caching + memoria |
| Tempo medio Step 4 (draft) | n/a | -20% via Sonnet 4.6 1M ctx |

## 1. Mantieni `SKILL.md` corto (alta priorità)

- Body sotto 500 righe — meglio 300. Tutto il resto va in `steps/*.md` caricati on-demand via Read.
- Anthropic carica SKILL.md per intero ogni turno dopo l'attivazione: ogni riga è un costo ricorrente.
- **Verifica**: `wc -l SKILL.md` prima di ogni release. Se cresce, sposta dettaglio in step file.

## 2. Sfrutta prompt caching (alta priorità, runtime)

La skill è caricata da Claude Code. L'utente può sfruttare cache quando il client supporta `cache_control` con `extended-cache-ttl-2025-04-11` (1h TTL):

- **Cache breakpoints suggeriti**: fine sistema, fine SKILL.md, fine `steps/*` caricato, fine `session-state.json` snapshot.
- **TTL**: per sessioni `relazione` che durano > 5 min (draft → self-check → export → approve), 1h TTL conviene quasi sempre.
- **Costi**: lettura cache = 0.1× input price; scrittura 1h = 2× input price. Soglia di break-even: 2 letture in 1h.
- **Verifica**: monitora `usage.cache_read_input_tokens` nei log API.

Per chi usa la skill via SDK, vedi [esempi prompt caching](https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools).

## 3. Memory tool come opzione (media priorità)

Il knowledge graph hash-128 in `scripts/intel/knowledge-graph.py` è una soluzione locale e portabile. Per chi gira la skill come Claude Agent SDK, considerare il [Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) ufficiale + [context editing](https://www.anthropic.com/news/context-management):

- **Quando usarlo**: sessione che attraversa più giorni, multi-relazione su stesso codebase, team che condivide stato semantico.
- **Quando NON usarlo**: utilizzo locale con Claude Code (il KG hash funziona già + zero dipendenze).
- **Pattern raccomandato**: hash-128 come L1 cache (zero costo, recall-prima), Memory tool come L2 (semantica, persistente).

## 4. Routing modelli per fase (alta priorità per chi usa via API)

| Fase | Modello consigliato | Perché |
|---|---|---|
| Step 4.5 self-check, forbidden terms, PII | **Haiku 4.5** | task fattuali e regex-like, costo $0.50/$2.50 batch |
| Step 4 draft, Step 5 follow-up | **Sonnet 4.6** | 1M context GA, qualità alta a costo medio |
| Step 5 cross-ref reasoning su thesis 80+ pp, defense-simulator | **Opus 4.7** | reasoning profondo |

L'utente che gira la skill via Claude Code lascia il routing a Claude. L'utente che la integra via SDK può forzare il modello per fase.

## 5. Batch API per export non interattivi (media priorità)

L'export finale (Step 7) e i companion artifact (Step 8) sono non interattivi e candidati ideali per la [Message Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing): -50% input + output, beta `output-300k-2026-03-24` per output lunghi.

Implementazione futura: `/relazione-batch` per generare in coda overnight su corpus di relazioni ricorrenti.

## 6. Sub-agent — quando sì, quando no

| Situazione | Delega | Motivo |
|---|---|---|
| Self-check completo (output 5k+ righe) | **Sì** | tieni il rumore fuori dal main context |
| Export PDF + DOCX + EPUB + LaTeX | **Sì** (parallelo) | 4 esportazioni indipendenti |
| Step 2 deep scan (4 facet) | **Sì** | già implementato |
| Resolve `{{var}}` da file vars | **No** | costo > startup |
| Read di un singolo step file | **No** | usa il Read tool diretto |
| Lookup classificazione tipologia | **No** | regex inline |

Costo subagent fisso: ~20k token. Soglia di break-even: l'output del subagent risparmia almeno 25k token al main context, OPPURE è una parallelizzazione genuina (4+ task indipendenti).

## 7. Embeddings — non aggiornare se non serve

Hash-128 attuale: zero dipendenze, ~84% recall a top-5 sui benchmark interni della skill. Sufficiente per la maggior parte dei casi.

**Aggiorna solo se** il KG produce miss frequenti su sezioni semanticamente vicine. In tal caso:

- **BGE-small-en-v1.5** (~30 MB, 384-dim, MTEB 64): default moderno
- **e5-small-instruct**: top-5 100% in benchmark prodotto 2025
- ⚠ Evita MiniLM-L6 (datato, MTEB 56)

## 8. Audit `SKILL.md` per prosa duplicata da scripts

Anthropic best practice: il codice in `scripts/` esegue via Bash e consuma **zero token di context**. Ogni riga di SKILL.md che descrive cosa fa uno script è duplicazione costosa. Periodicamente:

```bash
grep -E "fa X|esegue|orchestratore che lancia" SKILL.md
```

Se la riga descrive comportamento di uno script, sostituiscila con un puntatore breve.

## 9. Knowledge graph come single source of truth

Step 2.6 costruisce `.session/knowledge/`. Da Step 4 in poi, **mai re-read di file sorgente** se il dato è recuperabile da `query.py`. Riduzione tipica: 60–80% sui token di re-read.

Auditare periodicamente che gli step successivi non bypassino il KG con Read diretti.

## 10. Sessioni cross-reset (`.session/session-state.json`)

Lo state machine permette `Pausa + /clear`. Sfruttalo:

- A Step 3.9 (token budget guard), se stima > 60k → forza pausa
- A Step 5 (refinement) tra cicli
- A Step 7 prima dell'export pesante

L'utente fa `/clear`, riapre la skill, auto-resume rilegge il file (1.5k token) invece di tenere 60k in context attivo.

## Riferimenti

- [Anthropic Skills — best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Equipping agents with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)
- [Context management](https://www.anthropic.com/news/context-management)
- [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview)
- [Choosing the right Claude model](https://claude.com/resources/tutorials/choosing-the-right-claude-model)
- [Manage costs — Claude Code](https://code.claude.com/docs/en/costs)

## Quick-win order per maintainer

1. Mantieni `SKILL.md` < 500 righe (verifica ad ogni PR)
2. Aggiungi prosa nuova in `steps/*.md`, non in `SKILL.md`
3. Quando aggiungi uno script, NON descrivere cosa fa in `SKILL.md` — lascia il pointer
4. Periodicamente esegui `grep -c "scripts/" SKILL.md` e verifica che ogni riferimento sia un puntatore, non una spiegazione
5. Se aggiungi una fase nuova, considera prima di tutto se può girare in subagent (output verboso) o in batch (non interattiva)
