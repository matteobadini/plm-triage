# Sicurezza

## Regola zero: nessun dato del cliente in questo repository

Questo repository è pubblico. Non committare mai nomi di clienti, testi di ticket, schema reale del database, hostname, query reali o credenziali. Tutto questo materiale sta nel repository di istanza, privato ([ADR 0004](docs/adr/0004-template-pubblico-istanza-privata.md)). La CI esegue gitleaks a ogni modifica.

## Rischi e contromisure (sintesi)

| Rischio | Contromisura |
|---|---|
| **Istruzioni malevole nel testo del ticket** (prompt injection) e **fuga di dati** | La skill di triage non usa Bash, e Bash non è pre-autorizzato: ogni comando richiede la conferma dell'utente. `WebFetch` e `WebSearch` sono negati nell'istanza. Nessun SQL libero: solo query del catalogo approvate da una persona. In modalità di prova le scritture su Jira sono negate; in modalità operativa ogni scrittura va approvata a mano, una per una. L'esecuzione automatica è prevista solo in futuro, con un elenco chiuso di tool consentiti (`--allowedTools`). |
| **Esposizione delle credenziali** | Le credenziali restano nel processo del server MCP `plm-db`: opzioni del plugin (la password, marcata `sensitive`, finisce nell'archivio credenziali del sistema operativo), keyring o variabili d'ambiente per l'esecuzione automatica. Il triage non usa Bash, e un comando che tentasse di leggerle richiederebbe l'approvazione dell'utente. I messaggi di errore del server non contengono dati sensibili. |
| **Scritture o danni sul database** | Il vero confine è un login in sola lettura, da verificare con il DBA (viste dedicate, privilegi minimi). In più, quando carica il catalogo il server rifiuta più istruzioni nello stesso file, tutto ciò che non è `SELECT`/`WITH` e un ampio elenco di parole chiave (difesa in profondità). |
| **Carico sul database di produzione** | `LOCK_TIMEOUT 5000`, `DEADLOCK_PRIORITY LOW`, limite di righe e timeout per ogni query. Se esiste una replica di reporting o di standby, meglio usare quella. |
| **SQL Server 2008** | Versione fuori supporto, con TLS datato (TDS 7.3 come impostazione predefinita di pymssql/FreeTDS). Il rischio sulla rete aziendale va valutato con l'IT. |
| **Dati inviati ad Anthropic** | Il testo dei ticket e i risultati delle query passano dal modello. Prima di leggere qualunque ticket o riga reale servono: piano Claude aziendale (Team o Enterprise), **autorizzazione scritta del cliente** e login in sola lettura confermato dal DBA. Il setup lo verifica con un punto di controllo in fase 0. |
| **Identità su Jira** | I commenti iniziano con `[AI triage]` e sono pubblicati con l'utenza del collega. Un account di servizio è previsto solo per la futura esecuzione automatica. |

Log di audit locale: `<istanza>/logs/queries.jsonl` registra nome della query, hash dei parametri, numero di righe, durata ed esito. Non contiene i dati restituiti.

## Segnalare un problema

Non aprire issue pubbliche per vulnerabilità o per dati sensibili finiti nel repository. Usa la segnalazione privata di vulnerabilità di GitHub (Private Vulnerability Reporting), se è attiva sul repository, oppure contatta direttamente il maintainer (Matteo Badini). Se trovi dati del cliente committati, segnalalo subito: vanno rimossi dalla cronologia git e le eventuali credenziali esposte vanno cambiate.
