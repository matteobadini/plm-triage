---
name: setup
description: Guided, resumable setup of plm-triage — prerequisites, consent, instance folder, Jira MCP server, database credentials, query catalog, categories, valutazione di prova, via libera and collaudo — with human checkpoints. User-invoked only, via /plm-triage:setup (e.g. "/plm-triage:setup guidami fino al collaudo").
disable-model-invocation: true
---

# plm-triage setup

User instructions: `$ARGUMENTS`

Phased setup. Every phase has a **HUMAN CHECKPOINT** (PUNTO DI CONTROLLO): stop there and do not move to the next phase without the answer or action requested from the user. Phases 0-2 are personal; phases 3-5 are team phases (the result is shared in the instance repository); phases 6-8 are done once per team and repeated after relevant changes. Overview for people: `${CLAUDE_PLUGIN_ROOT}/docs/setup.md`.

## Language

Always communicate with the user in Italian: questions, summaries, explanations, errors, status recaps. Write any Jira comment and every local trace file in Italian. Strings marked "verbatim, Italian" must be shown exactly as written, with only the `<...>` placeholders replaced.

Use these Italian terms with the user (English → Italian):

| Concept | Term to use |
|---|---|
| the team's private git repository | repository di istanza |
| its local clone | cartella di istanza |
| `mode: shadow` | modalità di prova |
| `mode: live` | modalità operativa |
| phase 6 (shadow evaluation) | valutazione di prova |
| phase 7 (go/no-go gate) | via libera |
| phase 8 (first live run) | collaudo |
| human checkpoint | punto di controllo |
| preflight checks | controlli preliminari |
| escalation hand-off | passaggio di consegne |
| reduced-setup smoke test | prova rapida |
| trace file | file di traccia |

## Setup rules

- **Resume, don't restart.** Locate the instance folder: `${user_config.instance_dir}` if set (not empty, without `${`), otherwise the current directory if it contains `setup-state.json`. If you find it, read `<instance>/setup-state.json`, summarize what is already done, and resume from the first phase that is not `done`. If you do not find it, start from phase 0.
- **Consent before data.** Without `consent.confirmed: true` in `setup-state.json`, do not read any real ticket or database row: go back to the consent checkpoint of phase 0.
- **Never passwords or tokens in chat.** Credentials are entered only in the user's terminal (`plm-db set-credentials`, `claude mcp add`) or in the plugin options. If the user pastes a secret in chat, tell them to change it and do not use it.
- **Read-only** on Jira and the database until phase 8. Database only through the `plm-db` tools.
- **Restart only when needed:** after changing plugin options (`instance_dir`, DB fields) or registering an MCP server. A restart is **not** needed after changes to the catalog or to the keyring credentials: the server rereads them on every call. When a restart is needed, say so, save the state and stop.
- **Commands for the user's terminal:** print them in full, with absolute paths already expanded (no `${...}`), in PowerShell syntax.
- **No customer data in the public repository.** Everything specific goes into the instance repository.

State in `<instance>/setup-state.json` (personal, excluded from git via `.gitignore`):

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

After every phase, update `status`, `at` and `notes`.

## Phase 0 — Prerequisites, consent, instance folder

Runs even with nothing cloned, from any folder.

1. **Prerequisites.** Check `claude --version` (recent version), `uv --version`, `git --version`. If something is missing, explain how to install it; on Windows, after installing uv, a **new** terminal must be opened.
2. **Server dependencies.** `uv sync --directory "${CLAUDE_PLUGIN_ROOT}/server"` (downloads the dependencies once, so the first start of `plm-db` is fast).
3. **Instance folder.** Ask (verbatim, Italian): "Il tuo team ha già un repository di istanza di plm-triage, cioè il repository git privato con configurazione e query? Se sì, incolla qui il suo URL (HTTPS o SSH). Se non hai l'URL, chiedilo al collega che ha fatto il primo setup: lo trova nel messaggio di fine fase 3. Oppure copialo dalla pagina del repository privato sul vostro server git."
   - **Yes:** accept both HTTPS URLs (`https://...`) and SSH URLs (`git@<host>:...` or `ssh://...`), then `git clone <URL> <path chosen by the user>`.
   - **No** (first colleague on the team): copy `${CLAUDE_PLUGIN_ROOT}/instance-template/` (including the hidden files `.claude/` and `.gitignore`) to the path chosen by the user and run `git init`.
   - **Don't know:** do not create a new instance. Tell the user to check with the team first, because a second instance repository would split catalog and configuration; then stop.

   Create `setup-state.json` with the absolute `instance_dir`.
