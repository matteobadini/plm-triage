/* ---
# ESEMPIO su schema FITTIZIO (tabelle DEMO_*): non esiste in nessun database reale.
# I file che iniziano con "_" non vengono caricati dal server plm-db.
name: item_by_number
description: Dati anagrafici di un item (numero, descrizione, revisione corrente, stato del ciclo di vita).
when_to_use: Il ticket cita un numero di item e serve verificarne esistenza, revisione o stato.
params:
  item_number:
    type: str
    required: true
    max_len: 40
    pattern: "[A-Z0-9][A-Z0-9._-]*"
    description: Numero item esatto, maiuscolo.
max_rows: 5
timeout_s: 10
isolation: read_committed
--- */
SELECT i.ITEM_NUMBER,
       i.DESCRIPTION,
       i.CURRENT_REV,
       i.LIFECYCLE_PHASE
FROM DEMO_ITEM AS i
WHERE i.ITEM_NUMBER = @item_number
