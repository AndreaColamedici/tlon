# MASTER, il sistema di design di tlon.it/fabbricabellezza

Pagina di lancio di «La fabbrica della bellezza» di Maura Gancitano (Rizzoli, 3 novembre 2026). Scritto il 1° novembre 2026 con la pipeline paint di genjutsu, dopo tre domande ad Andrea (meraviglia d'archivio; un solo mondo radicale invece di due carte; niente trovate, deve essere semplicemente bellissimo e deve vivere). I token qui sotto sono quelli e soli usati da `tools/genera-fabbricabellezza.py`.

## Tesi visiva (validata, con la nota «vive poco»)

Quarta versione, 1 novembre 2026, sera: il dipinto di copertina (Ewa Juszkiewicz, *Lady with a Mirror (after Elisabeth Vigée Le Brun)*, 2026) viene dal PDF di stampa Rizzoli, intero e senza scritte (2023×2584), e sostituisce la ricostruzione; le sedi delle tappe sono immagini sempre visibili, nel blu, a colori in hover.

Un solo mondo, il blu profondo del vestito in copertina, su tutta la pagina. Dentro quel blu la copertina ingrandita a tutto schermo (dal PDF di stampa, il solo dipinto senza le scritte) e le fotografie d'epoca del libro a tutto schermo, nei loro toni seppia, che sul blu diventano calde. Titoli, anni e nomi in Gloock, un serif da manifesto con forti contrasti ma massiccio, un solo peso, a misure da cinema; il testo in Epilogue, un sans sottile che non gli fa ombra. L'arancione della fascia sugli occhi come unico accento, solo sul bottone. Nessuna card, nessun bordo, nessuna ombra, nessuna carta.

## Tesi di interazione (validata)

Cinema lento legato allo scorrimento, nativo, senza librerie: la copertina si avvicina mentre si scorre la prima schermata (scala 1 → 1,16 su 100 svh), ogni tavola a tutto schermo si assesta da 1,14 a 1 mentre entra, l'anno sale dal basso, le tavole piccole derivano di poche decine di pixel a velocità diverse, la frase dell'introduzione si inchiostra da 28% a 100% entrando; titoli e paragrafi si posano una volta sola in 1000 ms con ease-out esponenziale e scaglionamento di 90 ms; al passaggio del mouse il nome della città scivola di 16 px e la sua fotografia appare, i link si sottolineano, il bottone si scurisce. Nessun loop, nessun contatore, nessuna camera, nessuna parallasse a strati.

Pattern ammessi: un serif da manifesto (Gloock) nominato e motivato; anni a dimensione di schermo; immagini a tutto schermo con scala legata allo scroll; un velo blu sfumato sotto il titolo nell'apertura, che è l'unico uso di una maschera sfumata. Via: puntini mediani, trattini lunghi, nastri in loop, ritratti che respirano, carta.

## Colori

| Ruolo | Valore | Nota |
|---|---|---|
| blu, fondo | #15327a | il vestito della copertina |
| blu-2, fondo della chiusura | #0f2660 | un passo più scuro |
| blu-3, riserva | #1d3e92 | un passo più chiaro, per campi secondari |
| perla, inchiostro | #f3ecdf | su blu 10,1:1 |
| perla-2, inchiostro attenuato | #c9c4d8 | su blu 7,0:1, didascalie e note |
| arancio, accento | #e2772c | la fascia sugli occhi; solo il bottone |
| arancio-2, hover | #c9651f | |
| inchiostro, testo sul bottone | #1a1612 | su arancio 5,9:1 |

## Tipografia

Gloock (Duarte Pires, OFL), un peso, per titoli, anni, nomi delle città e frasi dal libro. Epilogue variabile (Etcetera Type, OFL) per il testo, 400 e 500–600 per le evidenze. Entrambi self-hosted in `/assets/fonts/fabbrica.css`, solo sottoinsieme latino.

Scala: titolo clamp(64px, 12vw, 190px); anni clamp(120px, 24vw, 380px); sezioni clamp(48px, 7vw, 112px); frase clamp(40px, 6.4vw, 104px); cifre clamp(72px, 9vw, 150px); città clamp(40px, 5vw, 80px); frasi dal libro clamp(26px, 2.6vw, 38px); capitoli clamp(28px, 3.4vw, 52px); lead 24px; testo 18px; note e didascalie 16px; crediti 15px.

## Spazi

Base 8: 8, 16, 24, 40, 64, 96, 160, 240 px. Margine laterale clamp(20px, 4.5vw, 72px). Sezioni distanti 160–240 px su desktop, 96–160 su telefono. Griglia a 12 colonne nei capitoli delle tavole, con le tavole posate su colonne diverse a ogni capitolo.

## Raggi, ombre, bordi

Nessuno. Spigoli vivi ovunque. Le superfici si distinguono per un passo di blu.

## Componenti

Bottone: rettangolo pieno arancione, testo inchiostro 600, 18 px, padding 18/28; stati: default, hover (arancio-2), focus (contorno arancione 3 px), active (scala 0,97), disabled non previsto. Variante perla sulla chiusura. Link: sottolineato a 0,25 em, colore della riga che si rafforza in hover. Tappa: la fotografia della sede (3:2, griglia a tre colonne, due a 1100 px, una sul telefono), tinta nel blu della pagina con un filtro CSS (grayscale, sepia, hue-rotate 190°) e a colori pieni in hover con una scala a 1,04; sotto, la città in Gloock, la data in Epilogue 600, la sede, chi accompagna, e i due link Indicazioni e Aggiungi al calendario. La fotografia porta alle indicazioni stradali. Chiusura: tre colonne, preghiera diné, la copertina stampata (resa dal PDF di stampa Rizzoli a 300 dpi), invito e bottone perla.

## Movimento

Durata di posa 1000 ms, micro 160 ms, curva `cubic-bezier(.16,1,.3,1)`. Scroll-driven dentro `@supports (animation-timeline: scroll())`, contenuto visibile per default. `prefers-reduced-motion: reduce` azzera tutto. Rete di sicurezza: dopo sei secondi ogni elemento `.posa` è visibile anche se l'osservatore non è scattato.
