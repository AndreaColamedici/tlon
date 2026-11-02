#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Toglie dallo statement delle tre home la figura (l'immagine generata della mappa):
la carta di Tlon vive ora accanto al globo, nella sezione del pianeta, messa lì da
applica-costellazione.py (markup in tools/mappa_tlon.py). Idempotente.
Uso:  python3 tools/applica-mappa-tlon.py
"""
import io, os, re

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = ['index.html', 'index-en.html', 'index-es.html']


def main():
    for f in FILE:
        path = os.path.join(SITE, f)
        s = io.open(path, encoding='utf-8').read()
        s, n = re.subn(r'[ \t]*<figure class="statement-figura reveal">.*?</figure>\n', '', s, flags=re.S)
        io.open(path, 'w', encoding='utf-8').write(s)
        print(f, 'figura tolta' if n else 'già senza figura')


if __name__ == '__main__':
    main()
