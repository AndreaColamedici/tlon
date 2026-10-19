# -*- coding: utf-8 -*-
"""«Il cielo degli appuntamenti»: carta celeste su canvas nella sezione News.

Parente del pianeta della costellazione, ma rovesciato: non un mondo visto da
fuori, un cielo visto da dentro. Un campo di stelle a seme fisso ruota piano
intorno al polo; un quadrante fisso segna i dodici mesi; ogni evento in
programma (letto dal DOM, data-fine) è una stella collocata alla sua data, e le
stelle degli eventi sono unite in una costellazione in ordine di tempo; una
linea sottile segna oggi. Con prefers-reduced-motion un solo fotogramma.
"""

CSS = """
        /* ============ CIELO DEGLI APPUNTAMENTI ============ */
        .news-cielo { margin: 0; position: sticky; top: 6rem; }
        .cielo-canvas { display: block; width: 100%; aspect-ratio: 4 / 3; height: auto; }
        .news-cielo figcaption { margin-top: 0.7rem; font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase;
            color: rgba(255,255,255,0.45); }
        @media (max-width: 900px) { .news-cielo { position: static; } }
"""

JS = r"""
    // Cielo degli appuntamenti: le stelle ruotano, gli eventi in programma sono stelle fisse alla loro data.
    (function () {
        var canvas = document.getElementById('cieloCanvas');
        if (!canvas || !canvas.getContext) return;
        var ctx = canvas.getContext('2d');
        var menoMoto = window.matchMedia('(prefers-reduced-motion: reduce)');
        var MESI = (canvas.getAttribute('data-mesi') || 'gen,feb,mar,apr,mag,giu,lug,ago,set,ott,nov,dic').split(',');
        var OGGI = canvas.getAttribute('data-oggi') || 'oggi';
        var evidenza = -1;
        var TEAL = '95,176,176';

        var SEME = 1940;
        function rnd() { SEME = (SEME * 1664525 + 1013904223) % 4294967296; return SEME / 4294967296; }

        // campo di stelle (coordinate polari, ruotano insieme)
        var stelle = [];
        for (var i = 0; i < 230; i++) {
            var r = Math.sqrt(rnd());
            stelle.push({ r: r, a: rnd() * Math.PI * 2, m: 0.25 + rnd() * 0.75, f: 0.4 + rnd() * 1.6, ph: rnd() * Math.PI * 2 });
        }
        // costellazioni di sfondo: gruppi di stelle vicine
        var costellazioni = [];
        for (var c = 0; c < 6; c++) {
            var base = stelle[Math.floor(rnd() * stelle.length)];
            var vicine = stelle.slice().sort(function (p, q) { return dist(p, base) - dist(q, base); }).slice(0, 4 + Math.floor(rnd() * 3));
            costellazioni.push(vicine);
        }
        function dist(p, q) {
            var x1 = p.r * Math.cos(p.a), y1 = p.r * Math.sin(p.a), x2 = q.r * Math.cos(q.a), y2 = q.r * Math.sin(q.a);
            return Math.hypot(x1 - x2, y1 - y2);
        }

        // eventi dal DOM
        function giornoAnno(iso) {
            var d = new Date(iso + 'T12:00:00'); var inizio = new Date(d.getFullYear(), 0, 1);
            return (d - inizio) / 86400000;
        }
        function angolo(iso) { return giornoAnno(iso) / 365.25 * Math.PI * 2 - Math.PI / 2; }
        function leggi() {
            var oggi = new Date().toISOString().slice(0, 10);
            var futuri = [], passati = [];
            [].forEach.call(document.querySelectorAll('#news-prossimi .news-item[data-fine], #news-recenti .news-item[data-fine]'), function (el) {
                var fine = el.getAttribute('data-fine'); if (!fine) return;
                var t = el.querySelector('.news-item-title'); var d = el.querySelector('.news-item-date');
                var voce = { fine: fine, a: angolo(fine), titolo: t ? t.textContent.trim() : '', data: d ? d.textContent.trim() : '', el: el };
                (fine >= oggi ? futuri : passati).push(voce);
            });
            futuri.sort(function (p, q) { return p.fine < q.fine ? -1 : 1; });
            passati.sort(function (p, q) { return p.fine < q.fine ? -1 : 1; });
            return { futuri: futuri.slice(0, 12), passati: passati.slice(-8), oggi: angolo(oggi) };
        }
        var dati = leggi();
        dati.futuri.forEach(function (ev, i) {
            ev.el.addEventListener('mouseenter', function () { evidenza = i; if (!girando) statico(); });
            ev.el.addEventListener('mouseleave', function () { evidenza = -1; if (!girando) statico(); });
        });

        var W = 0, H = 0, cx = 0, cy = 0, R = 0, dpr = 1, pt = { x: 0, y: 0, mx: 0, my: 0 };
        var visibile = true, girando = false, t0 = 0;

        function dimensiona() {
            var r = canvas.getBoundingClientRect(); if (!r.width) return;
            dpr = Math.min(window.devicePixelRatio || 1, 2);
            W = r.width; H = r.width * 0.75;
            canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
            canvas.style.height = H + 'px';
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            cx = W / 2; cy = H / 2; R = Math.min(W, H) * 0.45;
        }

        function polare(r, a, raggio) {
            return [cx + Math.cos(a) * r * raggio + pt.mx * 6, cy + Math.sin(a) * r * raggio + pt.my * 4];
        }

        function disegna(t) {
            ctx.clearRect(0, 0, W, H);
            var rot = t * 0.018;

            // alone del polo
            var g = ctx.createRadialGradient(cx, cy, 0, cx, cy, R * 1.05);
            g.addColorStop(0, 'rgba(' + TEAL + ',0.10)'); g.addColorStop(0.6, 'rgba(' + TEAL + ',0.03)'); g.addColorStop(1, 'rgba(' + TEAL + ',0)');
            ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, R * 1.05, 0, Math.PI * 2); ctx.fill();

            // costellazioni di sfondo
            ctx.lineWidth = 0.7;
            for (var c = 0; c < costellazioni.length; c++) {
                var gr = costellazioni[c];
                ctx.beginPath();
                for (var k = 0; k < gr.length; k++) { var p = polare(gr[k].r, gr[k].a + rot, R * 0.96); if (k) ctx.lineTo(p[0], p[1]); else ctx.moveTo(p[0], p[1]); }
                ctx.strokeStyle = 'rgba(255,255,255,0.09)'; ctx.stroke();
            }
            // stelle
            for (var i = 0; i < stelle.length; i++) {
                var s = stelle[i], q = polare(s.r, s.a + rot, R * 0.96);
                var tw = 0.75 + 0.25 * Math.sin(t * s.f + s.ph);
                ctx.beginPath(); ctx.arc(q[0], q[1], 0.5 + s.m * 1.1, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,' + (0.12 + 0.42 * s.m * tw).toFixed(3) + ')'; ctx.fill();
            }

            // quadrante dei mesi (fisso)
            ctx.beginPath(); ctx.arc(cx + pt.mx * 6, cy + pt.my * 4, R, 0, Math.PI * 2);
            ctx.strokeStyle = 'rgba(255,255,255,0.16)'; ctx.lineWidth = 1; ctx.stroke();
            ctx.beginPath(); ctx.arc(cx + pt.mx * 6, cy + pt.my * 4, R * 0.78, 0, Math.PI * 2);
            ctx.setLineDash([2, 6]); ctx.strokeStyle = 'rgba(' + TEAL + ',0.22)'; ctx.stroke(); ctx.setLineDash([]);
            var piccolo = W < 520;
            ctx.font = '500 ' + Math.max(9, R * 0.05).toFixed(1) + 'px Inter, sans-serif';
            ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
            for (var m = 0; m < 12; m++) {
                var a = m / 12 * Math.PI * 2 - Math.PI / 2;
                var p1 = polare(1, a, R), p2 = polare(1, a, R * 0.955), pl = polare(1, a + Math.PI / 12, R * 1.085);
                ctx.beginPath(); ctx.moveTo(p1[0], p1[1]); ctx.lineTo(p2[0], p2[1]); ctx.strokeStyle = 'rgba(255,255,255,0.35)'; ctx.stroke();
                ctx.fillStyle = 'rgba(255,255,255,0.45)'; ctx.fillText(piccolo ? MESI[m].slice(0, 1).toUpperCase() : MESI[m], pl[0], pl[1]);
            }

            // oggi
            var o1 = polare(1, dati.oggi, R * 0.08), o2 = polare(1, dati.oggi, R);
            var lg = ctx.createLinearGradient(o1[0], o1[1], o2[0], o2[1]);
            lg.addColorStop(0, 'rgba(' + TEAL + ',0)'); lg.addColorStop(1, 'rgba(' + TEAL + ',0.7)');
            ctx.beginPath(); ctx.moveTo(o1[0], o1[1]); ctx.lineTo(o2[0], o2[1]); ctx.strokeStyle = lg; ctx.lineWidth = 1; ctx.stroke();
            ctx.beginPath(); ctx.arc(o2[0], o2[1], 2.5, 0, Math.PI * 2); ctx.fillStyle = 'rgba(' + TEAL + ',0.9)'; ctx.fill();
            var om = polare(1, dati.oggi, R * 0.5);
            ctx.save(); ctx.translate(om[0], om[1]); var ang = dati.oggi; if (Math.cos(ang) < 0) ang += Math.PI; ctx.rotate(ang);
            ctx.font = '600 ' + Math.max(8.5, R * 0.042).toFixed(1) + 'px Inter, sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
            ctx.fillStyle = 'rgba(' + TEAL + ',0.95)'; ctx.fillText(OGGI.toUpperCase(), 0, -5); ctx.restore();

            // eventi passati: stelle spente
            for (var j = 0; j < dati.passati.length; j++) {
                var e = dati.passati[j], raggioE = R * (0.50 + (j % 3) * 0.06), pe = polare(1, e.a, raggioE);
                ctx.beginPath(); ctx.arc(pe[0], pe[1], 1.6, 0, Math.PI * 2); ctx.fillStyle = 'rgba(255,255,255,0.16)'; ctx.fill();
            }
            // eventi in programma: costellazione in ordine di tempo
            var punti = [];
            for (var n = 0; n < dati.futuri.length; n++) {
                var ev = dati.futuri[n], rr = R * (0.60 + (n % 4) * 0.055);
                punti.push(polare(1, ev.a, rr));
            }
            if (punti.length > 1) {
                ctx.beginPath(); ctx.moveTo(punti[0][0], punti[0][1]);
                for (var u = 1; u < punti.length; u++) ctx.lineTo(punti[u][0], punti[u][1]);
                ctx.strokeStyle = 'rgba(' + TEAL + ',0.45)'; ctx.lineWidth = 0.9; ctx.stroke();
            }
            var etichette = [];
            var fs = Math.max(9, R * 0.046), fs2 = Math.max(8.5, R * 0.04), maxEt = piccolo ? 4 : 12, maxCar = piccolo ? 16 : 26;
            for (var v = 0; v < punti.length; v++) {
                var pp = punti[v], vicinanza = 1 - v / Math.max(1, punti.length), pulsa = 1 + 0.25 * Math.sin(t * 1.4 + v);
                var acceso = evidenza === v, forzaAl = acceso ? 1 : (0.30 + 0.30 * vicinanza), ragAl = (acceso ? 16 : 6 + 6 * vicinanza);
                var al = ctx.createRadialGradient(pp[0], pp[1], 0, pp[0], pp[1], ragAl);
                al.addColorStop(0, 'rgba(' + TEAL + ',' + forzaAl + ')'); al.addColorStop(1, 'rgba(' + TEAL + ',0)');
                ctx.beginPath(); ctx.arc(pp[0], pp[1], ragAl * pulsa, 0, Math.PI * 2); ctx.fillStyle = al; ctx.fill();
                ctx.beginPath(); ctx.arc(pp[0], pp[1], (acceso ? 3.4 : 1.6 + 1.8 * vicinanza), 0, Math.PI * 2); ctx.fillStyle = 'rgba(255,255,255,0.95)'; ctx.fill();
                if (v < maxEt) {
                    var ev2 = dati.futuri[v], destra = pp[0] >= cx, tit = ev2.titolo.length > maxCar ? ev2.titolo.slice(0, maxCar - 1).replace(/\s+\S*$/, '') + '…' : ev2.titolo;
                    etichette.push({ x: pp[0] + (destra ? 16 : -16), y: pp[1], sx: pp[0], sy: pp[1], destra: destra, data: ev2.data, titolo: tit, acceso: acceso, h: fs + fs2 + 4 });
                }
            }
            // le etichette vicine si scostano in verticale
            etichette.sort(function (p, q) { return p.y - q.y; });
            for (var it = 0; it < 3; it++) for (var e1 = 0; e1 < etichette.length; e1++) for (var e2 = e1 + 1; e2 < etichette.length; e2++) {
                var A = etichette[e1], B = etichette[e2];
                if (A.destra !== B.destra || Math.abs(A.x - B.x) > 150) continue;
                var dy = B.y - A.y, min = A.h + 6;
                if (Math.abs(dy) < min) { var sp = (min - Math.abs(dy)) / 2; A.y -= sp; B.y += sp; }
            }
            ctx.textBaseline = 'middle';
            ctx.save(); ctx.shadowColor = 'rgba(8,10,10,0.95)'; ctx.shadowBlur = 6;
            for (var e3 = 0; e3 < etichette.length; e3++) {
                var L = etichette[e3];
                if (Math.abs(L.y - L.sy) > 6) {
                    ctx.beginPath(); ctx.moveTo(L.sx, L.sy); ctx.lineTo(L.x - (L.destra ? 4 : -4), L.y);
                    ctx.strokeStyle = 'rgba(255,255,255,0.22)'; ctx.lineWidth = 0.7; ctx.stroke();
                }
                ctx.textAlign = L.destra ? 'left' : 'right';
                ctx.font = '600 ' + fs2.toFixed(1) + 'px Inter, sans-serif';
                ctx.fillStyle = L.acceso ? 'rgba(' + TEAL + ',1)' : 'rgba(' + TEAL + ',0.9)';
                ctx.fillText(L.data.toUpperCase(), L.x, L.y - fs * 0.55);
                ctx.font = '400 ' + fs.toFixed(1) + 'px Inter, sans-serif';
                ctx.fillStyle = L.acceso ? 'rgba(255,255,255,1)' : 'rgba(255,255,255,0.78)';
                ctx.fillText(L.titolo, L.x, L.y + fs * 0.55);
            }
            ctx.restore();
        }

        function passo(ts) {
            if (!girando) return;
            if (!t0) t0 = ts;
            pt.mx += (pt.x - pt.mx) * 0.06; pt.my += (pt.y - pt.my) * 0.06;
            disegna((ts - t0) / 1000);
            requestAnimationFrame(passo);
        }
        function avvia() { if (girando || menoMoto.matches) return; girando = true; t0 = 0; requestAnimationFrame(passo); }
        function ferma() { girando = false; }
        function statico() { pt.mx = pt.my = 0; disegna(0); }

        dimensiona(); statico();
        if (window.ResizeObserver) new ResizeObserver(function () { dimensiona(); if (!girando) statico(); }).observe(canvas);
        else window.addEventListener('resize', function () { dimensiona(); statico(); });
        if (window.IntersectionObserver) {
            new IntersectionObserver(function (voci) { visibile = voci[0].isIntersecting; if (visibile && !menoMoto.matches) avvia(); else ferma(); }, { threshold: 0.05 }).observe(canvas);
        } else { avvia(); }
        canvas.addEventListener('pointermove', function (e) {
            var r = canvas.getBoundingClientRect();
            pt.x = ((e.clientX - r.left) / r.width - 0.5) * 2; pt.y = ((e.clientY - r.top) / r.height - 0.5) * 2;
        });
        canvas.addEventListener('pointerleave', function () { pt.x = 0; pt.y = 0; });
        document.addEventListener('visibilitychange', function () { if (document.hidden) ferma(); else if (visibile) avvia(); });
        if (menoMoto.addEventListener) menoMoto.addEventListener('change', function () { if (menoMoto.matches) { ferma(); statico(); } else if (visibile) avvia(); });
    })();
"""
