/* ---
# ESEMPIO su schema FITTIZIO (tabelle DEMO_*): non esiste in nessun database reale.
name: open_changes_for_item
description: Change aperti che coinvolgono un item, con stato e data di creazione.
when_to_use: Il ticket chiede perché un item è bloccato o in attesa di approvazione.
params:
  item_number:
    type: str
    max_len: 40
    pattern: "[A-Z0-9][A-Z0-9._-]*"
  status:
    type: enum
    required: false
    values: [SUBMITTED, REVIEW, HOLD]
    description: Filtra per stato; se assente, tutti gli stati aperti.
  created_since:
    type: date
    required: false
    description: Solo change creati da questa data (YYYY-MM-DD).
max_rows: 50
timeout_s: 15
# Lettura "sporca" ammessa solo per query di sola consultazione dove un dato
# non ancora committato non cambia la risposta.
isolation: read_uncommitted
--- */
WITH open_changes AS (
    SELECT c.CHANGE_ID, c.CHANGE_NUMBER, c.STATUS, c.CREATED_AT
    FROM DEMO_CHANGE AS c
    WHERE c.STATUS NOT IN ('RELEASED', 'CANCELLED')
)
SELECT oc.CHANGE_NUMBER,
       oc.STATUS,
       oc.CREATED_AT
FROM open_changes AS oc
JOIN DEMO_CHANGE_ITEM AS ci ON ci.CHANGE_ID = oc.CHANGE_ID
WHERE ci.ITEM_NUMBER = @item_number
  AND (@status IS NULL OR oc.STATUS = @status)
  AND (@created_since IS NULL OR oc.CREATED_AT >= @created_since)
ORDER BY oc.CREATED_AT DESC;
