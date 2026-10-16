# 0001 — Un plugin con skill semplici, senza router né playbook

## Contesto

Serve un risultato minimo, da condividere con un collega, per un solo caso d'uso: il triage dei ticket di supporto PLM. La proposta iniziale prevedeva una skill "router" che smistava su più playbook, sul modello di pstack (per Cursor) e della sua versione per Claude Code, pstack-claude: circa 70 skill, 24 skill di principi, hook all'avvio della sessione (SessionStart), agenti diversi per livello di impegno, `models.json` e un generatore.

## Decisione

Un plugin con due skill semplici, ciascuna in un solo file: `triage-ticket` (la procedura) e `setup`. Da pstack si riprendono solo quattro principi:

- i passi vengono copiati **alla lettera** nella task list, e ogni passo saltato riporta `skip: <motivo>`;
- si cita solo ciò che è stato letto nella sessione;
- ogni affermazione è etichettata `verificato`, `dedotto` o `ipotesi`;
- se i controlli preliminari falliscono, non si produce nulla.

I quattro principi sono scritti direttamente nella skill.

## Alternative considerate

- **Router con playbook**: scartata. C'è un solo caso d'uso, e Claude sceglie già da solo la skill giusta in base alla descrizione.
- **File di principi separati**: scartata. Quattro principi brevi stanno meglio dove vengono applicati.
- **Hook all'avvio della sessione**: scartata. Consuma token a ogni sessione, anche quando non si fa triage.
- **Ruoli di modello, generatori**: scartate. Aggiungono complessità senza benefici per questo caso.

A conferma: anche la skill di triage originale di pstack (automazioni Benny, `triage-issue-reports`) è un unico file.

## Conseguenze

- Pochi file, che un collega legge in pochi minuti.
- Cambiare i passi cambia il comportamento: va ripetuta la valutazione di prova ([0006](0006-autonomia-graduale-gate.md)).
- Se arrivano altri casi d'uso si aggiungono altre skill semplici; un router si rivaluta con un nuovo ADR.

## Stato

Accettata (0.1.0).
