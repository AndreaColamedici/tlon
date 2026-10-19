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
