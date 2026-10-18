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
