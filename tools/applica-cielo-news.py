#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mette (o rimette) il «cielo degli appuntamenti» nella cella sinistra della sezione News
delle tre home, al posto della figura statica. Idempotente.

Uso:  python3 tools/applica-cielo-news.py
"""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cielo_news import CSS, JS

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = {'index.html': 'it', 'index-en.html': 'en', 'index-es.html': 'es'}
MESI = {'it': 'gen,feb,mar,apr,mag,giu,lug,ago,set,ott,nov,dic', 'en': 'Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec', 'es': 'ene,feb,mar,abr,may,jun,jul,ago,sep,oct,nov,dic'}
OGGI = {'it': 'oggi', 'en': 'today', 'es': 'hoy'}
DID = {'it': 'I prossimi appuntamenti disposti sull\u2019anno, come stelle: la linea segna oggi',
       'en': 'The coming events laid out on the year, like stars: the line marks today',
       'es': 'Las pr\u00f3ximas citas dispuestas sobre el a\u00f1o, como estrellas: la l\u00ednea marca hoy'}


def figura(lang):
    return ('                        <figure class="news-figura news-cielo reveal">\n'
            '                            <canvas class="cielo-canvas" id="cieloCanvas" data-mesi="%s" data-oggi="%s" aria-hidden="true"></canvas>\n'
            '                            <figcaption>%s</figcaption>\n'
            '                        </figure>\n' % (MESI[lang], OGGI[lang], DID[lang]))


def main():
    for f, lang in FILE.items():
        path = os.path.join(SITE, f)
        s = io.open(path, encoding='utf-8').read()
        # figura: sostituisce quella con l'immagine (qualunque immagine) nella cella "in programma"
        m = re.search(r'                        <figure class="news-figura(?: news-cielo)? reveal">\n(?:(?!</figure>)[\s\S])*?</figure>\n(?=\s*</div>\n\s*<div class="news-preview" id="news-prossimi")', s)
        if not m:
            raise SystemExit(f + ': figura della cella "in programma" non trovata')
        s = s[:m.start()] + figura(lang) + s[m.end():]
        # CSS
        if 'CIELO DEGLI APPUNTAMENTI' not in s:
            s = s.replace('        /* ============ STATEMENT ============ */', CSS.strip('\n') + '\n\n        /* ============ STATEMENT ============ */', 1)
        # script: sostituisce o aggiunge
        i = s.find('    // Cielo degli appuntamenti:')
        if i >= 0:
            j = s.index('})();', i) + len('})();')
            s = s[:i] + JS.strip('\n') + s[j:]
        else:
            k = s.rfind('</script>')
            s = s[:k] + JS.rstrip('\n') + '\n\n    ' + s[k:]
        io.open(path, 'w', encoding='utf-8').write(s)
        print(f, 'cielo applicato')


if __name__ == '__main__':
    main()
