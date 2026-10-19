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
        .prossimo { margin: 0.5rem 0 0; }
        .prossimo-label { display: block; font-size: 0.68rem; font-weight: 600; letter-spacing: 0.22em; text-transform: uppercase;
            color: rgba(255,255,255,0.45); margin-bottom: 1.6rem; }
        .prossimo-data { display: flex; align-items: flex-end; gap: 1rem; line-height: 0.85; margin-bottom: 1.4rem; }
        .prossimo-giorno { font-family: 'Instrument Serif', serif; font-size: clamp(5rem, 9vw, 8.5rem); font-weight: 400; color: var(--bianco); letter-spacing: -0.03em; }
        .prossimo-mese { font-family: 'Instrument Serif', serif; font-style: italic; font-size: clamp(1.3rem, 1.9vw, 1.7rem); color: rgba(255,255,255,0.8); line-height: 1.15; padding-bottom: 0.6rem; }
        .prossimo-titolo { font-family: 'Instrument Serif', serif; font-weight: 400; font-size: clamp(1.5rem, 2.4vw, 2.1rem); line-height: 1.2; color: var(--bianco); margin: 0 0 0.8rem; }
        .prossimo-titolo a { color: inherit; text-decoration: none; border-bottom: 1px solid rgba(255,255,255,0.25); transition: border-color 0.3s ease; }
        .prossimo-titolo a:hover { border-bottom-color: var(--ottanio, #2a6b6b); }
        .prossimo-meta { font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(95,176,176,0.95); margin: 0; }
        .prossimo-meta .prossimo-punto { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #5fb0b0; margin-right: 0.6rem; vertical-align: middle;
            box-shadow: 0 0 0 0 rgba(95,176,176,0.5); animation: prossimoRespiro 2.8s ease-out infinite; }
        @keyframes prossimoRespiro { 0% { box-shadow: 0 0 0 0 rgba(95,176,176,0.55); } 70% { box-shadow: 0 0 0 10px rgba(95,176,176,0); } 100% { box-shadow: 0 0 0 0 rgba(95,176,176,0); } }
        .prossimo-nota { font-size: 0.9rem; line-height: 1.6; color: rgba(255,255,255,0.6); margin: 1rem 0 0; max-width: 34ch; }

        .lt { position: relative; margin-top: 3.2rem; padding-top: 1.6rem; height: 5.4rem; }
        .lt-titolo { position: absolute; top: 0; left: 0; font-size: 0.68rem; font-weight: 600; letter-spacing: 0.22em; text-transform: uppercase; color: rgba(255,255,255,0.45); }
        .lt-asse { position: absolute; left: 0; right: 0; top: 3.1rem; height: 1px; background: rgba(255,255,255,0.18); }
        .lt-mese { position: absolute; top: 3.5rem; transform: translateX(-50%); font-size: 0.66rem; letter-spacing: 0.12em; text-transform: uppercase; color: rgba(255,255,255,0.45); white-space: nowrap; }
        .lt-mese::before { content: ''; position: absolute; left: 50%; top: -0.55rem; width: 1px; height: 0.45rem; background: rgba(255,255,255,0.3); }
        .lt-oggi { position: absolute; top: 2.2rem; transform: translateX(-50%); font-size: 0.62rem; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: #5fb0b0; }
        .lt-oggi::after { content: ''; position: absolute; left: 50%; top: 1.05rem; width: 1px; height: 0.85rem; background: #5fb0b0; }
        .lt-evento { position: absolute; top: 3.1rem; width: 11px; height: 11px; transform: translate(-50%, -50%); border-radius: 50%;
            background: var(--nero, #0a0a0a); border: 1.5px solid #5fb0b0; cursor: pointer; transition: transform 0.25s ease, background-color 0.25s ease; }
        .lt-evento:hover, .lt-evento.acceso { background: #5fb0b0; transform: translate(-50%, -50%) scale(1.35); }
        .lt-evento:first-of-type { background: #5fb0b0; }
        .lt-evento .lt-tip { position: absolute; bottom: 1.3rem; left: 50%; transform: translateX(-50%); white-space: nowrap; font-size: 0.72rem; letter-spacing: 0.02em; text-transform: none;
            color: var(--bianco); background: rgba(10,10,10,0.92); border: 1px solid rgba(255,255,255,0.12); padding: 0.35rem 0.6rem; border-radius: 3px;
            opacity: 0; pointer-events: none; transition: opacity 0.2s ease; }
        .lt-evento:hover .lt-tip, .lt-evento.acceso .lt-tip { opacity: 1; }
        .lt-evento.lt-sinistra .lt-tip { left: 0; transform: none; }
        .lt-evento.lt-destra .lt-tip { left: auto; right: 0; transform: none; }
        .news-item.acceso { background: rgba(95,176,176,0.08); }
        @media (max-width: 900px) { .prossimo { margin-top: 0; } .lt { height: 5.8rem; } }
        @media (prefers-reduced-motion: reduce) { .prossimo-meta .prossimo-punto { animation: none; } }
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
