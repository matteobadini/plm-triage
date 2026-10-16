# Template di output — triage-ticket

Sostituisci i segnaposto `<...>`. Nei commenti Jira niente SQL, nomi di tabelle, host o righe grezze: solo il riepilogo necessario. La traccia completa va nel file di run.

## 1. Commento Jira — risposta proposta

```markdown
[AI triage] risposta proposta

Categoria: <categoria>

<Risposta al reporter in 2-5 frasi, solo su fatti verificati.>

Evidenze:
- <affermazione> — verificato (<campo del ticket | nome query>)
- <affermazione> — verificato (<campo del ticket | nome query>)

Questa risposta è stata preparata da un assistente AI in sola lettura e rivista da <nome operatore> prima della pubblicazione.
```

## 2. Commento Jira — escalation

```markdown
[AI triage – escalation]

Categoria: <categoria | sconosciuta>
Motivo: <trigger scattato, es. "query in timeout", "richiede correzione dati su PLM">

Cosa è stato verificato:
- <affermazione> — verificato (<campo | nome query>)

Cosa resta aperto:
- <domanda o verifica che serve a chi prende in carico>

Prossimo passo suggerito: <azione per l'assegnatario>
Assegnato a: <jira.assignee_for_escalation>
```

Le affermazioni `dedotto` o `ipotesi` possono comparire solo in "Cosa resta aperto", marcate come tali.

## 3. File di run locale

Percorso: `<instance>/evals/runs/<AAAA-MM-GG>/<CHIAVE>.md`. Non viene mai pubblicato su Jira.

```markdown
# Run triage <CHIAVE> — <AAAA-MM-GG HH:MM>

- Modalità: <shadow | live>
- Versione plugin: <version>
- Esito: <risposta proposta | escalation>
- Trigger scattati: <elenco | nessuno>

## Preflight
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
<testo esatto del commento, template 1 o 2>

## Scritture su Jira
| Azione | Confermata dall'utente | Esito |
|---|---|---|
<in shadow: "nessuna (modalità shadow)">
```
