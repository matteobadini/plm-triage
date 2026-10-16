# 0005 — Jira via MCP Atlassian, scelto in setup a scope utente

## Contesto

Non è ancora verificato se la board è su Jira Cloud o Data Center. Il collega usa già l'MCP server di Atlassian. L'autenticazione deve essere per utente e fuori dal repo.

## Decisione

Il plugin **non** include un server Jira. Il setup (fase 1) lo sceglie e lo registra a **scope utente** (`claude mcp add --scope user ...`):

- **Cloud**: Atlassian Rovo MCP remoto, OAuth per utente. L'endpoint (es. `https://mcp.atlassian.com/v1/mcp`) e il suo percorso vanno verificati dal setup sulla documentazione Atlassian corrente, non dati per scontati.
- **Data Center**: `sooperset/mcp-atlassian` (community) con PAT personale.

`config.yaml` dell'istanza indica il flavor (`cloud` | `datacenter`), `base_url` e `project_key`.

Identità: in fase interattiva i commenti sono pubblicati con l'utenza del collega e prefissati `[AI triage]`. Un service account si usa solo nella futura fase headless.

## Alternative considerate

- **`.mcp.json` nel plugin con l'URL Rovo**: rifiutato. Non copre Data Center e lega il plugin a un endpoint che può cambiare.
- **Client REST Jira proprio**: rifiutato. Duplica ciò che gli MCP esistenti fanno già e richiede gestione di token.

## Conseguenze

- Un passo in più nel setup, ma il plugin resta agnostico sul flavor.
- I nomi dei tool di scrittura Jira dipendono dal server scelto: il template parte senza deny Jira e la fase 1 li aggiunge. In fase 8 si tolgono solo quelli necessari (commento ed eventualmente etichetta/assegnatario) senza metterli in `allow`, così il prompt di permesso di Claude Code resta un secondo controllo. Su Rovo etichetta e assegnatario possono passare da un tool generico di modifica: ogni chiamata va approvata leggendone gli argomenti.
- La verifica dell'endpoint sul web si fa in fase 0, prima di aprire l'istanza, dove i tool web sono negati.
- Su Cloud, l'uso headless con token API può richiedere l'abilitazione da parte dell'admin dell'organizzazione.

## Stato

Accettata (0.1.0).
