# -*- coding: utf-8 -*-
"""Tema «Laboratorio sul presente» della home (2 novembre 2026).

Il foglio di stile intero delle tre home e il campo gravitazionale del titolo.
Ogni valore viene da tools/MASTER.md. Il CSS del pianeta e del prossimo
appuntamento vengono importati dai loro moduli, così i tre strumenti restano
d'accordo sui marcatori che usano per riapplicarsi.
"""

CSS_BASE = """
        /* ============ TEMA LABORATORIO ============ */
        /* Sistema di design in tools/MASTER.md. IMMAGINI DELLA HOME già applicate. */
        :root {
            --fondo: #F2F4F3;
            --foglio: #FFFFFF;
            --inchiostro: #0E1116;
            --grafite: #3A3F47;
            --nebbia: #6B7178;
            --linea: #D3D7D5;
            --segnale: #C72B2C;
            --segnale-scuro: #8F1F20;
            --acciaio: #5B6B7A;
            --notte: #0E1116;
            --notte-testo: #9AA1A8;
            --notte-linea: rgba(242,244,243,0.16);
            /* alias storici, usati dagli strumenti */
            --bianco: var(--foglio);
            --nero: var(--inchiostro);
            --grigio: var(--nebbia);
            --grigio-chiaro: var(--linea);
            --crema: var(--fondo);
            --ottanio: var(--segnale);

            --display: 'Bricolage Grotesque', 'Helvetica Neue', Arial, sans-serif;
            --testo: 'IBM Plex Sans', system-ui, -apple-system, sans-serif;
            --mono: 'IBM Plex Mono', ui-monospace, Menlo, monospace;

            --s1: 8px; --s2: 16px; --s3: 24px; --s4: 40px; --s5: 64px; --s6: 104px; --s7: 168px;
            --pad: clamp(1.25rem, 4vw, 3rem);
            --max: 1400px;

            --t-micro: 140ms; --t-ui: 280ms; --t-rivela: 480ms; --t-uscita: 200ms; --scalino: 60ms;
            --ease-out: cubic-bezier(0.2, 0, 0, 1);
            --ease-in: cubic-bezier(0.4, 0, 1, 1);
        }

        html { scroll-behavior: smooth; font-size: 16px; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        img { height: auto; }
        body {
            font-family: var(--testo);
            font-size: 1.0625rem;
            line-height: 1.65;
            background: var(--fondo);
            color: var(--inchiostro);
            -webkit-font-smoothing: antialiased;
        }
        ::selection { background: var(--segnale); color: var(--fondo); }
        a { color: inherit; text-decoration: none; }
        a, button, [role="button"] { cursor: pointer; }
        :focus-visible { outline: 2px solid var(--segnale); outline-offset: 3px; }
        h1, h2, h3, h4 { font-family: var(--display); font-weight: 400; letter-spacing: -0.02em; line-height: 1; }

        /* --- primitive --- */
        .eti, .hero-label, .news-label, .news-stat-label, .news-gruppo, .news-item-tag, .tl-label, .dimensione-link,
        .evidenza-label, .ultime-uscite-label, .uu-cta, .evidenza-cta, .luogo-type, .footer-col h3, .tl-prova-txt,
        .cost-eyebrow, .cost-etichetta, .prossimo-label, .lt-titolo, .lt-oggi {
            font-family: var(--testo);
            font-size: 0.72rem;
            font-weight: 500;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            line-height: 1.3;
        }
        .mono, .news-item-date, .lt-mese, .prossimo-meta, .footer-bottom p, .statement-figura figcaption,
        .news-figura figcaption, .tl-prova-num, .news-stat-number {
            font-family: var(--mono);
            font-weight: 400;
            letter-spacing: 0;
            text-transform: none;
        }
        .btn, .tl-submit, .news-cta-btn, .luoghi > .dimensione-link {
            display: inline-flex;
            align-items: center;
            gap: 0.6rem;
            font-family: var(--testo);
            font-size: 0.85rem;
            font-weight: 500;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            line-height: 1;
            padding: 16px 24px;
            background: var(--inchiostro);
            color: var(--fondo);
            border: 1px solid var(--inchiostro);
            border-radius: 0;
            transition: background-color var(--t-micro) linear, color var(--t-micro) linear, border-color var(--t-micro) linear;
        }
        .btn:hover, .tl-submit:hover, .news-cta-btn:hover, .luoghi > .dimensione-link:hover { background: var(--segnale); border-color: var(--segnale); color: var(--fondo); }
        .btn:active, .tl-submit:active, .news-cta-btn:active, .luoghi > .dimensione-link:active { background: var(--segnale-scuro); border-color: var(--segnale-scuro); }
        .btn[disabled], .tl-submit[disabled] { background: var(--linea); border-color: var(--linea); color: var(--nebbia); cursor: not-allowed; }
        .btn svg, .news-cta-btn svg { width: 14px; height: 14px; }

        .riga, .news-gruppo-link, .tl-nota a, .luogo-address a, .prossimo-titolo a {
            position: relative;
            transition: color var(--t-micro) linear;
        }
        .riga::after, .news-gruppo-link::after, .tl-nota a::after, .luogo-address a::after, .prossimo-titolo a::after {
            content: '';
            position: absolute;
            left: 0; right: 0; bottom: -2px;
            height: 1px;
            background: var(--segnale);
            transform: scaleX(0);
            transform-origin: left;
            transition: transform 180ms var(--ease-out);
        }
        .riga:hover, .news-gruppo-link:hover, .tl-nota a:hover, .luogo-address a:hover, .prossimo-titolo a:hover { color: var(--segnale); }
        .riga:hover::after, .news-gruppo-link:hover::after, .tl-nota a:hover::after, .luogo-address a:hover::after, .prossimo-titolo a:hover::after { transform: scaleX(1); }

        .skip-link {
            position: absolute; left: var(--pad); top: -200px; z-index: 2000;
            padding: 12px 16px; background: var(--inchiostro); color: var(--fondo);
            font-size: 0.85rem; font-weight: 500;
        }
        .skip-link:focus { top: 12px; }

        /* ============ HEADER ============ */
        header {
            position: fixed; top: 0; left: 0; right: 0; z-index: 1002;
            height: 72px;
            padding: 0 var(--pad);
            display: flex; justify-content: space-between; align-items: center; gap: var(--s3);
            background: var(--fondo);
            border-bottom: 1px solid var(--linea);
        }
        .logo { display: flex; align-items: center; }
        .logo img { height: 26px; width: auto; display: block; }
        nav { display: flex; flex-wrap: nowrap; gap: clamp(1rem, 2vw, 2.4rem); margin-left: auto; }
        nav a {
            white-space: nowrap;
            font-size: 0.72rem; font-weight: 500; letter-spacing: 0.12em; text-transform: uppercase;
            color: var(--grafite);
            padding: 26px 0;
            position: relative;
            transition: color var(--t-micro) linear;
        }
        nav a::after {
            content: ''; position: absolute; left: 0; right: 0; bottom: 22px; height: 1px;
            background: var(--segnale); transform: scaleX(0); transform-origin: left;
            transition: transform 180ms var(--ease-out);
        }
        nav a:hover { color: var(--segnale); }
        nav a:hover::after { transform: scaleX(1); }
        .lang-switch { display: flex; gap: 14px; padding-left: var(--s3); margin-left: var(--s2); border-left: 1px solid var(--linea); }
        .lang-switch a { font-size: 0.72rem; font-weight: 500; letter-spacing: 0.1em; color: var(--nebbia); padding: 8px 0; transition: color var(--t-micro) linear; }
        .lang-switch a:hover { color: var(--segnale); }
        .lang-switch a.active { color: var(--inchiostro); border-bottom: 1px solid var(--inchiostro); }

        .hamburger {
            display: none; flex-direction: column; justify-content: center; gap: 6px;
            width: 44px; height: 44px; margin-right: -10px; padding: 10px;
        }
        .hamburger span { display: block; height: 1.5px; background: var(--inchiostro); transition: transform var(--t-ui) var(--ease-out), opacity var(--t-micro) linear; }
        .hamburger.active span:nth-child(1) { transform: translateY(7.5px) rotate(45deg); }
        .hamburger.active span:nth-child(2) { opacity: 0; }
        .hamburger.active span:nth-child(3) { transform: translateY(-7.5px) rotate(-45deg); }

        .mobile-menu {
            position: fixed; inset: 0; z-index: 1001;
            display: none; flex-direction: column;
            padding: calc(72px + var(--s4)) var(--pad) var(--s4);
            background: var(--fondo);
            opacity: 1;
            transition: opacity var(--t-uscita) var(--ease-in), display var(--t-uscita) allow-discrete;
        }
        .mobile-menu.active { display: flex; }
        @starting-style { .mobile-menu.active { opacity: 0; } }
        .mobile-menu a {
            font-family: var(--display); font-size: clamp(1.9rem, 7vw, 2.6rem); font-weight: 400; letter-spacing: -0.02em; line-height: 1;
            padding: 18px 0; border-top: 1px solid var(--linea);
            transition: color var(--t-micro) linear;
        }
        .mobile-menu a:hover { color: var(--segnale); }
        .mobile-menu a:last-of-type { border-bottom: 1px solid var(--linea); }
        .mobile-menu-lang { display: flex; gap: 24px; margin-top: auto; padding-top: var(--s3); }
        .mobile-menu-lang a { font-family: var(--testo); font-size: 0.85rem; font-weight: 500; letter-spacing: 0.12em; padding: 12px 0; border: 0; color: var(--nebbia); }
        .mobile-menu-lang a.active { color: var(--inchiostro); border-bottom: 1px solid var(--inchiostro); }

        /* ============ HERO ============ */
        .hero {
            min-height: 100svh;
            padding: calc(72px + var(--s5)) var(--pad) var(--s5);
            display: flex; flex-direction: column; justify-content: center;
        }
        .hero-content {
            width: 100%; max-width: var(--max); margin: 0 auto;
            display: grid; grid-template-columns: minmax(0, 1fr) minmax(240px, 320px);
            gap: var(--s4) var(--s5); align-items: end;
        }
        .hero-label { color: var(--nebbia); margin-bottom: var(--s4); display: flex; align-items: center; gap: var(--s2); }
        .hero-label::before { content: ''; width: 40px; height: 1px; background: var(--segnale); flex: none; }
        .hero-title {
            font-size: clamp(3.2rem, 10vw, 9.5rem);
            line-height: 0.92;
            letter-spacing: -0.03em;
            font-variation-settings: 'opsz' 96, 'wdth' 100, 'wght' 300;
            max-width: 12ch;
            margin-bottom: var(--s4);
            cursor: crosshair;
        }
        .hero-title em { font-style: normal; color: var(--segnale); }
        .hero-title .lettera { font-variation-settings: inherit; }
        .hero-desc { font-size: 1.125rem; line-height: 1.6; color: var(--grafite); max-width: 52ch; }
        .hero-founders { display: flex; flex-direction: column; gap: var(--s2); }
        .founder {
            display: flex; align-items: center; gap: var(--s2);
            padding: 12px; background: var(--foglio); border: 1px solid var(--linea);
            transition: border-color var(--t-micro) linear;
        }
        .founder:hover { border-color: var(--inchiostro); }
        .founder-photo { width: 64px; height: 64px; flex: none; overflow: hidden; }
        .founder-photo img { width: 100%; height: 100%; object-fit: cover; object-position: center 20%; display: block; }
        .founder-name { font-family: var(--display); font-size: 1.15rem; font-weight: 500; letter-spacing: -0.01em; transition: color var(--t-micro) linear; }
        .founder:hover .founder-name { color: var(--segnale); }
        .hero-scroll { display: none; }

        /* ============ STATEMENT ============ */
        .statement {
            background: var(--foglio);
            border-top: 1px solid var(--linea);
            padding: var(--s6) var(--pad);
            display: grid; grid-template-columns: minmax(0, 1fr);
            max-width: none;
        }
        .statement-text {
            font-family: var(--display);
            font-size: clamp(1.6rem, 3vw, 2.7rem);
            font-weight: 400; line-height: 1.22; letter-spacing: -0.02em;
            width: 100%;
            max-width: min(34ch, var(--max));
            margin: 0 auto;
        }
        .statement-text em { font-style: normal; color: var(--segnale); }
        .statement-figura { margin: 0; justify-self: start; max-width: 560px; width: 100%; }
        .statement-figura img { display: block; width: 100%; border: 1px solid var(--linea); filter: grayscale(1) contrast(1.08); }
        .statement-figura figcaption { margin-top: var(--s2); font-size: 0.8rem; color: var(--nebbia); }

        /* ============ NEWS ============ */
        .news-section {
            padding: var(--s6) var(--pad);
            background: var(--notte);
            color: var(--fondo);
        }
        .news-deco { display: none; }
        .news-container { max-width: var(--max); margin: 0 auto; }
        .news-header {
            display: grid; grid-template-columns: 1fr auto; gap: var(--s4) var(--s5); align-items: end;
            padding-bottom: var(--s4); margin-bottom: var(--s4);
            border-bottom: 1px solid var(--notte-linea);
        }
        .news-label { color: var(--notte-testo); margin-bottom: var(--s3); }
        .news-main-title { font-size: clamp(3.5rem, 8vw, 7.5rem); line-height: 0.9; font-variation-settings: 'opsz' 96, 'wght' 300; }
        .news-main-title em { font-style: normal; }
        .news-stats { display: flex; flex-direction: column; align-items: flex-end; gap: var(--s1); text-align: right; }
        .news-stat-number { font-family: var(--display); font-size: clamp(3rem, 5vw, 5rem); line-height: 0.9; font-variation-settings: 'opsz' 96, 'wght' 300; }
        .news-stat-label { color: var(--notte-testo); }
        .news-content {
            display: grid; grid-template-columns: minmax(280px, 0.9fr) minmax(0, 1.5fr);
            gap: var(--s5) var(--s5); align-items: start;
        }
        .news-gruppo-col { display: flex; flex-direction: column; gap: var(--s3); padding: 0; }
        .news-gruppo { color: var(--notte-testo); padding: 0; margin: 0; display: flex; justify-content: space-between; align-items: baseline; gap: var(--s2); }
        .news-gruppo-link { color: var(--fondo); }
        .news-preview { border-top: 1px solid var(--notte-linea); }
        .news-item {
            display: grid; grid-template-columns: 7.5rem 1fr; gap: var(--s1) var(--s3); align-items: baseline;
            padding: var(--s3) 0; border-bottom: 1px solid var(--notte-linea);
            transition: background-color var(--t-micro) linear;
        }
        .news-item-tag { grid-column: 2; order: 1; color: var(--notte-testo); margin-bottom: 2px; }
        .news-item-date { grid-column: 1; grid-row: 1 / span 3; font-size: 0.85rem; color: var(--notte-testo); line-height: 1.4; padding-top: 3px; }
        .news-item-title { grid-column: 2; order: 2; font-size: 1.4rem; font-weight: 500; line-height: 1.15; letter-spacing: -0.015em; font-variation-settings: 'opsz' 40; transition: color var(--t-micro) linear; }
        .news-item-meta { grid-column: 2; order: 3; font-size: 0.92rem; line-height: 1.55; color: var(--notte-testo); }
        a.news-item:hover .news-item-title { color: var(--segnale); }
        .news-item.acceso { background: rgba(199,43,44,0.10); box-shadow: -12px 0 0 rgba(199,43,44,0.10), 12px 0 0 rgba(199,43,44,0.10); }
        .news-figura { margin: var(--s2) 0 0; }
        .news-figura img { display: block; width: 100%; border: 1px solid var(--notte-linea); }
        .news-figura figcaption { margin-top: var(--s2); font-size: 0.8rem; color: var(--notte-testo); }
        .news-cta-block {
            grid-column: 1 / -1; margin-top: var(--s2); padding-top: var(--s4);
            border-top: 1px solid var(--notte-linea);
            display: flex; justify-content: space-between; align-items: center; gap: var(--s3); flex-wrap: wrap;
        }
        .news-cta-text { font-family: var(--display); font-size: 1.4rem; line-height: 1.2; color: var(--fondo); max-width: 40ch; }
        .news-cta-btn { background: var(--fondo); color: var(--inchiostro); border-color: var(--fondo); }
        .news-cta-btn:hover { background: var(--segnale); border-color: var(--segnale); color: var(--fondo); }
"""

