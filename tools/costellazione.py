# -*- coding: utf-8 -*-
"""Sezione "costellazione": il pianeta Tlon su canvas, con le dieci dimensioni in orbita.

Il canvas disegna il pianeta (una sfera di punti con continenti generati da rumore
a seme fisso: la geografia di Tlon non cambia mai), il reticolo di meridiani e
paralleli, l'atmosfera, tre orbite inclinate nello spazio e i fili che legano ogni
dimensione al pianeta. I nodi restano ancore HTML vere, posizionate per frame:
navigabili da tastiera, leggibili dagli screen reader, visibili ai crawler.
Si trascina per far girare il pianeta; con prefers-reduced-motion si compone un
solo fotogramma. Sotto i 640px i nodi tornano in griglia e il canvas mostra solo
i punti in orbita.
"""

CSS = """
        /* ============ COSTELLAZIONE ============ */
        .costellazione {
            padding: 7rem 3rem 8rem;
            background: var(--bianco);
            display: flex;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }

        .cost-wrap {
            width: 100%;
            max-width: 980px;
            position: relative;
            z-index: 1;
        }

        .cost-intro {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 2rem;
            margin-bottom: 1.5rem;
        }

        .cost-eyebrow {
            font-size: 0.68rem;
            font-weight: 500;
            letter-spacing: 0.22em;
            text-transform: uppercase;
            color: var(--ottanio);
        }

        .cost-hint {
            font-size: 0.72rem;
            letter-spacing: 0.06em;
            color: var(--grigio);
            white-space: nowrap;
        }

        .cost-scena {
            position: relative;
            width: 100%;
            aspect-ratio: 16 / 10.5;
            touch-action: pan-y;
            cursor: grab;
            user-select: none;
            -webkit-user-select: none;
        }
        .cost-scena.cost-presa { cursor: grabbing; }

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
            gap: 0.6rem;
            padding: 0.32rem 0.62rem 0.32rem 0.32rem;
            border-radius: 100px;
            white-space: nowrap;
            transform: translate3d(0, -50%, 0);
            transform-origin: 14px 50%;
            will-change: transform, opacity;
            transition: color 0.35s ease, background-color 0.35s ease, box-shadow 0.35s ease;
            color: var(--nero);
            background: color-mix(in srgb, var(--bianco) 82%, transparent);
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
            text-decoration: none;
        }

        @supports not (background: color-mix(in srgb, white 50%, transparent)) {
            .cost-nodo { background: rgba(255,255,255,0.84); }
        }

        .cost-nodo--sinistra {
            flex-direction: row-reverse;
            padding: 0.32rem 0.32rem 0.32rem 0.62rem;
            transform-origin: calc(100% - 14px) 50%;
        }

        .cost-punto {
            width: 10px;
            height: 10px;
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
            background: color-mix(in srgb, var(--bianco) 96%, transparent);
            box-shadow: 0 10px 30px -14px rgba(42,107,107,0.45);
        }

        .cost-nodo:hover .cost-punto,
        .cost-nodo:focus-visible .cost-punto {
            background: var(--ottanio);
            box-shadow: 0 0 0 7px rgba(42,107,107,0.12);
        }

        .cost-nome {
            position: absolute;
            left: 0;
            top: 0;
            transform: translate3d(0, -50%, 0);
            pointer-events: none;
            white-space: nowrap;
            display: flex;
            flex-direction: column;
            gap: 0.15rem;
            padding-left: 0.9rem;
        }
        .cost-nome strong {
            font-family: 'Instrument Serif', serif;
            font-weight: 400;
            font-size: clamp(1.35rem, 2vw, 1.7rem);
            letter-spacing: 0.08em;
            line-height: 1;
            color: var(--nero);
        }
        .cost-nome em {
            font-family: 'Instrument Serif', serif;
            font-style: italic;
            font-size: 0.92rem;
            color: var(--grigio);
        }

        .cost-didascalia {
            margin-top: 2.5rem;
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
            .cost-hint { display: none; }
        }

        @media (max-width: 640px) {
            .cost-scena { aspect-ratio: auto; display: grid; cursor: default; }
            .cost-canvas { position: relative; aspect-ratio: 1 / 1; height: auto; }
            .cost-nome { position: relative; transform: none; padding: 0 0 1rem; text-align: center; align-items: center; order: -1; }
            .cost-nodi {
                position: relative;
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 0.35rem 0.5rem;
                padding: 1.5rem 0.25rem 1.5rem;
            }
            .cost-nodo {
                position: relative;
                transform: none !important;
                opacity: 1 !important;
                justify-content: flex-start;
            }
            .cost-nodo--sinistra { flex-direction: row; }
        }
"""

