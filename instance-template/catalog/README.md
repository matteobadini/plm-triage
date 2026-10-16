# Catalogo query

Ogni file `.sql` è **una** query nominata, eseguibile solo tramite il tool `run_query` di `plm-db`. Non esiste SQL libero. I file il cui nome inizia con `_` (come gli esempi `_example_*.sql`) non vengono caricati. Il server rilegge il catalogo a ogni chiamata: non serve riavviare.

## Regola di approvazione

Una query entra nel catalogo **solo tramite commit o PR approvato da una persona del team**, dopo averne letto il file completo. Il setup (fase 4) la esegue una volta solo dopo questa approvazione. L'agente non aggiunge né modifica query durante il triage.

## Formato

Il file inizia con un commento `/* --- ... --- */` che contiene un header YAML, seguito da una sola istruzione `SELECT` o `WITH`.

```sql
/* ---
name: item_by_number            # identificativo univoco, usato in config.yaml
description: Stato e revisione corrente di un item.
when_to_use: Il ticket cita un numero di item e chiede stato o revisione.
params:
  item_number:
    type: str                   # int | str | date | enum
    required: true
    max_len: 40
    pattern: "^[A-Z0-9-]+$"     # facoltativo
  # per enum: type: enum, values: [A, B, C]
max_rows: 50                    # default 50, massimo 500
timeout_s: 15                   # default 15, massimo 60
isolation: read_committed       # read_committed (default) | read_uncommitted (opt-in)
--- */
SELECT i.ITEM_NUMBER, i.REV, i.LIFECYCLE
FROM DEMO_ITEM i
WHERE i.ITEM_NUMBER = @item_number
```

## Controlli del server (difesa in profondità)

- Parametri come `@nome`, tutti dichiarati in `params` (le variabili di sistema `@@...` sono ammesse).
- Una sola istruzione, che inizia con `SELECT` o `WITH`.
- Un ampio elenco di parole chiave di scrittura, esecuzione o accesso esterno (`INSERT`, `UPDATE`, `DELETE`, `MERGE`, `EXEC`, `INTO`, `DROP`, `OPENROWSET`, ...) rifiutato fuori da stringhe e commenti.
- Righe oltre `max_rows` → risultato troncato con `truncated: true` (per il triage è un trigger di escalation).

Sono controlli sintattici, non una garanzia: il vero confine è un utente DB in sola lettura, idealmente su viste dedicate, confermato dal DBA.
