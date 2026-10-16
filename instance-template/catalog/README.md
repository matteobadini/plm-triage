# Catalogo query

Ogni file `.sql` contiene **una** query con un nome, che si può eseguire solo con il tool `run_query` di `plm-db`. Non esiste SQL libero. I file il cui nome inizia con `_` (come gli esempi `_example_*.sql`) non vengono caricati. Il server rilegge il catalogo a ogni chiamata, quindi non serve riavviare nulla.

## Regola di approvazione

Una query entra nel catalogo **solo con un commit o una pull request approvati da una persona del team**, dopo aver letto il file per intero. Durante il setup (fase 4) Claude la esegue una volta, solo dopo questa approvazione. Durante il triage Claude non aggiunge né modifica query.

## Formato

Il file inizia con un commento `/* --- ... --- */` che contiene un'intestazione YAML, seguito da una sola istruzione `SELECT` o `WITH`.

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
max_rows: 50                    # predefinito 50, massimo 500
timeout_s: 15                   # predefinito 15, massimo 60
isolation: read_committed       # read_committed (predefinito) | read_uncommitted (solo se richiesto)
--- */
SELECT i.ITEM_NUMBER, i.REV, i.LIFECYCLE
FROM DEMO_ITEM i
WHERE i.ITEM_NUMBER = @item_number
```

## Controlli del server (difesa in profondità)

- I parametri si scrivono come `@nome` e vanno tutti dichiarati in `params` (le variabili di sistema `@@...` sono ammesse).
- Una sola istruzione, che inizia con `SELECT` o `WITH`.
- Viene rifiutato un ampio elenco di parole chiave di scrittura, esecuzione o accesso esterno (`INSERT`, `UPDATE`, `DELETE`, `MERGE`, `EXEC`, `INTO`, `DROP`, `OPENROWSET`, ...) quando compaiono fuori da stringhe e commenti.
- Se le righe superano `max_rows`, il risultato viene troncato e marcato `truncated: true` (nel triage è una condizione di escalation).

Sono controlli sul testo della query, non una garanzia. Il vero confine è un utente del database in sola lettura, possibilmente limitato a viste dedicate, confermato dal DBA.
