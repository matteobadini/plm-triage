---
name: setup
description: Setup guidato e riprendibile di plm-triage — prerequisiti, consenso, cartella istanza, Jira MCP, credenziali DB, catalogo query, tassonomia, valutazione shadow, gate e prova live — con checkpoint umani.
disable-model-invocation: true
---

# Setup plm-triage

Indicazioni dell'utente: `$ARGUMENTS`

Setup a fasi. Ogni fase ha un **CHECKPOINT UMANO**: non passare alla fase successiva senza la risposta o l'azione richiesta. Le fasi 0-2 sono personali; le fasi 3-5 sono di team (il risultato è condiviso nel repo istanza); 6-8 si fanno una volta per team e si ripetono dopo cambi rilevanti. Panoramica per le persone: `${CLAUDE_PLUGIN_ROOT}/docs/setup.md`.

## Regole del setup

- **Riprendi, non ricominciare.** Individua la cartella istanza: `${user_config.instance_dir}` se valorizzato (non vuoto, senza `${`), altrimenti la directory corrente se contiene `setup-state.json`. Se la trovi, leggi `<instance>/setup-state.json`, riepiloga cosa è già fatto e riparti dalla prima fase non `done`. Se non la trovi, parti dalla fase 0.
- **Consenso prima dei dati.** Senza `consent.confirmed: true` in `setup-state.json` non leggere nessun ticket reale né riga del DB: torna al checkpoint di consenso della fase 0.
- **Mai password o token in chat.** Le credenziali si inseriscono solo nel terminale dell'utente (`plm-db set-credentials`, `claude mcp add`) o nel prompt del plugin. Se l'utente incolla un segreto in chat, digli di ruotarlo e non riusarlo.
- **Sola lettura** su Jira e DB fino alla fase 8. DB solo via tool `plm-db`.
- **Riavvio solo quando serve:** dopo aver cambiato le opzioni del plugin (`instance_dir`, campi DB) o registrato un server MCP. **Non** serve dopo modifiche al catalogo o alle credenziali nel keyring: il server le rilegge a ogni chiamata. Quando serve, dillo, salva lo stato e fermati.
- **Comandi per il terminale dell'utente:** stampali completi, con percorsi assoluti già espansi (niente `${...}`), in sintassi PowerShell.
- **Niente dati cliente nel repo pubblico.** Tutto ciò che è specifico va nel repo istanza.

Stato in `<instance>/setup-state.json` (personale, in `.gitignore`):

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

## Fase 0 — Prerequisiti, consenso, cartella istanza

Si esegue anche senza nulla di clonato, da qualunque cartella.

