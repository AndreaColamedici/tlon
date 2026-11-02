# -*- coding: utf-8 -*-
"""«Il prossimo appuntamento»: la cella sinistra della sezione News, senza canvas.

Il prossimo evento in programma, letto dal DOM, composto in grande: il giorno in
Instrument Serif, il mese e l'anno, il titolo, quanto manca. Sotto, una linea del
tempo orizzontale dei mesi a venire con un punto per ogni evento in programma e
il segno di oggi; passando su un punto si illumina la voce nell'elenco, e
viceversa. Niente animazioni oltre al respiro del punto del prossimo evento.
"""

CSS = """
        /* ============ PROSSIMO APPUNTAMENTO ============ */
        .prossimo { margin: 0; }
        .prossimo-label { display: block; color: var(--notte-testo); margin-bottom: var(--s3); }
        .prossimo-data { display: flex; align-items: baseline; gap: var(--s2); line-height: 0.85; margin-bottom: var(--s2); }
        .prossimo-giorno { font-family: var(--display); font-size: clamp(5rem, 9vw, 8.5rem); font-variation-settings: 'opsz' 96, 'wght' 300; color: var(--fondo); letter-spacing: -0.04em; line-height: 0.85; }
        .prossimo-mese { font-family: var(--display); font-size: clamp(1.3rem, 1.9vw, 1.7rem); font-weight: 400; color: var(--notte-testo); line-height: 1; }
        .prossimo-titolo { font-family: var(--display); font-weight: 500; font-size: clamp(1.4rem, 2.2vw, 1.9rem); line-height: 1.15; letter-spacing: -0.015em; font-variation-settings: 'opsz' 40; color: var(--fondo); margin: 0 0 var(--s2); max-width: 24ch; }
        .prossimo-titolo a { color: inherit; }
        .prossimo-meta { font-size: 0.85rem; color: var(--segnale); margin: 0; display: flex; align-items: center; gap: 0.6rem; }
        .prossimo-meta .prossimo-punto { display: inline-block; width: 8px; height: 8px; background: var(--segnale); flex: none; }
        .prossimo-nota { font-size: 0.9rem; line-height: 1.6; color: var(--notte-testo); margin: var(--s2) 0 0; max-width: 34ch; }

        .lt { position: relative; margin-top: var(--s3); padding-top: 1.6rem; height: 5.6rem; }
        .lt-titolo { position: absolute; top: 0; left: 0; color: var(--notte-testo); }
        .lt-asse { position: absolute; left: 0; right: 0; top: 3.1rem; height: 1px; background: var(--notte-linea); }
        .lt-mese { position: absolute; top: 3.5rem; transform: translateX(-50%); font-size: 0.72rem; color: var(--notte-testo); white-space: nowrap; }
        .lt-mese::before { content: ''; position: absolute; left: 50%; top: -0.55rem; width: 1px; height: 0.45rem; background: var(--notte-linea); }
        .lt-oggi { position: absolute; top: 2.1rem; transform: translateX(-50%); font-size: 0.62rem; color: var(--segnale); white-space: nowrap; }
        .lt-oggi::after { content: ''; position: absolute; left: 50%; top: 1.05rem; width: 1px; height: 0.85rem; background: var(--segnale); }
        .lt-evento { position: absolute; top: 3.1rem; width: 11px; height: 11px; transform: translate(-50%, -50%);
            background: var(--notte); border: 1.5px solid var(--segnale); cursor: pointer; transition: background-color var(--t-micro) linear; }
        .lt-evento:hover, .lt-evento.acceso { background: var(--segnale); }
        .lt-evento:first-of-type { background: var(--segnale); }
        .lt-evento .lt-tip { position: absolute; bottom: 1.3rem; left: 50%; transform: translateX(-50%); white-space: nowrap; font-family: var(--testo); font-size: 0.78rem;
            color: var(--fondo); background: var(--inchiostro); border: 1px solid var(--notte-linea); padding: 0.4rem 0.6rem;
            opacity: 0; pointer-events: none; transition: opacity var(--t-micro) linear; }
        .lt-evento:hover .lt-tip, .lt-evento.acceso .lt-tip { opacity: 1; }
        .lt-evento.lt-sinistra .lt-tip { left: 0; transform: none; }
        .lt-evento.lt-destra .lt-tip { left: auto; right: 0; transform: none; }
        @media (max-width: 900px) { .lt { height: 5.8rem; } }
"""

