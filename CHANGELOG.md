# Changelog

Formato [Keep a Changelog](https://keepachangelog.com/it/1.1.0/), versioni [SemVer](https://semver.org/lang/it/).

## [Unreleased]

### Changed

- Skill `triage-ticket` e `setup`: istruzioni per Claude riscritte in inglese, con una regola esplicita che impone l'italiano per tutto ciò che vede l'utente; domande dei punti di controllo, messaggio per i colleghi e modelli di commento e del file di traccia restano in italiano, testuali. Procedura invariata.
- Documentazione e modelli di commento riscritti in un italiano più semplice, con termini uniformi (glossario in `docs/architecture.md`).
- Skill `setup`: a fine fase 3 Claude prepara un messaggio da inoltrare ai colleghi con l'URL del repository di istanza; in fase 0 la domanda sul repository indica dove trovare l'URL e accetta indirizzi HTTPS e SSH.

## [0.1.0] - 2026-10-16

### Added

- Plugin e marketplace `plm-triage` nello stesso repository.
- Skill `triage-ticket`: principi scritti nella skill stessa (niente Bash né web); passi copiati nella task list, con il motivo di ogni passo saltato; controlli preliminari bloccanti, compresa la verifica che il server legga la stessa `instance_dir`; modalità `come-aperto`, che legge solo i campi presenti all'apertura del ticket; escalation basata su regole; modelli per la risposta e per il passaggio di consegne.
- Skill `setup`: setup a fasi, riprendibile, con punti di controllo in cui decide una persona; si avvia senza clonare nulla. Fase 0 con prerequisiti, consenso e verifiche sul web; valutazione di prova con un subagente per ticket; via libera e collaudo su ticket aperti.
- Server MCP locale `plm-db` (`plm_db_mcp`): catalogo di query con nome, riletto a ogni chiamata (i file che iniziano con `_` sono ignorati); nessun SQL libero; validazione dell'SQL come difesa in profondità; protezioni di sessione, limite di righe, timeout, errori privi di dati sensibili, log di audit locale. Comando `plm-db` per salvare le credenziali nel keyring e per la verifica `check`.
- `instance-template/`, modello del repository di istanza privato, con `WebFetch` e `WebSearch` negati.
- Documentazione: architettura, setup, protocollo di valutazione e collaudo, ADR 0001-0006.
- CI: ruff e pytest su Ubuntu e Windows, gitleaks.

[Unreleased]: https://github.com/matteobadini/plm-triage/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/matteobadini/plm-triage/releases/tag/v0.1.0
