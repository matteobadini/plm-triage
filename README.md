# plm-triage

Plugin di Claude Code che aiuta a smistare (triage) i ticket Jira di supporto su Agile PLM (Oracle Agile PLM su SQL Server).
Claude legge il ticket, consulta il database PLM in sola lettura e **solo** con query approvate dal team, poi propone una risposta oppure un'escalation motivata a una persona.
Ogni affermazione indica la query o il campo del ticket da cui proviene. Nel dubbio, l'escalation è la regola.

## Stato

Versione `0.1.0`: è un **modello** da adattare al proprio team. Va usato in produzione solo dopo che il team ha ottenuto il via libera previsto dal [protocollo di valutazione](docs/e2e-protocol.md).

## Prerequisiti

- [Claude Code](https://code.claude.com/) in versione recente, con un piano Claude aziendale (Team o Enterprise)
- [uv](https://docs.astral.sh/uv/) e git
- accesso alla board Jira di supporto e alla rete del database PLM (rete aziendale o VPN)

## Come iniziare

Non serve clonare nulla. In Claude Code, da qualsiasi cartella, installa il plugin:

```
/plugin marketplace add matteobadini/plm-triage
/plugin install plm-triage@plm-triage
```

Se Claude Code ti chiede le opzioni del plugin, puoi lasciare tutti i campi vuoti: li imposterai durante il setup. La password lasciala comunque vuota: andrà nel keyring.

Poi incolla questo messaggio. Deve **iniziare** con il comando `/plm-triage:setup`, altrimenti il setup non parte:

```
/plm-triage:setup guidami fino al collaudo su ticket reali, fermati a ogni punto di controllo
```

Il setup ti chiede se il team ha già un repository di istanza (il repository git privato del team, con configurazione e query). Se è così, tieni pronto il suo URL: te lo passa il collega che ha fatto il primo setup.

Nella fase 0 Claude crea o clona la cartella di istanza e ti chiede di riaprire Claude Code in quella cartella. Lì incolla di nuovo lo stesso messaggio: il setup riprende dal punto in cui si era fermato. Fasi e punti di controllo sono descritti in [docs/setup.md](docs/setup.md).

## Struttura

```
.claude-plugin/        plugin.json (opzioni del plugin, server MCP plm-db), marketplace.json
skills/triage-ticket/  procedura di triage + templates.md (modelli di commento)
skills/setup/          setup a fasi con punti di controllo
server/                server MCP locale plm-db (Python, pacchetto plm_db_mcp; comandi plm-db-mcp, plm-db)
instance-template/     modello del repository di istanza (config, catalog, evals)
docs/                  architettura, setup, protocollo di valutazione, ADR
```

## Documentazione

- [Architettura](docs/architecture.md)
- [Setup: panoramica](docs/setup.md)
- [Protocollo di valutazione e collaudo](docs/e2e-protocol.md)
- [Decisioni architetturali (ADR)](docs/adr/README.md)
- [Sicurezza](SECURITY.md) · [Istruzioni per chi modifica questo repository](AGENTS.md)

## Licenza

[MIT](LICENSE)