JS = r"""
    // Prossimo appuntamento e linea del tempo, letti dall'elenco accanto.
    (function () {
        var box = document.getElementById('prossimoBox');
        var lt = document.getElementById('lineaTempo');
        if (!box || !lt) return;
        var T = {
            mesi: (box.getAttribute('data-mesi') || '').split(','),
            tra: box.getAttribute('data-tra') || 'tra %d giorni', domani: box.getAttribute('data-domani') || 'domani',
            oggi: box.getAttribute('data-oggi') || 'oggi', incorso: box.getAttribute('data-incorso') || 'in corso'
        };
        var items = [].slice.call(document.querySelectorAll('#news-prossimi .news-item[data-fine]'));
        var oggi = new Date(); oggi.setHours(12, 0, 0, 0);
        function data(iso) { var d = new Date(iso + 'T12:00:00'); return isNaN(d) ? null : d; }
        function giorni(a, b) { return Math.round((a - b) / 86400000); }
        var eventi = items.map(function (el) {
            var fine = data(el.getAttribute('data-fine')); if (!fine) return null;
            var testo = (el.querySelector('.news-item-date') || {}).textContent || '';
            var m = testo.match(/(\d{1,2})\s*[–-]\s*(\d{1,2})/);
            var inizio = new Date(fine);
            if (m) inizio.setDate(fine.getDate() - (parseInt(m[2], 10) - parseInt(m[1], 10)));
            return { el: el, inizio: inizio, fine: fine, testo: testo.trim(),
                     titolo: ((el.querySelector('.news-item-title') || {}).textContent || '').trim(),
                     tag: ((el.querySelector('.news-item-tag') || {}).textContent || '').trim(),
                     href: el.getAttribute('href') };
        }).filter(Boolean).sort(function (p, q) { return p.inizio - q.inizio; });
        if (!eventi.length) { box.style.display = 'none'; lt.style.display = 'none'; return; }

        // il prossimo
        var p = eventi[0], d0 = giorni(p.inizio, oggi), dF = giorni(p.fine, oggi);
        var quando = d0 > 1 ? T.tra.replace('%d', d0) : d0 === 1 ? T.domani : (dF >= 0 && d0 <= 0 ? (dF > 0 ? T.incorso : T.oggi) : T.oggi);
        box.querySelector('.prossimo-giorno').textContent = p.inizio.getDate();
        box.querySelector('.prossimo-mese').innerHTML = T.mesi[p.inizio.getMonth()] + '<br>' + p.inizio.getFullYear();
        var tit = box.querySelector('.prossimo-titolo');
        tit.innerHTML = p.href ? '<a href="' + p.href.replace(/"/g, '&quot;') + '"' + (/^https?:/.test(p.href) ? ' target="_blank" rel="noopener"' : '') + '></a>' : '';
        (tit.firstChild || tit).textContent = p.titolo;
        box.querySelector('.prossimo-quando').textContent = (p.tag ? p.tag + ' · ' : '') + quando + (p.testo && /[–-]/.test(p.testo) ? ' · ' + p.testo : '');

        // linea del tempo: da oggi all'ultimo evento, almeno 90 giorni, al massimo 240
        var ultimo = eventi[eventi.length - 1].fine;
        var span = Math.min(240, Math.max(90, giorni(ultimo, oggi) + 10));
        var fineLt = new Date(oggi); fineLt.setDate(oggi.getDate() + span);
        function pos(d) { return Math.max(0, Math.min(100, giorni(d, oggi) / span * 100)); }
        var html = '<span class="lt-asse"></span><span class="lt-oggi" style="left:0%">' + T.oggi + '</span>';
        var cur = new Date(oggi.getFullYear(), oggi.getMonth() + 1, 1);
        while (cur <= fineLt) {
            html += '<span class="lt-mese" style="left:' + pos(cur).toFixed(2) + '%">' + T.mesi[cur.getMonth()].slice(0, 3) + '</span>';
            cur = new Date(cur.getFullYear(), cur.getMonth() + 1, 1);
        }
        lt.insertAdjacentHTML('beforeend', html);
        eventi.forEach(function (e, i) {
            var x = pos(e.inizio);
            var dot = document.createElement('span');
            dot.className = 'lt-evento' + (x < 12 ? ' lt-sinistra' : x > 88 ? ' lt-destra' : '');
            dot.style.left = x.toFixed(2) + '%';
            dot.setAttribute('role', 'img'); dot.setAttribute('aria-label', e.testo + ' · ' + e.titolo);
            dot.innerHTML = '<span class="lt-tip">' + e.testo + ' · ' + e.titolo.replace(/</g, '&lt;') + '</span>';
            dot.addEventListener('mouseenter', function () { e.el.classList.add('acceso'); });
            dot.addEventListener('mouseleave', function () { e.el.classList.remove('acceso'); });
            dot.addEventListener('click', function () { e.el.scrollIntoView({ behavior: 'smooth', block: 'center' }); });
            e.el.addEventListener('mouseenter', function () { dot.classList.add('acceso'); });
            e.el.addEventListener('mouseleave', function () { dot.classList.remove('acceso'); });
            lt.appendChild(dot);
        });
    })();
"""


def markup(lang, T):
    return ('                        <div class="prossimo" id="prossimoBox" data-mesi="%(mesi)s" data-tra="%(tra)s" data-domani="%(domani)s" data-oggi="%(oggi)s" data-incorso="%(incorso)s">\n'
            '                            <span class="prossimo-label">%(label)s</span>\n'
            '                            <div class="prossimo-data"><span class="prossimo-giorno"></span><span class="prossimo-mese"></span></div>\n'
            '                            <h3 class="prossimo-titolo"></h3>\n'
            '                            <p class="prossimo-meta"><span class="prossimo-punto" aria-hidden="true"></span><span class="prossimo-quando"></span></p>\n'
            '                        </div>\n'
            '                        <div class="lt" id="lineaTempo" aria-label="%(lt)s"><span class="lt-titolo">%(lt)s</span></div>\n') % T
