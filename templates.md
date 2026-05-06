# Templates per ogni tipologia

Struttura dettagliata, domande di follow-up, e note di tono per ciascuna tipologia. Usa la sezione corrispondente alla scelta dell'utente.

---

## tecnica — Relazione tecnica di progetto

**Scope:** descrizione tecnica di un prodotto / sistema / modulo realizzato.

**Sezioni obbligatorie:**
1. Frontespizio (titolo, autore, data, destinatario)
2. Indice
3. Abstract / Sommario esecutivo (1 pagina)
4. Introduzione e obiettivi
5. Contesto e requisiti
6. Architettura del sistema
7. Tecnologie utilizzate (stack, versioni, motivazione scelta)
8. Implementazione (moduli, flussi principali, estratti di codice)
9. Testing e validazione
10. Risultati
11. Limitazioni e sviluppi futuri
12. Conclusioni
13. Bibliografia / Riferimenti
14. Appendici (opzionale)

**Follow-up questions:**
- Qual è il pubblico tecnico di riferimento (sviluppatori, decision maker, entrambi)?
- Vuoi diagrammi ASCII / mermaid nel markdown?
- Servono metriche di performance, se sì quali?
- Includiamo una sezione sicurezza?

**Tono:** tecnico, terza persona ("il sistema", "l'applicazione"), presente o passato remoto.

---

## laboratorio — Relazione di laboratorio

**Scope:** esperimento scientifico / tecnico svolto in laboratorio.

**Sezioni obbligatorie:**
1. Titolo dell'esperienza
2. Data, luogo, partecipanti
3. Scopo dell'esperienza
4. Cenni teorici
5. Materiali e strumenti utilizzati
6. Procedimento
7. Dati raccolti (tabelle)
8. Elaborazione dati e calcoli
9. Grafici (descrizione testuale se non inseribili direttamente)
10. Analisi degli errori
11. Conclusioni
12. Bibliografia (se citati testi)

**Follow-up questions:**
- Hai dati numerici da inserire? In che formato?
- Qual era l'ipotesi iniziale?
- Ci sono state anomalie / errori sistematici?
- Serve calcolo dell'incertezza?

**Tono:** impersonale, passato prossimo o remoto ("è stato misurato", "si è osservato").

---

## stage — Relazione di stage / tirocinio

**Scope:** esperienza di stage curricolare o tirocinio professionalizzante.

**Sezioni obbligatorie:**
1. Frontespizio (studente, matricola, corso, tutor aziendale, tutor universitario, periodo)
2. Indice
3. Introduzione
4. Presentazione dell'azienda ospitante (storia, settore, prodotti/servizi, organizzazione)
5. Il reparto / team in cui si è svolto lo stage
6. Obiettivi formativi dello stage
7. Attività svolte (cronologia settimanale o per progetti)
8. Strumenti e tecnologie apprese
9. Progetti principali cui si è partecipato
10. Competenze acquisite (tecniche, trasversali)
11. Difficoltà incontrate e come sono state superate
12. Valutazione personale dell'esperienza
13. Conclusioni
14. Allegati (questionario tutor, certificato, ecc.)

**Follow-up questions:**
- Nome e sede dell'azienda?
- Periodo dello stage (da / a)?
- Chi erano i tutor (nome)?
- Monte ore totale?
- Progetti specifici cui hai lavorato?
- Software / linguaggi / tool nuovi appresi?

**Tono:** formale, prima persona ("ho svolto", "ho appreso") ma misurata.

---

## progetto — Relazione di progetto

**Scope:** progetto scolastico, universitario, lavorativo. La lunghezza è scelta dall'utente (vedi domanda 5 di SKILL.md): scala il dettaglio di ogni sezione al target richiesto. Target tipici: 30-50 pagine per progetti scolastici, 50-80 per universitari, 80-120+ per progetti aziendali complessi o tesi di progetto.

**Sezioni obbligatorie (tutte presenti; quanto espanderle dipende dal target di pagine):**

1. **Frontespizio** (titolo completo, autori, data, istituzione, destinatario, versione)
2. **Indice generale** (con numeri di pagina)
3. **Indice delle figure**
4. **Indice delle tabelle**
5. **Abstract / Sommario esecutivo** (2-3 pagine)
6. **Introduzione**
   - 6.1 Contesto del progetto
   - 6.2 Motivazioni
   - 6.3 Obiettivi generali e specifici
   - 6.4 Struttura della relazione
7. **Analisi dello stato dell'arte / mercato / tecnologie esistenti** (5-8 pagine — confronto con soluzioni esistenti)
8. **Analisi dei requisiti**
   - 8.1 Requisiti funzionali
   - 8.2 Requisiti non funzionali
   - 8.3 Vincoli
   - 8.4 Casi d'uso (almeno 5 dettagliati)
   - 8.5 Diagrammi UML / ER (descritti testualmente se non inseribili)
9. **Progettazione**
   - 9.1 Architettura generale
   - 9.2 Scelte tecnologiche e motivazione (confronto tra alternative considerate e scartate, con pro/contro)
   - 9.3 Design dei moduli
   - 9.4 Modello dati
   - 9.5 Mockup / wireframe (descritti)
