#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rigenera i blocchi del calendario nelle tre home (index.html, index-en.html,
index-es.html) da assets/data/eventi.json: i prossimi sei appuntamenti in
"In programma", gli ultimi otto conclusi in "Eventi passati", il contatore e
l'etichetta di stagione. Il resto della pagina non viene toccato.

La home mostra una selezione: le voci con `"home": true` nel JSON hanno la
precedenza, le altre riempiono i posti rimasti in ordine di data.

I testi in inglese e spagnolo si prendono dai campi facoltativi `testo_en` e
`testo_es`; se mancano resta l'italiano. Le date si traducono da sé.

Uso:  python3 tools/genera-home-news.py
"""
import os, io, json, html, datetime, re

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.join(SITE, 'assets', 'data', 'eventi.json')
QUANTI_PROSSIMI, QUANTI_PASSATI = 6, 8

MESI = {
    'it': ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre'],
    'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
    'es': ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'],
}
STAGIONI = {'it': ['Inverno', 'Primavera', 'Estate', 'Autunno'], 'en': ['Winter', 'Spring', 'Summer', 'Autumn'], 'es': ['Invierno', 'Primavera', 'Verano', 'Otoño']}
TESTI = {
    'it': dict(prossimi='In programma', link='vedi tutti i %d', passati='Eventi passati'),
    'en': dict(prossimi='Upcoming', link='see all %d', passati='Past events'),
    'es': dict(prossimi='En programa', link='ver los %d', passati='Eventos pasados'),
}
FILE = {'index.html': 'it', 'index-en.html': 'en', 'index-es.html': 'es'}


def data_breve(e, lang):
    """Toglie l'anno dal testo della data e traduce il mese; «Dicembre 2026 · data da confermare» resta com'è."""
    t = e['data_testo']
    m = re.match(r'^(\d{1,2}(?:–\d{1,2})?) (\w+) (\d{4})$', t)
    if not m:
        return t
    giorni, mese, anno = m.groups()
    try:
        i = MESI['it'].index(mese.lower())
    except ValueError:
        return t
    nome = MESI[lang][i]
    coda = ' %s' % anno if anno != str(datetime.date.today().year) else ''
    if lang == 'en':
        return '%s %s%s' % (nome, giorni, coda)
    if lang == 'es':
        return '%s de %s%s' % (giorni, nome, coda.replace(' ', ' de ', 1))
    return '%s %s%s' % (giorni, nome, coda)


def meta(e, lang, n=90):
    t = e.get('testo_' + lang) or e['testo']
    return t if len(t) <= n else t[:n].rsplit(' ', 1)[0] + '…'


def voce(e, lang):
    tag = ('<a class="news-item reveal" data-fine="%s" href="%s" target="_blank" rel="noopener">'
           % (e['fine'] or '', html.escape(e['url'], quote=True))) if e['url'] else \
          ('<div class="news-item reveal"%s>' % ((' data-fine="%s"' % e['fine']) if e['fine'] else ''))
    chiusura = '</a>' if e['url'] else '</div>'
    return ('                        %s\n'
            '                            <span class="news-item-tag">%s</span>\n'
            '                            <span class="news-item-date">%s</span>\n'
            '                            <h3 class="news-item-title">%s</h3>\n'
            '                            <p class="news-item-meta">%s</p>\n'
            '                        %s\n'
            % (tag, html.escape(e['categoria']), html.escape(data_breve(e, lang)), html.escape(e['titolo']), html.escape(meta(e, lang)), chiusura))


def stagione(lang, oggi):
    s = STAGIONI[lang]
    a = s[(oggi.month % 12) // 3]
    b = s[((oggi.month + 3) % 12) // 3]
    anno = oggi.year if oggi.month < 10 else '%d–%s' % (oggi.year, str(oggi.year + 1)[2:])
    return '%s — %s %s' % (a, b, anno)


def main():
    eventi = json.load(io.open(DATI, encoding='utf-8'))
    oggi = datetime.date.today()
    iso = oggi.isoformat()
    futuri = sorted([e for e in eventi if not e['fine'] or e['fine'] >= iso], key=lambda e: e['fine'] or '9999')
    passati = sorted([e for e in eventi if e['fine'] and e['fine'] < iso], key=lambda e: e['fine'], reverse=True)
    totale = len(futuri)
    # la home mostra una selezione: prima le voci con "home": true, poi le più vicine
    scelta = lambda L, n: (sorted([e for e in L if e.get('home')], key=L.index) + [e for e in L if not e.get('home')])[:n]
    in_home_futuri = sorted(scelta(futuri, QUANTI_PROSSIMI), key=lambda e: e['fine'] or '9999')
    in_home_passati = sorted(scelta(passati, QUANTI_PASSATI), key=lambda e: e['fine'], reverse=True)

    for nome, lang in FILE.items():
        path = os.path.join(SITE, nome)
        s = io.open(path, encoding='utf-8').read()
        T = TESTI[lang]
        blocco_prossimi = ''.join(voce(e, lang) for e in in_home_futuri)
        blocco_passati = ''.join(voce(e, lang) for e in in_home_passati)

        # i blocchi finiscono al </div> che precede, rispettivamente, l'etichetta dei passati e il blocco CTA
        s, n1 = re.subn(r'(<div class="news-preview" id="news-prossimi" data-totale=")\d+(">\n).*?(\n\s*</div>)(?=\s*\n\s*<p class="news-gruppo">)',
                        lambda m: m.group(1) + str(totale) + m.group(2) + blocco_prossimi.rstrip('\n') + '\n                    </div>', s, count=1, flags=re.S)
        s, n2 = re.subn(r'(<div class="news-preview" id="news-recenti">\n).*?(\n\s*</div>)(?=\s*\n\s*<div class="news-cta-block)',
                        lambda m: m.group(1) + blocco_passati.rstrip('\n') + '\n                    </div>', s, count=1, flags=re.S)
        s, n3 = re.subn(r'<span class="news-stat-number">\d+</span>', '<span class="news-stat-number">%d</span>' % totale, s, count=1)
        s, n4 = re.subn(r'<p class="news-gruppo">[^<]*<a class="news-gruppo-link" href="./news.html">[^<]*</a></p>',
                        '<p class="news-gruppo">%s <a class="news-gruppo-link" href="./news.html">%s</a></p>' % (T['prossimi'], T['link'] % totale), s, count=1)
        s, n5 = re.subn(r'<p class="news-gruppo">[^<]*</p>\n(\s*<div class="news-preview" id="news-recenti">)', '<p class="news-gruppo">%s</p>\n\\1' % T['passati'], s, count=1)
        s, n6 = re.subn(r'<p class="news-label">[^<]*</p>', '<p class="news-label">%s</p>' % stagione(lang, oggi), s, count=1)
        assert n1 == n2 == n3 == n4 == n5 == n6 == 1, (nome, n1, n2, n3, n4, n5, n6)
        io.open(path, 'w', encoding='utf-8').write(s)
        print('scritto %s (%d in programma in tutto, %d mostrati, %d passati mostrati)' % (nome, totale, min(QUANTI_PROSSIMI, totale), min(QUANTI_PASSATI, len(passati))))


if __name__ == '__main__':
    main()
