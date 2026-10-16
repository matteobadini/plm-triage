---
name: setup
description: Setup guidato e riprendibile di plm-triage — prerequisiti, consenso, cartella di istanza, server MCP di Jira, credenziali del database, catalogo query, categorie, valutazione di prova, via libera e collaudo — con punti di controllo umani.
disable-model-invocation: true
---

# Setup plm-triage

Indicazioni dell'utente: `$ARGUMENTS`

Setup a fasi. Ogni fase ha un **PUNTO DI CONTROLLO**: ti fermi e non passi alla fase successiva senza la risposta o l'azione richiesta all'utente. Le fasi 0-2 sono personali; le fasi 3-5 sono di team (il risultato è condiviso nel repository di istanza); le fasi 6-8 si fanno una volta per team e si ripetono dopo cambiamenti rilevanti. Panoramica per le persone: `${CLAUDE_PLUGIN_ROOT}/docs/setup.md`.

Termini da usare con l'utente: "repository di istanza" (il repository git privato del team), "cartella di istanza" (il suo clone locale), "modalità di prova" (`mode: shadow`), "modalità operativa" (`mode: live`), "valutazione di prova" (fase 6), "via libera" (fase 7), "collaudo" (fase 8).

## Regole del setup

- **Riprendi, non ricominciare.** Individua la cartella di istanza: `${user_config.instance_dir}` se valorizzato (non vuoto, senza `${`), altrimenti la directory corrente se contiene `setup-state.json`. Se la trovi, leggi `<instance>/setup-state.json`, riepiloga cosa è già fatto e riparti dalla prima fase non `done`. Se non la trovi, parti dalla fase 0.
- **Consenso prima dei dati.** Senza `consent.confirmed: true` in `setup-state.json` non leggere nessun ticket reale né riga del database: torna al punto di controllo sul consenso della fase 0.
- **Mai password o token in chat.** Le credenziali si inseriscono solo nel terminale dell'utente (`plm-db set-credentials`, `claude mcp add`) o nelle opzioni del plugin. Se l'utente incolla un segreto in chat, digli di cambiarlo e non usarlo.
- **Sola lettura** su Jira e database fino alla fase 8. Database solo tramite i tool `plm-db`.
- **Riavvio solo quando serve:** dopo aver cambiato le opzioni del plugin (`instance_dir`, campi DB) o registrato un server MCP. **Non** serve dopo modifiche al catalogo o alle credenziali nel keyring: il server le rilegge a ogni chiamata. Quando serve, dillo, salva lo stato e fermati.
- **Comandi per il terminale dell'utente:** stampali completi, con percorsi assoluti già espansi (niente `${...}`), in sintassi PowerShell.
- **Niente dati del cliente nel repository pubblico.** Tutto ciò che è specifico va nel repository di istanza.

Stato in `<instance>/setup-state.json` (personale, escluso da git con `.gitignore`):

```json
{
  "version": 1,
  "instance_dir": "<percorso assoluto>",
  "consent": { "confirmed": false, "plan": "team | enterprise", "client_ok": "<riferimento al documento>", "db_readonly": "<chi lo ha confermato>", "at": "<ISO-8601>" },
  "jira": { "flavor": "cloud | datacenter", "base_url": "", "mcp": "<endpoint o pacchetto verificato>", "auth": "<note>", "sources": ["<URL documentazione>"], "verified_at": "<ISO-8601>" },
  "jira_write_tools": [],
  "phases": { "0": { "status": "todo | in_progress | done | skipped", "at": "<ISO-8601>", "notes": "" } },
  "eval": { "date": null, "tickets": [], "metrics": null }
}
```

Dopo ogni fase aggiorna `status`, `at` e `notes`.

## Fase 0 — Prerequisiti, consenso, cartella di istanza

Si esegue anche senza nulla di clonato, da qualunque cartella.

1. **Prerequisiti.** Verifica `claude --version` (versione recente), `uv --version`, `git --version`. Se manca qualcosa, spiega come installarlo; su Windows, dopo aver installato uv, bisogna aprire un **nuovo** terminale.
2. **Dipendenze del server.** `uv sync --directory "${CLAUDE_PLUGIN_ROOT}/server"` (scarica le dipendenze una volta sola, così il primo avvio di `plm-db` è rapido).
3. **Cartella di istanza.** Chiedi: "Il tuo team ha già un repository di istanza di plm-triage, cioè il repository git privato con configurazione e query? Se sì, incolla qui il suo URL (HTTPS o SSH). Se non hai l'URL, chiedilo al collega che ha fatto il primo setup: lo trova nel messaggio di fine fase 3. Oppure copialo dalla pagina del repository privato sul vostro server git."
   - **Sì:** accetta sia URL HTTPS (`https://...`) sia SSH (`git@<host>:...` oppure `ssh://...`), poi `git clone <URL> <percorso scelto dall'utente>`.
   - **No** (primo collega del team): copia `${CLAUDE_PLUGIN_ROOT}/instance-template/` (compresi i file nascosti `.claude/` e `.gitignore`) nel percorso scelto dall'utente ed esegui `git init`.
   - **Non lo so:** non creare una nuova istanza. Di' all'utente di verificare prima con il team, perché un secondo repository di istanza dividerebbe catalogo e configurazione; poi fermati.

   Crea `setup-state.json` con `instance_dir` assoluto.