4. **Web checks (only here).** Web tools are denied in the instance, so do now the searches that will be needed later. Ask for the Jira base URL: `*.atlassian.net` → Cloud, otherwise Data Center (confirm with the user). Cloud: on the Atlassian documentation for the Remote MCP Server (Rovo), verify the current endpoint and authentication. Data Center: on the README of `sooperset/mcp-atlassian`, verify the start command and the variables for URL and PAT. Record everything in the state's `jira`, with the source URLs.
5. **HUMAN CHECKPOINT — consent.** Before reading any real ticket or row, ask for explicit confirmation of these three points (in Italian) and record them in `consent`:
   - stai usando un piano Claude **aziendale** (Team o Enterprise), non personale;
   - il cliente ha dato l'**autorizzazione scritta** al trattamento dei dati (il testo dei ticket e i risultati delle query passano dal modello);
   - il **DBA** ha confermato che il login del database è in sola lettura (meglio se su viste dedicate).

   If even one is missing: `consent.confirmed: false`, explain what is needed and **stop**; the setup does not continue.
6. **HUMAN CHECKPOINT — option and restart.** Say (verbatim, Italian): "Imposta l'opzione del plugin `instance_dir` = `<percorso>` (da `/plugin` → opzioni del plugin, oppure da `/config`, a seconda della versione). Poi chiudi Claude Code e riaprilo **nella cartella di istanza** (`cd <percorso>` e poi `claude`). Accetta l'abilitazione del plugin proposta da `.claude/settings.json` e rilancia `/plm-triage:setup`: riprendo da qui."

- **Completion (verified on resume):** prerequisites present; current directory = the state's `instance_dir`; `plm-db`'s `ping` reports the same `instance_dir` (it reports it even when it fails because of the database credentials, which are set in phase 2); `consent.confirmed: true`.
- **State:** `phases.0 = done`. If the cloned instance already has the catalog and a filled-in `config.yaml`, follow the reduced setup (at the end).

## Phase 1 — Jira MCP server

- **Goal:** Jira MCP server registered at user level with the name `jira`, read-only during modalità di prova.
- **What Claude does:** prepare the command `claude mcp add --scope user jira ...` with the `jira` values recorded in phase 0 (do not redo web searches). Data Center: the user enters the PAT in their own terminal, never in chat. Warn that with `-e <VAR>=<PAT>` the token remains in `~/.claude.json` and in the shell history: suggest reading it in PowerShell with `Read-Host -AsSecureString` into a variable to pass to the command, and clearing the history afterwards.
- **HUMAN CHECKPOINT:** say (verbatim, Italian): "Esegui nel tuo terminale: `<comando>`. Poi riavvia Claude Code nella cartella di istanza (se usate Jira Cloud, completa l'accesso OAuth da `/mcp`) e rilancia `/plm-triage:setup`."
- **After the restart:** list the `mcp__jira__*` tools and read a ticket indicated by the user. Identify the tools that write (create, edit, comment, transition, assign, labels, delete, upload) and propose the exact list; after confirmation, add them to `permissions.deny` in `<instance>/.claude/settings.json` (the template starts empty because the names depend on the server); verify with `/permissions`.
- **Completion:** ticket read succeeded; write tools in `deny`.
- **State:** `jira_write_tools`, `phases.1 = done`.

## Phase 2 — Database credentials and ping

