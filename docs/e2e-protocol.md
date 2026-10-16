# Protocollo di valutazione ed E2E

Obiettivo: dimostrare su ticket reali che il triage è affidabile prima di toccare Jira, e poi passare a Jira per gradi.

## 1. Shadow eval

- Campione: ~30 ticket **chiusi**, scelti dal collega in modo da coprire le categorie e includere casi difficili.
- `mode: shadow` in `config.yaml`; scritture Jira negate nei permessi dell'istanza.
- Claude esegue `triage-ticket <CHIAVE> come-aperto` su ciascuno, in un subagente nuovo per ticket: solo i campi d'apertura, nessuna risoluzione dei ticket precedenti nel contesto. Output solo in `evals/runs/<data>/<CHIAVE>.md`.
- Il collega confronta ogni output con la risoluzione reale e compila in `evals/grading.csv` le colonne `categoria_attesa`, `esito` e `note`.

## 2. Rubrica

Un `esito` per ticket (unici valori ammessi):

| Esito | Significato |
|---|---|
| `corretto` | bozza giusta e utilizzabile, evidenze corrette |
| `escalation_corretta` | escalation giustificata: serviva davvero un umano |
| `errato_sicuro` | bozza sbagliata presentata come verificata. **Il caso grave.** |
| `errato_dubbio` | bozza sbagliata o incompleta ma con incertezza dichiarata |
| `escalation_inutile` | escalation quando le evidenze bastavano a rispondere |

Escalation significa: trigger a regole scattato (vedi `skills/triage-ticket/SKILL.md`), etichetta `ai-escalated`, assegnazione all'umano in `assignee_for_escalation`, stato del ticket invariato, hand-off da `templates.md` con trigger, evidenze raccolte e passi saltati.

## 3. Metriche e gate

Con N = ticket valutati:

- `tasso_ok = (corretto + escalation_corretta) / N`
- `errati_sicuri = conteggio(errato_sicuro)`
- da osservare, non bloccanti: `tasso_escalation_inutile`, `errato_dubbio`

**Gate superato se `tasso_ok ≥ 0,80` e `errati_sicuri = 0`.**

Un solo `errato_sicuro` blocca: si corregge (query, categoria, trigger, procedura) e si ripete la shadow sui ticket interessati più un nuovo campione. Ogni modifica alla skill o al catalogo richiede di ripetere la shadow.

## 4. E2E live

Dopo il gate, con `mode: live`:

- 1-3 ticket **aperti**.
- Per ogni scrittura (commento con prefisso `[AI triage]`, etichetta, assegnatario) Claude mostra il contenuto esatto e attende un "sì" esplicito.
- Il file di run registra cosa è stato scritto.

## 5. Fase bozze (2-4 settimane)

Uso quotidiano in `live` con approvazione umana di ogni scrittura. Il collega continua a valutare gli esiti con la stessa rubrica. Se il gate non regge sui ticket nuovi si torna in shadow.

Solo dopo questa fase si valuta l'headless (vedi "Prossimi passi" in [architecture.md](architecture.md)).
