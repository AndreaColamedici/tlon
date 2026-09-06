# -*- coding: utf-8 -*-
"""Guscio condiviso delle pagine generate (press.html, news.html).

Tiene in un posto solo: palette, header, menu mobile, hero, stats, filtri,
footer, media query e il blocco prefers-reduced-motion. Le pagine aggiungono
in coda le proprie regole specifiche.
"""
import html, json, datetime

NAV_IT = [('./il-progetto.html', 'Il Progetto'), ('./andrea-colamedici/', 'Colamedici'),
          ('./maura-gancitano/', 'Gancitano'), ('./edizioni.html', 'Edizioni'),
          ('./librerie.html', 'Librerie'), ('./formazione.html', 'Formazione'),
          ('./eventi-festival.html', 'Eventi'), ('./press.html', 'Press'),
          ('./contatti/', 'Contatti')]
NAV_EN = [('./il-progetto-en.html', 'The Project'), ('./andrea-colamedici/en.html', 'Colamedici'),
          ('./maura-gancitano/en.html', 'Gancitano'), ('./edizioni-en.html', 'Publishing'),
          ('./librerie-en.html', 'Bookstores'), ('./formazione-en.html', 'Education'),
          ('./eventi-festival-en.html', 'Events'), ('./press-en.html', 'Press'),
          ('./contatti/en.html', 'Contact')]

CSS_BASE = """
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
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:2rem;
padding:3rem;border-top:1px solid var(--grigio-chiaro);
border-bottom:1px solid var(--grigio-chiaro);margin:3rem 0 0}
.stat-num{font-family:'Instrument Serif',serif;font-size:3rem;line-height:1;color:var(--nero)}
.stat-label{font-size:.75rem;letter-spacing:.15em;text-transform:uppercase;color:var(--grigio);
margin-top:.5rem}
.filtri{display:flex;flex-wrap:wrap;gap:1.2rem;padding:2.5rem 3rem 0}
.filtro{font:inherit;font-size:.75rem;letter-spacing:.08em;text-transform:uppercase;
padding:.5rem 1rem;border:1px solid var(--grigio-chiaro);background:transparent;color:var(--grigio);
border-radius:100px;cursor:pointer;transition:all .25s ease}
.filtro:hover{border-color:var(--nero);color:var(--nero)}
.filtro.attivo{background:var(--nero);border-color:var(--nero);color:var(--bianco)}
.filtri-gruppo{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center}
.filtri-label{font-size:.7rem;letter-spacing:.15em;text-transform:uppercase;color:var(--grigio);
margin-right:.5rem}
.conteggio{padding:1.5rem 3rem 0;font-size:.8rem;color:var(--grigio)}
.vuoto{padding:2.5rem 3rem;color:var(--grigio);font-size:.95rem}
.metodo{margin:5rem 3rem 0;padding:3rem;background:var(--crema)}
.metodo h2{font-family:'Instrument Serif',serif;font-size:1.8rem;font-weight:400;
margin-bottom:1.2rem}
.metodo p{font-size:.95rem;line-height:1.9;color:var(--grigio);max-width:70ch;margin-bottom:1rem}
.metodo p:last-child{margin-bottom:0}
footer{margin-top:6rem;padding:3rem;border-top:1px solid var(--grigio-chiaro);
display:flex;flex-wrap:wrap;gap:1.5rem;justify-content:space-between;
font-size:.8rem;color:var(--grigio)}
footer a:hover{color:var(--nero)}
.footer-links{display:flex;gap:1.5rem;flex-wrap:wrap}
@media (max-width:900px){
 header{padding:1rem 1.5rem}
 nav,.lang-switch{display:none}
 header .hamburger{display:flex}
 .mobile-menu .lang-switch{display:flex}
 .hero,.filtri,.conteggio,.stats,.vuoto{padding-left:1.5rem;padding-right:1.5rem}
 .metodo{margin-left:1.5rem;margin-right:1.5rem;padding:2rem}
 footer{padding:2rem 1.5rem}
}
@media (prefers-reduced-motion:reduce){
 *,*::before,*::after{animation-duration:.001ms!important;animation-iteration-count:1!important;
 transition-duration:.001ms!important;scroll-behavior:auto!important}
}
"""

