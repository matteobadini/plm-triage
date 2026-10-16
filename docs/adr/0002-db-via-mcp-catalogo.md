# 0002 — Accesso al database solo tramite server MCP locale e catalogo di query

## Contesto

Il database PLM è un SQL Server 2008 in sede, raggiungibile solo dalla rete aziendale, con un login in sola lettura. Il testo dei ticket può contenere istruzioni malevole (prompt injection). Il database è di produzione: query pesanti o lock possono rallentare gli utenti del PLM.

## Decisione

Al database si accede **solo** tramite il server MCP locale `plm-db` (comunicazione stdio; `server/`, pacchetto `plm_db_mcp`), dichiarato in `.claude-plugin/plugin.json`. Espone quattro tool: `ping`, `list_queries`, `describe_query`, `run_query(name, params)`. Nessun SQL libero.

- Catalogo: un file `.sql` per query in `<istanza>/catalog/`, con un'intestazione YAML (parametri con tipo, `max_rows`, `timeout_s`, `isolation`). Ogni query viene approvata da una persona durante il setup.
- Quando carica il catalogo, il server rifiuta: più istruzioni nello stesso file, tutto ciò che non inizia con `SELECT`/`WITH`, variabili `@` non dichiarate, parole chiave di scrittura o esecuzione fuori da stringhe e commenti. È una difesa in più: il vero confine sono i permessi del login, da verificare con il DBA (viste dedicate, privilegi minimi).
- Protezioni di sessione: `SET LOCK_TIMEOUT 5000; SET DEADLOCK_PRIORITY LOW;` (`READ UNCOMMITTED` solo se l'intestazione lo chiede), limite di righe con indicatore `truncated`, timeout, errori privi di dati sensibili. Se esiste una replica di reporting o di standby, meglio usare quella.
- Log di audit locale in formato JSONL, senza i dati restituiti.
- Il catalogo si costruisce a partire dalle query che il collega usa già, non esplorando `INFORMATION_SCHEMA`.
- Driver pymssql: include FreeTDS, quindi non servono ODBC né diritti di amministratore su Windows. Protocollo TDS 7.3 come impostazione predefinita.

## Alternative considerate

- **Script Python lanciato con Bash**: scartata. Con Bash disponibile Claude può leggere le credenziali ed eseguire qualunque comando: un'istruzione malevola nel ticket diventerebbe un comando eseguito.
- **Tool SQL libero filtrato a sole SELECT**: scartata. Un filtro non basta contro query costose o contro la lettura di tabelle non pertinenti.
- **pyodbc**: richiede driver ODBC installati, spesso con diritti di amministratore.

## Conseguenze

- Claude risponde solo a ciò che il catalogo copre; il resto va in escalation.
- Aggiungere una query è una decisione di una persona, tracciata nel repository di istanza.
- SQL Server 2008 è fuori supporto e usa un TLS datato: il rischio va valutato con l'IT.

## Stato

Accettata (0.1.0).
