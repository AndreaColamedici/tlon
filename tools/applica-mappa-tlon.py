#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mette la mappa di Tlon (tools/mappa_tlon.py) nella figura della sezione statement
delle tre home, al posto dell'immagine. Il CSS e lo script li porta applica-tema-home.py.
Idempotente. Uso:  python3 tools/applica-mappa-tlon.py
"""
import io, os, re, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
cost = importlib.import_module('applica-costellazione')

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = {'index.html': 'it', 'index-en.html': 'en', 'index-es.html': 'es'}
TESTI = {
    'it': dict(titolo='Tlon', sotto='Tavola I · la geografia del pianeta', lista='Le terre di Tlon',
               did='La geografia di Tlon, disegnata dalla stessa formula del pianeta che gira più sotto: ogni dimensione è una terra.'),
    'en': dict(titolo='Tlon', sotto='Plate I · the geography of the planet', lista='The lands of Tlon',
               did='The geography of Tlon, drawn by the same formula as the planet turning below: each dimension is a land.'),
    'es': dict(titolo='Tlon', sotto='Lámina I · la geografía del planeta', lista='Las tierras de Tlon',
               did='La geografía de Tlon, trazada con la misma fórmula del planeta que gira más abajo: cada dimensión es una tierra.'),
}


def figura(lang):
    T = TESTI[lang]
    voci = ''.join('<li><a class="mappa-nome" href="%s"%s>%s</a></li>' % (
        html.escape(h[lang], quote=True), ' target="_blank" rel="noopener"' if h[lang].startswith('http') else '', html.escape(e[lang]))
        for _, _, e, h in cost.NODI)
    return ('            <figure class="statement-figura reveal">\n'
            '                <div class="mappa" id="mappaTlon">\n'
            '                    <canvas class="mappa-canvas" id="mappaCanvas" aria-hidden="true"></canvas>\n'
            '                    <div class="mappa-titolo" aria-hidden="true"><strong>%s</strong><span>%s</span></div>\n'
            '                    <ul class="mappa-nomi" aria-label="%s">%s</ul>\n'
            '                    <span class="mappa-coord mono" aria-hidden="true"></span>\n'
            '                </div>\n'
            '                <figcaption>%s</figcaption>\n'
            '            </figure>\n') % (html.escape(T['titolo']), html.escape(T['sotto']), html.escape(T['lista'], quote=True), voci, html.escape(T['did']))


def main():
    for f, lang in FILE.items():
        path = os.path.join(SITE, f)
        s = io.open(path, encoding='utf-8').read()
        m = re.search(r'[ \t]*<figure class="statement-figura reveal">.*?</figure>\n', s, re.S)
        if not m:
            raise SystemExit(f + ': figura dello statement non trovata')
        s = s[:m.start()] + figura(lang) + s[m.end():]
        io.open(path, 'w', encoding='utf-8').write(s)
        print(f, 'mappa applicata')


if __name__ == '__main__':
    main()
