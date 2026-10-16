# Modelli di output — triage-ticket

Sostituisci i segnaposto `<...>`. I commenti Jira li leggono gli utenti che hanno aperto il ticket: niente SQL, nomi di tabelle, host o righe grezze, solo il riepilogo necessario. Il dettaglio completo va nel file di traccia (modello 3).

## 1. Commento Jira — proposta di risposta

```markdown
[AI triage] Proposta di risposta

Buongiorno,

<Risposta al reporter in 2-5 frasi, solo su fatti verificati.>

Su cosa si basa questa risposta:
- <affermazione> — verificato (<campo del ticket | nome query>)
- <affermazione> — verificato (<campo del ticket | nome query>)

Categoria: <categoria>

La risposta è stata preparata da un assistente AI con accesso in sola lettura e controllata da <nome operatore> prima della pubblicazione.
```

## 2. Commento Jira — escalation (passaggio di consegne)

```markdown
[AI triage – escalation]

Buongiorno,

questo ticket richiede la verifica di un collega del supporto ed è stato assegnato a <jira.assignee_for_escalation>.

Motivo: <condizione scattata, es. "una query non ha risposto in tempo", "serve una correzione dei dati sul PLM">
Categoria: <categoria | sconosciuta>

Già verificato:
- <affermazione> — verificato (<campo | nome query>)

Da chiarire:
- <domanda o verifica che serve a chi prende in carico il ticket>

Prossimo passo suggerito: <azione per l'assegnatario>
```

Le affermazioni `dedotto` o `ipotesi` possono comparire solo in "Da chiarire", marcate come tali.

## 3. File di traccia locale

Percorso: `<instance>/evals/runs/<AAAA-MM-GG>/<CHIAVE>.md`. Non viene mai pubblicato su Jira.

```markdown
# Traccia triage <CHIAVE> — <AAAA-MM-GG HH:MM>

- Modalità: <shadow | live>
- Versione plugin: <version>
- Esito: <risposta proposta | escalation>
- Condizioni di escalation scattate: <elenco | nessuna>

## Controlli preliminari
| Controllo | Esito | Note |
|---|---|---|
| config.yaml | ok/ko | |
| plm-db ping | ok/ko | |
| catalogo | ok/ko | <query mancanti> |
| Jira lettura ticket | ok/ko | |

## Passi
| # | Passo | Stato | Note / skip: <motivo> |
|---|---|---|---|
| 1 | Leggi il ticket | fatto | campi letti: <...> |
| 2 | Estrai gli identificativi | fatto | |
| 3 | Classifica | fatto | |
| 4 | Esegui le query di catalogo della categoria | fatto/skip | |
| 5 | Costruisci le evidenze | fatto | |
| 6 | Decidi | fatto | |
| 7 | Scrivi l'output | fatto | |

## Identificativi estratti
| Valore | Tipo | Campo di provenienza |
|---|---|---|

## Classificazione
Categoria: <categoria> — segnali: <...> — alternative scartate: <...>

## Query eseguite
| Query | Parametri | Righe | truncated | Durata ms | Esito |
|---|---|---|---|---|---|

## Evidenze
| Affermazione | Livello (verificato/dedotto/ipotesi) | Fonte |
|---|---|---|

## Commento proposto
<testo esatto del commento, modello 1 o 2>

## Scritture su Jira
| Azione | Confermata dall'utente | Esito |
|---|---|---|
<in shadow: "nessuna (modalità di prova)">
```
