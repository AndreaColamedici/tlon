#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Immagini e icone nelle sezioni della home che erano solo testo (IT/EN/ES).

Idempotente: ogni inserimento è marcato da una classe e non si ripete.
- statement: la mappa incisa del pianeta accanto al testo
- news: cella «in programma» riservata al cielo degli appuntamenti (tools/applica-cielo-news.py), foto del Teatro Municipale (IlPod) nella cella dei passati
- tlonletter: natura morta dello scrittoio sopra il ritmo settimanale
- dimensioni: dieci icone a tratto (tools/icone-dimensioni.py)
- dove trovarci: una fotografia per ogni libreria

Uso:  python3 tools/applica-immagini-home.py
"""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icone_dimensioni import ICONE

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = {'index.html': 'it', 'index-en.html': 'en', 'index-es.html': 'es'}

ALT = {
    'it': dict(mappa='Mappa incisa di un pianeta immaginario', piazza='Giovanni Battista Piranesi, Veduta della Piazza della Rotonda, Roma, 1751 circa: la piazza affollata davanti al Pantheon', did_piazza='G. B. Piranesi, Veduta della Piazza della Rotonda, 1751 ca. · The Met, Open Access',
               teatro='Il Teatro Municipale di Piacenza gremito per la cerimonia di IlPod', scrittoio='Una lettera, una penna e tre libri su uno scrittoio, alla luce di una lampada',
               did_mappa='La geografia di Tlon, immaginata', did_teatro='Teatro Municipale di Piacenza, cerimonia di IlPod',
               lib=['La Libreria Teatro Tlon a Roma Ostiense', 'Tlon Aleph, il bookshop della Galleria Nazionale', 'Il bookshop di Villa Medici', 'La Libreria Giovanni alla Querini Stampalia']),
    'en': dict(mappa='Engraved map of an imaginary planet', piazza='Giovanni Battista Piranesi, View of the Piazza della Rotonda, Rome, c. 1751: the crowded square in front of the Pantheon', did_piazza='G. B. Piranesi, View of the Piazza della Rotonda, c. 1751 · The Met, Open Access',
               teatro='The Teatro Municipale in Piacenza, full for the IlPod ceremony', scrittoio='A letter, a pen and three books on a desk, by lamplight',
               did_mappa='The geography of Tlon, imagined', did_teatro='Teatro Municipale, Piacenza, IlPod ceremony',
               lib=['Teatro Tlon bookstore in Rome, Ostiense', 'Tlon Aleph, the bookshop of the Galleria Nazionale', 'The Villa Medici bookshop', 'Giovanni bookstore at the Querini Stampalia']),
    'es': dict(mappa='Mapa grabado de un planeta imaginario', piazza='Giovanni Battista Piranesi, Vista de la Piazza della Rotonda, Roma, c. 1751: la plaza llena de gente frente al Panteón', did_piazza='G. B. Piranesi, Vista de la Piazza della Rotonda, c. 1751 · The Met, Open Access',
               teatro='El Teatro Municipale de Piacenza lleno para la ceremonia de IlPod', scrittoio='Una carta, una pluma y tres libros sobre un escritorio, a la luz de una lámpara',
               did_mappa='La geografía de Tlon, imaginada', did_teatro='Teatro Municipale de Piacenza, ceremonia de IlPod',
               lib=['La Librería Teatro Tlon en Roma Ostiense', 'Tlon Aleph, la librería de la Galleria Nazionale', 'La librería de Villa Medici', 'La Librería Giovanni en la Querini Stampalia']),
}

CSS = """
        /* ============ IMMAGINI DELLA HOME ============ */
        .statement { flex-direction: column; gap: 4rem; padding-top: 9rem; padding-bottom: 9rem; }
        .statement-figura { margin: 0; width: min(100%, 720px); position: relative; }
        .statement-figura img { display: block; width: 100%; height: auto; border-radius: 2px;
            box-shadow: 0 30px 80px -40px rgba(42,107,107,0.45); }
        .statement-figura figcaption { margin-top: 0.9rem; text-align: center; font-family: 'Instrument Serif', serif;
            font-style: italic; font-size: 0.95rem; color: var(--grigio); }
        .news-gruppo-col { display: flex; flex-direction: column; gap: 1.5rem; padding: 3rem; }
        .news-gruppo-col .news-gruppo { padding: 0; margin: 0; }
        .news-figura { margin: 0; position: sticky; top: 6rem; }
        .news-figura img { display: block; width: 100%; height: auto; border-radius: 2px; opacity: 0.92;
            filter: saturate(0.85); transition: opacity 0.6s ease, filter 0.6s ease; }
        .news-figura:hover img { opacity: 1; filter: none; }
        .news-figura figcaption { margin-top: 0.7rem; font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase;
            color: rgba(255,255,255,0.45); }
        .tl-figura { margin: 0 0 2.5rem; }
        .tl-figura img { display: block; width: 100%; height: auto; border-radius: 2px; }
        .dimensione-icona { display: block; width: 36px; height: 36px; color: var(--ottanio); margin-bottom: 1.25rem;
            opacity: 0.85; transition: transform 0.5s cubic-bezier(0.16,1,0.3,1), opacity 0.4s ease; }
        .dimensione:hover .dimensione-icona { opacity: 1; transform: translateY(-3px); }
        .luogo-foto { margin: -3rem -3rem 2rem; aspect-ratio: 4 / 3; overflow: hidden; background: var(--crema); }
        .luogo-foto img { display: block; width: 100%; height: 100%; object-fit: cover;
            transition: transform 0.8s cubic-bezier(0.16,1,0.3,1); }
        .luogo:hover .luogo-foto img { transform: scale(1.04); }
        @media (max-width: 900px) {
            .news-gruppo-col { padding: 2rem 1.5rem 0; }
            .news-figura { position: static; }
            .luogo-foto { margin: -2rem -2rem 1.5rem; }
        }
