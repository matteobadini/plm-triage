# Setup: panoramica

Il setup si avvia con `/plm-triage:setup` e Claude ti guida fase per fase. Il dettaglio di ogni fase è solo in [skills/setup/SKILL.md](../skills/setup/SKILL.md). Non serve clonare nulla prima di iniziare (vedi [README](../README.md)). Puoi interrompere e riprendere quando vuoi: l'avanzamento è salvato in `<istanza>/setup-state.json`. A ogni punto di controllo Claude si ferma e aspetta una persona.

## Chi fa cosa

- **Collega** (utente di Jira e del database): esegue il setup, inserisce le credenziali nel proprio terminale, approva query e configurazione, giudica le bozze.
- **DBA / IT del cliente**: conferma che il login è in sola lettura e con privilegi minimi (meglio se su viste dedicate); indica una replica di reporting, se esiste.
- **Referente del cliente**: dà l'autorizzazione scritta al trattamento dei dati con Claude, prima che si legga qualunque dato reale.
- **Claude**: guida, verifica e propone; non approva nulla da solo.

## Fasi e punti di controllo

Tempi indicativi, da confermare sul campo.

| # | Fase | Cosa decide o fa la persona | Tempo |
|---|---|---|---|
| 0 | Prerequisiti (Claude Code, uv, git), dipendenze, cartella di istanza, verifiche sul web per il server MCP di Jira | **consenso** (piano aziendale, autorizzazione scritta del cliente, login in sola lettura confermato dal DBA); imposta l'opzione `instance_dir` e riapre Claude Code nella cartella di istanza | 15 min + attese |
| 1 | Server MCP di Jira, a livello utente | esegue `claude mcp add` e fa il login (OAuth o token personale) nel proprio terminale; conferma l'elenco dei tool di scrittura da negare | 10 min |
| 2 | Credenziali del database nel keyring + `ping` | esegue `plm-db set-credentials` e `check` nel proprio terminale | 10 min |
| 3 | Repository di istanza privato (team) | crea il repository privato; approva il push. Alla fine Claude prepara il messaggio da inoltrare ai colleghi | 10 min |
| 4 | Catalogo query (team) | approva **ogni** query | 1-3 h |
| 5 | Categorie e `config.yaml` (team) | approva la configurazione | 1 h |
| 6 | Valutazione di prova su ~30 ticket chiusi | approva l'elenco dei ticket; giudica i risultati in `evals/grading.csv` | 2-4 h |
| 7 | Via libera ([protocollo](e2e-protocol.md)) | decide se procedere | 15 min |
| 8 | Collaudo su 1-3 ticket aperti | approva la modifica dei permessi; dice "sì" esplicitamente prima di ogni scrittura | 30 min |

Le fasi 3-5 si fanno **una volta per team** e il risultato si condivide tramite il repository di istanza.

## Colleghi che arrivano dopo

Chi arriva dopo fa solo le fasi 0-2 più una prova rapida su un ticket chiuso. Gli serve l'URL del repository di istanza: lo trova nel messaggio che Claude prepara alla fine della fase 3 (con i comandi di installazione e il messaggio di avvio del setup), oppure nella pagina del repository sul server git del team. Alla domanda della fase 0 sul repository di istanza risponde sì e incolla l'URL (HTTPS o SSH). Se non sa se il team ne ha già uno, deve chiederlo al team prima di proseguire: un secondo repository di istanza dividerebbe catalogo e configurazione.

## Quando riavviare Claude Code

Riavvia Claude Code solo dopo aver cambiato le opzioni del plugin o registrato un server MCP. Non serve dopo modifiche al catalogo o alle credenziali nel keyring.

## Permessi dell'istanza

Il formato JSON non ammette commenti, quindi la spiegazione è qui. `instance-template/.claude/settings.json`:

- abilita il plugin (`extraKnownMarketplaces`, `enabledPlugins`; verifica il formato sulla tua versione di Claude Code);
- consente i tool di `plm-db`;
- nega `WebFetch` e `WebSearch`.

Bash non è pre-autorizzato: ogni comando chiede conferma. I tool di scrittura su Jira vengono aggiunti a `deny` nella fase 1, perché i loro nomi dipendono dal server MCP scelto. Nella fase 8 si tolgono da `deny` solo quelli necessari, senza aggiungerli ad `allow`.

## Note sullo schema

Le nozioni generiche su Agile PLM (codici di classe numerici, `NODETABLE`, `LISTENTRY`, tabelle Page Two/Page Three) aiutano a leggere le query del collega, ma vanno considerate **da verificare sull'istanza**. Nessun dettaglio dello schema reale entra nel repository pubblico.
