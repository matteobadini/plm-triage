# 0004 — Modello pubblico, istanza privata

## Contesto

Il plugin deve essere installabile da un marketplace git e riutilizzabile. Le query reali, le categorie, i ticket valutati e i dettagli dello schema sono materiale del cliente.

## Decisione

- **Repository pubblico** (`matteobadini/plm-triage`): plugin, server, documentazione e `instance-template/`, il modello di istanza, con esempi su uno schema **fittizio** (`DEMO_ITEM`, `DEMO_CHANGE`). Mai dati del cliente.
- **Repository di istanza privato**, uno per team, creato a partire da `instance-template/`: contiene `config.yaml`, `catalog/*.sql`, `evals/`, `CLAUDE.md`, `.claude/settings.json`. I colleghi lo clonano e aprono Claude Code in quella cartella.
- Il `.gitignore` pubblico esclude `instance/` e `*.local.*`, nel caso qualcuno crei per errore l'istanza dentro il clone del repository pubblico.
- Le nozioni generiche su Agile PLM (codici di classe numerici, `NODETABLE`, `LISTENTRY`, tabelle Page Two/Page Three) possono comparire solo come conoscenza di prodotto, con la nota "da verificare sull'istanza".

## Alternative considerate

- **Un unico repository privato con tutto**: scartata. Il plugin non sarebbe riutilizzabile e il marketplace richiederebbe l'accesso al repository del cliente.
- **Configurazione nella cartella dati del plugin**: scartata. Non sarebbe condivisibile con il team né versionata.

## Conseguenze

- Catalogo e categorie si preparano una volta per team e si condividono con git.
- Ogni contributo al repository pubblico va riletto per escludere dati del cliente; in CI gira gitleaks.
- Le modifiche al modello non arrivano da sole alle istanze già create: vanno riportate a mano.

## Stato

Accettata (0.1.0).
