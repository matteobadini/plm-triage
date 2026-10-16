# 0004 — Template pubblico, istanza privata

## Contesto

Il plugin deve essere installabile da un marketplace git e riusabile. Le query reali, la tassonomia, i ticket valutati e i dettagli dello schema sono materiale del cliente.

## Decisione

- **Repo pubblico** (`matteobadini/plm-triage`): plugin, server, docs e `instance-template/` con esempi su schema **fittizio** (`DEMO_ITEM`, `DEMO_CHANGE`). Nessun dato cliente, mai.
- **Repo istanza privato**, uno per team: `config.yaml`, `catalog/*.sql`, `evals/`, `CLAUDE.md`, `.claude/settings.json`, creato da `instance-template/`. I colleghi lo clonano e aprono Claude Code lì.
- Il `.gitignore` pubblico ignora `instance/` e `*.local.*` per chi crea per errore l'istanza dentro il clone.
- La conoscenza generica di Agile PLM (codici di classe numerici, `NODETABLE`, `LISTENTRY`, tabelle di pagina due/tre) può comparire solo come conoscenza di prodotto, marcata "da verificare sull'istanza".

## Alternative considerate

- **Un solo repo privato con tutto**: rifiutato. Il plugin non sarebbe riusabile e il marketplace richiederebbe accessi al repo del cliente.
- **Config dentro la cartella dati del plugin**: rifiutato. Non condivisibile nel team e non versionata.

## Conseguenze

- Il lavoro di catalogo e tassonomia si fa una volta per team e si condivide via git.
- Ogni contributo al repo pubblico va riletto per escludere dati cliente; gitleaks in CI.
- Le modifiche al template non si propagano da sole alle istanze esistenti: vanno riportate a mano.

## Stato

Accettata (0.1.0).
