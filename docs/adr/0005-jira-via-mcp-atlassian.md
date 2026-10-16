# 0005 — Jira tramite server MCP Atlassian, scelto nel setup a livello utente

## Contesto

Non è ancora certo se la board sia su Jira Cloud o su Data Center. Il collega usa già il server MCP di Atlassian. L'autenticazione deve essere personale e restare fuori dai repository.

## Decisione

Il plugin **non** include un server per Jira. Lo sceglie e lo registra il setup (fase 1), **a livello utente** (`claude mcp add --scope user ...`), cioè nella configurazione personale di Claude Code e non nel repository:

- **Cloud**: server MCP remoto Atlassian Rovo, con OAuth personale. L'indirizzo (ad esempio `https://mcp.atlassian.com/v1/mcp`) va verificato dal setup sulla documentazione Atlassian aggiornata, senza darlo per scontato.
- **Data Center**: `sooperset/mcp-atlassian` (progetto della community) con token personale (PAT).

Nel `config.yaml` dell'istanza si indicano il tipo di Jira (`flavor`: `cloud` | `datacenter`), `base_url` e `project_key`.

Identità: nell'uso interattivo i commenti sono pubblicati con l'utenza del collega e iniziano con `[AI triage]`. Un account di servizio serve solo per la futura esecuzione automatica.

## Alternative considerate

- **`.mcp.json` nel plugin con l'indirizzo di Rovo**: scartata. Non copre Data Center e lega il plugin a un indirizzo che può cambiare.
- **Un client REST per Jira scritto da zero**: scartata. Rifà ciò che i server MCP esistenti fanno già e richiede di gestire i token.

## Conseguenze

- Il setup ha un passo in più, ma il plugin funziona sia con Cloud sia con Data Center.
- I nomi dei tool che scrivono su Jira dipendono dal server scelto: il modello di istanza parte senza divieti su Jira e la fase 1 li aggiunge. Nella fase 8 si tolgono dai divieti solo quelli necessari (il commento ed eventualmente etichetta e assegnatario), senza aggiungerli ad `allow`: così la richiesta di autorizzazione di Claude Code resta un secondo controllo. Su Rovo etichetta e assegnatario possono passare da un tool generico di modifica del ticket: ogni chiamata va approvata leggendone gli argomenti.
- La verifica dell'indirizzo sul web si fa in fase 0, prima di aprire l'istanza, dove i tool web sono negati.
- Su Cloud, l'esecuzione automatica con token API può richiedere l'abilitazione da parte dell'amministratore dell'organizzazione Atlassian.

## Stato

Accettata (0.1.0).
