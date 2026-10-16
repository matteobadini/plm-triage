# AGENTS.md

Istruzioni per agenti (e persone) che lavorano **su questo repo pubblico**. Non riguarda l'uso del plugin in un'istanza: per quello vedi `instance-template/CLAUDE.md`.

## Mappa del repo

| Percorso | Contenuto |
|---|---|
| `.claude-plugin/plugin.json` | manifest: `userConfig`, MCP `plm-db` inline |
| `.claude-plugin/marketplace.json` | marketplace `plm-triage`, plugin con `source: "."` |
| `skills/triage-ticket/SKILL.md` | procedura di triage (principi, passi, preflight, escalation) |
| `skills/triage-ticket/templates.md` | template bozza di risposta e hand-off di escalation |
| `skills/setup/SKILL.md` | setup a fasi con checkpoint, stato in `<istanza>/setup-state.json` |
| `server/` | MCP locale `plm-db` (pacchetto `plm_db_mcp`, CLI `plm-db-mcp` e `plm-db`), test in `server/tests/` |
| `instance-template/` | scheletro del repo istanza privato: `CLAUDE.md`, `.claude/settings.json`, `config.yaml`, `catalog/`, `inbox/`, `evals/` |
| `docs/` | architettura, setup, protocollo E2E, ADR |
| `.github/workflows/ci.yml` | ruff + pytest (ubuntu, windows), gitleaks |

## Regole non negoziabili

1. **Nessun dato cliente**, mai: niente nomi di clienti, testi di ticket, hostname interni, schema reale. Gli esempi usano uno schema fittizio (`DEMO_ITEM`, `DEMO_CHANGE`). La conoscenza generica di Agile PLM è ammessa solo se marcata "da verificare sull'istanza".
2. **Nessuna credenziale** nel repo, nemmeno di test. Le credenziali vivono nel processo del server MCP (userConfig sensitive, keyring, env).
3. **Lingue**: documentazione, skill e template in italiano; codice, identificatori, commenti nel codice e messaggi di commit in inglese.
4. **Essenzialità**: nessun file che non si guadagni il posto. Niente router, playbook, file di principi, hook.
5. **Niente SQL libero**: il server espone solo `ping`, `list_queries`, `describe_query`, `run_query`. Non aggiungere tool che eseguano SQL arbitrario.
6. Non affermare fatti su Claude Code non verificati sulla documentazione ufficiale.

## Comandi

```bash
cd server && uv sync              # dipendenze (uv.lock committato)
cd server && uv run pytest        # test offline (connessione finta)
cd server && uv run ruff check . && uv run ruff format --check .
claude plugin validate ./         # manuale, non in CI (richiede Claude Code)
claude --plugin-dir ./            # prova locale del plugin
```

## Aggiungere una query di esempio

1. Crea `instance-template/catalog/_example_<nome>.sql` con l'header YAML nel blocco iniziale `/* --- ... --- */` (`name`, `description`, `when_to_use`, `params`, `max_rows`, `timeout_s`, `isolation`). Formato in `instance-template/catalog/README.md`.
2. Solo `SELECT`/`WITH`, un'istruzione, parametri come `@param` tutti dichiarati, tabelle fittizie.
3. `uv run pytest`: un test carica tutti gli esempi del catalogo.

Le query reali stanno solo nel repo istanza privato.

## Cambiare uno skill

- I passi di `triage-ticket` vengono copiati verbatim nella task list: rinumerare o riformulare cambia il comportamento. Tieni i passi brevi e verificabili.
- I trigger di escalation sono regole, non giudizi: se ne aggiungi uno, aggiorna `instance-template/config.yaml` e `docs/e2e-protocol.md` se cambia la rubrica.
- Un cambio di procedura richiede di ripetere la shadow eval sull'istanza prima di tornare live.

## Versioning

SemVer. Ogni modifica rilasciata: bump di `version` in `.claude-plugin/plugin.json` e voce in `CHANGELOG.md` (Keep a Changelog).

## Definition of done

- [ ] ruff e pytest verdi; `claude plugin validate ./` senza errori
- [ ] nessun dato cliente o credenziale (gitleaks verde, rilettura del diff)
- [ ] documentazione aggiornata dove cambia il comportamento
- [ ] version + CHANGELOG aggiornati
- [ ] ADR se la modifica rientra nei casi sotto

## Quando scrivere un ADR

Quando cambi una decisione già registrata in `docs/adr/`, o ne prendi una che vincola chi viene dopo: confine di sicurezza, modello di accesso a DB o Jira, gestione credenziali, livello di autonomia, struttura del plugin. Formato in `docs/adr/README.md`.
