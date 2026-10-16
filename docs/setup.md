# Setup: panoramica

Il setup lo guida `/plm-triage:setup`; il dettaglio di ogni fase sta solo in [skills/setup/SKILL.md](../skills/setup/SKILL.md). Si parte senza nulla di clonato (vedi [README](../README.md)), è riprendibile (stato in `<istanza>/setup-state.json`) e a ogni checkpoint Claude si ferma e aspetta un umano.

## Chi fa cosa

- **Collega** (utente Jira + DB): esegue il setup, inserisce le credenziali nel proprio terminale, approva query e configurazione, valuta le bozze.
- **DBA / IT del cliente**: conferma che il login è in sola lettura e con privilegio minimo (idealmente su viste dedicate); indica, se c'è, una replica di reporting.
- **Referente del cliente**: OK scritto al trattamento dei dati con Claude, prima di leggere qualunque dato reale.
- **Claude**: guida, verifica, propone; non approva nulla da solo.

## Fasi e checkpoint

Tempi indicativi, da validare sul campo.

| # | Fase | Checkpoint umano | Tempo |
|---|---|---|---|
| 0 | Prerequisiti (Claude Code, uv, git), dipendenze, cartella istanza, verifiche web su Jira MCP | **consenso** (piano aziendale, OK scritto del cliente, login DB in sola lettura confermato dal DBA); opzione `instance_dir` e riavvio nella cartella istanza | 15 min + attese |
| 1 | Jira MCP a scope utente | comando `claude mcp add` e login OAuth o PAT nel proprio terminale; elenco dei tool di scrittura da negare | 10 min |
| 2 | Credenziali DB nel keyring + `ping` | `plm-db set-credentials` e `check` nel proprio terminale | 10 min |
| 3 | Repo istanza privato (team) | il repo è privato; push | 10 min |
| 4 | Catalogo query (team) | approvazione di **ogni** query | 1-3 h |
| 5 | Tassonomia e `config.yaml` (team) | approvazione della config | 1 h |
| 6 | Shadow eval su ~30 ticket chiusi | elenco ticket; valutazione in `evals/grading.csv` | 2-4 h |
| 7 | Gate ([protocollo](e2e-protocol.md)) | decisione go / no-go | 15 min |
| 8 | E2E live su 1-3 ticket aperti | modifica dei permessi; "sì" esplicito per ogni scrittura | 30 min |

Le fasi 3-5 si fanno **una volta per team** e si condividono tramite il repo istanza. Un collega che arriva dopo fa 0-2 più uno smoke test.

Riavvio di Claude Code solo dopo aver cambiato le opzioni del plugin o registrato un server MCP; non dopo modifiche al catalogo o alle credenziali nel keyring.

## Permessi dell'istanza

JSON non ammette commenti, quindi la nota sta qui. `instance-template/.claude/settings.json` abilita il plugin (`extraKnownMarketplaces`, `enabledPlugins`; verifica la forma sulla tua versione di Claude Code), consente i tool `plm-db` e nega `WebFetch` e `WebSearch`. Bash non è pre-autorizzato: ogni comando chiede conferma. I tool di scrittura Jira vengono aggiunti a `deny` in fase 1 (i nomi dipendono dal server MCP); in fase 8 si tolgono solo quelli necessari, senza metterli in `allow`.

## Note sullo schema

Le note generiche su Agile PLM (codici di classe numerici, `NODETABLE`, `LISTENTRY`, tabelle di pagina due/tre) aiutano a leggere le query del collega ma vanno trattate come **da verificare sull'istanza**. Nessun dettaglio dello schema reale entra nel repo pubblico.
