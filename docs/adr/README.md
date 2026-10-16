# Decisioni architetturali (ADR)

| # | Decisione | Stato |
|---|---|---|
| [0001](0001-plugin-skill-piatta.md) | Plugin con skill piatte, senza router né playbook | Accettata |
| [0002](0002-db-via-mcp-catalogo.md) | Accesso DB solo via MCP locale con catalogo di query nominate | Accettata |
| [0003](0003-credenziali-fuori-dal-repo.md) | Credenziali mai nel repo | Accettata |
| [0004](0004-template-pubblico-istanza-privata.md) | Template pubblico, istanza privata | Accettata |
| [0005](0005-jira-via-mcp-atlassian.md) | Jira via MCP Atlassian, scelto in setup a scope utente | Accettata |
| [0006](0006-autonomia-graduale-gate.md) | Autonomia graduale con escalation a regole e gate | Accettata |

## Formato (MADR-lite)

File `NNNN-titolo-breve.md`, massimo ~60 righe, sezioni: **Contesto**, **Decisione**, **Alternative considerate**, **Conseguenze**, **Stato** (Proposta | Accettata | Sostituita da NNNN). Un ADR non si riscrive: se la decisione cambia, se ne scrive uno nuovo e si aggiorna lo stato del vecchio.
