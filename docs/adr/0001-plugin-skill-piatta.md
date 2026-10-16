# 0001 — Plugin con skill piatte, senza router né playbook

## Contesto

Serve un deliverable minimo, condivisibile con un collega, per un solo caso d'uso: il triage dei ticket di supporto PLM. La proposta iniziale era una skill "router" con playbook, ispirata a pstack (Cursor) e al suo port per Claude Code, pstack-claude (~70 skill, 24 principle-skill, hook SessionStart, agenti per livello di effort, `models.json`, generatore).

## Decisione

Un plugin con due skill piatte: `triage-ticket` (procedura) e `setup`. Da pstack prendiamo solo:

- passi copiati **verbatim** nella task list, con `skip: <motivo>` per quelli saltati;
- citare solo ciò che è stato letto nella sessione;
- etichettare ogni affermazione `verificato` / `dedotto` / `ipotesi`;
- fail closed: se il preflight fallisce, nessun output.

I quattro principi stanno inline nella skill.

## Alternative considerate

- **Router + playbook**: rifiutato. C'è un solo caso d'uso e Claude sceglie già nativamente tra skill in base alla descrizione.
- **File di principi separati**: rifiutato. Quattro principi brevi stanno meglio dove vengono applicati.
- **Hook SessionStart**: rifiutato. Costa token a ogni sessione, anche quando non si fa triage.
- **Ruoli di modello, generatori**: rifiutati. Complessità senza beneficio per questo caso.

Evidenza a favore: anche lo skill di triage di pstack upstream (automazioni Benny, `triage-issue-reports`) è un singolo file piatto.

## Conseguenze

- Pochi file, leggibili da un collega in pochi minuti.
- Cambiare i passi cambia il comportamento: va ripetuta la shadow eval ([0006](0006-autonomia-graduale-gate.md)).
- Se arrivano altri casi d'uso, si aggiungono skill piatte; un router si rivaluta con un nuovo ADR.

## Stato

Accettata (0.1.0).