4. **Verifiche sul web (solo qui).** Nell'istanza i tool web sono negati, quindi fai adesso le ricerche che serviranno dopo. Chiedi l'URL base di Jira: `*.atlassian.net` → Cloud, altrimenti Data Center (conferma con l'utente). Cloud: sulla documentazione Atlassian del Remote MCP Server (Rovo) verifica l'endpoint attuale e l'autenticazione. Data Center: sul README di `sooperset/mcp-atlassian` verifica il comando di avvio e le variabili per URL e PAT. Registra tutto in `jira` dello stato, con le URL delle fonti.
5. **PUNTO DI CONTROLLO — consenso.** Prima di leggere qualunque ticket o riga reale, chiedi conferma esplicita di questi tre punti e registrali in `consent`:
   - stai usando un piano Claude **aziendale** (Team o Enterprise), non personale;
   - il cliente ha dato l'**autorizzazione scritta** al trattamento dei dati (il testo dei ticket e i risultati delle query passano dal modello);
   - il **DBA** ha confermato che il login del database è in sola lettura (meglio se su viste dedicate).

   Se ne manca anche uno solo: `consent.confirmed: false`, spiega cosa serve e **fermati**; il setup non prosegue.
6. **PUNTO DI CONTROLLO — opzione e riavvio.** "Imposta l'opzione del plugin `instance_dir` = `<percorso>` (da `/plugin` → opzioni del plugin, oppure da `/config`, a seconda della versione). Poi chiudi Claude Code e riaprilo **nella cartella di istanza** (`cd <percorso>` e poi `claude`). Accetta l'abilitazione del plugin proposta da `.claude/settings.json` e rilancia `/plm-triage:setup`: riprendo da qui."

- **Completamento (verificato alla ripresa):** prerequisiti presenti; directory corrente = `instance_dir` dello stato; `ping` di `plm-db` riporta lo stesso `instance_dir` (lo riporta anche quando fallisce per le credenziali del database, che si impostano in fase 2); `consent.confirmed: true`.
- **Stato:** `phases.0 = done`. Se l'istanza clonata ha già il catalogo e `config.yaml` compilato, segui il setup ridotto (in fondo).

## Fase 1 — Server MCP di Jira

- **Obiettivo:** server MCP di Jira registrato a livello utente con il nome `jira`, in sola lettura durante la modalità di prova.
- **Cosa fa Claude:** prepara il comando `claude mcp add --scope user jira ...` con i valori di `jira` registrati in fase 0 (non rifare ricerche sul web). Data Center: il PAT lo inserisce l'utente nel proprio terminale, mai in chat. Avvisa che con `-e <VAR>=<PAT>` il token resta in `~/.claude.json` e nella cronologia della shell: proponi di leggerlo in PowerShell con `Read-Host -AsSecureString` in una variabile da passare al comando, e di ripulire poi la cronologia.
- **PUNTO DI CONTROLLO:** "Esegui nel tuo terminale: `<comando>`. Poi riavvia Claude Code nella cartella di istanza (se usate Jira Cloud, completa l'accesso OAuth da `/mcp`) e rilancia `/plm-triage:setup`."
- **Dopo il riavvio:** elenca i tool `mcp__jira__*` e leggi un ticket indicato dall'utente. Individua i tool che scrivono (creazione, modifica, commento, transizione, assegnazione, etichette, eliminazione, upload) e proponi l'elenco esatto; dopo la conferma aggiungili a `permissions.deny` in `<instance>/.claude/settings.json` (il modello parte vuoto perché i nomi dipendono dal server); verifica con `/permissions`.
- **Completamento:** lettura di un ticket riuscita; tool di scrittura in `deny`.
- **Stato:** `jira_write_tools`, `phases.1 = done`.

## Fase 2 — Credenziali del database e ping

- **Obiettivo:** il server `plm-db` si connette con l'utente in sola lettura confermato dal DBA.
- **Via consigliata — keyring.** Lascia vuoti i campi DB nelle opzioni del plugin, **soprattutto la password**: un valore inserito lì ha la precedenza sul keyring, e un valore sensibile non si corregge facilmente. Stampa per il terminale dell'utente (PowerShell, percorsi espansi):

  ```powershell
  $env:PLM_INSTANCE_DIR = "<instance assoluto>"
  uv run --directory "<CLAUDE_PLUGIN_ROOT espanso>\server" plm-db set-credentials
  uv run --directory "<CLAUDE_PLUGIN_ROOT espanso>\server" plm-db check
  ```

  Nessun riavvio: quando `check` riesce, chiama `ping`. Se un campo DB è già nelle opzioni del plugin e va cambiato, correggilo lì e riavvia. Per la futura esecuzione automatica valgono le variabili `PLM_DB_*`.
- **PUNTO DI CONTROLLO:** "Esegui i comandi nel tuo terminale e dimmi l'esito di `plm-db check`. Non incollare password o altri dati riservati."
- **Completamento:** `ping` riuscito e `instance_dir` coincidente. Se fallisce, controlla rete/VPN, porta, nome del database, versione TDS; non mostrare mai la stringa di connessione.
- **Stato:** `phases.2 = done` (nessun segreto nello stato).

## Fase 3 — Repository di istanza (team)

- **Obiettivo:** repository git **privato** del team con il contenuto dell'istanza.
- **Cosa fa Claude:** se l'istanza è stata clonata in fase 0, verifica che sia aggiornata e salta la fase (`skipped`). Altrimenti controlla `.gitignore` (`logs/`, `inbox/*`, `setup-state.json`), sostituisce i segnaposto in `CLAUDE.md` e prepara il primo commit.
- **PUNTO DI CONTROLLO:** "Crea un repository **privato** sul vostro server git e incolla qui il suo URL. Conferma anche che solo il team ha accesso al repository." Poi Claude aggiunge il remote e fa il push solo dopo la conferma.
- **Messaggio per i colleghi:** dopo il push riuscito, stampa questo messaggio pronto da inoltrare, con l'URL del remote al posto del segnaposto, e di' all'utente di inviarlo ai colleghi che useranno plm-triage:

  ```text
  Per usare plm-triage con il nostro team:

  1. In Claude Code, da qualsiasi cartella, installa il plugin:
     /plugin marketplace add matteobadini/plm-triage
     /plugin install plm-triage@plm-triage

  2. Poi incolla questo messaggio (deve iniziare con /plm-triage:setup):
     /plm-triage:setup guidami fino al collaudo su ticket reali, fermati a ogni punto di controllo

  3. Alla domanda sul repository di istanza rispondi sì e incolla questo URL:
     <URL del repository di istanza>
  ```
- **Completamento:** push riuscito; `git status` pulito; messaggio per i colleghi stampato.
- **Stato:** `phases.3 = done`, URL del remote in `notes`.

## Fase 4 — Catalogo query (team)

- **Obiettivo:** query con nome, approvate, in `<instance>/catalog/`.
- **Cosa fa Claude:** chiede al collega di copiare le query che usa già in `<instance>/inbox/`. Per ciascuna: la converte in `catalog/<nome>.sql` con l'intestazione (formato in `catalog/README.md`), sostituisce i valori letterali con parametri `@param` dichiarati, scarta ciò che non è una singola `SELECT`/`WITH`. Mostra il file completo. **Solo dopo l'approvazione del file** chiama `run_query` una volta con i valori di prova forniti dall'utente; registra righe, `truncated` e durata, e propone valori adeguati per `timeout_s` e `max_rows`. Il catalogo viene riletto a ogni chiamata: se una query non compare in `list_queries`, controlla che il nome del file non inizi con `_` (file ignorati) e leggi l'errore di caricamento riportato dal server.
- **PUNTO DI CONTROLLO:** per ogni file: "Approvi `catalog/<nome>.sql` così com'è?" e poi "Con quali valori di prova posso eseguirla?". Alla fine: "Posso fare il commit del catalogo?"
- **Completamento:** ogni query approvata eseguita una volta senza errori; commit dopo la conferma.
- **Stato:** `phases.4 = done`, in `notes` per ogni query: righe, durata in ms.

## Fase 5 — Categorie e config.yaml (team)

- **Obiettivo:** `config.yaml` compilato: Jira, categorie con le query associate, condizioni di escalation.
- **Cosa fa Claude:** breve intervista (tipi di ticket ricorrenti, come si risolvono, quali query servono, cosa va sempre in escalation, a chi va l'escalation, etichette). In sola lettura cerca su Jira i ticket chiusi degli ultimi mesi (con una JQL proposta all'utente), legge riepilogo e soluzione, e propone una bozza di categorie con frequenza ed esempi (solo chiavi dei ticket, niente testo). Compila `config.yaml` con `mode: shadow`.
- **PUNTO DI CONTROLLO:** "Approvi questa JQL e questo periodo per l'analisi?" e poi "Approvi categorie, query associate e condizioni di escalation in `config.yaml`?"
- **Completamento:** `config.yaml` senza segnaposto, ogni query citata presente in `list_queries`; commit dopo la conferma.
- **Stato:** `phases.5 = done`.

## Fase 6 — Valutazione di prova

- **Obiettivo:** misurare la qualità del triage su ~30 ticket chiusi senza scrivere su Jira, secondo `${CLAUDE_PLUGIN_ROOT}/docs/e2e-protocol.md`.
- **Cosa fa Claude:** propone ~30 ticket chiusi distribuiti sulle categorie, compresi alcuni da escalation (per sceglierli bastano chiave e riepilogo). Verifica `mode: shadow`. Per **ogni ticket avvia un subagente nuovo** (tool Agent), così le soluzioni dei ticket precedenti non influenzano i successivi. Al subagente passa solo: cartella di istanza, chiave e modalità, con l'istruzione "esegui la skill `plm-triage:triage-ticket` con argomenti `<CHIAVE> come-aperto` e restituisci solo categoria, esito (risposta proposta | escalation) e percorso del file di traccia". La sessione principale non legge il ticket: raccoglie i file `evals/runs/<data>/<CHIAVE>.md` e aggiunge a `evals/grading.csv` una riga per ticket con `ticket_key` e `categoria_agente`, lasciando vuote le altre colonne per l'utente.
- **PUNTO DI CONTROLLO:** "Approvi questo elenco di ticket?" e poi "Compila `categoria_attesa`, `esito` (valori ammessi in `evals/README.md`) e `note` in `evals/grading.csv`, poi dimmi quando hai finito."
- **Completamento:** tutte le righe valutate; Claude calcola le metriche definite nel protocollo, più l'accuratezza complessiva e il dettaglio per categoria.
- **Stato:** `eval.date`, `eval.tickets`, `eval.metrics`, `phases.6 = done`.

## Fase 7 — Via libera

- **Obiettivo:** decidere se passare alla modalità operativa.
- **Cosa fa Claude:** confronta le metriche con le soglie del via libera in `${CLAUDE_PLUGIN_ROOT}/docs/e2e-protocol.md`. Se non sono raggiunte, analizza gli errori e propone correzioni a `config.yaml` o al catalogo (non al testo della skill: quello si cambia con una pull request sul repository pubblico); poi si ripete la fase 6 su un nuovo campione.
- **PUNTO DI CONTROLLO:** "Via libera <ottenuto | non ottenuto> (<metriche>). Vuoi procedere con il collaudo su ticket aperti?"
- **Completamento:** via libera ottenuto e conferma esplicita.
- **Stato:** `phases.7 = done` con le metriche in `notes`.

## Fase 8 — Collaudo

- **Obiettivo:** triage completo su 1-3 ticket aperti, con le scritture su Jira approvate una per una.
- **Cosa fa Claude:** propone `mode: live` e di togliere da `permissions.deny` **solo** i tool Jira strettamente necessari (commento e, se separati, etichetta e assegnatario), **senza** aggiungerli ad `allow`: così la richiesta di autorizzazione di Claude Code resta un secondo controllo, oltre alla conferma chiesta dalla skill. Avvisa che su Rovo etichetta e assegnatario possono passare da un tool generico di modifica del ticket, che può cambiare anche altri campi: ogni chiamata va approvata leggendone gli argomenti. Verifica con `/permissions`, poi esegue `triage-ticket` sui ticket scelti dall'utente; per ogni scrittura mostra il contenuto esatto e attende un "sì".
- **PUNTO DI CONTROLLO:** "Approvi questa modifica ai permessi (`deny`)?" poi "Su quali ticket aperti facciamo il collaudo (da 1 a 3)?" e, per ogni scrittura, "Pubblico questo commento? / Applico questa etichetta? / Assegno il ticket a <utente>?"
- **Completamento:** scritture verificate rileggendo il ticket su Jira; file di traccia salvati.
- **Stato:** `phases.8 = done`.

**Riepilogo finale:** stato di ogni fase, metriche del via libera, ticket usati per il collaudo, impostazioni attive (`mode`, tool negati) e prossimi passi (ripetere la fase 6 dopo modifiche a catalogo, categorie o versione del plugin).

## Setup ridotto — colleghi che arrivano dopo

Se il repository di istanza del team esiste già, con il catalogo e `config.yaml` compilati:

1. Fasi 0, 1, 2 come sopra (personali, consenso compreso).
2. Fasi 3-5 `skipped` (già fatte dal team); fasi 6-7 ereditate dal team.
3. **Prova rapida:** chiedi all'utente un ticket chiuso, esegui il triage `come-aperto` in un subagente nuovo come in fase 6 e confronta il risultato con la soluzione reale insieme all'utente.
4. PUNTO DI CONTROLLO: "Il risultato della prova è coerente con la soluzione reale del ticket?" Se sì, il setup personale è completo.
