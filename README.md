# Tlon.it

Sito web di Tlon – Scuola di Filosofia e Immaginazione.

## Struttura

```
/
├── index.html                      → tlon.it/
├── CNAME                           → configurazione dominio
├── maura-gancitano/
│   └── index.html                  → tlon.it/maura-gancitano/
├── andrea-colamedici/
│   └── index.html                  → tlon.it/andrea-colamedici/
└── assets/
    └── images/
        └── maura-gancitano.jpg
```

## Calendario

`assets/data/eventi.json` è la fonte; `tools/genera-news.py` produce news.html e `tools/genera-home-news.py` rigenera i blocchi del calendario nelle tre home (sei prossimi, otto passati, contatore) dallo stesso JSON; le voci con `"home": true` hanno la precedenza.

## Immagini della home

`tools/applica-immagini-home.py` inserisce (una volta sola) le immagini e le icone nelle sezioni della home che erano solo testo: la mappa incisa del pianeta, la foto del Teatro Municipale nella sezione News (la cella «in programma» ospita invece «Il prossimo appuntamento» e la linea del tempo dei mesi a venire, composti dal DOM da `tools/prossimo_news.py` e applicati con `tools/applica-prossimo-news.py`), la natura morta della Tlonletter, le dieci icone a tratto di `tools/icone_dimensioni.py`, le fotografie delle quattro librerie. Le immagini stanno in `assets/images/home/`; la mappa e la natura morta sono state generate il 19 ottobre 2026 e vanno rigenerate solo se si cambia soggetto.

`tools/applica-tema-home.py` applica alle tre home il tema «Laboratorio sul presente» (2 novembre 2026): il foglio di stile intero sta in `tools/tema_laboratorio.py` insieme al campo gravitazionale del titolo, i token e le regole in `tools/MASTER.md`; il CSS del pianeta e del prossimo appuntamento restano nei loro moduli e vengono inclusi con i marcatori che i rispettivi strumenti usano per riapplicarsi. I font (Bricolage Grotesque variabile, IBM Plex Sans variabile, IBM Plex Mono) sono in `assets/fonts/`. La home non carica più `tlonletter.css` ed `evidenza.css`, che restano per le altre pagine.

`tools/mappa_tlon.py` è la carta di Tlon: la stessa geografia del pianeta (seme 1940, soglia 0.49), rispecchiata come il globo (est a sinistra), incisa su canvas riga per riga, con le dieci dimensioni come alture e link; sta accanto al globo nella sezione del pianeta, dove la mette `applica-costellazione.py`, e il globo le passa a ogni fotogramma la longitudine che mostra (`window.tlonPianeta.onFrame`): la carta registra ciò che il globo ha mostrato: all'apertura si incide dal meridiano in luce fino ai due lembi, poi i lembi incidono terre nuove a ogni giro o trascinamento, finché la tavola è completa; il meridiano rosso segna la longitudine che il globo mostra; nodi in orbita e alture si accendono a vicenda. Due colonne solo da 1200 px, sotto la carta sta sotto il globo. CSS e script li porta `applica-tema-home.py`; `applica-mappa-tlon.py` toglie dallo statement la vecchia figura. L'immagine generata `assets/images/home/pianeta-mappa.jpg` non è più usata dalla home.

`tools/applica-fabbrica.py` mette «La fabbrica della bellezza» (Rizzoli, 3 novembre 2026) in evidenza nelle tre home (Botanica scende fra i nuovi libri), apre nella pagina di Maura (IT e en.html) una sezione nel blu del minisito con il dipinto, il libro e le sei tappe, e aggiunge la scheda nelle versioni en/, es/, zh/. Idempotente; le tappe sono nella lista TAPPE dello script e vanno tenute allineate a `genera-fabbricabellezza.py`.
