# Protocollo di valutazione e collaudo

Obiettivo: dimostrare su ticket reali che il triage è affidabile prima di scrivere su Jira, e poi dare a Claude accesso a Jira per gradi.

## 1. Valutazione di prova

- Campione: ~30 ticket **chiusi**, scelti dal collega in modo da coprire tutte le categorie e includere casi difficili.
- `mode: shadow` (modalità di prova) in `config.yaml`; scritture su Jira negate nei permessi dell'istanza.
- Claude esegue `triage-ticket <CHIAVE> come-aperto` su ogni ticket, in una sessione separata per ciascuno (subagente). Legge solo i campi presenti all'apertura del ticket, e nel contesto non ci sono le soluzioni dei ticket precedenti. Il risultato va solo nel file di traccia `evals/runs/<data>/<CHIAVE>.md`.
- Il collega confronta ogni risultato con la soluzione reale e compila in `evals/grading.csv` le colonne `categoria_attesa`, `esito` e `note`.

## 2. Criteri di giudizio

Ogni ticket riceve un solo `esito`, tra questi valori:

| Esito | Significato |
|---|---|
| `corretto` | bozza giusta e utilizzabile, evidenze corrette |
| `escalation_corretta` | escalation giustificata: serviva davvero una persona |
| `errato_sicuro` | bozza sbagliata presentata come verificata. **È il caso grave.** |
| `errato_dubbio` | bozza sbagliata o incompleta, ma con l'incertezza dichiarata |
| `escalation_inutile` | escalation anche se le evidenze bastavano per rispondere |

Un'escalation comprende: una condizione di escalation scattata (vedi `skills/triage-ticket/SKILL.md`), l'etichetta `ai-escalated`, l'assegnazione alla persona indicata in `assignee_for_escalation`, lo stato del ticket lasciato invariato e un commento di passaggio di consegne (modello in `templates.md`) con la condizione scattata, le evidenze raccolte e i passi saltati.

## 3. Metriche e via libera

Con N = numero di ticket valutati:

- `tasso_ok = (corretto + escalation_corretta) / N`
- `errati_sicuri = conteggio(errato_sicuro)`
- da tenere d'occhio, ma non bloccanti: `tasso_escalation_inutile`, `errato_dubbio`

**Via libera se `tasso_ok ≥ 0,80` e `errati_sicuri = 0`.**

Basta un solo `errato_sicuro` per bloccare: si corregge la causa (query, categoria, condizione di escalation, procedura) e si ripete la valutazione di prova sui ticket coinvolti più un nuovo campione. Ogni modifica alla skill o al catalogo richiede di ripetere la valutazione di prova.

## 4. Collaudo

Dopo il via libera, con `mode: live` (modalità operativa):

- si usano 1-3 ticket **aperti**;
- prima di ogni scrittura (commento che inizia con `[AI triage]`, etichetta, assegnatario) Claude mostra il contenuto esatto e aspetta un "sì" esplicito;
- il file di traccia registra cosa è stato scritto.

## 5. Periodo di rodaggio (2-4 settimane)

Uso quotidiano in modalità operativa, con l'approvazione di una persona per ogni scrittura. Il collega continua a giudicare i risultati con gli stessi criteri. Se sui ticket nuovi i risultati scendono sotto le soglie del via libera, si torna alla modalità di prova.

Solo dopo questo periodo si valuta l'esecuzione automatica (vedi "Sviluppi futuri" in [architecture.md](architecture.md)).
