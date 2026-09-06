# -*- coding: utf-8 -*-
"""Sezione "costellazione": campo orbitale su canvas + nodi che restano link nel DOM.

Il canvas disegna soltanto il campo (orbite, scie, linee di connessione, particelle,
alone del nucleo). I nodi sono ancore HTML vere, posizionate per frame con una
trasformazione: restano quindi navigabili da tastiera, leggibili dagli screen reader
e visibili ai crawler. Con prefers-reduced-motion si compone un solo fotogramma.
"""

CSS = """
        /* ============ COSTELLAZIONE ============ */
        @property --cost-angolo {
            syntax: '<angle>';
            inherits: false;
            initial-value: 0deg;
        }

        .costellazione {
            padding: 6rem 3rem 9rem;
            background: var(--bianco);
            display: flex;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }

        .costellazione::before {
            content: '';
            position: absolute;
            left: 50%;
            top: 50%;
            width: min(92vw, 860px);
            aspect-ratio: 1;
            translate: -50% -50%;
            border-radius: 50%;
            background:
                conic-gradient(from var(--cost-angolo),
                    rgba(42,107,107,0.000) 0deg,
                    rgba(42,107,107,0.030) 100deg,
                    rgba(42,107,107,0.000) 200deg,
                    rgba(42,107,107,0.022) 300deg,
                    rgba(42,107,107,0.000) 360deg),
                radial-gradient(circle at 50% 50%,
                    rgba(42,107,107,0.05) 0%,
                    rgba(42,107,107,0.018) 45%,
                    rgba(42,107,107,0) 72%);
            filter: blur(38px);
            animation: costDeriva 78s linear infinite;
            pointer-events: none;
        }

        @keyframes costDeriva { to { --cost-angolo: 360deg; } }

        .cost-wrap {
            width: 100%;
            max-width: 940px;
            position: relative;
            z-index: 1;
        }

        .cost-scena {
            position: relative;
            width: 100%;
            aspect-ratio: 16 / 10;
            touch-action: pan-y;
        }

        .cost-canvas {
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
            display: block;
        }

        .cost-nodi { list-style: none; margin: 0; padding: 0; }

        .cost-nodo {
            position: absolute;
            left: 0;
            top: 0;
            display: flex;
            align-items: center;
            gap: 0.55rem;
            padding: 0.3rem 0.55rem 0.3rem 0.3rem;
            border-radius: 100px;
            white-space: nowrap;
            transform: translate3d(0, -50%, 0);
            transform-origin: 14px 50%;
            will-change: transform, opacity;
            transition: color 0.35s ease, background-color 0.35s ease;
            color: var(--nero);
            background: color-mix(in srgb, var(--bianco) 78%, transparent);
            backdrop-filter: blur(3px);
            -webkit-backdrop-filter: blur(3px);
        }

        @supports not (background: color-mix(in srgb, white 50%, transparent)) {
            .cost-nodo { background: rgba(255,255,255,0.8); }
        }

        .cost-nodo--sinistra {
            flex-direction: row-reverse;
            padding: 0.3rem 0.3rem 0.3rem 0.55rem;
            transform-origin: calc(100% - 14px) 50%;
        }

        .cost-punto {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            flex: none;
            background: var(--bianco);
            border: 1.5px solid var(--ottanio);
            box-shadow: 0 0 0 0 rgba(42,107,107,0.35);
            transition: box-shadow 0.45s cubic-bezier(0.16,1,0.3,1),
                        background-color 0.35s ease, border-color 0.35s ease;
        }

        .cost-etichetta {
            font-size: 0.72rem;
            font-weight: 500;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        .cost-nodo:hover,
        .cost-nodo:focus-visible {
            color: var(--ottanio);
            background: color-mix(in srgb, var(--bianco) 94%, transparent);
        }

        .cost-nodo:hover .cost-punto,
        .cost-nodo:focus-visible .cost-punto {
            background: var(--ottanio);
            box-shadow: 0 0 0 7px rgba(42,107,107,0.12);
        }

        .cost-nucleo {
            position: absolute;
            left: 50%;
            top: 50%;
            translate: -50% -50%;
            display: grid;
            place-items: center;
            width: clamp(92px, 13vw, 128px);
            aspect-ratio: 1;
            border-radius: 50%;
            background: var(--nero);
            color: var(--bianco);
            font-family: 'Instrument Serif', serif;
            font-size: clamp(1rem, 1.7vw, 1.3rem);
            letter-spacing: 0.22em;
            text-indent: 0.22em;
            box-shadow: 0 18px 60px -18px rgba(42,107,107,0.55);
            transition: transform 0.6s cubic-bezier(0.16,1,0.3,1);
        }

        .cost-nucleo:hover { transform: scale(1.045); }

        .cost-didascalia {
            margin-top: 3rem;
            text-align: center;
            font-size: 0.85rem;
            letter-spacing: 0.05em;
            color: var(--grigio);
        }

        @media (max-width: 900px) {
            .costellazione { padding: 4rem 1.25rem 6rem; }
            .cost-scena { aspect-ratio: 1 / 1; }
            .cost-etichetta { font-size: 0.62rem; letter-spacing: 0.1em; }
            .cost-nodo { gap: 0.4rem; padding: 0.25rem 0.45rem 0.25rem 0.25rem; }
        }

        @media (max-width: 640px) {
            .cost-scena { aspect-ratio: auto; display: grid; }
            .cost-canvas { position: absolute; inset: 0; }
            .cost-nucleo { position: relative; left: auto; top: auto; translate: none;
                margin: 2.5rem auto 2rem; }
            .cost-nodi {
                position: relative;
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 0.35rem 0.5rem;
                padding: 0 0.25rem 2.5rem;
            }
            .cost-nodo {
                position: relative;
                transform: none !important;
                opacity: 1 !important;
                justify-content: flex-start;
            }
            .cost-nodo--sinistra { flex-direction: row; }
        }

        @media (prefers-reduced-motion: reduce) {
            .costellazione::before { animation: none; }
        }
"""

