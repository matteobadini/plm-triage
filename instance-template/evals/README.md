# Valutazione

Protocollo, rubrica e gate: [docs/e2e-protocol.md](https://github.com/matteobadini/plm-triage/blob/main/docs/e2e-protocol.md) nel repo pubblico.

## Shadow eval (setup, fase 6)

1. Si scelgono ~30 ticket chiusi, distribuiti sulle categorie, inclusi alcuni da escalation (elenco approvato da una persona).
2. Con `mode: shadow`, ogni ticket è triato in un subagente nuovo con `/plm-triage:triage-ticket <CHIAVE> come-aperto`: solo i campi d'apertura, nulla scritto su Jira.
3. Ogni run produce `runs/<AAAA-MM-GG>/<CHIAVE>.md` con la traccia completa e il commento proposto.
4. Claude aggiunge a `grading.csv` una riga per ticket con `ticket_key` e `categoria_agente`; la persona compila `categoria_attesa`, `esito` e `note`.

Valori ammessi per `esito`: `corretto`, `escalation_corretta`, `errato_sicuro`, `errato_dubbio`, `escalation_inutile`.

## Riservatezza

I file in `runs/` contengono dati del cliente: restano nel repo istanza privato (o fuori da git, vedi `.gitignore`).
