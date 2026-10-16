# Valutazione

Procedura, criteri di giudizio e via libera: [docs/e2e-protocol.md](https://github.com/matteobadini/plm-triage/blob/main/docs/e2e-protocol.md) nel repository pubblico.

## Valutazione di prova (setup, fase 6)

1. Si scelgono ~30 ticket chiusi, distribuiti sulle categorie, compresi alcuni che richiedono escalation. Una persona approva l'elenco.
2. Con `mode: shadow` (modalità di prova), ogni ticket viene analizzato in una sessione separata (subagente) con `/plm-triage:triage-ticket <CHIAVE> come-aperto`: Claude legge solo i campi presenti all'apertura del ticket e non scrive nulla su Jira.
3. Ogni triage produce il file di traccia `runs/<AAAA-MM-GG>/<CHIAVE>.md`, con la traccia completa e il commento proposto.
4. Claude aggiunge a `grading.csv` una riga per ticket con `ticket_key` e `categoria_agente`; la persona compila `categoria_attesa`, `esito` e `note`.

Valori ammessi per `esito`: `corretto`, `escalation_corretta`, `errato_sicuro`, `errato_dubbio`, `escalation_inutile`.

## Riservatezza

I file in `runs/` contengono dati del cliente: restano nel repository di istanza privato, oppure fuori da git (vedi `.gitignore`).
