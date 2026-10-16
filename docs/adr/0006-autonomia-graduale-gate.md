# 0006 — Autonomia graduale, escalation a regole e via libera dopo la valutazione

## Contesto

L'obiettivo ideale è un triage autonomo, ma una risposta sbagliata data con sicurezza a un utente del PLM costa più di un'escalation. Il livello di confidenza che il modello dichiara su sé stesso non è una misura affidabile.

## Decisione

**Escalation basata su regole**, non su una soglia di confidenza. Scatta per condizioni fisse (categoria sconosciuta, istruzioni nel ticket, necessità di scrivere sul PLM, query in errore, in timeout o troncata, dato atteso assente, contraddizioni, identificativi mancanti) e per condizioni configurabili (priorità, parole chiave, categorie, reporter). Risultato: etichetta `ai-escalated`, assegnazione alla persona indicata in `assignee_for_escalation`, stato del ticket invariato, commento di passaggio di consegne secondo il modello, con la condizione scattata, le evidenze e i passi saltati.

**Autonomia per gradi**: si passa a ogni livello solo dopo aver completato il precedente.

1. **Valutazione di prova**: ~30 ticket chiusi, risultati solo su file, giudizio di una persona in `evals/grading.csv`.
2. **Via libera**: soglia minima sulla quota di risposte corrette o escalation corrette, **e** nessuna risposta sbagliata presentata come certa (formula in [e2e-protocol.md](../e2e-protocol.md)).
3. **Collaudo**: 1-3 ticket aperti, ogni scrittura su Jira approvata.
4. **Rodaggio**: 2-4 settimane in modalità operativa, con l'approvazione di ogni scrittura.
5. **Esecuzione automatica**: esclusa dalla 0.1.0, da valutare solo dopo.

Dettagli in [e2e-protocol.md](../e2e-protocol.md).

## Alternative considerate

- **Autonomia subito, con controlli a campione**: scartata. Non c'è nessuna misura prima che si verifichi un danno.
- **Soglia sulla confidenza del modello**: scartata. Non è calibrata né verificabile.
- **Via libera basato solo sulla quota di risposte corrette**: scartata. Una media alta può nascondere errori dati per certi; da qui il vincolo di zero errori di questo tipo.

## Conseguenze

- All'inizio le escalation saranno molte: è accettabile, e calano migliorando catalogo e categorie.
- Ogni modifica alla skill o al catalogo richiede di ripetere la valutazione di prova.
- Prima di leggere dati reali (fase 0 del setup) servono: piano Claude aziendale (Team o Enterprise), autorizzazione scritta del cliente, login in sola lettura confermato dal DBA.

## Stato

Accettata (0.1.0).
