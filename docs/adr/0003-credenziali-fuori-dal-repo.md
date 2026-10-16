# 0003 — Credenziali mai nel repo

## Contesto

Vincolo di partenza: nessuna credenziale nel plugin o nei repo. La proposta iniziale affermava "Claude non vede mai la password" con uno script lanciato via Bash: la review avversaria ha mostrato che è falso, perché con Bash Claude può leggere env, keyring o file.

## Decisione

Le credenziali DB vivono **nel processo del server MCP** `plm-db`, risolte in quest'ordine:

1. env `PLM_DB_HOST/PORT/DATABASE/USER/PASSWORD` (per il futuro headless);
2. userConfig del plugin, con `db_password` `sensitive` (salvata nel credential store del SO), passato come `PLM_UC_*`; ignorati valori vuoti o che iniziano ancora con `${`;
3. keyring del SO (servizio `plm-triage`), impostato dal collega nel proprio terminale con `plm-db set-credentials` (getpass).

Il triage non usa Bash e l'istanza non lo pre-autorizza: ogni comando richiede l'approvazione dell'umano. Gli errori del server non includono mai password o stringa di connessione.

Jira: OAuth per utente (Rovo) o PAT nella configurazione MCP a scope utente, mai nel repo ([0005](0005-jira-via-mcp-atlassian.md)).

## Alternative considerate

- **File `.env` nel repo istanza con deny di lettura**: rifiutato. Il deny di Read non ferma script che aprono file da soli.
- **Solo keyring**: insufficiente per l'headless futuro.
- **Solo env**: scomodo e meno sicuro sul PC del collega.

## Conseguenze

- La garanzia regge solo se Bash resta fuori da `allow` e l'umano non approva comandi che leggono credenziali: da mantenere nelle revisioni di `instance-template/.claude/settings.json`.
- Password nel keyring (via raccomandata): un valore inserito nelle opzioni del plugin ha la precedenza e un valore sensibile non si corregge facilmente.
- gitleaks in CI come rete di sicurezza.
- Rotazione: cambio password lato DB, poi nuovo inserimento in userConfig o keyring.

## Stato

Accettata (0.1.0).
