#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Applica (o riapplica) il tema «Laboratorio sul presente» alle tre home.

- sostituisce il primo blocco <style> (il foglio di stile della home) con il CSS di
  tools/tema_laboratorio.py, dentro cui stanno anche il CSS del pianeta
  (tools/costellazione.py) e del prossimo appuntamento (tools/prossimo_news.py),
  con i marcatori che quegli strumenti usano per riapplicarsi;
- toglie i fogli esterni tlonletter.css ed evidenza.css (la home li sostituisce);
- toglie il richiamo «Scorri», le decorazioni della sezione News e di «In evidenza»,
  la numerazione delle sezioni e delle dimensioni;
- inserisce il campo gravitazionale del titolo prima dell'ultimo </script>.

Idempotente. Dopo, se servono, si rilanciano applica-costellazione.py e
applica-prossimo-news.py: trovano i marcatori al loro posto.

Uso:  python3 tools/applica-tema-home.py
"""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tema_laboratorio import CSS_BASE, CSS_DOPO, JS_CAMPO
from costellazione import CSS as CSS_COST
from prossimo_news import CSS as CSS_PROSSIMO

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = ['index.html', 'index-en.html', 'index-es.html']


def foglio():
    # ordine: base (fino alla sezione News) → prossimo appuntamento → pianeta → STATEMENT → resto
    cost = CSS_COST.strip('\n')
    assert cost.startswith('        /* ============ COSTELLAZIONE ============ */')
    return (CSS_BASE.strip('\n') + '\n\n' + CSS_PROSSIMO.strip('\n') + '\n\n' + cost + '\n\n'
            + CSS_DOPO.strip('\n') + '\n')


def main():
    css = foglio()
    for f in FILE:
        path = os.path.join(SITE, f)
        s = io.open(path, encoding='utf-8').read()

        # fogli esterni
        s = re.sub(r'\n[ \t]*<link rel="stylesheet" href="/tlonletter\.css">', '', s)
        s = re.sub(r'\n[ \t]*<link rel="stylesheet" href="\./evidenza\.css">', '', s)

        # primo blocco <style>: il foglio della home
        m = re.search(r'    <style>\n.*?\n    </style>', s, re.S)
        assert m and m.start() < s.index('<body'), f + ': blocco style non trovato'
        s = s[:m.start()] + '    <style>\n' + css + '    </style>' + s[m.end():]

        # markup: richiamo allo scorrimento, decorazioni, numerazioni
        s = re.sub(r'\n[ \t]*<div class="hero-scroll">\s*<div class="scroll-line"></div>\s*[^<]*?</div>', '', s)
        s = re.sub(r'\n[ \t]*<div class="news-deco news-deco-\d"></div>', '', s)
        s = re.sub(r'\n[ \t]*<style>\n\s*\.ev-deco-ring \{.*?</style>\n', '\n', s, flags=re.S)
        s = re.sub(r'\n[ \t]*<!-- Decorazioni -->.*?</svg>\n', '\n', s, flags=re.S)
        s = re.sub(r'\n[ \t]*<span class="section-num reveal">[^<]*</span>', '', s)
        s = re.sub(r'\n[ \t]*<span class="dimensione-num">[^<]*</span>', '', s)

        # script del campo gravitazionale, prima dell'ultimo </script>
        i = s.find('    // Campo gravitazionale del titolo')
        if i >= 0:
            j = s.index('})();', i) + len('})();')
            s = s[:i] + JS_CAMPO.strip('\n') + s[j:]
        else:
            k = s.rfind('</script>')
            s = s[:k] + JS_CAMPO.rstrip('\n') + '\n\n    ' + s[k:]

        io.open(path, 'w', encoding='utf-8').write(s)
        print(f, 'tema applicato')


if __name__ == '__main__':
    main()
