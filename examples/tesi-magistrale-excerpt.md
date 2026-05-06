---
title: "Verifica formale di smart contract tramite model checking simbolico"
author: "Mario Rossi"
matricola: "M58/000123"
relatore: "Prof.ssa Anna Bianchi"
correlatore: "Dott. Luca Verdi"
universita: "Università degli Studi di Esempio"
dipartimento: "Dipartimento di Informatica"
corso: "Laurea Magistrale in Informatica"
anno_accademico: "2025–2026"
---

# Abstract

La diffusione delle architetture decentralizzate ha reso lo smart contract un'unità computazionale critica per il movimento di valore on-chain. La verifica della loro correttezza è tuttavia complicata dalla semantica non locale dell'esecuzione, dalla presenza di stati condivisi e dalla mancanza di un meccanismo di rollback successivo all'inclusione in blocco.

Questo lavoro presenta un framework di **model checking simbolico** applicato a contratti scritti in Solidity, con particolare attenzione alle proprietà di reentrancy safety, integer overflow e access control. L'approccio è stato validato su un corpus di 412 contratti raccolti da Etherscan tra il 2024 e il 2025, evidenziando una copertura delle proprietà critiche del 94,3% con un tempo medio di verifica inferiore a 18 secondi per contratto.

I risultati indicano che la combinazione di analisi simbolica e oracoli SMT può ridurre in modo significativo il numero di vulnerabilità sfruttabili, mantenendo un overhead computazionale compatibile con un'integrazione in pipeline di sviluppo continuo.

**Parole chiave:** smart contract, verifica formale, model checking, SMT, Solidity.

\newpage

# 1. Introduzione

## 1.1 Contesto e motivazione

Negli ultimi cinque anni, l'ammontare di valore custodito da smart contract ha superato i 100 miliardi di dollari, esponendo l'ecosistema a perdite quantificabili in oltre 3,8 miliardi soltanto nel periodo 2022–2024 [@chainalysis2024]. La causa prevalente non è una rottura del consenso del livello sottostante, bensì un difetto logico nel codice del contratto.

Questa osservazione orienta naturalmente la ricerca verso tecniche che intervengano **prima** del deployment, anziché reagire dopo l'incidente. Il presente lavoro si inserisce in tale linea, con l'obiettivo di rendere il model checking simbolico applicabile in fase di sviluppo da team di dimensione contenuta, non specialisti di metodi formali.

## 1.2 Domanda di ricerca

> *In che misura un framework di model checking simbolico può individuare le tre classi di vulnerabilità più sfruttate (reentrancy, integer overflow, access control) mantenendo un tempo di verifica per contratto inferiore a 30 secondi?*

## 1.3 Contributo

Il contributo si articola in tre punti:

1. Una formalizzazione SMT-LIB delle tre classi di proprietà sopra citate, parametriche rispetto allo storage layout.
2. Un'implementazione open-source che integra Z3 e cvc5 come back-end intercambiabili.
3. Una valutazione empirica su un corpus reale di 412 contratti, con confronto rispetto a Slither e Mythril.

[…]
