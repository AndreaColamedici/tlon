#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera news.html dal file assets/data/eventi.json.

Il calendario si ordina da sé: le voci con `fine` anteriore a oggi finiscono
in "Passati", le altre in "In programma". Le voci senza data certa (la fonte
dice solo "Autunno 2026" o "Q1 2026") restano in programma e non vengono
inventate.

Uso:  python3 tools/genera-news.py
"""
import os, io, json, html, datetime, re
from genera_comune import CSS_BASE, NAV_IT, guscio

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.join(SITE, 'assets', 'data', 'eventi.json')

CSS = CSS_BASE + """
.evento{display:grid;grid-template-columns:190px 1fr;gap:2rem;align-items:start;
padding:1.8rem 0;border-top:1px solid var(--grigio-chiaro)}
.evento-data{font-size:.85rem;color:var(--grigio);padding-top:.25rem}
.evento-cat{display:inline-block;font-size:.65rem;letter-spacing:.12em;text-transform:uppercase;
color:var(--ottanio);border:1px solid var(--grigio-chiaro);border-radius:100px;
padding:.2rem .65rem;margin-bottom:.7rem}
.evento-titolo{font-family:'Instrument Serif',serif;font-size:1.5rem;line-height:1.3;
margin-bottom:.5rem}
.evento-testo{font-size:.95rem;line-height:1.75;color:var(--grigio);max-width:64ch}
.evento-link{display:inline-block;margin-top:.8rem;font-size:.8rem;letter-spacing:.06em;
text-transform:uppercase;color:var(--nero);border-bottom:1px solid var(--grigio-chiaro);
padding-bottom:2px;transition:border-color .3s ease}
.evento-link:hover{border-color:var(--nero)}
.evento[hidden]{display:none}
.gruppo-titolo{font-family:'Instrument Serif',serif;font-size:2.2rem;font-weight:400;
padding:3.5rem 3rem 0}
.gruppo-nota{padding:.6rem 3rem 0;font-size:.85rem;color:var(--grigio)}
ul.eventi{list-style:none;padding:0 3rem;margin:0}
@media (max-width:900px){
 .evento{grid-template-columns:1fr;gap:.4rem}
 ul.eventi{padding-left:1.5rem;padding-right:1.5rem}
 .gruppo-titolo,.gruppo-nota{padding-left:1.5rem;padding-right:1.5rem}
}
"""


def voce(e):
    link = ''
    if e['url']:
        etichetta = e['url_label'] or re.sub(r'^https?://(www\.)?', '', e['url']).rstrip('/')
        link = ('<a class="evento-link" href="%s" target="_blank" rel="noopener">%s</a>'
                % (html.escape(e['url'], quote=True), html.escape(etichetta)))
    return (
        '<li class="evento" data-cat="{cat}"{fine}>'
        '<div class="evento-data">{data}</div>'
        '<div><span class="evento-cat">{cat_lbl}</span>'
        '<h3 class="evento-titolo">{titolo}</h3>'
        '<p class="evento-testo">{testo}</p>{link}</div></li>'
    ).format(cat=html.escape(e['categoria'], quote=True),
             fine=(' data-fine="%s"' % e['fine']) if e['fine'] else '',
             data=html.escape(e['data_testo']), cat_lbl=html.escape(e['categoria']),
             titolo=html.escape(e['titolo']), testo=html.escape(e['testo']), link=link)


def main():
    eventi = json.load(io.open(DATI, encoding='utf-8'))
    oggi = datetime.date.today().isoformat()
    futuri = [e for e in eventi if not e['fine'] or e['fine'] >= oggi]
    passati = [e for e in eventi if e['fine'] and e['fine'] < oggi]
    futuri.sort(key=lambda e: e['fine'] or '9999')
    passati.sort(key=lambda e: e['fine'], reverse=True)

    categorie = sorted({e['categoria'] for e in eventi})
    filtri = ('<div class="filtri"><div class="filtri-gruppo">'
              '<span class="filtri-label">Tipo</span>'
              '<button class="filtro attivo" data-gruppo="cat" data-val="tutte">Tutti</button>'
              + ''.join('<button class="filtro" data-gruppo="cat" data-val="%s">%s</button>'
                        % (html.escape(c, quote=True), html.escape(c)) for c in categorie)
              + '</div></div>')

    corpo = (filtri
             + '<h2 class="gruppo-titolo">In programma</h2>'
             + '<ul class="eventi" id="gruppo-futuri">' + ''.join(voce(e) for e in futuri) + '</ul>'
             + '<p class="vuoto" id="vuoto-futuri"%s>Nessun evento in programma con questo filtro.</p>'
               % ('' if futuri else '')
             + '<h2 class="gruppo-titolo">Passati</h2>'
             + '<ul class="eventi" id="gruppo-passati">' + ''.join(voce(e) for e in passati) + '</ul>'
             + '<p class="vuoto" id="vuoto-passati" hidden>Nessun evento passato con questo filtro.</p>')

    script = """
