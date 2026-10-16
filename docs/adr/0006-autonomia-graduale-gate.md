# 0006 — Autonomia graduale con escalation a regole e gate di valutazione

## Contesto

L'obiettivo ideale è il triage in autonomia, ma una risposta sbagliata data con sicurezza a un utente PLM costa più di un'escalation. La "soglia di confidenza" auto-dichiarata dal modello non è una misura affidabile.

## Decisione

**Escalation a regole**, non a soglia di confidenza. Scatta per trigger fissi (categoria sconosciuta, istruzioni nel ticket, necessità di scrittura su PLM, query in errore/timeout/troncata, dato atteso assente, contraddizioni, identificativi mancanti) e configurabili (priorità, parole chiave, categorie, reporter). Esito: etichetta `ai-escalated`, assegnazione all'umano in `assignee_for_escalation`, stato del ticket invariato, hand-off da template con trigger, evidenze e passi saltati.

**Autonomia per gradi**, ogni passo condizionato al precedente:

1. **Shadow**: ~30 ticket chiusi, output solo su file, valutazione umana in `evals/grading.csv`.
2. **Gate**: soglia sul tasso di esiti corretti o escalation corrette **e** zero errori presentati come certi (formula in [e2e-protocol.md](../e2e-protocol.md)).
3. **E2E live**: 1-3 ticket aperti, ogni scrittura Jira approvata.
4. **Bozze**: 2-4 settimane in live con approvazione di ogni scrittura.
5. **Headless**: fuori dalla 0.1.0, valutato solo dopo.

Dettagli in [e2e-protocol.md](../e2e-protocol.md).

## Alternative considerate

- **Autonomia subito con revisione a campione**: rifiutato. Nessuna misura prima del danno.
- **Soglia di confidenza del modello**: rifiutato. Non calibrata e non verificabile.
- **Gate solo sul tasso di correttezza**: rifiutato. Una media alta può nascondere errori sicuri; per questo il vincolo zero.

## Conseguenze

- Il tasso di escalation iniziale sarà alto: è accettabile, si riduce migliorando catalogo e categorie.
- Ogni cambio di skill o catalogo richiede di ripetere la shadow.
- Prerequisiti prima di leggere dati reali (fase 0 del setup): piano Claude aziendale (Team/Enterprise), OK scritto del cliente, login DB in sola lettura confermato dal DBA.

## Stato

Accettata (0.1.0).