10. **Esperienze con fornitori / servizi / librerie** (DEDICA 5-10 PAGINE)
    - 10.1 Fornitori valutati e scelti (hosting, API, SaaS) con motivazione
    - 10.2 Librerie / framework principali: versioni, perché scelti, alternative, problemi riscontrati
    - 10.3 Strumenti di sviluppo e collaborazione (IDE, versioning, CI/CD, issue tracker)
    - 10.4 Contatti / documentazione / supporto ricevuto
11. **Implementazione** (SEZIONE CENTRALE — 15-25 pagine)
    - 11.1 Struttura del codice e organizzazione dei file
    - 11.2 Moduli principali, ciascuno con:
        - Scopo del modulo
        - Interfaccia pubblica
        - **Estratti di codice significativi, ciascuno SPIEGATO riga per riga**
        - Integrazione con altri moduli
    - 11.3 Pattern e best practice adottate
    - 11.4 Gestione errori e logging
    - 11.5 Sicurezza (autenticazione, autorizzazione, validazione input, OWASP)
    - 11.6 Performance e ottimizzazioni
12. **Testing e validazione**
    - 12.1 Strategia di testing (unitari, integrazione, end-to-end)
    - 12.2 Esempi di test significativi
    - 12.3 Copertura raggiunta
    - 12.4 Bug trovati e risolti (tabella con ID, descrizione, severità, fix)
13. **Deployment e messa in produzione**
    - 13.1 Ambienti (dev, staging, prod)
    - 13.2 Pipeline CI/CD
    - 13.3 Monitoring e alerting
14. **Difficoltà incontrate e soluzioni adottate** (4-6 pagine, racconto narrativo delle sfide tecniche)
15. **Risultati ottenuti**
    - 15.1 Obiettivi raggiunti vs obiettivi iniziali
    - 15.2 Metriche (performance, uptime, utenti, ecc.)
    - 15.3 Feedback ricevuti
16. **Analisi costi / tempi** (se applicabile)
17. **Limitazioni e criticità residue**
18. **Sviluppi futuri** (roadmap con priorità)
19. **Conclusioni**
20. **Bibliografia e sitografia**
21. **Appendici**
    - A. Glossario
    - B. Codice sorgente completo dei moduli principali
    - C. Schemi database
    - D. Screenshot / mockup
    - E. Documentazione API

**Follow-up questions (poni in batch di 3-5):**

*Batch 1 — contesto:*
- Chi sono gli autori (nomi completi)?
- Istituzione / azienda committente?
- Data di inizio e fine del progetto?
- Destinatario (docente, commissione, cliente)?

*Batch 2 — tecnologie:*
- Quali fornitori / servizi cloud avete usato? Perché?
- Quali librerie principali? Quali alternative avete scartato?
- Che strumenti di sviluppo?

*Batch 3 — processo:*
- Quali difficoltà principali avete incontrato?
- Casi in cui avete cambiato approccio a metà strada?
- Feedback ricevuti da utenti / tester?

*Batch 4 — risultati:*
- Metriche concrete (utenti, performance, ecc.)?
- Obiettivi non raggiunti?
- Cosa rifareste diversamente?

**Come scalare la lunghezza al target richiesto senza gonfiare:**
- Più pagine target → più dettaglio. Non ripetizioni.
- Spiega motivazione dietro ogni scelta (non solo "abbiamo usato X", ma "abbiamo valutato X, Y, Z e scelto X perché...")
- Per ogni estratto di codice: commento riga per riga, non solo il blocco
- Descrivi esempi concreti invece di affermazioni generiche
- Includi dati reali, screenshot descritti, log di errori risolti
- Racconta esperienze dirette con fornitori e tool
- Appendici con codice completo, schemi, glossario contano nel totale pagine
- Se il materiale disponibile non basta a raggiungere il target, chiedi all'utente informazioni aggiuntive; non inventare

**Tono:** formale accademico / professionale, prima persona plurale ("abbiamo implementato") o impersonale ("è stato implementato") — decide lo stile scelto dall'utente.

---

## codice — Documentazione tecnica del codice

**Scope:** documentare un codebase (non raccontare un progetto).

