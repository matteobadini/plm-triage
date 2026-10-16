/* ---
# ESEMPIO su schema FITTIZIO (tabelle DEMO_*): non esiste in nessun database reale.
name: change_history
description: Cronologia delle transizioni di stato di un change, dalla più recente.
when_to_use: Serve ricostruire chi ha spostato un change e quando (es. ticket su approvazioni).
params:
  change_id:
    type: int
    description: Identificativo numerico interno del change.
max_rows: 100
--- */
SELECT h.FROM_STATUS,
       h.TO_STATUS,
       h.CHANGED_AT,
       h.CHANGED_BY_ROLE
FROM DEMO_CHANGE_HISTORY AS h
WHERE h.CHANGE_ID = @change_id
ORDER BY h.CHANGED_AT DESC
