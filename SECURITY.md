# Sicurezza

## Regola zero: nessun dato cliente in questo repo

Questo repo è pubblico. Mai committare nomi di clienti, testi di ticket, schema reale, hostname, query reali, credenziali. Tutto ciò vive nel repo istanza privato ([ADR 0004](docs/adr/0004-template-pubblico-istanza-privata.md)). CI esegue gitleaks.

## Modello delle minacce (sintesi)

| Minaccia | Mitigazione |
|---|---|
| **Prompt injection ed esfiltrazione** dal testo del ticket | La skill di triage non usa Bash e Bash non è pre-autorizzato (ogni comando chiede conferma all'umano); `WebFetch`/`WebSearch` negati nell'istanza; nessun SQL libero, solo query di catalogo approvate da un umano; scritture Jira negate in shadow e, in live, approvate a mano una per una; headless solo in futuro, con allowlist `--allowedTools`. |
| **Esposizione delle credenziali** | Le credenziali stanno nel processo del server MCP `plm-db` (userConfig `sensitive` nel credential store del SO, keyring, oppure env per headless). Il triage non usa Bash e un comando che provasse a leggerle richiederebbe l'approvazione dell'umano. Gli errori del server sono sanitizzati. |
| **Scritture o danni sul DB** | Login in sola lettura, da verificare con il DBA (viste, privilegio minimo): è il vero confine. Il loader rifiuta più istruzioni, ciò che non è `SELECT`/`WITH` e un ampio elenco di parole chiave (difesa in profondità). |
| **Impatto sul DB di produzione** | `LOCK_TIMEOUT 5000`, `DEADLOCK_PRIORITY LOW`, limite righe, timeout per query; preferire una replica di reporting/standby se disponibile. |
| **SQL Server 2008** | Fuori supporto; TLS datato (TDS 7.3 di default via pymssql/FreeTDS). Valutare con l'IT il rischio sulla rete aziendale. |
| **Dati inviati ad Anthropic** | Ticket e risultati delle query passano dal modello. Prima di leggere qualunque ticket o riga reale servono piano Claude aziendale (Team/Enterprise), **OK scritto del cliente** e login DB in sola lettura confermato dal DBA: checkpoint di consenso in fase 0 del setup. |
| **Identità su Jira** | Commenti prefissati `[AI triage]` e pubblicati con l'utenza del collega. Un service account solo per la futura fase headless. |

Audit locale: `<istanza>/logs/queries.jsonl` registra nome query, hash dei parametri, righe, durata, esito; nessun dato di risultato.

## Segnalare un problema

Non aprire issue pubbliche per vulnerabilità o per dati sensibili finiti nel repo. Usa GitHub Private Vulnerability Reporting del repo, se attivo, oppure contatta direttamente il maintainer (Matteo Badini). Se trovi dati cliente committati, segnalalo subito: vanno rimossi dalla history e le credenziali eventualmente esposte ruotate.