"""


def main():
    for f, lang in FILE.items():
        path = os.path.join(SITE, f)
        s = io.open(path, encoding='utf-8').read()
        A = ALT[lang]
        if 'IMMAGINI DELLA HOME' in s:
            print(f, 'già applicato'); continue

        # CSS, prima del blocco STATEMENT
        s = s.replace('        /* ============ STATEMENT ============ */', CSS.strip('\n') + '\n\n        /* ============ STATEMENT ============ */', 1)

        # 1. statement: figura dopo il testo
        m = re.search(r'(<section class="statement">\n\s*<p class="statement-text reveal">.*?</p>\n)', s, re.S)
        assert m, f + ': statement'
        fig = ('            <figure class="statement-figura reveal">\n'
               '                <img src="./assets/images/home/pianeta-mappa.jpg" width="1456" height="1088" alt="%s" loading="lazy" decoding="async">\n'
               '                <figcaption>%s</figcaption>\n'
               '            </figure>\n' % (A['mappa'], A['did_mappa']))
        s = s[:m.end()] + fig + s[m.end():]

        # 2. news: le due celle di sinistra ospitano le immagini
        m = re.search(r'                    <p class="news-gruppo">((?:(?!<div)[\s\S])*?)</p>\n(\s*<div class="news-preview" id="news-prossimi")', s)
        assert m, f + ': news prossimi'
        s = s[:m.start()] + ('                    <div class="news-gruppo-col">\n'
                             '                        <p class="news-gruppo">%s</p>\n'
                             '                        <figure class="news-figura reveal">\n'
                             '                            <img src="./assets/images/home/piranesi-piazza.jpg" width="1400" height="923" alt="%s" loading="lazy" decoding="async">\n'
                             '                            <figcaption>%s</figcaption>\n'
                             '                        </figure>\n'
                             '                    </div>\n' % (m.group(1), A['piazza'], A['did_piazza'])) + m.group(2) + s[m.end():]
        m = re.search(r'                    <p class="news-gruppo">((?:(?!<div)[\s\S])*?)</p>\n(\s*<div class="news-preview" id="news-recenti")', s)
        assert m, f + ': news recenti'
        s = s[:m.start()] + ('                    <div class="news-gruppo-col">\n'
                             '                        <p class="news-gruppo">%s</p>\n'
                             '                        <figure class="news-figura reveal">\n'
                             '                            <img src="./assets/images/home/ilpod-teatro.jpg" width="1200" height="800" alt="%s" loading="lazy" decoding="async">\n'
                             '                            <figcaption>%s</figcaption>\n'
                             '                        </figure>\n'
                             '                    </div>\n' % (m.group(1), A['teatro'], A['did_teatro'])) + m.group(2) + s[m.end():]

        # 3. tlonletter: natura morta in testa alla colonna del ritmo
        s = s.replace('                    <div class="tl-ritmo">\n',
                      '                    <div class="tl-ritmo">\n'
                      '                    <figure class="tl-figura reveal"><img src="./assets/images/home/tlonletter-scrittoio.jpg" width="1456" height="1088" alt="%s" loading="lazy" decoding="async"></figure>\n' % A['scrittoio'], 1)

        # 4. dimensioni: icona prima del numero
        mappa_icone = {'dim-edizioni': 'edizioni', 'dim-librerie': 'librerie', 'dim-podcast': 'podcast', 'dim-festival': 'eventi',
                       'dim-formazione': 'formazione', 'dim-ricerca': 'ricerca', 'dim-press': 'press', 'dim-progetto': 'progetto',
                       'dim-newsletter': 'tlonletter', 'dim-contatti': 'contatti'}
        n_ic = 0
        for did, nome in mappa_icone.items():
            svg = ICONE[nome].replace('<svg ', '<svg class="dimensione-icona" ', 1)
            s, n = re.subn(r'(<div class="dimensione reveal" id="%s">\n)(\s*)(<span class="dimensione-num">)' % did,
                           lambda m: m.group(1) + m.group(2) + svg + '\n' + m.group(2) + m.group(3), s, count=1)
            n_ic += n
        assert n_ic == 10, (f, n_ic)

        # 5. luoghi: una foto per libreria
        k = [0]
        def foto(m):
            i = k[0]; k[0] += 1
            return m.group(1) + ('                    <figure class="luogo-foto"><img src="./assets/images/home/libreria-%d.jpg" alt="%s" loading="lazy" decoding="async"></figure>\n' % (i + 1, A['lib'][i])) + m.group(2)
        s, n = re.subn(r'(<div class="luogo reveal">\n)(\s*<div class="luogo-marker">)', foto, s)
        assert n == 4, (f, n)

        io.open(path, 'w', encoding='utf-8').write(s)
        print(f, 'immagini applicate')


if __name__ == '__main__':
    main()