(function(){
 var stato='tutte';
 function applica(){
  ['futuri','passati'].forEach(function(g){
   var n=0;
   document.querySelectorAll('#gruppo-'+g+' .evento').forEach(function(v){
    var ok=(stato==='tutte'||v.dataset.cat===stato); v.hidden=!ok; if(ok) n++;});
   document.getElementById('gruppo-'+g).hidden=!n;
   document.getElementById('vuoto-'+g).hidden=!!n;
  });
 }
 document.querySelectorAll('.filtro').forEach(function(b){
  b.addEventListener('click',function(){
   document.querySelectorAll('.filtro').forEach(function(o){o.classList.remove('attivo');});
   b.classList.add('attivo'); stato=b.dataset.val; applica();});
 });
 applica();
})();
"""

    jsonld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "@id": "https://www.tlon.it/news.html",
        "url": "https://www.tlon.it/news.html",
        "name": "News — Tlon",
        "inLanguage": "it",
        "isPartOf": {"@id": "https://www.tlon.it/#website"},
        "publisher": {"@id": "https://www.tlon.it/#organization"},
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(eventi),
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1,
                 "item": dict([("@type", "Event"), ("name", e['titolo']),
                               ("description", e['testo'])]
                              + ([("startDate", e['inizio'])] if e['inizio'] else [])
                              + ([("endDate", e['fine'])] if e['fine'] else [])
                              + ([("url", e['url'])] if e['url'] else [])
                              + [("organizer", {"@id": "https://www.tlon.it/#organization"})])}
                for i, e in enumerate(eventi)
            ],
        },
    }

    pagina = guscio(
        lang='it', nav=NAV_IT, attiva='./news.html', css=CSS, jsonld=jsonld,
        title='News — Eventi, festival e lezioni | Tlon',
        desc=('Il calendario di Tlon: festival, conferenze, lezioni, mostre e uscite. '
              '%d appuntamenti tra Italia ed estero, con gli eventi conclusi archiviati '
              'e consultabili.' % len(eventi)),
        canonical='https://www.tlon.it/news.html',
        ogimg='https://www.tlon.it/assets/images/og-tlon.png',
        label='Calendario',
        h1='Dove <em>siamo stati</em> e dove <em>saremo</em>',
        hero_desc=('Festival, conferenze, lezioni, mostre e presentazioni in Italia e all\'estero. '
                   'Gli eventi conclusi restano consultabili: questa pagina è anche un archivio.'),
        stats=[(len(eventi), 'appuntamenti'), (len(futuri), 'in programma'),
               (len(categorie), 'tipi di evento')],
        corpo=corpo, script=script,
        lang_switch=[('./news.html', 'IT', True)],
    )
    io.open(os.path.join(SITE, 'news.html'), 'w', encoding='utf-8').write(pagina)
    print('scritto news.html (%d eventi: %d in programma, %d passati)'
          % (len(eventi), len(futuri), len(passati)))


if __name__ == '__main__':
    main()