- **Goal:** the `plm-db` server connects with the read-only user confirmed by the DBA.
- **Recommended path — keyring.** Leave the DB fields in the plugin options empty, **especially the password**: a value entered there takes precedence over the keyring, and a sensitive value is not easy to correct. Print for the user's terminal (PowerShell, expanded paths):

  ```powershell
  $env:PLM_INSTANCE_DIR = "<instance assoluto>"
  uv run --directory "<CLAUDE_PLUGIN_ROOT espanso>\server" plm-db set-credentials
  uv run --directory "<CLAUDE_PLUGIN_ROOT espanso>\server" plm-db check
  ```

  No restart: when `check` succeeds, call `ping`. If a DB field is already in the plugin options and must be changed, fix it there and restart. For future automated runs, the `PLM_DB_*` variables apply.
- **HUMAN CHECKPOINT:** say (verbatim, Italian): "Esegui i comandi nel tuo terminale e dimmi l'esito di `plm-db check`. Non incollare password o altri dati riservati."
- **Completion:** `ping` succeeded and `instance_dir` matches. If it fails, check network/VPN, port, database name, TDS version; never show the connection string.
- **State:** `phases.2 = done` (no secret in the state).

## Phase 3 — Instance repository (team)

- **Goal:** the team's **private** git repository with the instance content.
- **What Claude does:** if the instance was cloned in phase 0, verify it is up to date and skip the phase (`skipped`). Otherwise check `.gitignore` (`logs/`, `inbox/*`, `setup-state.json`), replace the placeholders in `CLAUDE.md` and prepare the first commit.
- **HUMAN CHECKPOINT:** say (verbatim, Italian): "Crea un repository **privato** sul vostro server git e incolla qui il suo URL. Conferma anche che solo il team ha accesso al repository." Then add the remote and push only after the confirmation.
- **Message for colleagues:** after a successful push, print this ready-to-forward message (verbatim, Italian), with the remote URL in place of the placeholder, and tell the user to send it to the colleagues who will use plm-triage:

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
- **Completion:** push succeeded; `git status` clean; message for colleagues printed.
- **State:** `phases.3 = done`, remote URL in `notes`.

## Phase 4 — Query catalog (team)

- **Goal:** named, approved queries in `<instance>/catalog/`.
- **What Claude does:** ask the colleague to copy the queries they already use into `<instance>/inbox/`. For each: convert it to `catalog/<nome>.sql` with the header (format in `catalog/README.md`), replace literal values with declared `@param` parameters, discard anything that is not a single `SELECT`/`WITH`. Show the full file. **Only after the file is approved**, call `run_query` once with the test values provided by the user; record rows, `truncated` and duration, and propose suitable values for `timeout_s` and `max_rows`. The catalog is reread on every call: if a query does not appear in `list_queries`, check that the file name does not start with `_` (ignored files) and read the load error reported by the server.
- **HUMAN CHECKPOINT:** for each file, ask (verbatim, Italian): "Approvi `catalog/<nome>.sql` così com'è?" and then "Con quali valori di prova posso eseguirla?". At the end: "Posso fare il commit del catalogo?"
- **Completion:** every approved query run once without errors; commit after confirmation.
- **State:** `phases.4 = done`, in `notes` for each query: rows, duration in ms.

## Phase 5 — Categories and config.yaml (team)

- **Goal:** `config.yaml` filled in: Jira, categories with their linked queries, escalation conditions.
- **What Claude does:** short interview (recurring ticket types, how they are resolved, which queries are needed, what always goes to escalation, who receives the escalation, labels). In read-only mode, search Jira for tickets closed in recent months (with a JQL proposed to the user), read summary and resolution, and propose a draft of categories with frequency and examples (ticket keys only, no text). Fill in `config.yaml` with `mode: shadow`.
- **HUMAN CHECKPOINT:** ask (verbatim, Italian): "Approvi questa JQL e questo periodo per l'analisi?" and then "Approvi categorie, query associate e condizioni di escalation in `config.yaml`?"
- **Completion:** `config.yaml` without placeholders, every referenced query present in `list_queries`; commit after confirmation.
- **State:** `phases.5 = done`.

## Phase 6 — Valutazione di prova