**Sezioni obbligatorie:**
1. Introduzione al progetto
2. Prerequisiti (versioni runtime, dipendenze)
3. Installazione e setup
4. Struttura delle directory
5. Architettura generale (flusso dati, layer)
6. Moduli principali (per ciascuno: scopo, interfaccia, dipendenze)
7. API / funzioni pubbliche (firma, parametri, valore di ritorno, esempio)
8. Modello dati / schema database
9. Configurazione (variabili d'ambiente, file di config)
10. Build, test, deploy
11. Troubleshooting
12. Contribuire (coding standards, workflow git)
13. Licenza

**Follow-up questions:**
- Il codebase è pubblico / interno / proprietario?
- Pubblico target: nuovi dev che entrano nel team, utenti API, entrambi?
- Vuoi esempi eseguibili per ogni API?

**Tono:** tecnico diretto, seconda persona ("Per installare, esegui…").

---

## analisi-codice — Analisi critica di un codebase

**Scope:** review / audit di un codice esistente, tipicamente non scritto da chi scrive la relazione.

**Sezioni obbligatorie:**
1. Oggetto dell'analisi (repository, versione analizzata, commit hash)
2. Metodologia dell'analisi (strumenti, criteri di valutazione)
3. Panoramica architetturale
4. Punti di forza
5. Criticità individuate, classificate per severità (critica / alta / media / bassa)
6. Debito tecnico
7. Sicurezza (vulnerabilità OWASP, gestione secrets, input validation)
8. Performance (hotspot, query N+1, leak)
9. Manutenibilità (complessità ciclomatica, duplicazione, test coverage)
10. Conformità a standard (naming, struttura, convenzioni)
11. Raccomandazioni prioritizzate
12. Roadmap di miglioramento suggerita
13. Appendice: elenco dettagliato dei file analizzati

**Follow-up questions:**
- Quali aree sono prioritarie (sicurezza, performance, manutenibilità)?
- Il committente vuole solo fotografia o anche piano di intervento?
- Budget/tempo stimato per ogni raccomandazione?

**Tono:** tecnico critico ma costruttivo, terza persona.

---

## bug — Post-mortem / Incident report

**Scope:** analisi di un bug / incidente produttivo.

**Sezioni obbligatorie:**
1. Sommario (1 paragrafo)
2. Timeline (cronologia degli eventi con orari precisi)
3. Impatto (utenti coinvolti, servizi degradati, durata, dati persi)
4. Root cause
5. Come è stato rilevato
6. Azioni di contenimento (cosa ha risolto l'immediato)
7. Azioni di remediation (fix definitivo)
8. Cosa è andato bene
9. Cosa è andato male
10. Azioni correttive (con owner e scadenze)
11. Lezioni apprese

**Follow-up questions:**
- Data e ora dell'incidente?
- Durata?
- Numero utenti impattati?
- Servizio/feature interessata?
- Chi ha gestito la risposta?
- Il fix è già in produzione?

**Tono:** fattuale, blameless, al passato.

---

## finale — Relazione finale / riepilogativa

**Scope:** conclusiva di un percorso (corso, anno scolastico, progetto pluriennale).

**Sezioni obbligatorie:**
1. Introduzione (oggetto del percorso)
2. Obiettivi iniziali
3. Attività svolte (cronologia)
4. Risultati conseguiti
5. Criticità e difficoltà
6. Valutazione complessiva
7. Suggerimenti / proposte migliorative
8. Conclusioni

**Follow-up questions:**
- Qual era il percorso? Periodo?
- Risultati misurabili?
- Destinatari della relazione?

**Tono:** riepilogativo, misto prima persona / impersonale.

---

## tesi — Tesi di laurea / dottorato

**Scope:** tesi triennale, magistrale, o dottorato.

**Sezioni obbligatorie:**
1. Frontespizio accademico (università, facoltà, corso di laurea, titolo, candidato, relatore, correlatore, anno accademico)
2. Ringraziamenti (opzionale)
3. Abstract (in lingua + eventualmente inglese)
4. Indice
5. Introduzione
   - Contesto
   - Obiettivi
   - Struttura della tesi
6. **Capitolo 1 — Stato dell'arte / Background teorico** (espanso, con riferimenti bibliografici estesi)
7. **Capitolo 2 — Metodologia** (approccio, strumenti, protocollo di ricerca)
8. **Capitolo 3 — Sviluppo / Implementazione / Analisi** (contributo originale del candidato)
9. **Capitolo 4 — Risultati e validazione**
10. **Capitolo 5 — Discussione**
11. Conclusioni e lavori futuri
12. Bibliografia (formato accademico — APA, IEEE, o Chicago secondo il corso)
13. Appendici

**Follow-up questions:**
- Triennale, magistrale o dottorato?
- Università, corso di laurea, relatore, correlatore?
- Titolo esatto della tesi?
- Stile bibliografico richiesto (APA / IEEE / Chicago / altro)?
- Lingua richiesta dal regolamento?
- Tesi compilativa o sperimentale?
- Anno accademico?

**Tono:** accademico rigoroso, impersonale ("si è analizzato", "la ricerca ha evidenziato"), evitare prima persona singolare se non nei ringraziamenti.

**Citazioni:** ogni affermazione non banale deve avere riferimento bibliografico. Chiedi all'utente la bibliografia da citare.

---

## ricerca — Relazione di ricerca / Paper

**Scope:** ricerca scientifica (paper di conferenza, rivista, o relazione di progetto di ricerca).

**Sezioni obbligatorie (formato IMRaD):**
1. Titolo
2. Autori e affiliazioni
3. Abstract (150-300 parole)
4. Keywords
5. Introduction (problema, lavori correlati, contributo)
6. Related Work / Stato dell'arte
7. Method / Materials and Methods
8. Results
9. Discussion
10. Conclusion
11. References (formato specifico della venue)
12. Acknowledgments (opzionale)
13. Appendix (opzionale)

**Follow-up questions:**
- Venue target (conferenza, rivista, workshop)?
- Formato bibliografico richiesto?
- Numero pagine richiesto dalla call?
- Keywords principali?
- Dataset / esperimenti già disponibili?

**Tono:** accademico scientifico, impersonale, presente o passato prossimo per risultati ("we show" / "si mostra").

---

## esperienza — Relazione di esperienza

**Scope:** viaggio studio, convegno, workshop, PCTO (alternanza scuola-lavoro), visita aziendale, conferenza.

**Sezioni obbligatorie:**
1. Frontespizio (studente, classe/corso, docente referente, data, luogo)
2. Introduzione (tipo di esperienza e sua collocazione nel percorso formativo)
3. Descrizione dell'ente / luogo / evento ospitante
4. Obiettivi formativi
5. Programma / attività svolte (cronologia)
6. Aspetti più significativi (narrativa)
7. Competenze e conoscenze acquisite
8. Riflessione personale
9. Valutazione dell'esperienza
10. Conclusioni
11. Allegati (foto descritte, attestati, materiali)

**Follow-up questions:**
- Tipo di esperienza (PCTO, Erasmus, convegno, visita…)?
- Ente ospitante / luogo?
- Periodo e durata?
- Ore totali (per PCTO)?
- Momenti più significativi?
- Che competenze hai sviluppato?

**Tono:** narrativo ma strutturato, prima persona, riflessivo.

---

## custom — Struttura libera

Chiedi all'utente:
1. Titolo della relazione
2. Scopo
3. Destinatario
4. Struttura desiderata (sezioni principali)
5. Lunghezza indicativa
6. Tono
7. Materiale di riferimento

Poi procedi con quella struttura.

---

# Tipologie enterprise

Le tipologie sotto attivano automaticamente il **control sheet** (vedi `steps/cover-control.md`) e caricano il brand profile se presente.

---

## proposta — Proposta commerciale

**Scope:** documento commerciale per acquisire un cliente. Deve vendere, non documentare.

**Sezioni obbligatorie:**
1. Cover + Document Control
2. Executive summary (1 pagina — problema, soluzione, valore, investimento)
3. Comprensione del contesto (mostra di aver capito il cliente)
4. Obiettivi dell'intervento
5. Approccio metodologico
6. Scope di lavoro (dettagliato per fasi/deliverable)
7. Timeline e milestone
8. Team dedicato (CV sintetici, ruoli, commitment)
9. Case study / referenze analoghe (2-3 max)
10. Investimento economico (pricing table con opzioni)
11. Termini e condizioni
12. Prossimi passi
13. Appendici (CV completi, portfolio, certificazioni)

**Follow-up questions:**
- Nome cliente, settore, dimensione?
- Brief ricevuto / call di kick-off?
- Deliverable attesi dal cliente?
- Budget indicativo?
- Scadenza della proposta (validità)?
- Competitor già valutati dal cliente?
- Chi firma lato cliente?

**Tono:** consulenziale, diretto, orientato al valore. Prima persona plurale aziendale ("proponiamo", "realizziamo"). Evitare gergo eccessivo.

**Pricing table pattern:**
```markdown
| Opzione | Scope | Investimento | Durata |
|---|---|---|---|
| Base | Deliverable 1+2 | € {{price_base}} + IVA | 4 settimane |
| Standard | + Deliverable 3+4 | € {{price_std}} + IVA | 8 settimane |
| Premium | + Supporto 3 mesi | € {{price_prem}} + IVA | 12 settimane |
```

---

## rfp-response — Risposta a Request for Proposal

**Scope:** risposta formale a RFP / gara con requisiti strutturati del committente.

**Sezioni obbligatorie:**
1. Cover + Document Control + riferimenti RFP (numero protocollo, data pubblicazione)
2. Lettera di accompagnamento firmata
3. Executive summary
4. **Conformità requisiti** (tabella punto per punto: requisito RFP → nostra risposta → dove nel doc)
5. Comprensione del bisogno
6. Soluzione proposta (architettura, componenti)
7. Metodologia di delivery
8. Team proposto con CV
9. Esperienze e referenze (case study simili)
10. Piano di progetto (WBS, Gantt)
11. Gestione rischi (risk register)
12. Piano qualità
13. Sicurezza e compliance (ISO/GDPR/SOC2)
14. Offerta economica (tabella dettagliata)
15. Allegati obbligatori da RFP (certificazioni, bilanci, ecc.)

**Follow-up questions:**
- Numero RFP e titolo gara?
- Stazione appaltante?
- Deadline presentazione?
- Criteri di valutazione (tecnico/economico, pesi)?
- Requisiti di qualificazione specifici?
- Lotti (se gara a lotti)?
- Formato richiesto (PDF firmato digitalmente, buste separate, ecc.)?

**Tono:** formale-istituzionale, rigoroso, aderente al lessico della RFP.

**Nota critica:** ogni requisito RFP deve essere citato letteralmente prima della risposta. Niente parafrasi creative.

---

## sow — Statement of Work

**Scope:** accordo operativo fra fornitore e cliente dopo firma contratto quadro. Definisce cosa, come, quando, quanto.

**Sezioni obbligatorie:**
1. Cover + Document Control (riferimento contratto quadro)
2. Scopo e oggetto
3. Descrizione servizi/prodotti
4. Deliverable (tabella con codice, descrizione, criteri accettazione, data)
5. Milestone e scadenze (Gantt)
6. Team e ruoli (RACI matrix)
7. Responsabilità del fornitore
8. Responsabilità del cliente
9. Dipendenze e assunzioni
10. Modalità di accettazione dei deliverable
11. Gestione change request
12. Corrispettivo economico (effort + tariffe + totale)
13. Modalità di pagamento e fatturazione
14. Termini contrattuali specifici (SLA, penali, IP, riservatezza)
15. Firme

**Follow-up questions:**
- Riferimento contratto quadro (numero, data)?
- Cliente e referente operativo (PM lato cliente)?
- PM lato fornitore?
- Deliverable numerabili con data target?
- T&M, fixed price o milestone-based?
- SLA specifici richiesti?
- Penali per ritardo/non conformità?

**Tono:** contrattuale, preciso, non ambiguo. Evitare "circa", "più o meno", "dovrebbe".

---

## business-case — Business Case

**Scope:** giustifica un investimento in un'iniziativa (nuovo prodotto, progetto di trasformazione, acquisizione) con analisi economica.

**Sezioni obbligatorie:**
1. Cover + Document Control
2. Executive summary (raccomandazione finale in prima pagina)
3. Contesto e problema / opportunità
4. Obiettivi strategici
5. Analisi delle alternative considerate
   - 5.1 Status quo (do nothing)
   - 5.2 Opzione A
   - 5.3 Opzione B (raccomandata)
   - 5.4 Opzione C
6. Descrizione dettagliata opzione raccomandata
7. Analisi costi (CAPEX, OPEX, anno 1-5)
8. Analisi benefici (tangibili: ricavi, saving; intangibili: brand, compliance)
9. Flussi di cassa attualizzati (NPV, IRR, payback period)
10. Analisi sensitività (scenari best/base/worst)
11. Risk assessment (risk register con impatto €)
12. Piano di implementazione ad alto livello
13. KPI di successo e misurazione
14. Raccomandazione
15. Next steps e richiesta decisione

**Follow-up questions:**
- Sponsor e decision maker finale?
- Orizzonte temporale dell'analisi (3, 5, 10 anni)?
- Tasso di sconto aziendale (WACC)?
- Benefit già quantificati o da stimare?
- Budget cap disponibile?
- Scadenza decisione?

**Tono:** executive, numeri-driven, orientato alla decisione. Scarso adornamento.

**Tabelle chiave obbligatorie:**
- Confronto opzioni (criteri × opzioni con scoring)
- Cash flow 5 anni
- NPV/IRR calcolo
- Risk register

---

## spec-funzionale — Specifica funzionale

**Scope:** cosa farà il sistema dal punto di vista dell'utente. Base per sviluppo e UAT.

**Sezioni obbligatorie:**
1. Cover + Document Control
2. Scopo del documento e audience
3. Glossario
4. Contesto di business
5. Personas e attori del sistema
6. User journey (as-is e to-be)
7. **Requisiti funzionali** (RF-001, RF-002, ...)
   - Per ogni RF: ID, descrizione, attore, trigger, input, processo, output, priorità (MoSCoW), fonte
8. User stories (formato "Come … voglio … per …") con criteri di accettazione Gherkin (Given/When/Then)
9. **Requisiti non funzionali** (RNF-001, ...): performance, scalabilità, sicurezza, usabilità, accessibilità, compliance
10. Vincoli (tecnici, regolatori, temporali, budget)
11. Assunzioni
12. Flussi applicativi principali (BPMN o sequenze)
13. Regole di business
14. Requisiti di integrazione con sistemi esistenti
15. Requisiti di dato (volumi, retention, privacy)
16. Fuori scope (what's NOT in)
17. Traceability matrix (req → user story → test)

**Follow-up questions:**
- Committente e approvatore funzionale?
- Stakeholder business da intervistare?
- Sistemi esistenti da integrare?
- Utenti target (numero, geografie, device)?
- Requisiti regolatori (GDPR, PCI-DSS, settore)?
- Metodologia (waterfall, agile)?

**Tono:** preciso, univoco, testabile. Ogni requisito deve essere verificabile.

---

## spec-tecnica — Specifica tecnica / Architecture Decision Record

**Scope:** come sarà costruito il sistema. Per sviluppatori.

**Sezioni obbligatorie:**
1. Cover + Document Control
2. Scopo e audience
3. Architettura target (diagramma C4: Context, Container, Component, Code)
4. Stack tecnologico (linguaggi, framework, DB, infrastruttura) con motivazione
5. Design dati (ER, schema, indici, partizionamento)
6. API design (REST/GraphQL/gRPC endpoint list con schema)
7. Flussi end-to-end (sequence diagram)
8. Gestione autenticazione e autorizzazione (OAuth2, JWT, RBAC)
9. Sicurezza (threat model STRIDE, mitigazioni, OWASP ASVS livello target)
10. Performance e scalabilità (load expected, caching, rate limiting, horizontal/vertical scaling)
11. Observability (logging, metrics, tracing — Prometheus/OpenTelemetry/ELK)
12. Deployment (ambienti, CI/CD, IaC Terraform/Pulumi, rollback strategy)
13. Disaster recovery (RTO, RPO, backup, failover)
14. Dipendenze esterne e fallback
15. Architecture Decision Records (ADR) per scelte critiche
16. Migrazione dati (se legacy)
17. Roadmap implementazione (fasi)
18. Open questions

**Follow-up questions:**
- Team size e skill set disponibili?
- Cloud provider preferito / vincoli?
- Budget infrastrutturale mensile?
- Carico atteso (RPS, dati, utenti)?
- Vincoli di latenza / SLA?
- Tool di monitoring già in uso?

**Tono:** tecnico rigoroso, impersonale, decisioni motivate. Usa diagrammi (Mermaid/PlantUML) ovunque utile.

---

## incident-postmortem — Incident Post-mortem (enterprise, blameless)

**Scope:** post-mortem formale per incidenti produttivi con impatto cliente / revenue / compliance. Più strutturato del `bug`.

**Sezioni obbligatorie:**
1. Cover + Document Control (severity, classification)
2. Sommario executive (1 paragrafo leggibile dal C-level)
3. Classificazione incidente (SEV-1/2/3/4) e categoria
4. Timeline dettagliata (UTC timestamps precisi al minuto)
5. Impatto quantificato
   - Utenti impattati (numero, %)
   - Servizi degradati/down
   - Durata totale e durata impatto utente
   - Revenue impact stimato
   - SLA breach (sì/no, dettaglio)
   - Compliance / notifiche regolatorie dovute
6. Rilevamento (chi, quando, come — paging automatico o manuale?)
7. Risposta (team coinvolto, tempi di escalation, decisioni)
8. Root cause analysis (5-whys)
9. Fattori contribuenti (non-root causes)
10. Mitigazione immediata
11. Fix definitivo
12. Cosa è andato bene
13. Cosa è andato male
14. Action items (owner + deadline + priority + Jira ID)
15. Lezioni apprese
16. Appendici: log estratti, grafici metriche, runbook usato

**Follow-up questions:**
- Data/ora inizio-fine (UTC)?
- Severity classification secondo policy interna?
- Servizi/componenti impattati?
- Customer-facing? Quanti utenti?
- Revenue lost stimato?
- SLA breached?
- On-call engineer primario?
- Comunicazioni esterne fatte (status page, email cliente)?
- Comunicazioni regolatore/autorità (GDPR data breach, NIS2)?

**Tono:** fattuale assoluto, blameless (azioni e sistemi, non persone), al passato. Evitare aggettivi emotivi.

**Blameless guidance:** mai "Mario ha sbagliato", sempre "il sistema permetteva il deploy senza review". Se necessario nominare, usa ruolo non persona.

---

## status-report — Status Report di progetto

**Scope:** aggiornamento periodico al committente/sponsor. Formato conciso, RAG status, progress vs plan.

**Sezioni obbligatorie (1 pagina executive + 2-3 di dettaglio):**
1. Header compatto (Progetto, Periodo, Data, PM, RAG status complessivo)
2. **RAG status** per dimensione: Scope / Schedule / Budget / Quality / Risk (verde/giallo/rosso con motivazione in 1 riga)
3. Highlight del periodo (bullet: 3-5 risultati principali)
4. Progress vs baseline (tabella: milestone, data target, data prevista, status)
5. Burn-down / progress chart (Mermaid se possibile)
6. Lowlight / blocker attivi con mitigation in corso
7. Decisioni necessarie dallo sponsor (con deadline)
8. Risk register (top 5 rischi con trend ↑↓→)
9. Change request nel periodo (lista con impatto scope/time/cost)
10. Attività prossimo periodo
11. KPI progetto (velocity, burn rate, quality metrics)
12. Escalation requested
13. Appendice: dettaglio tecnico se necessario

**Follow-up questions:**
- Periodo di riferimento (settimana/mese/sprint)?
- Cadenza (weekly/biweekly/monthly)?
- Sponsor e destinatari distribution list?
- Milestone imminenti?
- Jira/Linear project key (per auto-estrazione con fase 11)?

**Tono:** compatto, visual, action-oriented. Usa emoji status sparingly (🟢🟡🔴). Niente prosa lunga.

**Pattern RAG status:**
```markdown
| Dimensione | Status | Nota |
|---|---|---|
| Scope | 🟢 | On track, no scope changes |
| Schedule | 🟡 | Slippage 3 giorni su milestone M4, recupero previsto |
| Budget | 🟢 | 47% consumed vs 52% planned |
| Quality | 🟢 | Zero defect escaped |
| Risk | 🔴 | Dipendenza vendor X non confermata entro deadline |
```

---

## whitepaper — Whitepaper tecnico / marketing

**Scope:** documento leadership di pensiero su un tema tecnico o di business. Thought leadership, lead generation.

**Sezioni obbligatorie:**
1. Cover ricercata (grafica curata, titolo evocativo)
2. Abstract (250 parole max)
3. Executive summary (1 pagina)
4. Introduzione al problema/trend
5. Contesto e dati di mercato (con fonti autorevoli)
6. Analisi del problema
7. Soluzione proposta / tesi dell'autore
8. Approfondimento (3-5 sotto-capitoli)
9. Case study (1-2 storie di successo concrete)
10. Best practice / framework proposto
11. Conclusioni e call-to-action
12. Riferimenti bibliografici (solo fonti autorevoli)
13. About the author(s)
14. About the company

**Follow-up questions:**
- Audience target (CTO, CIO, CFO, decision maker tecnico)?
- Obiettivo (lead gen, brand, education, vendor positioning)?
- Call to action desiderata (contatta, scarica tool, iscriviti)?
- Fonti disponibili (report analyst, paper, dati proprietari)?
- Case study disponibili?
- Lunghezza target (tipica 8-15 pp)?

**Tono:** autorevole, fluente, storytelling moderato. Evitare hard-sell, privilegiare valore informativo.

---

## case-study — Case study cliente

**Scope:** storia di successo cliente per marketing/sales. Challenge → Solution → Results.

**Sezioni obbligatorie:**
1. Cover con logo cliente (se autorizzato)
2. Quote in apertura dal cliente (statement potente)
3. Client snapshot (nome, settore, dimensione, geografia)
4. Challenge (il problema da risolvere, con contesto)
5. Objectives (cosa voleva raggiungere il cliente)
6. Solution (cosa abbiamo fatto: approccio, tecnologie, team)
7. Implementation (tempistiche, fasi, sfide superate)
8. Results (metriche concrete before/after, ROI quantificato)
9. Testimonial cliente (quote + foto + nome ruolo autorizzata)
10. About [tua azienda]
11. Next steps per il prospect

**Follow-up questions:**
- Hai autorizzazione all'uso del nome cliente?
- Metriche disponibili before/after?
- Quote raccolta dal cliente?
- Periodo dell'intervento?
- Tecnologie usate?
- Team dedicato?

**Tono:** storytelling concreto, numeri protagonisti, prima persona del cliente nei quote.

---

## handover — Handover document

**Scope:** passaggio di consegne (fine progetto al cliente, cambio team, offboarding persona chiave).

**Sezioni obbligatorie:**
1. Cover + Document Control
2. Scopo dell'handover (a chi, da chi, perché)
3. Stato attuale del sistema/progetto (snapshot)
4. Architettura e stack
5. Repository, accessi, credenziali (con riferimento a password manager, MAI credenziali inline)
6. Ambienti (dev, staging, prod) e URL
7. Procedure operative
   - Deploy
   - Rollback
   - Backup/restore
   - Monitoring dashboard
   - Alerting e on-call
8. Runbook incidenti comuni (top 10 per frequenza)
9. Contatti chiave (vendor, referenti, SLA contracts)
10. Contratti attivi e scadenze
11. Debito tecnico noto
12. Piano di knowledge transfer (sessioni pianificate, durata, partecipanti)
13. Issue aperti (link Jira/Linear)
14. Roadmap in corso
15. Documentazione esistente (link)
16. Punti di attenzione critici (gotchas, cose non ovvie)

**Follow-up questions:**
- Data effettiva passaggio?
- Chi riceve (nome, ruolo)?
- Chi consegna?
- Periodo di affiancamento previsto?
- Sistemi/progetti inclusi?
- Access provisioning completato?
- Knowledge gaps noti?

**Tono:** operativo, esaustivo, action-oriented. Zero prosa. Tabelle e checklist.

---

## runbook — Runbook operativo / Playbook

**Scope:** procedura operativa step-by-step per task ricorrenti (es. "come fare release", "come risolvere alert X", "procedure onboarding").

**Sezioni obbligatorie (una sezione per playbook, più playbook per documento):**
1. Cover + indice playbook
2. Per ogni playbook:
   - **Nome** e ID procedura
   - **Quando usare** (trigger condition)
   - **Chi** (ruolo autorizzato)
   - **Prerequisiti** (accessi, tool, condizioni)
   - **Durata stimata**
   - **Rischio/impatto** (reversibile? impatta utenti?)
   - **Procedura numerata** (ogni step: azione + comando + output atteso + verifica)
   - **Troubleshooting** (cosa fare se step N fallisce)
   - **Rollback** (come tornare indietro)
   - **Escalation** (chi chiamare se bloccato)
   - **Validation post-procedure**
   - **Owner & last-reviewed date**

**Follow-up questions:**
- Quali playbook includere (lista)?
- Team che userà il runbook?
- Tool principali (monitoring, deploy, access)?
- Policy esistenti da referenziare?

**Tono:** imperativo diretto, comandi in code block, zero ambiguità. "Esegui X" non "potresti eseguire X".

**Pattern ogni step:**
```markdown
### Step 3 — Verifica health endpoint

**Azione:** chiama l'endpoint di health del servizio in produzione.

```bash
curl -f https://api.example.com/health
```

**Output atteso:** HTTP 200 con JSON `{"status":"ok"}`.

**Se fallisce:** vai a Troubleshooting > "Health check failed".
```

---

## audit-report — Audit report

**Scope:** audit interno o esterno (sicurezza, compliance, qualità, finanziario). Formato strutturato con finding classificati.

**Sezioni obbligatorie:**
1. Cover + Document Control + classification (spesso `confidential` o `restricted`)
2. Executive summary (1 pagina)
3. Scope dell'audit
   - Oggetto
   - Perimetro (sistemi, processi, periodo)
   - Fuori scope
4. Metodologia (standard applicati: ISO 27001, SOC 2, NIST CSF, ecc.)
5. Team di audit e ruoli
6. Riassunto dei finding (tabella: ID, titolo, severità, stato)
7. **Finding dettagliati** (uno per sezione)
   - Per ogni finding: ID, titolo, severità (Critical/High/Medium/Low/Informational), descrizione, evidenza (log, screenshot, doc), standard violato, rischio, raccomandazione, owner, due date, stato
8. Compliance matrix (requisito standard → verificato → gap → action plan)
9. Sample testing (liste campioni esaminati con esito)
10. Interviste condotte
11. Documenti esaminati
12. Conclusioni
13. Piano d'azione raccomandato con priorità
14. Dichiarazione di conformità / non conformità
15. Firme del lead auditor
16. Appendici (evidenze, log, questionnaire compilati)

**Follow-up questions:**
- Standard di riferimento (ISO 27001, SOC 2 Type I/II, PCI-DSS, GDPR, ecc.)?
- Tipo audit (interno, pre-certification, surveillance, cliente)?
- Lead auditor e team?
- Perimetro esatto (sistemi/processi)?
- Periodo osservato?
- Finding severity scale aziendale?

**Tono:** impersonale, fattuale, evidence-based. Ogni affermazione supportata da evidenza citata.

---

## compliance-report — Compliance report (GDPR/ISO/SOC2)

**Scope:** report di conformità per regolatori, clienti enterprise, o uso interno governance.

**Sezioni obbligatorie:**
1. Cover + Document Control
2. Executive summary (livello di conformità complessivo)
3. Framework di riferimento (GDPR artt. / ISO 27001 controls / SOC 2 TSC / HIPAA / PCI-DSS)
4. Scope (entità legali, sistemi, perimetro geografico, periodo)
5. **Control matrix** (control ID → nome → applicabilità → implementazione → evidenza → status: Implemented/Partial/Not Implemented/Not Applicable)
6. Per ogni control NON Implemented o Partial: gap + remediation plan + owner + target date
7. Policies e procedure attive (elenco con versioni)
8. Records of processing activities (GDPR Art. 30, se pertinente)
9. Data Protection Impact Assessment (DPIA, se richiesto)
10. Data breach register (se presente)
11. Training e awareness (evidenza formazione)
12. Terze parti (DPA firmati, valutazione rischio vendor)
13. Incident response capability
14. Business continuity / DR
15. Conclusioni e roadmap compliance
16. Dichiarazione finale (attestazione o non-attestazione)
17. Appendici: policies, evidenze, log audit

**Follow-up questions:**
- Framework target (GDPR, ISO 27001:2022, SOC 2 Type II, PCI-DSS 4.0, NIS2)?
- Scope esatto (entità, paesi, sistemi)?
- Livello certificazione target?
- DPO / CISO responsabile?
- Audit esterno già eseguito? Quando?
- Gap analysis già disponibile?

**Tono:** formale, preciso, evidence-based. Mai dichiarare conformità senza evidenza documentale.

**Control matrix pattern (esempio SOC 2):**
```markdown
| Control ID | Nome | Applicabilità | Status | Evidenza | Gap |
|---|---|---|---|---|---|
| CC1.1 | Integrity and ethical values | Sì | Implemented | Code of Conduct v2.1 | — |
| CC6.1 | Logical access controls | Sì | Partial | IAM policy | MFA non universale |
| CC7.2 | System monitoring | Sì | Implemented | Datadog dashboards + runbook | — |
```

---

# Note trasversali (valide per tutte le tipologie)

- **Autore:** chiedi sempre nome e cognome dell'autore. Non inventare mai.
- **Date:** chiedi date precise. Se l'utente non le sa, metti `[DA INSERIRE]`.
- **Dati numerici, percentuali, metriche:** chiedi. Non inventare mai numeri.
- **Nomi propri** (aziende, docenti, colleghi, prodotti): chiedi.
- **Bibliografia:** chiedi le fonti. Non inventare referenze. Se l'utente non ne ha, segnala che vanno aggiunte.
- **Codice:** se serve includerne, prendilo dai file scansionati; non inventare codice che "potrebbe esserci".
- **Lingua:** mantieni coerenza, non mescolare italiano e inglese salvo termini tecnici consolidati.
