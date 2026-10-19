#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mette «Il prossimo appuntamento» + linea del tempo nella cella sinistra della sezione News
delle tre home, al posto di qualunque figura o canvas ci fosse. Idempotente.

Uso:  python3 tools/applica-prossimo-news.py
"""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prossimo_news import CSS, JS, markup

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = {'index.html': 'it', 'index-en.html': 'en', 'index-es.html': 'es'}
TESTI = {
    'it': dict(mesi='gennaio,febbraio,marzo,aprile,maggio,giugno,luglio,agosto,settembre,ottobre,novembre,dicembre',
               tra='tra %d giorni', domani='domani', oggi='oggi', incorso='in corso', label='Il prossimo appuntamento', lt='I prossimi mesi'),
    'en': dict(mesi='January,February,March,April,May,June,July,August,September,October,November,December',
               tra='in %d days', domani='tomorrow', oggi='today', incorso='under way', label='Next up', lt='The coming months'),
    'es': dict(mesi='enero,febrero,marzo,abril,mayo,junio,julio,agosto,septiembre,octubre,noviembre,diciembre',
               tra='en %d días', domani='mañana', oggi='hoy', incorso='en curso', label='La próxima cita', lt='Los próximos meses'),
}


def main():
    for f, lang in FILE.items():
        path = os.path.join(SITE, f)
        s = io.open(path, encoding='utf-8').read()
        # la cella «in programma»: tutto ciò che sta fra l'etichetta e la chiusura della colonna
        m = re.search(r'(<p class="news-gruppo">[^\n]*</p>\n)((?:(?!</div>\n\s*<div class="news-preview" id="news-prossimi")[\s\S])*?)(\n?\s*</div>\n\s*<div class="news-preview" id="news-prossimi")', s)
        if not m:
            raise SystemExit(f + ': cella "in programma" non trovata')
        s = s[:m.end(1)] + markup(lang, TESTI[lang]) + s[m.start(3) + 1:]
        if 'PROSSIMO APPUNTAMENTO' not in s:
            s = s.replace('        /* ============ STATEMENT ============ */', CSS.strip('\n') + '\n\n        /* ============ STATEMENT ============ */', 1)
        # togli il cielo, se c'è
        s = re.sub(r'\n[ \t]*/\* ============ CIELO DEGLI APPUNTAMENTI ============ \*/\n(?:.*\n)*?(?=\n?[ \t]*/\* ============ (?:PROSSIMO APPUNTAMENTO|STATEMENT) ============ \*/)', '\n', s)
        i = s.find('    // Cielo degli appuntamenti:')
        if i >= 0:
            j = s.index('})();', i) + len('})();')
            s = s[:i] + s[j:].lstrip('\n')
        i = s.find('    // Prossimo appuntamento e linea del tempo')
        if i >= 0:
            j = s.index('})();', i) + len('})();')
            s = s[:i] + JS.strip('\n') + s[j:]
        else:
            k = s.rfind('</script>')
            s = s[:k] + JS.rstrip('\n') + '\n\n    ' + s[k:]
        io.open(path, 'w', encoding='utf-8').write(s)
        print(f, 'prossimo applicato')


if __name__ == '__main__':
    main()
