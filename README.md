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

## Configurazione DNS

Presso il registrar del dominio tlon.it, impostare:

**Record A** (tutti e quattro):
- 185.199.108.153
- 185.199.109.153
- 185.199.110.153
- 185.199.111.153

**Record CNAME** per www:
- www.tlon.it → andreacolamedici.github.io

## Attivazione GitHub Pages

1. Vai su Settings → Pages
2. Source: Deploy from a branch
3. Branch: main, cartella / (root)
4. Custom domain: tlon.it
5. Enforce HTTPS: attivare dopo la propagazione DNS