1. **Prerequisiti.** Verifica `claude --version` (versione recente), `uv --version`, `git --version`. Se manca qualcosa, indica come installarlo; su Windows, dopo aver installato uv, va aperto un **nuovo** terminale.
2. **Dipendenze del server.** `uv sync --directory "${CLAUDE_PLUGIN_ROOT}/server"` (scarica le dipendenze una volta, così il primo avvio di `plm-db` è rapido).
3. **Cartella istanza.** Chiedi se il team ha già un repo istanza privato. Se sì: `git clone <URL> <percorso scelto dall'utente>`. Se no (primo collega del team): copia `${CLAUDE_PLUGIN_ROOT}/instance-template/` (inclusi i file nascosti `.claude/` e `.gitignore`) nel percorso scelto dall'utente ed esegui `git init`. Crea `setup-state.json` con `instance_dir` assoluto.
4. **Verifiche sul web (solo qui).** Nell'istanza i tool web sono negati, quindi fai ora le ricerche che servono dopo. Chiedi l'URL base di Jira: `*.atlassian.net` → Cloud, altrimenti Data Center (conferma con l'utente). Cloud: sulla documentazione Atlassian del Remote MCP Server (Rovo) verifica endpoint attuale e autenticazione. Data Center: sul README di `sooperset/mcp-atlassian` verifica comando di avvio e variabili per URL e PAT. Registra tutto in `jira` dello stato, con le URL delle fonti.
5. **CHECKPOINT UMANO — consenso.** Prima di leggere qualunque ticket o riga reale, chiedi conferma esplicita di tre punti e registrali in `consent`:
   - stai usando un piano Claude **aziendale** (Team o Enterprise), non personale;
   - il cliente ha dato l'**OK scritto** al trattamento dei dati (ticket e risultati delle query passano dal modello);
   - il **DBA** ha confermato che il login DB è in sola lettura (idealmente su viste dedicate).

   Se anche uno solo manca: `consent.confirmed: false`, spiega cosa serve e **fermati**; il setup non prosegue.
6. **CHECKPOINT UMANO — opzione e riavvio.** "Imposta l'opzione del plugin `instance_dir` = `<percorso>` (da `/plugin` → opzioni del plugin, oppure `/config`, a seconda della versione). Poi chiudi Claude Code, riaprilo **nella cartella istanza** (`cd <percorso>` e `claude`), accetta l'abilitazione del plugin proposta da `.claude/settings.json` e rilancia `/plm-triage:setup`: riprendo da qui."

- **Completamento (verificato alla ripresa):** prerequisiti presenti; directory corrente = `instance_dir` dello stato; `ping` di `plm-db` riporta lo stesso `instance_dir` (lo riporta anche quando fallisce per le credenziali DB, che si fanno in fase 2); `consent.confirmed: true`.
- **Stato:** `phases.0 = done`. Se l'istanza clonata ha già catalogo e `config.yaml` compilato, segui il percorso rapido (in fondo).

## Fase 1 — Jira MCP

- **Obiettivo:** server MCP Jira registrato a scope utente con nome `jira`, in sola lettura durante shadow.
- **Cosa fa Claude:** prepara il comando `claude mcp add --scope user jira ...` con i valori di `jira` registrati in fase 0 (non rifare ricerche web). Data Center: il PAT lo inserisce l'utente nel proprio terminale, mai in chat; avvisa che con `-e <VAR>=<PAT>` il token resta in `~/.claude.json` e nella cronologia della shell: proponi di leggerlo in PowerShell con `Read-Host -AsSecureString` in una variabile da passare al comando, e di ripulire poi la cronologia.
- **CHECKPOINT UMANO:** "Esegui nel tuo terminale: `<comando>`. Poi riavvia Claude Code nella cartella istanza (per Cloud completa l'autenticazione OAuth da `/mcp`) e rilancia `/plm-triage:setup`."
- **Dopo il riavvio:** elenca i tool `mcp__jira__*` e leggi un ticket indicato dall'utente. Individua i tool che scrivono (creazione, modifica, commento, transizione, assegnazione, etichette, eliminazione, upload) e proponi l'elenco esatto; dopo conferma aggiungili a `permissions.deny` in `<instance>/.claude/settings.json` (il template parte vuoto perché i nomi dipendono dal server); verifica con `/permissions`.
- **Completamento:** lettura di un ticket riuscita; tool di scrittura in `deny`.
- **Stato:** `jira_write_tools`, `phases.1 = done`.

## Fase 2 — Credenziali DB e ping

- **Obiettivo:** il server `plm-db` si connette con l'utente di sola lettura confermato dal DBA.
- **Via raccomandata — keyring.** Lascia vuoti i campi DB nel prompt del plugin, **soprattutto la password**: un valore inserito lì ha la precedenza sul keyring e un valore sensibile non si corregge facilmente. Stampa per il terminale dell'utente (PowerShell, percorsi espansi):

  ```powershell
  $env:PLM_INSTANCE_DIR = "<instance assoluto>"
  uv run --directory "<CLAUDE_PLUGIN_ROOT espanso>\server" plm-db set-credentials
  uv run --directory "<CLAUDE_PLUGIN_ROOT espanso>\server" plm-db check
  ```

  Nessun riavvio: dopo `check` ok, chiama `ping`. Se un campo DB è già nelle opzioni del plugin e va cambiato, correggilo lì e riavvia. Per l'headless futuro valgono le variabili `PLM_DB_*`.
- **CHECKPOINT UMANO:** "Esegui i comandi nel tuo terminale e dimmi l'esito di `plm-db check` (senza incollare segreti)."
- **Completamento:** `ping` ok e `instance_dir` coincidente. Se fallisce: rete/VPN, porta, nome database, versione TDS; mai mostrare la stringa di connessione.
- **Stato:** `phases.2 = done` (nessun segreto nello stato).

## Fase 3 — Repo istanza (team)

- **Obiettivo:** repo git **privato** del team con il contenuto dell'istanza.
- **Cosa fa Claude:** se l'istanza è stata clonata in fase 0, verifica che sia aggiornata e salta (`skipped`). Altrimenti controlla `.gitignore` (`logs/`, `inbox/*`, `setup-state.json`), sostituisce i segnaposto in `CLAUDE.md` e prepara il primo commit.
- **CHECKPOINT UMANO:** "Crea un repository **privato** sul vostro host git e dammi l'URL. Conferma che solo il team vi ha accesso." Poi Claude aggiunge il remote e fa push solo dopo conferma.
- **Completamento:** push riuscito; `git status` pulito.
- **Stato:** `phases.3 = done`, URL del remote in `notes`.

## Fase 4 — Catalogo query (team)

- **Obiettivo:** query nominate e approvate in `<instance>/catalog/`.
- **Cosa fa Claude:** chiede al collega di mettere le query salvate in `<instance>/inbox/`. Per ciascuna: la converte in `catalog/<nome>.sql` con header (formato in `catalog/README.md`), sostituisce i valori letterali con parametri `@param` dichiarati, scarta ciò che non è una singola `SELECT`/`WITH`. Mostra il file completo. **Solo dopo l'approvazione del file** chiama `run_query` una volta con parametri di prova forniti dall'utente; registra righe, `truncated` e durata, e propone `timeout_s`/`max_rows` coerenti. Il catalogo è riletto a ogni chiamata: se una query non compare in `list_queries`, controlla che il nome del file non inizi con `_` (file ignorati) e l'errore di caricamento riportato dal server.
- **CHECKPOINT UMANO:** per ogni file: "Approvi `catalog/<nome>.sql` così com'è?" e poi "Valori di prova per i parametri?". Alla fine: "Approvi il commit del catalogo?"
- **Completamento:** ogni query approvata eseguita una volta senza errori; commit dopo conferma.
- **Stato:** `phases.4 = done`, in `notes` per query: righe, durata ms.

## Fase 5 — Tassonomia e config.yaml (team)

- **Obiettivo:** `config.yaml` compilato: Jira, categorie con query associate, trigger di escalation.
- **Cosa fa Claude:** intervista breve (tipi di ticket ricorrenti, come si risolvono, quali query servono, cosa non va mai risolto in automatico, a chi va l'escalation, etichette). In sola lettura cerca su Jira i ticket chiusi degli ultimi mesi (JQL proposta all'utente), legge riepilogo e risoluzione, e propone una bozza di categorie con frequenza ed esempi (solo chiavi, niente testo). Compila `config.yaml` con `mode: shadow`.
- **CHECKPOINT UMANO:** "Approvi JQL e periodo per l'analisi?" poi "Approvi categorie, query associate e trigger di escalation in `config.yaml`?"
- **Completamento:** `config.yaml` senza segnaposto, ogni query citata presente in `list_queries`; commit dopo conferma.
- **Stato:** `phases.5 = done`.

## Fase 6 — Valutazione shadow

- **Obiettivo:** misurare il triage su ~30 ticket chiusi senza scrivere su Jira, secondo `${CLAUDE_PLUGIN_ROOT}/docs/e2e-protocol.md`.
- **Cosa fa Claude:** propone ~30 ticket chiusi distribuiti sulle categorie, inclusi alcuni da escalation (per sceglierli bastano chiave e riepilogo). Verifica `mode: shadow`. Per **ogni ticket avvia un subagente nuovo** (tool Agent), così le risoluzioni dei ticket precedenti non contaminano i successivi. Al subagente passa solo: cartella istanza, chiave e modalità, con l'istruzione "esegui la skill `plm-triage:triage-ticket` con argomenti `<CHIAVE> come-aperto` e restituisci solo categoria, esito (risposta proposta | escalation) e percorso del file di run". La sessione principale non legge il ticket: raccoglie i file `evals/runs/<data>/<CHIAVE>.md` e aggiunge a `evals/grading.csv` una riga per ticket con `ticket_key` e `categoria_agente`, lasciando vuote le altre colonne per l'umano.
- **CHECKPOINT UMANO:** "Approvi questo elenco di ticket?" poi "Compila `categoria_attesa`, `esito` (valori in `evals/README.md`) e `note` in `evals/grading.csv` e dimmi quando hai finito."
- **Completamento:** tutte le righe valutate; Claude calcola le metriche definite nel protocollo, più accuratezza e dettaglio per categoria.
- **Stato:** `eval.date`, `eval.tickets`, `eval.metrics`, `phases.6 = done`.

## Fase 7 — Gate

- **Obiettivo:** decidere se andare live.
- **Cosa fa Claude:** applica il gate di `${CLAUDE_PLUGIN_ROOT}/docs/e2e-protocol.md` alle metriche. Se non passa, analizza gli errori e propone correzioni a `config.yaml` o al catalogo (non al testo dello skill: quello si cambia con una PR sul repo pubblico), poi si ripete la fase 6 su un nuovo campione.
- **CHECKPOINT UMANO:** "Il gate è <superato | non superato> (<metriche>). Vuoi procedere alla prova live?"
- **Completamento:** gate superato e conferma esplicita.
- **Stato:** `phases.7 = done` con le metriche in `notes`.

## Fase 8 — Prova live E2E

- **Obiettivo:** triage completo su 1-3 ticket aperti, con scritture su Jira approvate una per una.
- **Cosa fa Claude:** propone `mode: live` e di togliere da `permissions.deny` **solo** i tool Jira strettamente necessari (commento e, se separati, etichetta e assegnatario), **senza** aggiungerli ad `allow`: così il prompt di permesso di Claude Code resta un secondo controllo oltre alla conferma della skill. Avvisa che su Rovo etichetta e assegnatario possono passare da un tool generico di modifica del ticket che può cambiare anche altri campi: ogni chiamata va approvata leggendone gli argomenti. Verifica con `/permissions`, poi esegue `triage-ticket` sui ticket scelti dall'utente; per ogni scrittura mostra il contenuto esatto e attende un "sì".
- **CHECKPOINT UMANO:** "Approvi questa modifica a `deny`?" poi "Quali 1-3 ticket aperti usiamo?" e, per ogni scrittura, "Pubblico questo commento / applico questa etichetta / assegno a <utente>?"
- **Completamento:** scritture verificate rileggendo il ticket su Jira; file di run salvati.
- **Stato:** `phases.8 = done`.

**Riepilogo finale:** stato di ogni fase, metriche del gate, ticket della prova live, impostazioni attive (`mode`, tool negati) e prossimi passi (ripetere la fase 6 dopo modifiche a catalogo, categorie o versione del plugin).

## Percorso rapido — collega successivo

Se il repo istanza del team esiste già con catalogo e `config.yaml` compilato:

1. Fasi 0, 1, 2 come sopra (personali, consenso incluso).
2. Fasi 3-5 `skipped` (fatte dal team); fasi 6-7 ereditate dal team.
3. **Smoke test:** chiedi all'utente un ticket chiuso, esegui il triage `come-aperto` in un subagente nuovo come in fase 6 e confronta l'esito con la risoluzione reale insieme all'utente.
4. CHECKPOINT UMANO: "L'esito dello smoke test è coerente con la risoluzione reale?" Se sì, il setup personale è completo.
