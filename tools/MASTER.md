# MASTER.md: sistema di design della home di tlon.it

Scritto il 2 novembre 2026 con la pipeline genjutsu paint (ridisegno completo della home, tesi validate da Andrea). Ogni valore usato nelle tre home (index.html, index-en.html, index-es.html) viene da qui. I fogli di stile si applicano con `tools/applica-tema-home.py`; il pianeta e «Il prossimo appuntamento» leggono gli stessi token da `tools/costellazione.py` e `tools/prossimo_news.py`.

## Tesi visiva

Un laboratorio sul presente su fondo chiaro e freddo (grigio da tavolo luminoso, mai carta calda), inchiostro blu-nero, un solo segnale che è il rosso del punto del logo; tipografia grande in Bricolage Grotesque, una grottesca costruita per bricolage come l'enciclopedia di Tlön, variabile in peso e larghezza; IBM Plex Sans per il testo e Plex Mono solo per date e cifre; spazi larghi tra le sezioni e densi dentro le liste; componenti piatti, squadrati, senza ombre, delimitati da filetti.

## Tesi di interazione

Tempi asciutti (140 ms micro, 280 ms transizioni, 480 ms rivelazioni) con uscita cubic-bezier(0.2,0,0,1); al passaggio del puntatore il testo diventa rosso e una riga si traccia da sinistra; il titolo della home è un campo gravitazionale, le lettere vicine al puntatore si fanno pesanti e strette senza che la riga cambi lunghezza; allo scorrimento solo rivelazioni con riga rossa e scalino di 60 ms; vietati rimbalzi, parallasse, zoom sulle foto, sfumature sfocate, vetro, bagliori e ogni ciclo infinito salvo la rotazione del pianeta.

Pattern ammessi: rotazione perpetua del pianeta; una sezione notte per «Il prossimo appuntamento»; mono solo per date e cifre; filetti solo nelle liste (calendario, dimensioni, uscite); il rosso segnale del logo; etichette maiuscole di sezione; trattino breve negli intervalli di date; display grande con una parola che cambia colore.

## Quadranti passati al dataset ui-ux-pro-max

- variance 7: «tipografia grande», «componenti piatti, squadrati», composizione asimmetrica.
- motion 4: «tempi asciutti», «allo scorrimento solo rivelazioni», lista dei vietati.
- density 5: «spazi larghi tra le sezioni e densi dentro le liste».

Dal dataset (stile proposto: Brutalism, Space Mono, palette navy) si è tenuto: angoli a 0, filetti visibili, contrasto alto, scalino di 60 ms. Scartato: Space Mono ovunque (il mono resta su date e cifre), la palette navy-verde (contraddice la tesi), l'easing back.out (rimbalzo vietato), «nessuna transizione» (la tesi fissa 140 ms lineari sul colore).

## Colori

| Token | Valore | Uso | Contrasto |
|---|---|---|---|
| --fondo | #F2F4F3 | fondo di pagina, freddo | |
| --foglio | #FFFFFF | schede, sezioni alternate | |
| --inchiostro | #0E1116 | testo, pulsanti pieni, sezione notte | 17.1:1 su fondo |
| --grafite | #3A3F47 | testo secondario | 9.6:1 su fondo |
| --nebbia | #6B7178 | etichette, didascalie | 4.5:1 su fondo |
| --linea | #D3D7D5 | filetti | 13.0:1 inchiostro su linea |
| --segnale | #C72B2C | il rosso del punto del logo: hover, righe, enfasi | 5.0:1 su fondo |
| --acciaio | #5B6B7A | mari e orbite del pianeta | 5.0:1 su fondo |
| --notte | #0E1116 | fondo della sezione News | fondo su notte 17.1:1 |
| --notte-testo | #9AA1A8 | testo secondario sulla notte | 6.5:1 su notte |
| --notte-linea | rgba(242,244,243,0.16) | filetti sulla notte | |

Alias storici mantenuti per gli strumenti: --bianco = --foglio, --nero = --inchiostro, --grigio = --nebbia, --grigio-chiaro = --linea, --crema = --fondo. L'ottanio non esiste più nella home.

## Tipografia

- Display: Bricolage Grotesque (variabile, assi opsz 12–96, wdth 75–100, wght 200–800), self-hosted in assets/fonts. Fallback: "Helvetica Neue", Arial, sans-serif.
- Testo: IBM Plex Sans (variabile 100–700), usati 400 e 500. Fallback: system-ui, sans-serif.
- Cifre e date: IBM Plex Mono 400. Mai su etichette, navigazione o didascalie di testo.

| Ruolo | Dimensione | Peso | Interlinea | opsz |
|---|---|---|---|---|
| Titolo home | clamp(3.2rem, 10vw, 9.5rem) | 300 (campo fino a 800) | 0.92 | 96 |
| Titolo sezione | clamp(2rem, 4.5vw, 4rem) | 400 | 1 | 60 |
| Titolo grande (News, Tlonletter) | clamp(2.8rem, 6.5vw, 6rem) | 300 | 0.92 | 96 |
| Titolo scheda | 1.4–1.6rem | 500 | 1.15 | 40 |
| Testo | 1.0625rem | 400 | 1.65 | |
| Testo lead | 1.35rem | 400 | 1.45 | |
| Etichetta | 0.72rem | 500, maiuscolo, +0.14em | 1.2 | |
| Cifre e date | 0.85rem mono | 400 | 1.4 | |

## Spazi

Base 8 px. Scala: 8, 16, 24, 40, 64, 104, 168 (token --s1 … --s7). Padding orizzontale di pagina clamp(1.25rem, 4vw, 3rem). Larghezza massima dei contenuti 1400 px, del testo 64ch.

## Raggi e ombre

Raggi: 0 ovunque; solo i punti sono cerchi. Ombre: nessuna.

## Movimento

| Token | Valore |
|---|---|
| --t-micro | 140ms, lineare, solo colore |
| --t-ui | 280ms, --ease-out |
| --t-rivela | 480ms, --ease-out |
| --t-uscita | 200ms, --ease-in, solo opacità |
| --scalino | 60ms |
| --ease-out | cubic-bezier(0.2, 0, 0, 1) |
| --ease-in | cubic-bezier(0.4, 0, 1, 1) |

Campo gravitazionale del titolo: raggio 220 px, interpolazione 0.12 per frame, wght 300→800 e wdth 100→w* dove w* è calcolata al caricamento perché la riga conservi la larghezza. Con prefers-reduced-motion il titolo è fermo a 400 e le rivelazioni sono immediate.

## Componenti

- Pulsante: Plex Sans 500 0.85rem maiuscolo +0.06em, padding 16/24, fondo inchiostro e testo fondo; hover segnale; focus-visible contorno 2 px segnale a 3 px; active segnale scuro #8F1F20; disattivo fondo linea e testo nebbia.
- Pulsante secondario: trasparente con filetto inchiostro; hover testo e filetto segnale.
- Link nel testo: riga di 1 px segnale che si traccia da sinistra in 180 ms; testo che diventa segnale.
- Scheda: foglio, filetto linea, padding 24; hover filetto inchiostro.
- Lista (calendario, dimensioni, uscite): righe separate da filetti; data in mono a sinistra.
