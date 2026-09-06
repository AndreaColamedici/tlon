#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sostituisce la vecchia sezione "ecosistema" con la nuova costellazione."""
import re, io, sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from costellazione import CSS, JS

# (orbita, fase, etichetta per lingua, href per lingua)
NODI = [
    (2, 0.00, {'it': 'Edizioni',    'en': 'Publishing',  'es': 'Editorial'},
              {'it': './edizioni.html', 'en': './edizioni-en.html', 'es': './edizioni-en.html'}),
    (2, 0.25, {'it': 'Librerie',    'en': 'Bookstores',  'es': 'Librerías'},
              {'it': './librerie.html', 'en': './librerie-en.html', 'es': './librerie-en.html'}),
    (2, 0.50, {'it': 'Eventi',      'en': 'Events',      'es': 'Eventos'},
              {'it': './eventi-festival.html', 'en': './eventi-festival-en.html', 'es': './eventi-festival-en.html'}),
    (2, 0.75, {'it': 'IlPod',       'en': 'IlPod',       'es': 'IlPod'},
              {'it': './ilpod.html', 'en': './ilpod-en.html', 'es': './ilpod-en.html'}),
    (1, 0.10, {'it': 'Formazione',  'en': 'Education',   'es': 'Formación'},
              {'it': './formazione.html', 'en': './formazione-en.html', 'es': './formazione-en.html'}),
    (1, 0.43, {'it': 'Ipnocrazia',  'en': 'Hypnocracy',  'es': 'Hipnocracia'},
              {'it': './ipnocrazia.html', 'en': './ipnocrazia-en.html', 'es': './ipnocrazia-en.html'}),
    (1, 0.76, {'it': 'Press',       'en': 'Press',       'es': 'Press'},
              {'it': './press.html', 'en': './press-en.html', 'es': './press-en.html'}),
    (0, 0.20, {'it': 'Il Progetto', 'en': 'The Project', 'es': 'El Proyecto'},
              {'it': './il-progetto.html', 'en': './il-progetto-en.html', 'es': './il-progetto-en.html'}),
    (0, 0.53, {'it': 'Newsletter',  'en': 'Newsletter',  'es': 'Newsletter'},
              {'it': 'https://www.tlonletter.it', 'en': 'https://www.tlonletter.it', 'es': 'https://www.tlonletter.it'}),
    (0, 0.86, {'it': 'Contatti',    'en': 'Contact',     'es': 'Contacto'},
              {'it': './contatti/', 'en': './contatti/en.html', 'es': './contatti/en.html'}),
]

DIDASCALIA = {
    'it': 'Un ecosistema in cui ogni dimensione si intreccia con le altre',
    'en': 'An ecosystem where every dimension interweaves with the others',
    'es': 'Un ecosistema donde cada dimensión se entrelaza con las demás',
}
ETICHETTA_LISTA = {
    'it': 'Le dimensioni di Tlon',
    'en': 'The dimensions of Tlon',
    'es': 'Las dimensiones de Tlon',
}

FILE = {'index.html': 'it', 'index-en.html': 'en', 'index-es.html': 'es'}


def sezione(lang):
    voci = []
    for orbita, fase, etichette, href in NODI:
        u = href[lang]
        esterno = u.startswith('http')
        voci.append(
            '<li><a class="cost-nodo" data-orbita="{o}" data-fase="{f}" href="{u}"{ext}>'
            '<span class="cost-punto" aria-hidden="true"></span>'
            '<span class="cost-etichetta">{t}</span></a></li>'.format(
                o=orbita, f=fase, u=html.escape(u, quote=True),
                ext=' target="_blank" rel="noopener"' if esterno else '',
                t=html.escape(etichette[lang])))
    return (
        '        <!-- COSTELLAZIONE -->\n'
        '        <section class="costellazione" id="ecosistema">\n'
        '            <div class="cost-wrap">\n'
        '                <div class="cost-scena" id="costScena">\n'
        '                    <canvas class="cost-canvas" id="costCanvas" aria-hidden="true"></canvas>\n'
        '                    <div class="cost-nucleo" aria-hidden="true">TLON</div>\n'
        '                    <ul class="cost-nodi" aria-label="{lista}">' + ''.join(voci) + '</ul>\n'
        '                </div>\n'
        '                <p class="cost-didascalia">{did}</p>\n'
        '            </div>\n'
        '        </section>\n'
    ).format(lista=html.escape(ETICHETTA_LISTA[lang]), did=html.escape(DIDASCALIA[lang]))


def main():
    for f, lang in FILE.items():
        s = io.open(f, encoding='utf-8').read()
        if 'cost-scena' in s:
            print(f, "gia' applicata"); continue

        # 1. CSS: sostituisco il blocco ECOSISTEMA
        a = s.index('/* ============ ECOSISTEMA ============ */')
        b = s.index('/* ============ STATEMENT ============ */')
        s = s[:a] + CSS.strip() + '\n\n        ' + s[b:]

        # 2. CSS: elimino le regole .eco-* e i keyframe rimasti altrove
        s = re.sub(r'\n\s*[^{}\n]*\.eco-[a-z-]*[^{}]*\{[^}]*\}', '', s)
        s = re.sub(r'\n\s*@keyframes\s+(rotateOrbit|orbitFloat|particleFloat|pulseGlow|nodePulse)\s*\{(?:[^{}]|\{[^}]*\})*\}', '', s)

        # 3. markup
        m = re.search(r'[ \t]*<!-- ECOSISTEMA -->\n?\s*<section class="ecosistema">.*?</section>\n', s, re.S)
        if not m:
            m = re.search(r'[ \t]*<section class="ecosistema">.*?</section>\n', s, re.S)
        s = s[:m.start()] + sezione(lang) + s[m.end():]

        # 4. script, in coda a quello esistente
        i = s.rfind('</script>')
        s = s[:i] + JS + '\n    ' + s[i:]

        io.open(f, 'w', encoding='utf-8').write(s)
        print("%s: costellazione applicata (%d nodi)" % (f, len(NODI)))


if __name__ == '__main__':
    main()
