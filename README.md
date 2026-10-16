# plm-triage

Plugin Claude Code per il triage dei ticket Jira di supporto su un PLM agile (Oracle Agile PLM su SQL Server).
Claude legge il ticket, interroga il DB PLM **solo** tramite query di catalogo approvate (sola lettura) e propone una bozza di risposta o un'escalation motivata.
Ogni affermazione cita la query che la prova; nel dubbio, escalation a un umano.

## Stato

`0.1.0`: **template**. Non è pronto per la produzione finché un'istanza non supera il gate di valutazione ([docs/e2e-protocol.md](docs/e2e-protocol.md)).

## Prerequisiti

- [Claude Code](https://code.claude.com/) in versione recente, con un piano Claude aziendale (Team/Enterprise)
- [uv](https://docs.astral.sh/uv/) e git
- accesso alla board Jira di supporto e alla rete del DB PLM (rete aziendale o VPN)

## Avvio rapido

Non serve clonare nulla. In Claude Code, da qualsiasi cartella:

```
/plugin marketplace add matteobadini/plm-triage
/plugin install plm-triage@plm-triage
```

Se compare il prompt delle opzioni del plugin, puoi lasciare vuoti i campi: li imposterai in fase 0/2 (la password lasciala comunque vuota, va nel keyring).

Poi incolla questo messaggio. Deve **iniziare** con lo slash command, perché il setup si avvia solo così:

```
/plm-triage:setup guidami fino ai test E2E su ticket reali, fermati a ogni checkpoint umano
```

La fase 0 crea o clona la cartella istanza e ti chiede di riaprire Claude Code lì: rilancia lo stesso messaggio e il setup riprende da dove era. Panoramica di fasi e checkpoint: [docs/setup.md](docs/setup.md).

## Struttura

```
.claude-plugin/        plugin.json (userConfig, MCP plm-db), marketplace.json
skills/triage-ticket/  procedura di triage + templates.md
skills/setup/          setup a fasi con checkpoint umani
server/                MCP locale plm-db (Python, pacchetto plm_db_mcp; CLI plm-db-mcp, plm-db)
instance-template/     scheletro del repo istanza privato (config, catalog, evals)
docs/                  architettura, setup, protocollo E2E, ADR
```

## Documentazione

- [Architettura](docs/architecture.md)
- [Setup: panoramica](docs/setup.md)
- [Protocollo di valutazione ed E2E](docs/e2e-protocol.md)
- [Decisioni (ADR)](docs/adr/README.md)
- [Sicurezza](SECURITY.md) · [Per agenti che lavorano su questo repo](AGENTS.md)

## Licenza

[MIT](LICENSE)