SCRIPT_HEADER = """
(function(){
 var h=document.getElementById('hamburger'),m=document.getElementById('mobileMenu'),
     hd=document.querySelector('header');
 function toggle(){h.classList.toggle('active');m.classList.toggle('active');
  hd.classList.toggle('menu-open');
  h.setAttribute('aria-expanded',m.classList.contains('active'));
  document.body.style.overflow=m.classList.contains('active')?'hidden':'';}
 h.addEventListener('click',toggle);
 h.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();toggle();}});
 m.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){
  h.classList.remove('active');m.classList.remove('active');hd.classList.remove('menu-open');
  h.setAttribute('aria-expanded','false');document.body.style.overflow='';});});
 window.addEventListener('scroll',function(){hd.classList.toggle('scrolled',window.scrollY>10);});
})();
"""

ETICHETTE = {
    'it': {'skip': 'Vai al contenuto', 'menu': 'Apri il menu', 'home': 'Home',
           'progetto': 'Il Progetto', 'contatti': 'Contatti',
           'progetto_url': './il-progetto.html', 'contatti_url': './contatti/'},
    'en': {'skip': 'Skip to content', 'menu': 'Open menu', 'home': 'Home',
           'progetto': 'The Project', 'contatti': 'Contact',
           'progetto_url': './il-progetto-en.html', 'contatti_url': './contatti/en.html'},
}


def guscio(lang, nav, attiva, css, jsonld, title, desc, canonical, ogimg,
           label, h1, hero_desc, stats, corpo, script='', lang_switch=None, metodo=None):
    E = ETICHETTE[lang]
    voci_nav = ''.join('<a href="%s"%s>%s</a>' % (u, ' class="attivo"' if u == attiva else '', t)
                       for u, t in nav)
    switch = ''.join('<a href="%s"%s>%s</a>' % (u, ' class="active"' if att else '', t)
                     for u, t, att in (lang_switch or []))
    blocco_switch = ('<div class="lang-switch">%s</div>' % switch) if switch else ''
    blocco_stats = ''.join('<div class="stat"><div class="stat-num">%s</div>'
                           '<div class="stat-label">%s</div></div>'
                           % (n, html.escape(l)) for n, l in stats)
    blocco_metodo = ''
    if metodo:
        blocco_metodo = ('<section class="metodo"><h2>%s</h2>%s</section>'
                         % (html.escape(metodo[0]), ''.join('<p>%s</p>' % p for p in metodo[1])))
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
<meta property="og:type" content="website">
<meta property="og:site_name" content="Tlon">
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
{switch}
<div class="hamburger" id="hamburger" role="button" tabindex="0" aria-label="{menu}" aria-expanded="false" aria-controls="mobileMenu"><span></span><span></span><span></span></div>
</header>
<div class="mobile-menu" id="mobileMenu">{nav}{switch}</div>
<main id="contenuto">
<section class="hero">
<p class="hero-label">{label}</p>
<h1>{h1}</h1>
<p class="hero-desc">{hero_desc}</p>
</section>
<section class="stats">{stats}</section>
{corpo}
{metodo}
</main>
<footer>
<div>&copy; {anno} Tlon Srl &mdash; Via Nicol&ograve; da Pistoia, 12, 00154 Roma &mdash; P.IVA 13583341006</div>
<div class="footer-links"><a href="./">{home}</a><a href="{progetto_url}">{progetto}</a><a href="https://www.tlonletter.it">Tlonletter</a><a href="{contatti_url}">{contatti}</a></div>
</footer>
<script>{script_header}{script}</script>
</body>
</html>
""".format(lang=lang, title=html.escape(title), desc=html.escape(desc), canonical=canonical,
           ogimg=ogimg, css=css, jsonld=json.dumps(jsonld, ensure_ascii=False),
           skip=E['skip'], menu=E['menu'], nav=voci_nav, switch=blocco_switch,
           label=html.escape(label), h1=h1, hero_desc=html.escape(hero_desc),
           stats=blocco_stats, corpo=corpo, metodo=blocco_metodo,
           anno=datetime.date.today().year, home=E['home'],
           progetto=E['progetto'], progetto_url=E['progetto_url'],
           contatti=E['contatti'], contatti_url=E['contatti_url'],
           script_header=SCRIPT_HEADER, script=script)
