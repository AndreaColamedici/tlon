#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera press.html e press-en.html dal dossier mappatura-citazioni del Castello.

Fonte: ~/castello/lavori/mappatura-citazioni/citazioni/AAAA/*.md
Entrano in pagina SOLO i record con `verifica: confermato` e una `url` non vuota:
il protocollo del dossier definisce "confermato" come fonte aperta e letta
direttamente. I record `da-verificare` restano fuori finché non sono verificati.

Uso:  python3 tools/genera-press.py
"""
import os, re, io, glob, html, collections, datetime

DOSSIER = os.path.expanduser('~/castello/lavori/mappatura-citazioni/citazioni')
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LINGUE = {'it': 'Italiano', 'en': 'English', 'es': 'Español', 'fr': 'Français',
          'de': 'Deutsch', 'ca': 'Català', 'zh': '中文', 'pt': 'Português'}
LINGUE_EN = dict(LINGUE)

TIPI_IT = {'giornalistico': 'Stampa', 'accademico': 'Accademico', 'broadcast': 'Radio/TV',
           'editoriale': 'Editoriale', 'evento': 'Evento', 'istituzionale': 'Istituzionale',
           'recensione': 'Recensione', 'social': 'Social', 'wiki': 'Enciclopedico'}
TIPI_EN = {'giornalistico': 'Press', 'accademico': 'Academic', 'broadcast': 'Radio/TV',
           'editoriale': 'Publisher', 'evento': 'Event', 'istituzionale': 'Institutional',
           'recensione': 'Review', 'social': 'Social', 'wiki': 'Encyclopedic'}

MESI_IT = ['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio',
           'agosto','settembre','ottobre','novembre','dicembre']
MESI_EN = ['January','February','March','April','May','June','July',
           'August','September','October','November','December']


def campo(fm, chiave, default=''):
    # `[ \t]*` e non `\s*`: quest'ultimo scavalcherebbe il ritorno a capo su un
    # campo vuoto, catturando il valore della riga successiva
    m = re.search(r'^%s:[ \t]*(.*)$' % chiave, fm, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else default


def titolo_leggibile(t, testata):
    """`[servizio televisivo sul caso Xun]` -> `Servizio televisivo sul caso Xun`.
    I segnaposto del dossier non devono comparire in pagina con le parentesi."""
    import re as _re
    t = (t or '').strip()
    if '[' not in t:
        return t or testata
    if t.startswith('[') and t.endswith(']'):
        t = t[1:-1].strip()
    else:
        # segnaposto come prefisso: `[titolo da verificare] — pezzo di lancio`
        t = _re.sub(r'^\[[^\]]*\]\s*[—-]?\s*', '', t).strip()
    for prefisso in ('da verificare —', 'da verificare -', 'titolo da verificare'):
        if t.lower().startswith(prefisso):
            t = t[len(prefisso):].strip(' —-')
    if not t:
        return testata
    return t[0].upper() + t[1:]


def pulisci(v):
    """`[Nel Gómez]` -> `Nel Gómez`; segnaposto -> stringa vuota."""
    v = v.strip()
    if v.startswith('[') and v.endswith(']'):
        v = v[1:-1]
    if v.lower() in ('da verificare', 'non specificato', 'internazionale', 'redazione'):
        return ''
    return v


def leggi_record():
    out = []
    for f in sorted(glob.glob(os.path.join(DOSSIER, '*', '*.md'))):
        s = io.open(f, encoding='utf-8').read()
        if not s.startswith('---'):
            continue
        fm = s.split('---')[1]
        if campo(fm, 'verifica') != 'confermato':
            continue
        url = campo(fm, 'url')
        # una rassegna raccoglie fonti terze: i domini di casa restano fuori
        if campo(fm, 'autopubblicazione'):
            continue
        # cronaca locale di eventi in cui Tlon è uno dei nomi in cartellone
        if campo(fm, 'periferico'):
            continue
        # scheda generica sostituita dal pezzo reale della stessa testata
        if campo(fm, 'duplicato_di'):
            continue
        data = campo(fm, 'data')
        out.append({
            'data': data,
            'anno': data[:4],
            'testata': campo(fm, 'testata'),
            'sede': pulisci(campo(fm, 'sede_testata')),
            'lingua': campo(fm, 'lingua'),
            'paese': pulisci(campo(fm, 'paese')),
            'tipo': campo(fm, 'tipo'),
            'autore': pulisci(campo(fm, 'autore')),
            'titolo': titolo_leggibile(campo(fm, 'titolo'), campo(fm, 'testata')),
            'url': url,
            'rilevanza': campo(fm, 'rilevanza'),
            'senza_data': bool(campo(fm, 'data_incerta')),
        })
    out.sort(key=lambda r: ((1 if r['senza_data'] else 0), 
                            r['testata'].lower() if r['senza_data'] else ''),
             reverse=False)
    datati = sorted([r for r in out if not r['senza_data']],
                    key=lambda r: r['data'], reverse=True)
    perenni = sorted([r for r in out if r['senza_data']],
                     key=lambda r: r['testata'].lower())
    return datati + perenni


def data_estesa(data, mesi):
    """`2026-01-28` -> `28 gennaio 2026`. Giorno `XX` o `01` incerto -> solo mese e anno."""
    y, m, d = data.split('-')
    mese = mesi[int(m) - 1] if m.isdigit() and 1 <= int(m) <= 12 else ''
    if not d.isdigit() or d == 'XX':
        return ('%s %s' % (mese, y)).strip()
    return '%s %s %s' % (int(d), mese, y)


def riga(r, lang):
    mesi = MESI_IT if lang == 'it' else MESI_EN
    tipi = TIPI_IT if lang == 'it' else TIPI_EN
    meta = []
    # molti siti dichiarano sé stessi come autore: non ha senso ripetere la testata
    if r['autore'] and r['autore'].lower().strip() not in (r['testata'].lower().strip(),
                                                           'redazione', 'non specificato'):
        meta.append(html.escape(r['autore']))
    if r['sede']:
        meta.append(html.escape(r['sede']))
    return (
        '<li class="voce" data-lingua="{lingua}" data-tipo="{tipo}">'
        '<div class="voce-data">{data}</div>'
        '<div class="voce-corpo">'
        '<div class="voce-testata">{testata}</div>'
        '{titolo_reso}'
        '{meta}'
        '</div>'
        '<div class="voce-tag"><span class="tag-lingua">{lingua_label}</span>'
        '<span class="tag-tipo">{tipo_label}</span></div>'
        '</li>'
    ).format(
        lingua=r['lingua'], tipo=r['tipo'],
        data=('&mdash;' if r['senza_data'] else html.escape(data_estesa(r['data'], mesi))),
        testata=html.escape(r['testata']),
        titolo_reso=(
            '<a class="voce-titolo" href="%s" target="_blank" rel="noopener">%s</a>'
            % (html.escape(r['url'], quote=True), html.escape(r['titolo']) or html.escape(r['testata']))
            if r['url'] else
            '<span class="voce-titolo voce-titolo--muto">%s</span>'
            % (html.escape(r['titolo']) or html.escape(r['testata']))),
        meta=('<div class="voce-meta">%s</div>' % ' · '.join(meta)) if meta else '',
        lingua_label=r['lingua'].upper(),
        tipo_label=html.escape(tipi.get(r['tipo'], r['tipo'])),
    )


NAV_IT = [('./il-progetto.html', 'Il Progetto'), ('./andrea-colamedici/', 'Colamedici'),
          ('./maura-gancitano/', 'Gancitano'), ('./edizioni.html', 'Edizioni'), ('./formazione.html', 'Formazione'),
          ('./eventi-festival.html', 'Eventi'), ('./press.html', 'Press'),
          ('./contatti/', 'Contatti')]
NAV_EN = [('./il-progetto-en.html', 'The Project'), ('./andrea-colamedici/en.html', 'Colamedici'),
          ('./maura-gancitano/en.html', 'Gancitano'), ('./edizioni-en.html', 'Publishing'), ('./formazione-en.html', 'Education'),
          ('./eventi-festival-en.html', 'Events'), ('./press-en.html', 'Press'),
          ('./contatti/en.html', 'Contact')]

CSS = """
:root{--bianco:#ffffff;--nero:#0a0a0a;--ottanio:#2a6b6b;--grigio:#6b6b6b;
--grigio-chiaro:#e5e5e5;--crema:#f8f6f3}
*{margin:0;padding:0;box-sizing:border-box}
html{font-size:16px;scroll-behavior:smooth}
body{font-family:'Inter',-apple-system,sans-serif;background:var(--bianco);color:var(--nero);
-webkit-font-smoothing:antialiased}
::selection{background:var(--nero);color:var(--bianco)}
a{color:inherit;text-decoration:none}
.skip-link{position:absolute;left:-9999px;top:0;background:var(--nero);color:var(--bianco);
padding:.75rem 1.25rem;z-index:2000}
.skip-link:focus{left:0}
:focus-visible{outline:2px solid var(--ottanio);outline-offset:3px}
header{position:fixed;top:0;left:0;right:0;z-index:1002;padding:1.5rem 3rem;display:flex;
justify-content:space-between;align-items:center;background:var(--bianco);
border-bottom:1px solid transparent;transition:border-color .3s ease}
header.scrolled{border-bottom-color:var(--grigio-chiaro)}
header.menu-open{background:var(--nero)}
header.menu-open .logo img{filter:invert(1)}
.logo img{height:28px;width:auto;display:block}
nav{display:flex;flex-wrap:nowrap;gap:clamp(.9rem,1.9vw,2.4rem)}
nav a{font-size:.8rem;letter-spacing:.05em;text-transform:uppercase;color:var(--grigio);
white-space:nowrap;transition:color .3s ease}
nav a:hover,nav a.attivo{color:var(--nero)}
.lang-switch{display:flex;gap:.6rem;font-size:.75rem;letter-spacing:.08em}
.lang-switch a{color:var(--grigio)}
.lang-switch a.active{color:var(--nero);font-weight:600}
.hamburger{display:none;flex-direction:column;gap:5px;cursor:pointer;padding:4px}
.hamburger span{width:24px;height:2px;background:var(--nero);transition:all .3s ease}
header.menu-open .hamburger span{background:var(--bianco)}
.mobile-menu{position:fixed;inset:0;background:var(--nero);z-index:1001;display:none;
flex-direction:column;justify-content:center;align-items:center;gap:1.5rem}
.mobile-menu.active{display:flex}
.mobile-menu a{color:var(--bianco);font-size:1.4rem;font-family:'Instrument Serif',serif}
main{padding-top:7rem}
.hero{padding:4rem 3rem 3rem;max-width:1100px}
.hero-label{font-size:.8rem;font-weight:500;letter-spacing:.25em;text-transform:uppercase;
color:var(--ottanio);margin-bottom:2rem;display:flex;align-items:center;gap:1rem}
.hero-label::before{content:'';width:40px;height:1px;background:var(--ottanio);flex:none}
h1{font-family:'Instrument Serif',serif;font-size:clamp(2.6rem,6.5vw,5rem);font-weight:400;
line-height:1.05;letter-spacing:-.02em;margin-bottom:2rem}
h1 em{font-style:italic}
.hero-desc{font-size:1.1rem;line-height:1.8;color:var(--grigio);max-width:640px}
.stats{display:flex;flex-wrap:wrap;gap:3rem;padding:3rem;border-top:1px solid var(--grigio-chiaro);
border-bottom:1px solid var(--grigio-chiaro);margin:3rem 0 0}
.stat-num{font-family:'Instrument Serif',serif;font-size:3rem;line-height:1;color:var(--nero)}
.stat-label{font-size:.75rem;letter-spacing:.15em;text-transform:uppercase;color:var(--grigio);
margin-top:.5rem}
.filtri{display:flex;flex-wrap:wrap;gap:.5rem;padding:2.5rem 3rem 0}
.filtro{font:inherit;font-size:.75rem;letter-spacing:.08em;text-transform:uppercase;
padding:.5rem 1rem;border:1px solid var(--grigio-chiaro);background:transparent;color:var(--grigio);
border-radius:100px;cursor:pointer;transition:all .25s ease}
.filtro:hover{border-color:var(--nero);color:var(--nero)}
.filtro.attivo{background:var(--nero);border-color:var(--nero);color:var(--bianco)}
.filtri-gruppo{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center}
.filtri-label{font-size:.7rem;letter-spacing:.15em;text-transform:uppercase;color:var(--grigio);
margin-right:.5rem}
.conteggio{padding:1.5rem 3rem 0;font-size:.8rem;color:var(--grigio)}
.anno{font-family:'Instrument Serif',serif;font-size:2.5rem;color:var(--grigio-chiaro);
padding:3rem 3rem 1rem}
ul.voci{list-style:none;padding:0 3rem}
.voce{display:grid;grid-template-columns:170px 1fr auto;gap:2rem;align-items:start;
padding:1.6rem 0;border-top:1px solid var(--grigio-chiaro)}
.voce-data{font-size:.8rem;color:var(--grigio);letter-spacing:.04em;padding-top:.2rem}
.voce-testata{font-size:.75rem;letter-spacing:.15em;text-transform:uppercase;
color:var(--ottanio);margin-bottom:.4rem}
.voce-titolo{font-family:'Instrument Serif',serif;font-size:1.35rem;line-height:1.35;
display:inline-block;background-image:linear-gradient(var(--nero),var(--nero));
background-size:0 1px;background-repeat:no-repeat;background-position:0 100%;
transition:background-size .3s ease}
.voce-titolo:hover{background-size:100% 1px}
.voce-titolo--muto{color:var(--nero);cursor:default}
.voce-titolo--muto:hover{background-size:0 1px}
.voce-meta{font-size:.8rem;color:var(--grigio);margin-top:.5rem}
.voce-tag{display:flex;gap:.4rem;flex-wrap:wrap;justify-content:flex-end}
.tag-lingua,.tag-tipo{font-size:.65rem;letter-spacing:.1em;text-transform:uppercase;
padding:.25rem .6rem;border-radius:100px;white-space:nowrap}
.tag-lingua{background:var(--nero);color:var(--bianco)}
.tag-tipo{border:1px solid var(--grigio-chiaro);color:var(--grigio)}
.voce[hidden]{display:none}
.vuoto{padding:3rem;color:var(--grigio);font-size:.95rem}
.metodo{margin:5rem 3rem 0;padding:3rem;background:var(--crema)}
.metodo h2{font-family:'Instrument Serif',serif;font-size:1.8rem;font-weight:400;
margin-bottom:1.2rem}
.metodo p{font-size:.95rem;line-height:1.9;color:var(--grigio);max-width:70ch;
margin-bottom:1rem}
.metodo p:last-child{margin-bottom:0}
footer{margin-top:6rem;padding:3rem;border-top:1px solid var(--grigio-chiaro);
display:flex;flex-wrap:wrap;gap:1.5rem;justify-content:space-between;
font-size:.8rem;color:var(--grigio)}
footer a:hover{color:var(--nero)}
.footer-links{display:flex;gap:1.5rem;flex-wrap:wrap}
@media (max-width:900px){
 header{padding:1rem 1.5rem}
 nav,.lang-switch{display:none}
 .hamburger{display:flex}
 .hero,.filtri,.conteggio,ul.voci,.anno,.stats{padding-left:1.5rem;padding-right:1.5rem}
 .metodo{margin-left:1.5rem;margin-right:1.5rem;padding:2rem}
 .stats{gap:2rem}
 .voce{grid-template-columns:1fr;gap:.5rem}
 .voce-tag{justify-content:flex-start;margin-top:.6rem}
 footer{padding:2rem 1.5rem}
}
@media (prefers-reduced-motion:reduce){
 *,*::before,*::after{animation-duration:.001ms!important;animation-iteration-count:1!important;
 transition-duration:.001ms!important;scroll-behavior:auto!important}
}
"""

TESTI = {
 'it': {
  'title': 'Press — Rassegna internazionale | Tlon',
  'desc': ('Hanno scritto di Tlon: stampa, riviste accademiche, radio, televisione ed '
           'enciclopedie in più lingue e paesi. Libri, festival, podcast, casa editrice.'),
  'label': 'Rassegna internazionale',
  'h1': 'Hanno scritto <em>di noi</em>',
  'hero_desc': ('Le fonti che hanno raccontato i libri, i concetti e i progetti nati in Tlon: '
                'dalla casa editrice ai festival, dai podcast a Ipnocrazia e Prompt Thinking.'),
  'f_tutte': 'Tutte', 'f_lingua': 'Lingua', 'f_tipo': 'Tipo',
  'conteggio': 'voci visibili',
  'vuoto': 'Nessuna voce con questi filtri.',
  'metodo_h': 'Come è costruita questa pagina',
  'metodo': [
   ('Le voci provengono da una mappatura sistematica delle citazioni tenuta dal 2025. '
    'Ogni record nasce solo dopo che la fonte è stata aperta e letta direttamente: una '
    'segnalazione di seconda mano non basta a farla comparire. Le fonti riportate qui sono '
    'quelle che hanno superato questa verifica; quelle ancora in corso di controllo restano '
    'nell\'archivio interno e compariranno soltanto quando saranno confermate.'),
   ('Dove la testata blocca l\'accesso automatico o ha rimosso la pagina, il link punta alla '
    'copia archiviata. Se trovi un errore o conosci una citazione che manca, '
    '<a href="./contatti/" style="color:var(--nero);text-decoration:underline">scrivici</a>.'),
  ],
  'nav': NAV_IT, 'altra': ('./press-en.html', 'EN'), 'questa': ('./press.html', 'IT'),
  'menu_label': 'Apri il menu',
  'skip': 'Vai al contenuto',
  'canonical': 'https://www.tlon.it/press.html',
  'ogimg': 'https://www.tlon.it/assets/images/og-tlon.png',
  'locale': 'it_IT', 'altloc': 'en_US', 'lang': 'it',
  'aggiornato': 'Pagina aggiornata il',
 },
 'en': {
  'title': 'Press — International coverage | Tlon',
  'desc': ('Coverage of Tlon: press, academic journals, radio, television and '
           'encyclopedias across several languages and countries. Books, festivals, '
           'podcasts, publishing house.'),
  'label': 'International coverage',
  'h1': 'What has been <em>written about us</em>',
  'hero_desc': ('The sources that have covered the books, concepts and projects born at Tlon: '
                'from the publishing house to the festivals, from the podcasts to '
                'Hypnocracy and Prompt Thinking.'),
  'f_tutte': 'All', 'f_lingua': 'Language', 'f_tipo': 'Type',
  'conteggio': 'entries shown',
  'vuoto': 'No entries match these filters.',
  'metodo_h': 'How this page is built',
  'metodo': [
   ('Entries come from a systematic citation mapping maintained since 2025. A record is '
    'created only after the source has been opened and read directly: a second-hand report '
    'is not enough to list it. The sources shown here are those that passed this check; '
    'those still under review stay in the internal archive and will appear only once '
    'confirmed.'),
   ('Where a publication blocks automated access or has taken the page down, the link points '
    'to the archived copy. If you spot an error or know of a missing citation, '
    '<a href="./contatti/en.html" style="color:var(--nero);text-decoration:underline">'
    'write to us</a>.'),
  ],
  'nav': NAV_EN, 'altra': ('./press.html', 'IT'), 'questa': ('./press-en.html', 'EN'),
  'menu_label': 'Open menu',
  'skip': 'Skip to content',
  'canonical': 'https://www.tlon.it/press-en.html',
  'ogimg': 'https://www.tlon.it/assets/images/og-tlon-en.png',
  'locale': 'en_US', 'altloc': 'it_IT', 'lang': 'en',
  'aggiornato': 'Page updated on',
 },
}


def costruisci(recs, lang):
    T = TESTI[lang]
    tipi = TIPI_IT if lang == 'it' else TIPI_EN
    mesi = MESI_IT if lang == 'it' else MESI_EN

    lingue = sorted({r['lingua'] for r in recs})
    tipi_presenti = sorted({r['tipo'] for r in recs}, key=lambda t: -sum(1 for r in recs if r['tipo'] == t))
    paesi = {r['paese'] for r in recs if r['paese']}
    valori = {'n': len(recs), 'paesi': len(paesi), 'lingue': len(lingue),
              'accademiche': sum(1 for r in recs if r['tipo'] == 'accademico')}

    nav = ''.join('<a href="%s"%s>%s</a>' % (u, ' class="attivo"' if 'press' in u else '', t)
                  for u, t in T['nav'])

    f_lingua = ('<div class="filtri-gruppo"><span class="filtri-label">%s</span>'
                '<button class="filtro attivo" data-gruppo="lingua" data-val="tutte">%s</button>%s</div>'
                % (T['f_lingua'], T['f_tutte'],
                   ''.join('<button class="filtro" data-gruppo="lingua" data-val="%s">%s</button>'
                           % (l, html.escape(LINGUE.get(l, l.upper()))) for l in lingue)))
    f_tipo = ('<div class="filtri-gruppo"><span class="filtri-label">%s</span>'
              '<button class="filtro attivo" data-gruppo="tipo" data-val="tutte">%s</button>%s</div>'
              % (T['f_tipo'], T['f_tutte'],
                 ''.join('<button class="filtro" data-gruppo="tipo" data-val="%s">%s</button>'
                         % (t, html.escape(tipi.get(t, t))) for t in tipi_presenti)))

    corpo = []
    gruppo_corrente = None
    senza_data_lbl = 'Senza data' if lang == 'it' else 'Undated'
    for r in recs:
        gruppo = senza_data_lbl if r['senza_data'] else r['anno']
        if gruppo != gruppo_corrente:
            if gruppo_corrente is not None:
                corpo.append('</ul>')
            gruppo_corrente = gruppo
            corpo.append('<h2 class="anno">%s</h2><ul class="voci">' % html.escape(gruppo))
        corpo.append(riga(r, lang))
    corpo.append('</ul>')

    jsonld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "@id": T['canonical'],
        "url": T['canonical'],
        "name": T['title'],
        "description": T['desc'],
        "inLanguage": lang,
        "isPartOf": {"@id": "https://www.tlon.it/#website"},
        "publisher": {"@id": "https://www.tlon.it/#organization"},
    }
    import json as _json
    oggi = datetime.date.today()
    data_oggi = ('%d %s %d' % (oggi.day, mesi[oggi.month - 1], oggi.year)) if lang == 'it' \
        else ('%s %d, %d' % (mesi[oggi.month - 1], oggi.day, oggi.year))

    return """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="it" href="https://www.tlon.it/press.html">
<link rel="alternate" hreflang="en" href="https://www.tlon.it/press-en.html">
<link rel="alternate" hreflang="x-default" href="https://www.tlon.it/press.html">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Tlon">
<meta property="og:locale" content="{locale}">
<meta property="og:locale:alternate" content="{altloc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{ogimg}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{ogimg}">
<link rel="stylesheet" href="/assets/fonts/fonts.css">
<style>{css}</style>
<script type="application/ld+json">{jsonld}</script>
</head>
<body>
<a class="skip-link" href="#contenuto">{skip}</a>
<header>
<a href="./" class="logo"><img src="./assets/images/tlon-logo.png" alt="Tlon" width="112" height="28"></a>
<nav>{nav}</nav>
<div class="lang-switch">{switch}</div>
<div class="hamburger" id="hamburger" role="button" tabindex="0" aria-label="{menu_label}" aria-expanded="false" aria-controls="mobileMenu"><span></span><span></span><span></span></div>
</header>
<div class="mobile-menu" id="mobileMenu">{nav}<div class="lang-switch" style="margin-top:1rem">{switch}</div></div>
<main id="contenuto">
<section class="hero">
<p class="hero-label">{label}</p>
<h1>{h1}</h1>
<p class="hero-desc">{hero_desc}</p>
</section>
<div class="filtri">{f_lingua}{f_tipo}</div>
<p class="conteggio"><span id="conteggio">{n}</span> {conteggio_label}</p>
{corpo}
<p class="vuoto" id="vuoto" hidden>{vuoto}</p>
</main>
<footer>
<div>&copy; {anno} Tlon Srl &mdash; Via Nicol&ograve; da Pistoia, 12, 00154 Roma &mdash; P.IVA 13583341006</div>
<div class="footer-links"><a href="./">Home</a><a href="./il-progetto.html">Il Progetto</a><a href="https://www.tlonletter.it">Tlonletter</a><a href="./contatti/">Contatti</a></div>
</footer>
<script>
(function(){{
 var h=document.getElementById('hamburger'),m=document.getElementById('mobileMenu'),hd=document.querySelector('header');
 function toggle(){{h.classList.toggle('active');m.classList.toggle('active');hd.classList.toggle('menu-open');
  h.setAttribute('aria-expanded',m.classList.contains('active'));
  document.body.style.overflow=m.classList.contains('active')?'hidden':'';}}
 h.addEventListener('click',toggle);
 h.addEventListener('keydown',function(e){{if(e.key==='Enter'||e.key===' '){{e.preventDefault();toggle();}}}});
 m.querySelectorAll('a').forEach(function(a){{a.addEventListener('click',function(){{
  h.classList.remove('active');m.classList.remove('active');hd.classList.remove('menu-open');
  h.setAttribute('aria-expanded','false');document.body.style.overflow='';}});}});
 window.addEventListener('scroll',function(){{hd.classList.toggle('scrolled',window.scrollY>10);}});
 var stato={{lingua:'tutte',tipo:'tutte'}},voci=document.querySelectorAll('.voce'),
     cont=document.getElementById('conteggio');
 function applica(){{
  var n=0;
  voci.forEach(function(v){{
   var ok=(stato.lingua==='tutte'||v.dataset.lingua===stato.lingua)&&
          (stato.tipo==='tutte'||v.dataset.tipo===stato.tipo);
   v.hidden=!ok; if(ok) n++;
  }});
  document.querySelectorAll('ul.voci').forEach(function(ul){{
   var vis=ul.querySelectorAll('.voce:not([hidden])').length;
   ul.hidden=!vis;
   var h2=ul.previousElementSibling;
   if(h2&&h2.classList.contains('anno')) h2.hidden=!vis;
  }});
  cont.textContent=n;
  document.getElementById('vuoto').hidden=(n>0);
 }}
 document.querySelectorAll('.filtro').forEach(function(b){{
  b.addEventListener('click',function(){{
   var g=b.dataset.gruppo;
   document.querySelectorAll('.filtro[data-gruppo="'+g+'"]').forEach(function(o){{o.classList.remove('attivo');}});
   b.classList.add('attivo'); stato[g]=b.dataset.val; applica();
  }});
 }});
}})();
</script>
</body>
</html>
""".format(lang=T['lang'], title=html.escape(T['title']), desc=html.escape(T['desc']),
           canonical=T['canonical'], locale=T['locale'], altloc=T['altloc'],
           ogimg=T['ogimg'], css=CSS, jsonld=_json.dumps(jsonld, ensure_ascii=False),
           skip=T['skip'], menu_label=T['menu_label'], nav=nav,
           switch=''.join('<a href="%s"%s>%s</a>' % (u, ' class="active"' if u.endswith(
               'press-en.html' if lang == 'en' else 'press.html') else '', l)
               for u, l in (('./press.html', 'IT'), ('./press-en.html', 'EN'))),
           label=html.escape(T['label']), h1=T['h1'], hero_desc=html.escape(T['hero_desc']),
           f_lingua=f_lingua, f_tipo=f_tipo, n=len(recs),
           conteggio_label=T['conteggio'], corpo=''.join(corpo), vuoto=html.escape(T['vuoto']),
           anno=oggi.year)


def main():
    recs = leggi_record()
    if not recs:
        raise SystemExit('Nessun record confermato trovato in %s' % DOSSIER)
    for lang, nome in (('it', 'press.html'), ('en', 'press-en.html')):
        p = os.path.join(SITE, nome)
        io.open(p, 'w', encoding='utf-8').write(costruisci(recs, lang))
        print('scritto %s (%d voci)' % (nome, len(recs)))


if __name__ == '__main__':
    main()