- **Goal:** measure triage quality on ~30 closed tickets without writing to Jira, according to `${CLAUDE_PLUGIN_ROOT}/docs/e2e-protocol.md`.
- **What Claude does:** propose ~30 closed tickets spread across the categories, including some escalation cases (key and summary are enough to choose them). Verify `mode: shadow`. For **each ticket, start a fresh subagent** (Agent tool), so the solutions of earlier tickets do not influence later ones. Pass the subagent only: instance folder, key and mode, with the instruction (verbatim, Italian) "esegui la skill `plm-triage:triage-ticket` con argomenti `<CHIAVE> come-aperto` e restituisci solo categoria, esito (risposta proposta | escalation) e percorso del file di traccia". The main session does not read the ticket: it collects the `evals/runs/<data>/<CHIAVE>.md` files and appends to `evals/grading.csv` one row per ticket with `ticket_key` and `categoria_agente`, leaving the other columns empty for the user.
- **HUMAN CHECKPOINT:** ask (verbatim, Italian): "Approvi questo elenco di ticket?" and then "Compila `categoria_attesa`, `esito` (valori ammessi in `evals/README.md`) e `note` in `evals/grading.csv`, poi dimmi quando hai finito."
- **Completion:** all rows graded; compute the metrics defined in the protocol, plus overall accuracy and the per-category breakdown.
- **State:** `eval.date`, `eval.tickets`, `eval.metrics`, `phases.6 = done`.

## Phase 7 — Via libera

- **Goal:** decide whether to switch to modalità operativa.
- **What Claude does:** compare the metrics with the via libera thresholds in `${CLAUDE_PLUGIN_ROOT}/docs/e2e-protocol.md`. If they are not met, analyze the errors and propose fixes to `config.yaml` or to the catalog (not to the skill text: that is changed with a pull request on the public repository); then phase 6 is repeated on a new sample.
- **HUMAN CHECKPOINT:** ask (verbatim, Italian): "Via libera <ottenuto | non ottenuto> (<metriche>). Vuoi procedere con il collaudo su ticket aperti?"
- **Completion:** via libera obtained and explicit confirmation.
- **State:** `phases.7 = done` with the metrics in `notes`.

## Phase 8 — Collaudo

- **Goal:** full triage on 1-3 open tickets, with Jira writes approved one by one.
- **What Claude does:** propose `mode: live` and removing from `permissions.deny` **only** the strictly necessary Jira tools (comment and, if separate, label and assignee), **without** adding them to `allow`: this way Claude Code's permission prompt stays as a second check, on top of the confirmation requested by the skill. Warn that on Rovo, label and assignee may go through a generic ticket-edit tool that can also change other fields: every call must be approved after reading its arguments. Verify with `/permissions`, then run `triage-ticket` on the tickets chosen by the user; for each write, show the exact content and wait for a "sì".
- **HUMAN CHECKPOINT:** ask (verbatim, Italian): "Approvi questa modifica ai permessi (`deny`)?" then "Su quali ticket aperti facciamo il collaudo (da 1 a 3)?" and, for each write, "Pubblico questo commento? / Applico questa etichetta? / Assegno il ticket a <utente>?"
- **Completion:** writes verified by rereading the ticket on Jira; trace files saved.
- **State:** `phases.8 = done`.

**Final summary (in Italian):** status of each phase, via libera metrics, tickets used for the collaudo, active settings (`mode`, denied tools) and next steps (repeat phase 6 after changes to the catalog, categories or plugin version).

## Reduced setup — colleagues who join later

If the team's instance repository already exists, with the catalog and `config.yaml` filled in:

1. Phases 0, 1, 2 as above (personal, consent included).
2. Phases 3-5 `skipped` (already done by the team); phases 6-7 inherited from the team.
3. **Prova rapida:** ask the user for a closed ticket, run the triage `come-aperto` in a fresh subagent as in phase 6, and compare the result with the real solution together with the user.
4. HUMAN CHECKPOINT: ask (verbatim, Italian): "Il risultato della prova è coerente con la soluzione reale del ticket?" If yes, the personal setup is complete.
