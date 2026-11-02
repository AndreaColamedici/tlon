#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""«La fabbrica della bellezza» (Maura Gancitano, Rizzoli, 3 novembre 2026) nella home
e nella pagina di Maura, in tutte le lingue. Idempotente.

- home (index, index-en, index-es): il libro prende il posto di «In evidenza»; Botanica
  della meraviglia scende fra «I nuovi libri di Andrea e Maura» (che diventano tre);
- maura-gancitano/index.html e en.html: una sezione nel blu del minisito subito dopo il
  ritratto, con il dipinto di copertina, il libro e le sei tappe; il libro in testa all'elenco;
- maura-gancitano/en|es|zh/index.html: una scheda in testa alla striscia dei libri.

Uso:  python3 tools/applica-fabbrica.py
"""
import io, os, re, html

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MINI = 'fabbricabellezza/'
COPERTINA = 'fabbricabellezza/img/copertina-750.webp'   # 750×961
DIPINTO = 'fabbricabellezza/img/dipinto-900.webp'       # 900×1150

TAPPE = [('Milano', '4 nov', 'Libreria Rizzoli, Galleria'), ('Firenze', '5 nov', 'Libraccio'), ('Prato', '5 nov', 'Centro Pecci'),
         ('Pescara', '6 nov', 'FLA'), ('Roma', '8 nov', 'Spazio Sette'), ('Bologna', '21 nov', 'L’Eredità delle Donne')]

T = {
 'it': dict(label='Nuovo libro · Rizzoli, dal 3 novembre', autori='Maura Gancitano',
            sotto='L’invenzione del corpo perfetto dalla fotografia all’intelligenza artificiale',
            testo='Trecentoventi pagine e centosessantanove immagini: un secolo e mezzo di sguardi, dal dagherrotipo alle immagini generate, e la domanda su quando abbiamo smesso di riconoscerci. In libreria dal 3 novembre 2026, con le presentazioni in sei città.',
            cta='Il libro e le tappe', eti='Il nuovo libro', tappe='Le presentazioni', credito='In copertina: Ewa Juszkiewicz, Lady with a Mirror (after Elisabeth Vigée Le Brun), 2026',
            nuovi='I nuovi libri di Andrea e Maura', bot_desc='Come possiamo andare avanti quando tutto crolla? Un’indagine sullo spirito umano che documenta le pratiche di resistenza culturale tra le crepe dell’apocalisse.',
            bot_titolo='Botanica della meraviglia', scopri='Scopri', mini='../fabbricabellezza/', meta='Rizzoli 2026', libro_sotto='L’invenzione del corpo perfetto dalla fotografia all’intelligenza artificiale'),
 'en': dict(label='New book · Rizzoli, from 3 November', autori='Maura Gancitano',
            sotto='The invention of the perfect body, from photography to artificial intelligence',
            testo='Three hundred and twenty pages and one hundred and sixty-nine images: a century and a half of gazes, from the daguerreotype to generated images, and the question of when we stopped recognising ourselves. In bookshops from 3 November 2026, with launches in six cities.',
            cta='The book and the dates', eti='The new book', tappe='Launches', credito='Cover: Ewa Juszkiewicz, Lady with a Mirror (after Elisabeth Vigée Le Brun), 2026',
            nuovi='The new books by Andrea and Maura', bot_desc='How can we move forward when everything collapses? An investigation into the human spirit documenting practices of cultural resistance in the cracks of the apocalypse.',
            bot_titolo='Botany of Wonder', scopri='Discover', mini='../fabbricabellezza/', meta='Rizzoli 2026', libro_sotto='The invention of the perfect body, from photography to artificial intelligence'),
 'es': dict(label='Nuevo libro · Rizzoli, desde el 3 de noviembre', autori='Maura Gancitano',
            sotto='La invención del cuerpo perfecto, de la fotografía a la inteligencia artificial',
            testo='Trescientas veinte páginas y ciento sesenta y nueve imágenes: un siglo y medio de miradas, del daguerrotipo a las imágenes generadas, y la pregunta de cuándo dejamos de reconocernos. En librerías desde el 3 de noviembre de 2026, con presentaciones en seis ciudades.',
            cta='El libro y las fechas', eti='El nuevo libro', tappe='Presentaciones', credito='Portada: Ewa Juszkiewicz, Lady with a Mirror (after Elisabeth Vigée Le Brun), 2026',
            nuovi='Los nuevos libros de Andrea y Maura', bot_desc='¿Cómo podemos seguir adelante cuando todo se derrumba? Una investigación sobre el espíritu humano que documenta las prácticas de resistencia cultural entre las grietas del apocalipsis.',
            bot_titolo='Botánica de la maravilla', scopri='Descubre', mini='../fabbricabellezza/', meta='Rizzoli 2026', libro_sotto='La invención del cuerpo perfecto, de la fotografía a la inteligencia artificial'),
 'zh': dict(meta='Rizzoli 2026', mini='../../fabbricabellezza/'),
}
MINI_NUOVE = '../../fabbricabellezza/'
E = lambda s: html.escape(s, quote=True)
FRECCIA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>'


# ---------------------------------------------------------------- home
def home(f, lang):
    t = T[lang]; p = os.path.join(SITE, f); s = io.open(p, encoding='utf-8').read()
    blocco = ('        <a href="./%s" class="evidenza-main reveal">\n'
              '            <div class="evidenza-main-visual">\n'
              '                <div class="evidenza-book-frame">\n'
              '                    <img src="./%s" alt="La fabbrica della bellezza" class="evidenza-book-cover" width="750" height="961" loading="lazy" decoding="async">\n'
              '                </div>\n'
              '                <div class="evidenza-book-glow"></div>\n'
              '            </div>\n'
              '            <div class="evidenza-main-content">\n'
              '                <span class="evidenza-label">%s</span>\n'
              '                <h3 class="evidenza-main-title">La fabbrica della bellezza</h3>\n'
              '                <p class="evidenza-authors">%s · %s</p>\n'
              '                <p class="evidenza-excerpt">%s</p>\n'
              '                <span class="evidenza-cta">%s %s</span>\n'
              '            </div>\n'
              '        </a>') % (MINI, COPERTINA, E(t['label']), E(t['autori']), E(t['sotto']), E(t['testo']), E(t['cta']), FRECCIA)
    s, n1 = re.subn(r'        <a href="[^"]*" class="evidenza-main reveal">.*?\n        </a>', lambda m: blocco, s, count=1, flags=re.S)
    assert n1 == 1, f
    # Botanica fra i nuovi libri, se non c'è già
    if 'botanica.jpg' not in s:
        carta = ('            <a href="https://shop.tlon.it/prodotto/botanica-della-meraviglia-andrea-colamedici-maura-gancitano/" class="uu-card">\n'
                 '                <div class="uu-cover">\n'
                 '                    <img src="./assets/libri/botanica.jpg" alt="Botanica della meraviglia" width="667" height="1000" loading="lazy" decoding="async">\n'
                 '                </div>\n'
                 '                <div class="uu-info">\n'
                 '                    <h3 class="uu-title">%s</h3>\n'
                 '                    <p class="uu-author">Maura Gancitano · Andrea Colamedici</p>\n'
                 '                    <p class="uu-desc">%s</p>\n'
                 '                    <span class="uu-cta">%s %s</span>\n'
                 '                </div>\n'
                 '            </a>\n') % (E(t['bot_titolo']), E(t['bot_desc']), E(t['scopri']), FRECCIA)
        s, n2 = re.subn(r'(<div class="ultime-uscite ultime-uscite--due reveal"[^>]*>\n\s*<p class="ultime-uscite-label">[^<]*</p>\n\s*<div class="ultime-uscite-grid">\n)',
                        lambda m: m.group(1).replace(' ultime-uscite--due', '') + carta, s, count=1)
        assert n2 == 1, f
    io.open(p, 'w', encoding='utf-8').write(s); print(f, 'home: libro in evidenza')


# ---------------------------------------------------------------- pagina di Maura (IT e vecchia EN)
CSS_FB = """
    <style>
        /* ============ LA FABBRICA DELLA BELLEZZA ============ */
        .fb { background: #15327a; color: #f3ecdf; position: relative; overflow: hidden; }
        .fb-inner { max-width: 1400px; margin: 0 auto; padding: 6rem 3rem; display: grid; grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr); gap: 5rem; align-items: center; }
        .fb-quadro { margin: 0; position: relative; perspective: 1400px; }
        .fb-quadro img { display: block; width: 100%; height: auto; transform: rotateY(var(--ry, 0deg)) rotateX(var(--rx, 0deg)); transition: transform 600ms cubic-bezier(.16,1,.3,1); will-change: transform; }
        .fb-quadro figcaption { margin-top: 1rem; font-family: 'Epilogue', 'Inter', sans-serif; font-size: 0.8rem; line-height: 1.5; color: #c9c4d8; }
        .fb-eti { font-family: 'Epilogue', 'Inter', sans-serif; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.22em; text-transform: uppercase; color: #c9c4d8; display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; }
        .fb-eti::before { content: ''; width: 30px; height: 1px; background: #e2772c; }
        .fb-titolo { font-family: 'Gloock', 'Instrument Serif', serif; font-weight: 400; font-size: clamp(2.6rem, 5.2vw, 4.6rem); line-height: 0.98; letter-spacing: -0.01em; margin: 0 0 1rem; }
        .fb-sotto { font-family: 'Epilogue', 'Inter', sans-serif; font-size: clamp(1.1rem, 1.6vw, 1.35rem); line-height: 1.35; color: #f3ecdf; max-width: 32ch; margin: 0 0 1.5rem; }
        .fb-sotto strong { font-weight: 600; }
        .fb-testo { font-family: 'Epilogue', 'Inter', sans-serif; font-size: 1.05rem; line-height: 1.75; color: #c9c4d8; max-width: 56ch; margin: 0 0 2.5rem; }
        .fb-tappe-eti { font-family: 'Epilogue', 'Inter', sans-serif; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.22em; text-transform: uppercase; color: #c9c4d8; margin: 0 0 0.75rem; }
        .fb-tappe { list-style: none; margin: 0 0 2.5rem; padding: 0; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.75rem 1.5rem; }
        .fb-tappa { border-top: 1px solid rgba(243,236,223,0.25); padding-top: 0.6rem; }
        .fb-citta { display: block; font-family: 'Gloock', 'Instrument Serif', serif; font-size: 1.5rem; line-height: 1.1; }
        .fb-data { display: block; font-family: 'Epilogue', 'Inter', sans-serif; font-size: 0.85rem; font-weight: 600; margin-top: 0.2rem; }
        .fb-sede { display: block; font-family: 'Epilogue', 'Inter', sans-serif; font-size: 0.8rem; color: #c9c4d8; }
        .fb-cta { display: inline-flex; align-items: center; gap: 0.75rem; padding: 1.1rem 1.75rem; background: #e2772c; color: #1a1612; font-family: 'Epilogue', 'Inter', sans-serif; font-size: 1rem; font-weight: 600; transition: background-color 160ms linear, transform 160ms linear; }
        .fb-cta:hover { background: #c9651f; }
        .fb-cta:active { transform: scale(0.97); }
        .fb-cta:focus-visible { outline: 3px solid #e2772c; outline-offset: 3px; }
        .fb-cta svg { width: 18px; height: 18px; }
        @media (max-width: 1024px) { .fb-inner { grid-template-columns: 1fr; gap: 3rem; padding: 4rem 1.5rem; } .fb-quadro { max-width: 460px; } .fb-tappe { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
        @media (max-width: 560px) { .fb-tappe { grid-template-columns: 1fr; } }
        @media (prefers-reduced-motion: reduce) { .fb-quadro img { transform: none !important; transition: none; } }
    </style>
"""
JS_FB = """
    <script>
    // il quadro si inclina sotto la mano, come nel minisito
    (function () {
        var q = document.querySelector('.fb-quadro'); if (!q) return;
        var img = q.querySelector('img');
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !window.matchMedia('(hover: hover)').matches) return;
        q.addEventListener('pointermove', function (e) {
            var r = q.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
            img.style.setProperty('--ry', (x * 10).toFixed(2) + 'deg'); img.style.setProperty('--rx', (-y * 8).toFixed(2) + 'deg');
        });
        q.addEventListener('pointerleave', function () { img.style.setProperty('--ry', '0deg'); img.style.setProperty('--rx', '0deg'); });
    })();
    </script>
"""


def sezione_fb(lang):
    t = T[lang]
    tappe = ''.join('<li class="fb-tappa"><span class="fb-citta">%s</span><span class="fb-data">%s</span><span class="fb-sede">%s</span></li>' % (E(c), E(d), E(v)) for c, d, v in TAPPE)
    return ('        <!-- LA FABBRICA DELLA BELLEZZA -->\n'
            '        <section class="fb reveal" aria-labelledby="fb-titolo">\n'
            '            <div class="fb-inner">\n'
            '                <figure class="fb-quadro">\n'
            '                    <img src="../%s" alt="Il dipinto di copertina: una dama con lo specchio, il volto coperto da una fascia arancione" width="900" height="1150" loading="lazy" decoding="async">\n'
            '                    <figcaption>%s</figcaption>\n'
            '                </figure>\n'
            '                <div class="fb-corpo">\n'
            '                    <p class="fb-eti">%s</p>\n'
            '                    <h2 class="fb-titolo" id="fb-titolo">La fabbrica della bellezza</h2>\n'
            '                    <p class="fb-sotto">%s. <strong>%s</strong></p>\n'
            '                    <p class="fb-testo">%s</p>\n'
            '                    <p class="fb-tappe-eti">%s</p>\n'
            '                    <ul class="fb-tappe">%s</ul>\n'
            '                    <a class="fb-cta" href="%s">%s %s</a>\n'
            '                </div>\n'
            '            </div>\n'
            '        </section>\n') % (DIPINTO, E(t['credito']), E(t['eti']), E(t['sotto']), E('Rizzoli, 2026.'), E(t['testo']), E(t['tappe']), tappe, t['mini'], E(t['cta']), FRECCIA)


def maura_vecchia(f, lang):
    t = T[lang]; p = os.path.join(SITE, f); s = io.open(p, encoding='utf-8').read()
    if '/assets/fonts/fabbrica.css' not in s:
        s = s.replace('    <link rel="stylesheet" href="/assets/fonts/fonts.css">', '    <link rel="stylesheet" href="/assets/fonts/fonts.css">\n    <link rel="stylesheet" href="/assets/fonts/fabbrica.css">', 1)
    # la pagina aveva una chiusura doppia dello style e un noscript senza chiusura: si ripara
    s = s.replace('\n</style></style>\n    <noscript><style>.reveal{opacity:1 !important;transform:none !important}</noscript>',
                  '\n    </style>\n    <noscript><style>.reveal{opacity:1 !important;transform:none !important}</style></noscript>', 1)
    if 'LA FABBRICA DELLA BELLEZZA ====' not in s:
        k = s.index('    <noscript><style>')
        s = s[:k] + CSS_FB.strip('\n') + '\n' + s[k:]
    s = re.sub(r'[ \t]*<!-- LA FABBRICA DELLA BELLEZZA -->\n\s*<section class="fb reveal".*?</section>\n', '', s, flags=re.S)
    m = re.search(r'</section>\n\s*\n\s*<div class="bio-content">', s)
    assert m, f + ': punto di inserimento'
    k = s.index('<div class="bio-content">', m.start())
    s = s[:k] + sezione_fb(lang).lstrip() + '\n        ' + s[k:]
    if 'fb-quadro\'); if (!q) return;' not in s:
        k2 = s.rfind('</body>'); s = s[:k2] + JS_FB.strip('\n') + '\n' + s[k2:]
    if 'La fabbrica della bellezza</span>' not in s:
        voce = ('                    <div class="libro"><span class="libro-anno">2026</span><div class="libro-info"><span class="libro-titolo">La fabbrica della bellezza</span><span class="libro-sottotitolo">%s</span></div><span class="libro-editore">Rizzoli</span></div>\n' % E(t['libro_sotto']))
        s, n = re.subn(r'(<div class="libro-categoria">\n\s*<div class="categoria-title">[^<]*</div>\n)', lambda mm: mm.group(1) + voce, s, count=1)
        assert n == 1, f + ': elenco libri'
    io.open(p, 'w', encoding='utf-8').write(s); print(f, 'pagina di Maura: sezione e voce')


# ---------------------------------------------------------------- versioni nuove EN/ES/ZH
def maura_nuova(f, lang):
    p = os.path.join(SITE, f); s = io.open(p, encoding='utf-8').read()
    if 'fabbricabellezza/img/copertina' in s: print(f, 'già presente'); return
    alt = {'en': 'Cover of La fabbrica della bellezza by Maura Gancitano', 'es': 'Portada de La fabbrica della bellezza de Maura Gancitano', 'zh': 'La fabbrica della bellezza 封面 — Maura Gancitano'}[lang]
    meta = {'en': 'Rizzoli 2026 &middot; new', 'es': 'Rizzoli 2026 &middot; novedad', 'zh': 'Rizzoli 2026 &middot; 新书'}[lang]
    carta = ('        <a href="%s" class="book-card">\n'
             '            <div class="book-cover-inner"><img src="../../%s" alt="%s" width="750" height="961" loading="lazy"></div>\n'
             '            <div class="book-title">La fabbrica della bellezza</div>\n'
             '            <div class="book-meta">%s</div>\n'
             '        </a>\n') % (MINI_NUOVE, COPERTINA, E(alt), meta)
    s, n = re.subn(r'(<div class="book-strip">\n)', lambda m: m.group(1) + carta, s, count=1)
    assert n == 1, f
    io.open(p, 'w', encoding='utf-8').write(s); print(f, 'scheda aggiunta')


def main():
    for f, lang in (('index.html', 'it'), ('index-en.html', 'en'), ('index-es.html', 'es')): home(f, lang)
    for f, lang in (('maura-gancitano/index.html', 'it'), ('maura-gancitano/en.html', 'en')): maura_vecchia(f, lang)
    for f, lang in (('maura-gancitano/en/index.html', 'en'), ('maura-gancitano/es/index.html', 'es'), ('maura-gancitano/zh/index.html', 'zh')): maura_nuova(f, lang)


if __name__ == '__main__':
    main()
