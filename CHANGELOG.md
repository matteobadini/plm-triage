# Changelog

Formato [Keep a Changelog](https://keepachangelog.com/it/1.1.0/), versioni [SemVer](https://semver.org/lang/it/).

## [Unreleased]

## [0.1.0] - 2026-10-16

### Added

- Plugin e marketplace `plm-triage` nello stesso repo.
- Skill `triage-ticket`: principi inline (niente Bash né web), passi copiati nella task list con motivo di salto, preflight fail-closed con verifica dell'`instance_dir` del server, modalità `come-aperto` con soli campi d'apertura, escalation a regole, template di risposta e hand-off.
- Skill `setup`: setup a fasi riprendibile con checkpoint umani, avviabile senza nulla di clonato; fase 0 con prerequisiti, checkpoint di consenso e verifiche web; shadow eval con un subagente per ticket; gate ed E2E live.
- Server MCP locale `plm-db` (`plm_db_mcp`): catalogo di query nominate riletto a ogni chiamata (file con prefisso `_` ignorati), nessun SQL libero, validazione SQL come difesa in profondità, guardrail di sessione, limite righe, timeout, errori sanitizzati, audit log locale; CLI `plm-db` per credenziali nel keyring e `check`.
- `instance-template/` per il repo istanza privato, con `WebFetch`/`WebSearch` negati.
- Documentazione: architettura, setup, protocollo E2E, ADR 0001-0006.
- CI: ruff e pytest su ubuntu e windows, gitleaks.

[Unreleased]: https://github.com/matteobadini/plm-triage/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/matteobadini/plm-triage/releases/tag/v0.1.0