JS = """
    // Costellazione: il canvas disegna il campo, i nodi restano ancore HTML.
    (function () {
        var scena = document.getElementById('costScena');
        if (!scena || !scena.getContext === undefined) { /* no-op */ }
        var canvas = document.getElementById('costCanvas');
        if (!scena || !canvas || !canvas.getContext) return;
        var ctx = canvas.getContext('2d');
        var nodiEl = [].slice.call(scena.querySelectorAll('.cost-nodo'));
        if (!nodiEl.length) return;

        var menoMoto = window.matchMedia('(prefers-reduced-motion: reduce)');
        var compatto = window.matchMedia('(max-width: 640px)');
        var RAGGI = [0.44, 0.71, 0.99];
        var VEL = [0.062, -0.041, 0.027];
        var TILT = 0.60;

        var nodi = nodiEl.map(function (el) {
            var o = Math.max(0, Math.min(2, parseInt(el.dataset.orbita, 10) || 0));
            return {
                el: el, orbita: o,
                raggio: RAGGI[o], vel: VEL[o],
                fase: parseFloat(el.dataset.fase || '0') * Math.PI * 2,
                scia: [], luce: 0, x: 0, y: 0, z: 0
            };
        });

        var particelle = [];
        for (var i = 0; i < 84; i++) {
            particelle.push({
                r: 0.18 + Math.random() * 1.0,
                a: Math.random() * Math.PI * 2,
                v: (0.006 + Math.random() * 0.016) * (Math.random() < 0.5 ? -1 : 1),
                p: Math.random(),
                s: 0.35 + Math.random() * 1.15
            });
        }

        var W = 0, H = 0, cx = 0, cy = 0, U = 0, dpr = 1;
        var pt = { x: 0, y: 0, mx: 0, my: 0 };
        var visibile = true, girando = false, t0 = 0, tempo = 0;

        function dimensiona() {
            var r = scena.getBoundingClientRect();
            if (!r.width) return;
            dpr = Math.min(window.devicePixelRatio || 1, 2);
            W = r.width; H = r.height;
            canvas.width = Math.round(W * dpr);
            canvas.height = Math.round(H * dpr);
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            cx = W / 2; cy = H / 2;
            var margineX = Math.max(52, Math.min(140, W * 0.13));
            U = Math.min((W / 2 - margineX) / (0.99 * 1.06),
                         (H / 2 - 44) / (0.99 * TILT));
        }

        function posizione(n, tempo) {
            var a = n.fase + tempo * n.vel;
            var rx = U * n.raggio * 1.06;
            var ry = U * n.raggio * TILT;
            var sx = Math.cos(a), sy = Math.sin(a);
            n.z = sy;
            n.x = cx + rx * sx + pt.mx * (10 + n.orbita * 9);
            n.y = cy + ry * sy + pt.my * (7 + n.orbita * 6);
            n.scala = 0.82 + 0.22 * (sy + 1) / 2;
            n.alfa = 0.5 + 0.5 * (sy + 1) / 2;
        }

        function ellisse(raggio, alfa, larghezza, tratteggio, rotazione) {
            var rx = U * raggio * 1.06, ry = U * raggio * TILT;
            ctx.save();
            ctx.translate(cx + pt.mx * (10 + raggio * 14), cy + pt.my * (7 + raggio * 10));
            ctx.rotate(rotazione);
            ctx.beginPath();
            ctx.ellipse(0, 0, rx, ry, 0, 0, Math.PI * 2);
            ctx.setLineDash(tratteggio);
            ctx.lineWidth = larghezza;
            ctx.strokeStyle = 'rgba(42,107,107,' + alfa + ')';
            ctx.stroke();
            ctx.restore();
        }

        function disegna(tempo) {
            ctx.clearRect(0, 0, W, H);

            // orbite
            for (var o = 0; o < 3; o++) {
                ellisse(RAGGI[o], 0.16 - o * 0.028, 1, [2, 7], tempo * 0.012 * (o % 2 ? -1 : 1));
            }

            // particelle in deriva, con parallasse
            for (var p = 0; p < particelle.length; p++) {
                var q = particelle[p];
                var ang = q.a + tempo * q.v;
                var rx = U * q.r * 1.06, ry = U * q.r * TILT;
                var px = cx + rx * Math.cos(ang) + pt.mx * (6 + q.r * 16);
                var py = cy + ry * Math.sin(ang) + pt.my * (4 + q.r * 11);
                var prof = (Math.sin(ang) + 1) / 2;
                ctx.beginPath();
                ctx.arc(px, py, q.s * (0.55 + prof * 0.7), 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(42,107,107,' + (0.06 + prof * 0.16) + ')';
                ctx.fill();
            }

            for (var i = 0; i < nodi.length; i++) posizione(nodi[i], tempo);

            var ordinati = nodi.slice().sort(function (a, b) { return a.z - b.z; });

            // linee di connessione e scie
            for (var k = 0; k < ordinati.length; k++) {
                var n = ordinati[k];
                var prof = (n.z + 1) / 2;
                var g = ctx.createLinearGradient(cx, cy, n.x, n.y);
                var forza = 0.05 + prof * 0.10 + n.luce * 0.30;
                g.addColorStop(0, 'rgba(42,107,107,' + forza + ')');
                g.addColorStop(1, 'rgba(42,107,107,0)');
                ctx.beginPath();
                ctx.moveTo(cx, cy);
                ctx.lineTo(n.x, n.y);
                ctx.strokeStyle = g;
                ctx.lineWidth = 1 + n.luce * 0.8;
                ctx.setLineDash([]);
                ctx.stroke();

                n.scia.push([n.x, n.y]);
                if (n.scia.length > 26) n.scia.shift();
                for (var s = 1; s < n.scia.length; s++) {
                    var f = s / n.scia.length;
                    ctx.beginPath();
                    ctx.moveTo(n.scia[s - 1][0], n.scia[s - 1][1]);
                    ctx.lineTo(n.scia[s][0], n.scia[s][1]);
                    ctx.strokeStyle = 'rgba(42,107,107,' + (f * f * (0.10 + prof * 0.14 + n.luce * 0.25)) + ')';
                    ctx.lineWidth = f * 2.1;
                    ctx.stroke();
                }

                if (n.luce > 0.01) {
                    var al = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, 44);
                    al.addColorStop(0, 'rgba(42,107,107,' + (0.20 * n.luce) + ')');
                    al.addColorStop(1, 'rgba(42,107,107,0)');
                    ctx.beginPath();
                    ctx.arc(n.x, n.y, 44, 0, Math.PI * 2);
                    ctx.fillStyle = al;
                    ctx.fill();
                }

                if (compatto.matches) { continue; }
                var sinistra = n.x < cx;
                if (n.sinistra !== sinistra) {
                    n.el.classList.toggle('cost-nodo--sinistra', sinistra);
                    n.sinistra = sinistra;
                }
                n.el.style.transform = 'translate3d(' + n.x + 'px,' + n.y + 'px,0) '
                    + 'translate(' + (sinistra ? '-100%' : '0') + ',-50%) '
                    + 'scale(' + n.scala.toFixed(3) + ')';
                n.el.style.opacity = n.alfa.toFixed(3);
                n.el.style.zIndex = String(10 + Math.round(n.z * 10));
            }

            // alone del nucleo
            var pulsa = 1 + Math.sin(tempo * 0.9) * 0.045;
            var rg = ctx.createRadialGradient(cx, cy, 0, cx, cy, U * 0.52 * pulsa);
            rg.addColorStop(0, 'rgba(42,107,107,0.17)');
            rg.addColorStop(0.45, 'rgba(42,107,107,0.06)');
            rg.addColorStop(1, 'rgba(42,107,107,0)');
            ctx.beginPath();
            ctx.arc(cx, cy, U * 0.52 * pulsa, 0, Math.PI * 2);
            ctx.fillStyle = rg;
            ctx.fill();
        }

        function passo(ts) {
            if (!girando) return;
            if (!t0) t0 = ts;
            tempo = (ts - t0) / 1000;
            pt.mx += (pt.x - pt.mx) * 0.06;
            pt.my += (pt.y - pt.my) * 0.06;
            for (var i = 0; i < nodi.length; i++) {
                var obiettivo = nodi[i].el.matches(':hover, :focus-visible') ? 1 : 0;
                nodi[i].luce += (obiettivo - nodi[i].luce) * 0.12;
            }
            disegna(tempo);
            requestAnimationFrame(passo);
        }

        function avvia() {
            if (girando || menoMoto.matches) return;
            girando = true; t0 = 0;
            requestAnimationFrame(passo);
        }
        function ferma() { girando = false; }

        function statico() {
            pt.mx = pt.my = 0;
            for (var i = 0; i < nodi.length; i++) nodi[i].scia = [];
            disegna(0);
        }

        dimensiona();

        if (window.ResizeObserver) {
            new ResizeObserver(function () {
                dimensiona();
                if (menoMoto.matches) statico();
            }).observe(scena);
        } else {
            window.addEventListener('resize', dimensiona);
        }

        if (window.IntersectionObserver) {
            new IntersectionObserver(function (voci) {
                visibile = voci[0].isIntersecting;
                if (visibile && !menoMoto.matches) avvia(); else ferma();
            }, { threshold: 0.05 }).observe(scena);
        } else { avvia(); }

        scena.addEventListener('pointermove', function (e) {
            var r = scena.getBoundingClientRect();
            pt.x = ((e.clientX - r.left) / r.width - 0.5) * 2;
            pt.y = ((e.clientY - r.top) / r.height - 0.5) * 2;
        });
        scena.addEventListener('pointerleave', function () { pt.x = 0; pt.y = 0; });

        document.addEventListener('visibilitychange', function () {
            if (document.hidden) ferma();
            else if (visibile) avvia();
        });

        function cambioPreferenza() {
            if (menoMoto.matches) { ferma(); statico(); }
            else if (visibile) avvia();
        }
        if (menoMoto.addEventListener) menoMoto.addEventListener('change', cambioPreferenza);
        cambioPreferenza();
    })();
"""
