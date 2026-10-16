# Decisioni architetturali (ADR)

Un ADR (Architecture Decision Record) registra una decisione di progetto, il perché e le alternative scartate.

| # | Decisione | Stato |
|---|---|---|
| [0001](0001-plugin-skill-piatta.md) | Un plugin con skill semplici, senza router né playbook | Accettata |
| [0002](0002-db-via-mcp-catalogo.md) | Accesso al database solo tramite server MCP locale e catalogo di query | Accettata |
| [0003](0003-credenziali-fuori-dal-repo.md) | Credenziali mai nei repository | Accettata |
| [0004](0004-template-pubblico-istanza-privata.md) | Modello pubblico, istanza privata | Accettata |
| [0005](0005-jira-via-mcp-atlassian.md) | Jira tramite server MCP Atlassian, scelto nel setup a livello utente | Accettata |
| [0006](0006-autonomia-graduale-gate.md) | Autonomia graduale, escalation a regole e via libera dopo la valutazione | Accettata |

## Formato

Un file `NNNN-titolo-breve.md` di al massimo ~60 righe, con le sezioni **Contesto**, **Decisione**, **Alternative considerate**, **Conseguenze**, **Stato** (Proposta | Accettata | Sostituita da NNNN). Un ADR non si riscrive: se la decisione cambia, se ne scrive uno nuovo e si aggiorna lo stato di quello vecchio.
