# 0002 — Accesso DB solo via MCP locale con catalogo di query nominate

## Contesto

Il DB PLM è SQL Server 2008 on-prem, raggiungibile solo dalla rete aziendale, con un login in sola lettura. Il testo dei ticket può contenere prompt injection. Il DB è di produzione: query pesanti o lock possono disturbare gli utenti PLM.

## Decisione

Accesso al DB **solo** tramite il server MCP locale stdio `plm-db` (`server/`, pacchetto `plm_db_mcp`), dichiarato inline in `.claude-plugin/plugin.json`. Tool: `ping`, `list_queries`, `describe_query`, `run_query(name, params)`. Nessun SQL libero.

- Catalogo: un `.sql` per query in `<istanza>/catalog/`, con header YAML (parametri tipizzati, `max_rows`, `timeout_s`, `isolation`). Ogni query è approvata da un umano nel setup.
- Il loader rifiuta: più istruzioni, tutto ciò che non inizia con `SELECT`/`WITH`, variabili `@` non dichiarate, parole chiave di scrittura/esecuzione fuori da stringhe e commenti. È difesa in profondità: il confine vero sono i permessi del login, da verificare con il DBA (viste, privilegio minimo).
- Guardrail per sessione: `SET LOCK_TIMEOUT 5000; SET DEADLOCK_PRIORITY LOW;` (`READ UNCOMMITTED` solo se l'header lo richiede), limite righe con flag `truncated`, timeout, errori sanitizzati. Preferire una replica di reporting/standby se esiste.
- Audit locale JSONL senza dati di risultato.
- Il catalogo si costruisce dalle query salvate del collega, non esplorando `INFORMATION_SCHEMA`.
- Driver pymssql (wheel con FreeTDS, nessun ODBC né diritti admin su Windows), TDS 7.3 di default.

## Alternative considerate

- **Script Python invocato via Bash**: rifiutato. Con Bash disponibile Claude può leggere credenziali ed eseguire qualunque cosa; l'injection diventa esecuzione.
- **Tool SQL libero con filtro SELECT-only**: rifiutato. Un filtro non basta contro query costose o esfiltrazione di tabelle non pertinenti.
- **pyodbc**: richiede driver ODBC installati, spesso con diritti admin.

## Conseguenze

- Claude risponde solo a ciò che il catalogo copre; il resto va in escalation.
- Aggiungere una query è un atto umano, rivedibile nel repo istanza.
- SQL Server 2008 è fuori supporto e il TLS è datato: rischio da valutare con l'IT.

## Stato

Accettata (0.1.0).