CSS_DOPO = """
        /* ============ TLONLETTER ============ */
        .tl-rivista { position: relative; overflow: visible; padding: var(--s6) var(--pad); background: var(--fondo); color: var(--inchiostro); border-top: 1px solid var(--linea); }
        .tl-rivista::before, .tl-rivista::after { content: none; }
        .tl-inner { max-width: var(--max); margin: 0 auto; display: grid; grid-template-columns: minmax(0, 1fr) minmax(240px, 320px); gap: var(--s5); align-items: start; }
        .tl-grid { display: grid; grid-template-columns: minmax(0, 820px); gap: var(--s4); }
        .tl-label { display: block; color: var(--nebbia); margin-bottom: var(--s3); }
        .tl-titolo { font-size: clamp(3rem, 7vw, 6.5rem); line-height: 0.92; letter-spacing: -0.03em; font-variation-settings: 'opsz' 96, 'wght' 300; margin: 0 0 var(--s3); }
        .tl-titolo em { font-style: normal; color: var(--segnale); }
        .tl-lead { font-family: var(--display); font-size: clamp(1.35rem, 2.2vw, 1.8rem); font-weight: 400; line-height: 1.3; letter-spacing: -0.015em; color: var(--inchiostro); max-width: 30ch; margin: 0 0 var(--s2); }
        .tl-lead em { font-style: normal; font-size: 1em; color: var(--segnale); }
        .tl-sotto { font-size: 1rem; line-height: 1.65; color: var(--grafite); max-width: 56ch; margin: 0 0 var(--s4); }
        .tl-form { display: flex; align-items: stretch; gap: 0; max-width: 32rem; border: 1px solid var(--inchiostro); background: var(--foglio); transition: border-color var(--t-micro) linear; }
        .tl-form:focus-within { border-color: var(--segnale); }
        .tl-input { flex: 1; min-width: 0; border: 0; background: transparent; padding: 0 var(--s2); font-family: var(--testo); font-size: 1rem; color: var(--inchiostro); }
        .tl-input::placeholder { color: var(--nebbia); }
        .tl-input:focus { outline: none; }
        .tl-form:focus-within .tl-input { box-shadow: inset 2px 0 0 var(--segnale); }
        .tl-submit { border: 0; margin: -1px; }
        .tl-nota { font-size: 0.85rem; color: var(--nebbia); margin: var(--s2) 0 0; }
        .tl-prove { display: grid; grid-template-columns: 1fr; gap: var(--s4); margin-top: 0; padding-top: 0; }
        .tl-prova { display: flex; flex-direction: column; gap: var(--s1); padding-left: var(--s2); border-left: 1px solid var(--linea); }
        .tl-prova-num { font-family: var(--display); font-size: clamp(2rem, 3.5vw, 3rem); line-height: 1; font-variation-settings: 'opsz' 96, 'wght' 300; }
        .tl-prova-txt { color: var(--nebbia); }
        .tl-figura { display: none; }

        /* ============ SEZIONI ============ */
        .section-header {
            max-width: var(--max); margin: 0 auto var(--s4);
            display: flex; justify-content: space-between; align-items: baseline; gap: var(--s3);
        }
        .section-title {
            font-size: clamp(2rem, 4.5vw, 4rem); line-height: 1; letter-spacing: -0.025em; font-variation-settings: 'opsz' 60, 'wght' 400;
            position: relative; padding-top: var(--s3);
        }
        .section-title::before {
            content: ''; position: absolute; top: 0; left: 0; width: 120px; height: 1px; background: var(--segnale);
            transform: scaleX(0); transform-origin: left; transition: transform var(--t-rivela) var(--ease-out);
        }
        .section-title.visible::before { transform: scaleX(1); }
        .section-num { display: none; }

        /* ============ DIMENSIONI ============ */
        .dimensioni { background: var(--foglio); border-top: 1px solid var(--linea); padding: var(--s6) var(--pad); }
        .dimensioni-grid {
            max-width: var(--max); margin: 0 auto;
            display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 1px;
            background: var(--linea); border: 1px solid var(--linea);
        }
        .dimensione {
            background: var(--foglio); padding: var(--s3) var(--s3) var(--s4);
            display: flex; flex-direction: column; gap: var(--s2); min-height: 100%;
            transition: background-color var(--t-micro) linear;
        }
        .dimensione:hover { background: var(--fondo); }
        .dimensione-icona { width: 36px; height: 36px; color: var(--inchiostro); margin-bottom: var(--s2); }
        .dimensione-num { display: none; }
        .dimensione-title { font-size: 1.4rem; font-weight: 500; letter-spacing: -0.015em; font-variation-settings: 'opsz' 40; transition: color var(--t-micro) linear; }
        .dimensione:hover .dimensione-title { color: var(--segnale); }
        .dimensione-desc { font-size: 0.92rem; line-height: 1.55; color: var(--grafite); flex: 1; }
        .dimensione-link { color: var(--inchiostro); display: inline-flex; align-items: center; gap: 0.5rem; align-self: flex-start; transition: color var(--t-micro) linear; }
        .dimensione-link::after { content: '\\2192'; font-family: var(--testo); transition: transform var(--t-ui) var(--ease-out); }
        .dimensione-link:hover { color: var(--segnale); }
        .dimensione-link:hover::after { transform: translateX(4px); }

        /* ============ EVIDENZA ============ */
        .evidenza { background: var(--fondo); color: var(--inchiostro); padding: var(--s6) var(--pad); border-top: 1px solid var(--linea); }
        .ev-deco-ring, .ev-dot, .ev-line-deco, .ev-constellation { display: none; }
        .evidenza-grid { max-width: var(--max); margin: 0 auto; display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(280px, 1fr); gap: var(--s4); align-items: start; }
        .evidenza-main {
            display: grid; grid-template-columns: 240px 1fr; gap: var(--s4); align-items: center;
            padding: var(--s4); background: var(--foglio); border: 1px solid var(--linea);
            transition: border-color var(--t-micro) linear;
        }
        .evidenza-main:hover { border-color: var(--inchiostro); }
        .evidenza-main-visual { position: relative; }
        .evidenza-book-frame { transform: none; }
        .evidenza-book-cover { width: 100%; display: block; border: 1px solid var(--linea); box-shadow: none; }
        .evidenza-book-glow { display: none; }
        .evidenza-main-content { display: flex; flex-direction: column; gap: var(--s2); }
        .evidenza-label { color: var(--segnale); display: flex; align-items: center; gap: var(--s2); }
        .evidenza-label::before { content: ''; width: 28px; height: 1px; background: var(--segnale); }
        .evidenza-main-title { font-size: clamp(2rem, 3.4vw, 2.8rem); line-height: 1.02; letter-spacing: -0.02em; font-variation-settings: 'opsz' 60; color: var(--inchiostro); transition: color var(--t-micro) linear; }
        .evidenza-main:hover .evidenza-main-title { color: var(--segnale); }
        .evidenza-authors { font-size: 0.95rem; color: var(--grafite); }
        .evidenza-excerpt { font-size: 1rem; line-height: 1.6; color: var(--grafite); }
        .evidenza-cta { display: inline-flex; align-items: center; gap: 0.6rem; color: var(--inchiostro); margin-top: var(--s1); }
        .evidenza-cta svg { width: 16px; height: 16px; transition: transform var(--t-ui) var(--ease-out); }
        .evidenza-main:hover .evidenza-cta svg { transform: translateX(4px); }
        .evidenza-list { display: flex; flex-direction: column; border-top: 1px solid var(--linea); }
        .evidenza-item { display: flex; flex-direction: column; gap: 4px; padding: var(--s3) 0; border-bottom: 1px solid var(--linea); }
        .evidenza-item-title { font-size: 1.35rem; font-weight: 500; letter-spacing: -0.015em; font-variation-settings: 'opsz' 40; transition: color var(--t-micro) linear; }
        .evidenza-item:hover .evidenza-item-title { color: var(--segnale); }
        .evidenza-item-meta { font-size: 0.9rem; color: var(--nebbia); }
        .ultime-uscite { max-width: var(--max); margin: var(--s5) auto 0; padding-top: var(--s4); border-top: 1px solid var(--linea); }
        .ultime-uscite-label { color: var(--nebbia); margin-bottom: var(--s3); }
        .ultime-uscite-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1px; background: var(--linea); border: 1px solid var(--linea); }
        .ultime-uscite--due .ultime-uscite-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .uu-card { display: grid; grid-template-columns: 110px 1fr; gap: var(--s3); align-items: start; padding: var(--s3); background: var(--foglio); transition: background-color var(--t-micro) linear; }
        .uu-card:hover { background: var(--fondo); }
        .uu-cover img { width: 100%; display: block; border: 1px solid var(--linea); box-shadow: none; transform: none; }
        .uu-info { display: flex; flex-direction: column; gap: 6px; min-height: 100%; }
        .uu-title { font-size: 1.25rem; font-weight: 500; letter-spacing: -0.015em; font-variation-settings: 'opsz' 40; line-height: 1.15; color: var(--inchiostro); transition: color var(--t-micro) linear; }
        .uu-card:hover .uu-title { color: var(--segnale); }
        .uu-author { font-size: 0.9rem; color: var(--grafite); }
        .uu-desc { font-size: 0.88rem; line-height: 1.55; color: var(--grafite); display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
        .uu-cta { display: inline-flex; align-items: center; gap: 0.5rem; color: var(--inchiostro); margin-top: auto; padding-top: var(--s1); }
        .uu-cta svg { width: 14px; height: 14px; transition: transform var(--t-ui) var(--ease-out); }
        .uu-card:hover .uu-cta svg { transform: translateX(4px); }

        /* ============ LUOGHI ============ */
        .luoghi { background: var(--foglio); border-top: 1px solid var(--linea); padding: var(--s6) var(--pad); }
        .luoghi-grid { max-width: var(--max); margin: 0 auto var(--s4); display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: var(--s4); }
        .luogo { display: flex; flex-direction: column; gap: var(--s1); }
        .luogo-foto { margin: 0 0 var(--s2); aspect-ratio: 4 / 3; overflow: hidden; border: 1px solid var(--linea); }
        .luogo-foto img { width: 100%; height: 100%; object-fit: cover; display: block; }
        .luogo-marker { display: none; }
        .luogo-name { font-size: 1.4rem; font-weight: 500; letter-spacing: -0.015em; font-variation-settings: 'opsz' 40; }
        .luogo-type { color: var(--nebbia); }
        .luogo-address { font-size: 0.95rem; line-height: 1.6; color: var(--grafite); margin-top: var(--s1); }
        .luoghi > .dimensione-link { max-width: var(--max); margin: 0 auto; display: inline-flex; }
        .luoghi > .dimensione-link::after { content: none; }
        .luoghi-wrap { max-width: var(--max); margin: 0 auto; }

        /* ============ FOOTER ============ */
        footer { background: var(--notte); color: var(--fondo); padding: var(--s5) var(--pad) var(--s4); }
        .footer-grid { max-width: var(--max); margin: 0 auto; display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.4fr); gap: var(--s5); padding-bottom: var(--s4); border-bottom: 1px solid var(--notte-linea); }
        .footer-brand { font-family: var(--display); font-size: clamp(2.4rem, 4vw, 3.5rem); line-height: 0.9; letter-spacing: -0.02em; font-variation-settings: 'opsz' 96, 'wght' 300; margin-bottom: var(--s2); }
        .footer-tagline { color: var(--notte-testo); font-size: 1rem; }
        .footer-links { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--s3); }
        .footer-col { display: flex; flex-direction: column; gap: var(--s1); }
        .footer-col h3 { color: var(--notte-testo); margin-bottom: var(--s1); font-family: var(--testo); }
        .footer-col a { font-size: 1rem; color: var(--fondo); padding: 2px 0; transition: color var(--t-micro) linear; }
        .footer-col a:hover { color: var(--segnale); }
        .footer-bottom { max-width: var(--max); margin: var(--s3) auto 0; display: flex; justify-content: space-between; gap: var(--s3); flex-wrap: wrap; }
        .footer-bottom p { font-size: 0.75rem; line-height: 1.6; color: var(--notte-testo); }
        .footer-social { display: flex; gap: var(--s3); }
        .footer-social a { font-size: 0.75rem; font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase; color: var(--fondo); transition: color var(--t-micro) linear; }
        .footer-social a:hover { color: var(--segnale); }

        /* ============ RIVELAZIONI ============ */
        .reveal { opacity: 0; transform: translateY(12px); transition: opacity var(--t-rivela) var(--ease-out), transform var(--t-rivela) var(--ease-out); }
        .reveal.visible { opacity: 1; transform: none; }
        .dimensioni-grid .reveal:nth-child(2), .luoghi-grid .reveal:nth-child(2), .evidenza-list .reveal:nth-child(2), .news-preview .reveal:nth-child(2) { transition-delay: calc(var(--scalino) * 1); }
        .dimensioni-grid .reveal:nth-child(3), .luoghi-grid .reveal:nth-child(3), .evidenza-list .reveal:nth-child(3), .news-preview .reveal:nth-child(3) { transition-delay: calc(var(--scalino) * 2); }
        .dimensioni-grid .reveal:nth-child(4), .luoghi-grid .reveal:nth-child(4), .evidenza-list .reveal:nth-child(4), .news-preview .reveal:nth-child(4) { transition-delay: calc(var(--scalino) * 3); }
        .dimensioni-grid .reveal:nth-child(5), .news-preview .reveal:nth-child(5) { transition-delay: calc(var(--scalino) * 4); }
        .dimensioni-grid .reveal:nth-child(6), .news-preview .reveal:nth-child(6) { transition-delay: calc(var(--scalino) * 5); }
        .dimensioni-grid .reveal:nth-child(7), .news-preview .reveal:nth-child(7) { transition-delay: calc(var(--scalino) * 6); }
        .dimensioni-grid .reveal:nth-child(8), .news-preview .reveal:nth-child(8) { transition-delay: calc(var(--scalino) * 7); }
        .dimensioni-grid .reveal:nth-child(9) { transition-delay: calc(var(--scalino) * 8); }
        .dimensioni-grid .reveal:nth-child(10) { transition-delay: calc(var(--scalino) * 9); }

        @media (prefers-reduced-motion: reduce) {
            .reveal { opacity: 1 !important; transform: none !important; transition: none !important; }
            .section-title::before { transform: scaleX(1); transition: none; }
            .hero-title .lettera { font-variation-settings: 'opsz' 96, 'wdth' 100, 'wght' 400 !important; }
            .hero-title { font-variation-settings: 'opsz' 96, 'wdth' 100, 'wght' 400; cursor: default; }
            *, *::before, *::after { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.01ms !important; scroll-behavior: auto !important; }
        }

        /* ============ RESPONSIVE ============ */
        @media (max-width: 1200px) {
            .dimensioni-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
        }
        @media (max-width: 1024px) {
            .news-content { grid-template-columns: 1fr; }
            .evidenza-grid { grid-template-columns: 1fr; }
            .luoghi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .ultime-uscite-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        @media (max-width: 900px) {
            nav, .lang-switch { display: none; }
            .hamburger { display: flex; }
            .hero { min-height: auto; padding-top: calc(72px + var(--s4)); }
            .hero-content { grid-template-columns: 1fr; }
            .hero-founders { flex-direction: row; }
            .founder { flex: 1; }
            .statement { padding: var(--s5) var(--pad); }
            .news-section, .tl-rivista, .dimensioni, .evidenza, .luoghi { padding: var(--s5) var(--pad); }
            .news-header { grid-template-columns: 1fr; }
            .news-stats { align-items: flex-start; text-align: left; }
            .dimensioni-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .evidenza-main { grid-template-columns: 1fr; padding: var(--s3); }
            .evidenza-main-visual { max-width: 200px; }
            .ultime-uscite-grid, .ultime-uscite--due .ultime-uscite-grid { grid-template-columns: 1fr; }
            .footer-grid { grid-template-columns: 1fr; gap: var(--s4); }
            .tl-inner { grid-template-columns: 1fr; gap: var(--s4); }
            .tl-prove { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--s3); padding-top: var(--s3); border-top: 1px solid var(--linea); }
        }
        @media (max-width: 640px) {
            .hero-title { font-size: clamp(2.8rem, 13vw, 4.5rem); max-width: none; }
            .hero-founders { flex-direction: column; }
            .news-item { grid-template-columns: 1fr; }
            .news-item-date { grid-row: auto; grid-column: 1; order: 0; }
            .news-item-tag, .news-item-title, .news-item-meta { grid-column: 1; }
            .luoghi-grid { grid-template-columns: 1fr; }
            .dimensioni-grid { grid-template-columns: 1fr; }
            .footer-links { grid-template-columns: 1fr; }
            .footer-bottom { flex-direction: column; }
            .tl-prove { grid-template-columns: 1fr; }
            .tl-form { flex-direction: column; }
            .tl-input { padding: 14px var(--s2); }
            .tl-submit { margin: 0; }
            .uu-card { grid-template-columns: 90px 1fr; }
        }
"""