JS = r"""
    // Costellazione: il pianeta Tlon su canvas, le dimensioni in orbita come ancore HTML.
    (function () {
        var scena = document.getElementById('costScena');
        var canvas = document.getElementById('costCanvas');
        var nome = document.getElementById('costNome');
        if (!scena || !canvas || !canvas.getContext) return;
        var ctx = canvas.getContext('2d');
        var nodiEl = [].slice.call(scena.querySelectorAll('.cost-nodo'));
        if (!nodiEl.length) return;

        var menoMoto = window.matchMedia('(prefers-reduced-motion: reduce)');
        var compatto = window.matchMedia('(max-width: 640px)');
        var TEAL = '42,107,107', NERO = '10,10,10';

        // ---- rumore 3D a seme fisso: la geografia di Tlon è sempre la stessa
        var SEME = 1940;
        function hash(x, y, z) {
            var h = x * 374761393 + y * 668265263 + z * 2147483647 + SEME * 1274126177;
            h = (h ^ (h >>> 13)) * 1274126177;
            h = (h ^ (h >>> 16)) >>> 0;
            return h / 4294967295;
        }
        function liscia(t) { return t * t * (3 - 2 * t); }
        function valore(x, y, z) {
            var xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
            var xf = liscia(x - xi), yf = liscia(y - yi), zf = liscia(z - zi);
            function l(a, b, t) { return a + (b - a) * t; }
            return l(
                l(l(hash(xi, yi, zi), hash(xi + 1, yi, zi), xf), l(hash(xi, yi + 1, zi), hash(xi + 1, yi + 1, zi), xf), yf),
                l(l(hash(xi, yi, zi + 1), hash(xi + 1, yi, zi + 1), xf), l(hash(xi, yi + 1, zi + 1), hash(xi + 1, yi + 1, zi + 1), xf), yf), zf);
        }
        function fbm(x, y, z) {
            var s = 0, a = 0.5, f = 1.0;
            for (var o = 0; o < 5; o++) { s += a * valore(x * f + 11, y * f + 7, z * f + 3); a *= 0.5; f *= 2.05; }
            return s;
        }

        // ---- punti della sfera (spirale di Fibonacci), con terra o mare
        var N = 6200, punti = [];
        var aureo = Math.PI * (3 - Math.sqrt(5));
        for (var i = 0; i < N; i++) {
            var y = 1 - (i / (N - 1)) * 2;
            var r = Math.sqrt(1 - y * y);
            var th = aureo * i + (hash(i, 1, 1) - 0.5) * 0.09;   // un po' di disordine: niente spirale visibile
            y += (hash(i, 2, 2) - 0.5) * 0.012;
            r = Math.sqrt(Math.max(0, 1 - y * y));
            var x = Math.cos(th) * r, z = Math.sin(th) * r;
            var n = fbm(x * 1.55, y * 1.55, z * 1.55);
            var SOGLIA = 0.49;
            var terra = n > SOGLIA;
            var costa = terra && n < SOGLIA + 0.025;
            if (!terra && hash(i, 3, 9) < 0.55) continue;  // il mare è più rado
            punti.push({ x: x, y: y, z: z, terra: terra, costa: costa,
                         q: terra ? Math.min(1, 0.55 + (n - SOGLIA) * 5) : 0.3 + hash(i, 5, 1) * 0.3 });
        }

        // ---- reticolo
        var reticolo = [];
        for (var m = 0; m < 12; m++) {
            var lon = (m / 12) * Math.PI * 2, linea = [];
            for (var k = 0; k <= 72; k++) { var lat = -Math.PI / 2 + (k / 72) * Math.PI; linea.push([Math.cos(lat) * Math.cos(lon), Math.sin(lat), Math.cos(lat) * Math.sin(lon)]); }
            reticolo.push(linea);
        }
        for (var pl = 1; pl < 6; pl++) {
            var lat2 = -Math.PI / 2 + (pl / 6) * Math.PI, linea2 = [];
            for (var k2 = 0; k2 <= 96; k2++) { var lon2 = (k2 / 96) * Math.PI * 2; linea2.push([Math.cos(lat2) * Math.cos(lon2), Math.sin(lat2), Math.cos(lat2) * Math.sin(lon2)]); }
            reticolo.push(linea2);
        }

        // ---- orbite inclinate nello spazio
        var ORBITE = [
            { r: 1.55, inc: 1.28, rot: -0.30, vel: 0.060 },
            { r: 1.98, inc: 1.05, rot: 0.28, vel: -0.040 },
            { r: 2.40, inc: 0.84, rot: 0.04, vel: 0.027 }
        ];
        var nodi = nodiEl.map(function (el) {
            var o = Math.max(0, Math.min(2, parseInt(el.dataset.orbita, 10) || 0));
            return { el: el, orbita: o, fase: parseFloat(el.dataset.fase || '0') * Math.PI * 2, luce: 0, x: 0, y: 0, z: 0, sinistra: null };
        });

        var W = 0, H = 0, cx = 0, cy = 0, R = 0, dpr = 1;
        var pt = { x: 0, y: 0, mx: 0, my: 0 };
        var giro = 0, giroVel = 0, presa = null;
        var visibile = true, girando = false, t0 = 0, tempo = 0, ultimo = 0;
        var TILT = 23.4 * Math.PI / 180;
        var LUCE = norm([-0.55, 0.62, 0.62]);

        function norm(v) { var l = Math.hypot(v[0], v[1], v[2]); return [v[0] / l, v[1] / l, v[2] / l]; }

        function dimensiona() {
            var r = canvas.getBoundingClientRect();
            if (!r.width) return;
            dpr = Math.min(window.devicePixelRatio || 1, 2);
            W = r.width; H = r.height;
            canvas.width = Math.round(W * dpr);
            canvas.height = Math.round(H * dpr);
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            cx = W / 2; cy = H / 2;
            var est = ORBITE[ORBITE.length - 1];
            var estV = est.r * Math.sin(est.inc), estH = est.r;
            R = compatto.matches
                ? Math.min((W / 2 - 14) / estH, (H / 2 - 14) / estV)
                : Math.min((H / 2 - 30) / estV, (W / 2 - 150) / estH);
        }

        // rotazione del pianeta: inclinazione dell'asse + rotazione propria + parallasse del puntatore
        function ruota(p, ang) {
            var ca = Math.cos(ang), sa = Math.sin(ang);
            var x = p[0] * ca + p[2] * sa, z = -p[0] * sa + p[2] * ca, y = p[1];
            var ct = Math.cos(TILT), st = Math.sin(TILT);
            var x2 = x * ct - y * st, y2 = x * st + y * ct;
            return parallasse([x2, y2, z]);
        }
        function parallasse(p) {
            var ax = pt.my * 0.18, ay = -pt.mx * 0.22;
            var cy1 = Math.cos(ax), sy1 = Math.sin(ax);
            var y = p[1] * cy1 - p[2] * sy1, z = p[1] * sy1 + p[2] * cy1, x = p[0];
            var cx1 = Math.cos(ay), sx1 = Math.sin(ay);
            return [x * cx1 + z * sx1, y, -x * sx1 + z * cx1];
        }
        function proietta(p, raggio) {
            var k = 1 / (1 - p[2] * raggio / (R * 9));
            return [cx + p[0] * raggio * k, cy - p[1] * raggio * k, p[2]];
        }
        function orbita(o, a) {
            var p = [Math.cos(a) * o.r * R, 0, Math.sin(a) * o.r * R];
            var ci = Math.cos(o.inc), si = Math.sin(o.inc);
            var y = -p[2] * si, z = p[2] * ci;
            var cr = Math.cos(o.rot), sr = Math.sin(o.rot);
            var q = parallasse([p[0] * cr - y * sr, p[0] * sr + y * cr, z]);
            var k = 1 / (1 - q[2] / (R * 9));
            return [cx + q[0] * k, cy - q[1] * k, q[2] / (o.r * R)];
        }

        function disegna(t) {
            ctx.clearRect(0, 0, W, H);
            var ang = t * 0.11 + giro;

            // atmosfera
            var atm = ctx.createRadialGradient(cx, cy, R * 0.96, cx, cy, R * 1.34);
            atm.addColorStop(0, 'rgba(' + TEAL + ',0.20)');
            atm.addColorStop(0.35, 'rgba(' + TEAL + ',0.07)');
            atm.addColorStop(1, 'rgba(' + TEAL + ',0)');
            ctx.fillStyle = atm; ctx.beginPath(); ctx.arc(cx, cy, R * 1.34, 0, Math.PI * 2); ctx.fill();

            // orbite (dietro)
            disegnaOrbite(t, false);

            // ombra del globo (lato in ombra più denso)
            var ombra = ctx.createRadialGradient(cx - R * 0.45, cy - R * 0.45, R * 0.1, cx, cy, R);
            ombra.addColorStop(0, 'rgba(' + TEAL + ',0.02)');
            ombra.addColorStop(0.75, 'rgba(' + TEAL + ',0.07)');
            ombra.addColorStop(1, 'rgba(' + TEAL + ',0.16)');
            ctx.fillStyle = ombra; ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.fill();

            // riflesso
            var luce = ctx.createRadialGradient(cx - R * 0.38, cy - R * 0.40, 0, cx - R * 0.38, cy - R * 0.40, R * 0.95);
            luce.addColorStop(0, 'rgba(255,255,255,0.55)');
            luce.addColorStop(0.5, 'rgba(255,255,255,0.12)');
            luce.addColorStop(1, 'rgba(255,255,255,0)');
            ctx.fillStyle = luce; ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.fill();

            // reticolo
            ctx.lineWidth = 0.8;
            for (var l = 0; l < reticolo.length; l++) {
                var linea = reticolo[l], prev = null;
                for (var s = 0; s < linea.length; s++) {
                    var q = ruota(linea[s], ang), pr = proietta(q, R);
                    if (prev) {
                        var fronte = (pr[2] + prev[2]) * 0.5;
                        ctx.beginPath(); ctx.moveTo(prev[0], prev[1]); ctx.lineTo(pr[0], pr[1]);
                        ctx.strokeStyle = 'rgba(' + TEAL + ',' + (fronte > 0 ? 0.05 + fronte * 0.10 : 0.025) + ')';
                        ctx.stroke();
                    }
                    prev = pr;
                }
            }

            // punti del pianeta: prima il retro, poi il fronte
            for (var passo = 0; passo < 2; passo++) {
                for (var i = 0; i < punti.length; i++) {
                    var p = punti[i], v = ruota([p.x, p.y, p.z], ang);
                    var dietro = v[2] < 0;
                    if ((passo === 0) !== dietro) continue;
                    var pp = proietta(v, R);
                    var lit = Math.max(0, v[0] * LUCE[0] + v[1] * LUCE[1] + v[2] * LUCE[2]);
                    var lembo = Math.sqrt(Math.min(1, Math.abs(v[2]) + 0.12));
                    var a, raggio;
                    if (dietro) {
                        if (!p.terra) continue;
                        a = 0.045; raggio = 0.75 * lembo;
                    } else if (p.terra) {
                        a = (0.42 + 0.50 * Math.pow(lit, 0.7)) * (0.7 + 0.3 * p.q) + (p.costa ? 0.08 : 0);
                        raggio = ((p.costa ? 1.25 : 1.0) + (0.35 + lit * 0.55) * p.q) * lembo;
                    } else {
                        a = 0.05 + 0.22 * lit * p.q; raggio = (0.6 + lit * 0.5) * lembo;
                    }
                    ctx.beginPath(); ctx.arc(pp[0], pp[1], raggio, 0, Math.PI * 2);
                    ctx.fillStyle = 'rgba(' + (p.terra ? NERO : TEAL) + ',' + a.toFixed(3) + ')';
                    ctx.fill();
                }
            }

            // lembo
            ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2);
            ctx.strokeStyle = 'rgba(' + TEAL + ',0.28)'; ctx.lineWidth = 1; ctx.stroke();

            // orbite (davanti) e nodi
            disegnaOrbite(t, true);
            disegnaNodi(t);

            // nome del pianeta: filo dal lembo all'etichetta
            if (nome && !compatto.matches) {
                var a0 = -0.62, lx = cx + Math.cos(a0) * R * 1.02, ly = cy + Math.sin(a0) * R * 1.02;
                var ex = cx + R * 1.28, ey = cy - R * 0.98;
                ctx.beginPath(); ctx.moveTo(lx, ly); ctx.lineTo(ex, ey); ctx.lineTo(ex + 26, ey);
                ctx.strokeStyle = 'rgba(' + NERO + ',0.35)'; ctx.lineWidth = 0.8; ctx.stroke();
                ctx.beginPath(); ctx.arc(lx, ly, 2.2, 0, Math.PI * 2); ctx.fillStyle = 'rgba(' + NERO + ',0.7)'; ctx.fill();
                nome.style.transform = 'translate3d(' + (ex + 26) + 'px,' + ey + 'px,0) translateY(-50%)';
            }
        }

        function disegnaOrbite(t, davanti) {
            ctx.setLineDash([]);
            for (var o = 0; o < ORBITE.length; o++) {
                var orb = ORBITE[o], prev = null, SEG = 140;
                for (var s = 0; s <= SEG; s++) {
                    var p = orbita(orb, (s / SEG) * Math.PI * 2);
                    if (prev) {
                        var z = (p[2] + prev[2]) * 0.5;
                        var dentro = Math.hypot(p[0] - cx, p[1] - cy) < R;
                        var fronte = z > 0;
                        if (fronte === davanti) {
                            var a = fronte ? 0.16 + z * 0.18 : (dentro ? 0.03 : 0.08);
                            ctx.beginPath(); ctx.moveTo(prev[0], prev[1]); ctx.lineTo(p[0], p[1]);
                            ctx.strokeStyle = 'rgba(' + TEAL + ',' + a.toFixed(3) + ')';
                            ctx.lineWidth = fronte ? 1 : 0.8; ctx.stroke();
                        }
                    }
                    prev = p;
                }
            }
        }

        function disegnaNodi(t) {
            for (var i = 0; i < nodi.length; i++) {
                var n = nodi[i], orb = ORBITE[n.orbita];
                var p = orbita(orb, n.fase + t * orb.vel);
                n.x = p[0]; n.y = p[1]; n.z = p[2];
            }
            // le etichette vicine si scostano un poco, per non sovrapporsi
            for (var i2 = 0; i2 < nodi.length; i2++) nodi[i2].sy = 0;
            if (!compatto.matches) {
                for (var iter = 0; iter < 2; iter++) {
                    for (var a1 = 0; a1 < nodi.length; a1++) for (var b1 = a1 + 1; b1 < nodi.length; b1++) {
                        var A = nodi[a1], B = nodi[b1];
                        if ((A.x < cx) !== (B.x < cx)) continue;
                        var dy = (B.y + B.sy) - (A.y + A.sy), dx = Math.abs(A.x - B.x);
                        if (dx < 170 && Math.abs(dy) < 24) {
                            var spinta = (24 - Math.abs(dy)) / 2 * (dy >= 0 ? 1 : -1);
                            A.sy -= spinta; B.sy += spinta;
                        }
                    }
                }
            }
            var ordinati = nodi.slice().sort(function (a, b) { return a.z - b.z; });
            for (var k = 0; k < ordinati.length; k++) {
                var n = ordinati[k];
                var prof = (n.z + 1) / 2;
                var dentro = Math.hypot(n.x - cx, n.y - cy) < R * 1.02;
                var coperto = n.z < 0 && dentro;

                // filo verso il pianeta
                var dx = n.x - cx, dy = n.y - cy, d = Math.hypot(dx, dy) || 1;
                var sx = cx + dx / d * R * 1.01, sy = cy + dy / d * R * 1.01;
                if (!coperto && d > R * 1.1) {
                    var g = ctx.createLinearGradient(sx, sy, n.x, n.y);
                    var forza = 0.04 + prof * 0.10 + n.luce * 0.35;
                    g.addColorStop(0, 'rgba(' + TEAL + ',' + forza + ')');
                    g.addColorStop(1, 'rgba(' + TEAL + ',' + (forza * 0.25) + ')');
                    ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(n.x, n.y);
                    ctx.strokeStyle = g; ctx.lineWidth = 0.8 + n.luce; ctx.setLineDash([]); ctx.stroke();
                }
                if (n.luce > 0.01) {
                    var al = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, 46);
                    al.addColorStop(0, 'rgba(' + TEAL + ',' + (0.22 * n.luce) + ')');
                    al.addColorStop(1, 'rgba(' + TEAL + ',0)');
                    ctx.beginPath(); ctx.arc(n.x, n.y, 46, 0, Math.PI * 2); ctx.fillStyle = al; ctx.fill();
                }

                if (compatto.matches) {
                    ctx.beginPath(); ctx.arc(n.x, n.y, coperto ? 2 : 3.2 + prof * 1.4, 0, Math.PI * 2);
                    ctx.fillStyle = 'rgba(255,255,255,1)'; ctx.fill();
                    ctx.strokeStyle = 'rgba(' + TEAL + ',' + (coperto ? 0.25 : 0.55 + prof * 0.45) + ')'; ctx.lineWidth = 1.5; ctx.stroke();
                    continue;
                }
                var sinistra = n.x < cx;
                if (n.sinistra !== sinistra) { n.el.classList.toggle('cost-nodo--sinistra', sinistra); n.sinistra = sinistra; }
                var scala = coperto ? 0.78 : 0.84 + 0.22 * prof;
                var alfa = coperto ? 0.30 : 0.55 + 0.45 * prof;
                n.el.style.transform = 'translate3d(' + n.x + 'px,' + (n.y + n.sy) + 'px,0) translate(' + (sinistra ? '-100%' : '0') + ',-50%) scale(' + scala.toFixed(3) + ')';
                n.el.style.opacity = alfa.toFixed(3);
                n.el.style.zIndex = String(10 + Math.round(n.z * 10));
            }
        }

        function passo(ts) {
            if (!girando) return;
            if (!t0) t0 = ts;
            var dt = ultimo ? Math.min(0.05, (ts - ultimo) / 1000) : 0.016; ultimo = ts;
            tempo = (ts - t0) / 1000;
            pt.mx += (pt.x - pt.mx) * 0.06;
            pt.my += (pt.y - pt.my) * 0.06;
            if (!presa) { giro += giroVel * dt; giroVel *= 0.94; }
            for (var i = 0; i < nodi.length; i++) {
                var obiettivo = nodi[i].el.matches(':hover, :focus-visible') ? 1 : 0;
                nodi[i].luce += (obiettivo - nodi[i].luce) * 0.12;
            }
            disegna(tempo);
            requestAnimationFrame(passo);
        }
        function avvia() { if (girando || menoMoto.matches) return; girando = true; t0 = 0; ultimo = 0; requestAnimationFrame(passo); }
        function ferma() { girando = false; }
        function statico() { pt.mx = pt.my = 0; disegna(0); }

        dimensiona();
        if (window.ResizeObserver) {
            new ResizeObserver(function () { dimensiona(); if (menoMoto.matches || !girando) statico(); }).observe(scena);
        } else { window.addEventListener('resize', function () { dimensiona(); statico(); }); }

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
            if (presa) {
                var dx = e.clientX - presa.x; presa.x = e.clientX;
                giro += dx * 0.006; giroVel = dx * 0.006 * 60 * 0.6;
            }
        });
        scena.addEventListener('pointerleave', function () { pt.x = 0; pt.y = 0; });
        scena.addEventListener('pointerdown', function (e) {
            if (compatto.matches || e.button !== 0 || e.target.closest('a')) return;
            presa = { x: e.clientX }; giroVel = 0; scena.classList.add('cost-presa');
        });
        window.addEventListener('pointerup', function () { presa = null; scena.classList.remove('cost-presa'); });

        document.addEventListener('visibilitychange', function () { if (document.hidden) ferma(); else if (visibile) avvia(); });
        function cambioPreferenza() { if (menoMoto.matches) { ferma(); statico(); } else if (visibile) avvia(); }
        if (menoMoto.addEventListener) menoMoto.addEventListener('change', cambioPreferenza);
        if (compatto.addEventListener) compatto.addEventListener('change', function () { dimensiona(); statico(); });
        cambioPreferenza();
        if (menoMoto.matches) statico();
    })();
"""
