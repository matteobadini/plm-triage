# 0003 — Credenziali mai nei repository

## Contesto

Vincolo di partenza: nessuna credenziale nel plugin o nei repository. La proposta iniziale sosteneva che "Claude non vede mai la password", usando uno script lanciato con Bash. Una revisione critica ha mostrato che non è vero: con Bash Claude può leggere variabili d'ambiente, keyring o file.

## Decisione

Le credenziali del database restano **nel processo del server MCP** `plm-db`, che le cerca in quest'ordine:

1. variabili d'ambiente `PLM_DB_HOST/PORT/DATABASE/USER/PASSWORD` (per la futura esecuzione automatica);
2. opzioni del plugin, con `db_password` marcata `sensitive` (salvata nell'archivio credenziali del sistema operativo), passate al server come `PLM_UC_*`; i valori vuoti o che iniziano ancora con `${` vengono ignorati;
3. keyring del sistema operativo (servizio `plm-triage`), dove il collega salva le credenziali dal proprio terminale con `plm-db set-credentials` (la password non viene mostrata durante la digitazione).

Il triage non usa Bash e l'istanza non lo pre-autorizza: ogni comando richiede l'approvazione dell'utente. Gli errori del server non contengono mai la password né la stringa di connessione.

Jira: OAuth personale (Rovo) oppure token personale nella configurazione del server MCP a livello utente, mai nel repository ([0005](0005-jira-via-mcp-atlassian.md)).

## Alternative considerate

- **File `.env` nel repository di istanza, con lettura negata**: scartata. Negare il tool Read non ferma uno script che apre il file da solo.
- **Solo keyring**: non basta per la futura esecuzione automatica.
- **Solo variabili d'ambiente**: scomodo e meno sicuro sul PC del collega.

## Conseguenze

- La garanzia regge solo se Bash resta fuori da `allow` e l'utente non approva comandi che leggono le credenziali. Va controllato a ogni revisione di `instance-template/.claude/settings.json`.
- La password va nel keyring (via consigliata): un valore inserito nelle opzioni del plugin ha la precedenza, e un valore `sensitive` non si corregge facilmente.
- gitleaks in CI come ulteriore protezione.
- Cambio password: si cambia sul database, poi si inserisce di nuovo nelle opzioni del plugin o nel keyring.

## Stato

Accettata (0.1.0).