JS_CAMPO = r"""
    // Campo gravitazionale del titolo: le lettere vicine al puntatore si fanno pesanti e strette,
    // lungo una traiettoria (wght 300→800, wdth 100→w*) calcolata perché la riga non cambi larghezza.
    (function () {
        var h = document.querySelector('.hero-title');
        var hero = document.querySelector('.hero');
        if (!h || !hero || !('fonts' in document)) return;
        var menoMoto = window.matchMedia('(prefers-reduced-motion: reduce)');
        var lettere = [];
        function spezza(nodo) {
            [].slice.call(nodo.childNodes).forEach(function (n) {
                if (n.nodeType === 3) {
                    var frag = document.createDocumentFragment();
                    n.textContent.split('').forEach(function (ch) {
                        if (ch === ' ' || ch === '\n') { frag.appendChild(document.createTextNode(' ')); return; }
                        var s = document.createElement('span'); s.className = 'lettera'; s.textContent = ch; frag.appendChild(s); lettere.push(s);
                    });
                    nodo.replaceChild(frag, n);
                } else if (n.nodeType === 1) spezza(n);
            });
        }
        spezza(h);
        if (!lettere.length) return;
        var WD = 100, R = 220, px = -1e4, py = -1e4, attivo = false, cur = lettere.map(function () { return 0; });
        var sonda = document.createElement('span');
        sonda.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap;font:inherit;letter-spacing:inherit;pointer-events:none';
        sonda.textContent = h.textContent;
        function larghezza(wg, wd) { sonda.style.fontVariationSettings = '"opsz" 96,"wdth" ' + wd + ',"wght" ' + wg; return sonda.getBoundingClientRect().width; }
        function calibra() {
            h.appendChild(sonda);
            var base = larghezza(300, 100), lo = 75, hi = 100;
            for (var i = 0; i < 18; i++) { var m = (lo + hi) / 2; if (larghezza(800, m) > base) hi = m; else lo = m; }
            WD = (lo + hi) / 2; sonda.remove();
        }
        document.fonts.ready.then(function () { return document.fonts.load('800 40px "Bricolage Grotesque"'); }).then(calibra, calibra);
        window.addEventListener('resize', function () { if (!menoMoto.matches) calibra(); });
        function frame() {
            var vivo = false;
            for (var i = 0; i < lettere.length; i++) {
                var s = lettere[i], r = s.getBoundingClientRect();
                var d = Math.hypot(r.left + r.width / 2 - px, r.top + r.height / 2 - py);
                var t = d < R ? 1 - d / R : 0; t = t * t * (3 - 2 * t);
                cur[i] += (t - cur[i]) * 0.12;
                var v = cur[i];
                if (v < 0.004) { if (s.style.fontVariationSettings) { s.style.fontVariationSettings = ''; s.style.color = ''; } continue; }
                vivo = true;
                s.style.fontVariationSettings = '"opsz" 96,"wdth" ' + (100 + (WD - 100) * v).toFixed(2) + ',"wght" ' + (300 + 500 * v).toFixed(0);
                s.style.color = v > 0.55 ? 'var(--segnale)' : '';
            }
            if (vivo || px > -1e3) requestAnimationFrame(frame); else attivo = false;
        }
        function avvia() { if (!attivo) { attivo = true; requestAnimationFrame(frame); } }
        hero.addEventListener('pointermove', function (e) { if (menoMoto.matches) return; px = e.clientX; py = e.clientY; avvia(); });
        hero.addEventListener('pointerleave', function () { px = py = -1e4; avvia(); });
        hero.addEventListener('pointerup', function () { px = py = -1e4; avvia(); });
    })();
"""
