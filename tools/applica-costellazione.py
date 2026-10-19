#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Applica (o riapplica) la sezione "costellazione" alle tre home.

Sostituisce tre blocchi delimitati da marcatori: il CSS tra
`/* ============ COSTELLAZIONE ============ */` e `/* ============ STATEMENT ============ */`,
il markup da `<!-- COSTELLAZIONE -->` alla chiusura della sezione, e lo script
che comincia con `// Costellazione:` e finisce con `})();` prima dell'ultimo </script>.
Il testo dei nodi e delle didascalie vive qui sotto, in tre lingue.

Uso:  python3 tools/applica-costellazione.py
"""
import re, io, sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from costellazione import CSS, JS

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
    (0, 0.53, {'it': 'Tlonletter',  'en': 'Tlonletter',  'es': 'Tlonletter'},
              {'it': '#tlonletter', 'en': '#tlonletter', 'es': '#tlonletter'}),
    (0, 0.86, {'it': 'Contatti',    'en': 'Contact',     'es': 'Contacto'},
              {'it': './contatti/', 'en': './contatti/en.html', 'es': './contatti/en.html'}),
]

TESTI = {
    'it': dict(eyebrow='Il pianeta', hint='Trascina per farlo girare',
               nome='Tlon', sotto='un pianeta immaginario, che esiste',
               lista='Le dimensioni di Tlon',
               did='Un ecosistema in cui ogni dimensione si intreccia con le altre'),
    'en': dict(eyebrow='The planet', hint='Drag to spin it',
               nome='Tlon', sotto='an imaginary planet that exists',
               lista='The dimensions of Tlon',
               did='An ecosystem where every dimension interweaves with the others'),
    'es': dict(eyebrow='El planeta', hint='Arrastra para girarlo',
               nome='Tlon', sotto='un planeta imaginario que existe',
               lista='Las dimensiones de Tlon',
               did='Un ecosistema donde cada dimensión se entrelaza con las demás'),
}

FILE = {'index.html': 'it', 'index-en.html': 'en', 'index-es.html': 'es'}


def sezione(lang):
    T = TESTI[lang]
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
        '                <div class="cost-intro"><span class="cost-eyebrow">{eyebrow}</span><span class="cost-hint" aria-hidden="true">{hint}</span></div>\n'
        '                <div class="cost-scena" id="costScena">\n'
        '                    <canvas class="cost-canvas" id="costCanvas" aria-hidden="true"></canvas>\n'
        '                    <div class="cost-nome" id="costNome"><strong>{nome}</strong><em>{sotto}</em></div>\n'
        '                    <ul class="cost-nodi" aria-label="{lista}">' + ''.join(voci) + '</ul>\n'
        '                </div>\n'
        '                <p class="cost-didascalia">{did}</p>\n'
        '            </div>\n'
        '        </section>\n'
    ).format(eyebrow=html.escape(T['eyebrow']), hint=html.escape(T['hint']), nome=html.escape(T['nome']),
             sotto=html.escape(T['sotto']), lista=html.escape(T['lista']), did=html.escape(T['did']))


def main():
    for f, lang in FILE.items():
        path = os.path.join(SITE, f)
        s = io.open(path, encoding='utf-8').read()

        # 1. CSS
        a = s.index('/* ============ COSTELLAZIONE ============ */')
        b = s.index('/* ============ STATEMENT ============ */')
        s = s[:a] + CSS.strip() + '\n\n        ' + s[b:]
        # vecchia @property rimasta sopra il marcatore
        s = re.sub(r'\n\s*@property --cost-angolo \{[^}]*\}\n', '\n', s)
        s = re.sub(r'\n\s*@keyframes costDeriva \{[^}]*\}\n', '\n', s)

        # 2. markup
        m = re.search(r'[ \t]*<!-- COSTELLAZIONE -->\n\s*<section class="costellazione" id="ecosistema">.*?</section>\n', s, re.S)
        if not m:
            raise SystemExit(f + ': sezione costellazione non trovata')
        s = s[:m.start()] + sezione(lang) + s[m.end():]

        # 3. script
        i = s.index('    // Costellazione:')
        j = s.index('})();', i) + len('})();')
        s = s[:i] + JS.strip('\n') + s[j:]

        io.open(path, 'w', encoding='utf-8').write(s)
        print('%s: costellazione applicata (%d nodi)' % (f, len(NODI)))


if __name__ == '__main__':
    main()
