# -*- coding: utf-8 -*-
"""La mappa di Tlon: la tavola d'atlante disegnata dal browser nella sezione statement.

Stessa geografia del pianeta (tools/costellazione.py): rumore a seme 1940, scala 1.55,
soglia 0.49 fra terra e mare. Proiezione equirettangolare, incisa a tratteggio su canvas;
le dieci terre più estese prendono i nomi delle dimensioni di Tlon e sono ancore HTML.
Entrando nello schermo la tavola si disegna riga per riga, come sotto un pennino;
con prefers-reduced-motion compare già finita.
"""

CSS = """
        /* ============ MAPPA DI TLON ============ */
        .mappa { position: relative; width: 100%; aspect-ratio: 2 / 1; border: 1px solid var(--inchiostro); background: var(--foglio); overflow: hidden; cursor: crosshair; }
        .mappa-canvas { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
        .mappa-nomi { list-style: none; margin: 0; padding: 0; }
        .mappa-nome {
            position: absolute; transform: translate(-50%, -50%);
            padding: 3px 6px; background: var(--foglio); border: 1px solid var(--linea);
            font-size: 0.6rem; letter-spacing: 0.12em; white-space: nowrap;
            color: var(--inchiostro); opacity: 0;
            transition: opacity var(--t-ui) var(--ease-out), color var(--t-micro) linear, border-color var(--t-micro) linear;
        }
        .mappa-nome.visibile { opacity: 1; }
        .mappa-nome:hover, .mappa-nome.acceso { color: var(--segnale); border-color: var(--segnale); }
        .mappa-titolo { position: absolute; left: 10px; top: 10px; display: flex; flex-direction: column; gap: 2px; padding: 6px 8px; background: var(--foglio); border: 1px solid var(--inchiostro); pointer-events: none; }
        .mappa-titolo strong { font-family: var(--display); font-weight: 500; font-size: 1rem; letter-spacing: -0.01em; line-height: 1; }
        .mappa-titolo span { font-size: 0.62rem; color: var(--nebbia); }
        .mappa-coord { position: absolute; left: 10px; bottom: 8px; min-width: 14ch; font-size: 0.7rem; color: var(--segnale); pointer-events: none; opacity: 0; transition: opacity var(--t-micro) linear; }
        .mappa-coord.visibile { opacity: 1; }
        .mappa-colonna { display: flex; flex-direction: column; gap: var(--s2); align-self: center; }
        .mappa-didascalia { font-size: 0.85rem; line-height: 1.5; color: var(--nebbia); max-width: 44ch; margin: 0; }
        .mappa-meridiano { font-family: var(--mono); font-size: 0.7rem; color: var(--segnale); }
        @media (max-width: 640px) { .mappa-nome { font-size: 0.52rem; padding: 2px 4px; } .mappa-titolo strong { font-size: 0.85rem; } }
"""

JS = r"""
    // Mappa di Tlon: la stessa geografia del pianeta, proiettata e incisa riga per riga.
    (function () {
        var box = document.getElementById('mappaTlon');
        var canvas = document.getElementById('mappaCanvas');
        if (!box || !canvas || !canvas.getContext) return;
        var nomi = [].slice.call(box.querySelectorAll('.mappa-nome'));
        var coord = box.querySelector('.mappa-coord');
        var menoMoto = window.matchMedia('(prefers-reduced-motion: reduce)');
        var ctx = canvas.getContext('2d');
        var INK = '14,17,22', MARE = '91,107,122', LINEA = '211,215,213', SEGNALE = '199,43,44';

        // ---- lo stesso rumore del pianeta (seme 1940)
        var SEME = 1940, SOGLIA = 0.49, SCALA = 1.55;
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
        function quota(lon, lat) {   // lon, lat in radianti
            var cl = Math.cos(lat);
            var x = Math.cos(lon) * cl, y = Math.sin(lat), z = Math.sin(lon) * cl;
            return fbm(x * SCALA, y * SCALA, z * SCALA);
        }

        var W = 0, H = 0, dpr = 1, PASSO = 3, cols = 0, rows = 0, campo = null, terra = null, comp = null, aree = [], off = null, offGrat = null, pronto = false;
        var inciso = null, incise = 0, avviato = false, t0 = 0, DURATA = 2400, xMeridiano = -1, rivelato = 0;

        function misura() {
            var r = box.getBoundingClientRect();
            W = Math.max(1, Math.round(r.width)); H = Math.max(1, Math.round(r.height));
            dpr = Math.min(2, window.devicePixelRatio || 1);
            canvas.width = W * dpr; canvas.height = H * dpr;
        }

        function calcola() {
            cols = Math.ceil(W / PASSO) + 1; rows = Math.ceil(H / PASSO) + 1;
            campo = new Float32Array(cols * rows); terra = new Uint8Array(cols * rows);
            for (var j = 0; j < rows; j++) {
                var lat = (0.5 - j / (rows - 1)) * Math.PI;
                for (var i = 0; i < cols; i++) {
                    var lon = (0.5 - i / (cols - 1)) * 2 * Math.PI;   // est a sinistra, come sul globo accanto
                    var n = quota(lon, lat); campo[j * cols + i] = n; terra[j * cols + i] = n > SOGLIA ? 1 : 0;
                }
            }
            // componenti connesse delle terre, con la longitudine che si richiude
            comp = new Int32Array(cols * rows); for (var k = 0; k < comp.length; k++) comp[k] = -1;
            aree = []; var pila = [];
            for (var s = 0; s < cols * rows; s++) {
                if (!terra[s] || comp[s] >= 0) continue;
                var id = aree.length, area = 0, sx = 0, sy = 0, cx = 0, sxs = 0, sxc = 0;
                pila.push(s); comp[s] = id;
                while (pila.length) {
                    var c = pila.pop(); var ci = c % cols, cj = (c - ci) / cols;
                    area++; sy += cj; var ang = (ci / (cols - 1)) * 2 * Math.PI; sxs += Math.sin(ang); sxc += Math.cos(ang);
                    var vic = [[ci - 1, cj], [ci + 1, cj], [ci, cj - 1], [ci, cj + 1]];
                    for (var v = 0; v < 4; v++) {
                        var vi = vic[v][0], vj = vic[v][1];
                        if (vj < 0 || vj >= rows) continue;
                        if (vi < 0) vi = cols - 1; if (vi >= cols) vi = 0;
                        var q = vj * cols + vi;
                        if (terra[q] && comp[q] < 0) { comp[q] = id; pila.push(q); }
                    }
                }
                var lonm = Math.atan2(sxs, sxc); if (lonm < 0) lonm += 2 * Math.PI;
                aree.push({ id: id, area: area, x: (lonm / (2 * Math.PI)) * (cols - 1), y: sy / area });
            }
            aree.sort(function (a, b) { return b.area - a.area; });
        }

        function incidi() {
            off = document.createElement('canvas'); off.width = W * dpr; off.height = H * dpr;
            var c = off.getContext('2d'); c.scale(dpr, dpr);
            c.fillStyle = '#FFFFFF'; c.fillRect(0, 0, W, H);
            // mare: puntinato rado, più fitto verso la costa
            for (var j = 0; j < rows; j++) for (var i = 0; i < cols; i++) {
                var k = j * cols + i; if (terra[k]) continue;
                var n = campo[k]; var vic = (n - 0.36) / (SOGLIA - 0.36); if (vic < 0) vic = 0;
                var passo = vic > 0.6 ? 1 : (vic > 0.3 ? 2 : 3);
                if ((i + (j % 2) * 2) % (passo * 2) !== 0 || j % passo !== 0) continue;
                c.fillStyle = 'rgba(' + MARE + ',' + (0.18 + vic * 0.32).toFixed(2) + ')';
                c.fillRect(i * PASSO, j * PASSO, 1, 1);
            }
            // terra: tratteggio orizzontale, più denso dove la quota sale; sopra, un secondo tratto obliquo
            c.lineWidth = 1;
            for (var j2 = 0; j2 < rows; j2++) {
                var y = j2 * PASSO + 1.5, i0 = -1;
                for (var i2 = 0; i2 <= cols; i2++) {
                    var dentro = i2 < cols && terra[j2 * cols + i2];
                    if (dentro && i0 < 0) i0 = i2;
                    if (!dentro && i0 >= 0) {
                        var somma = 0; for (var m = i0; m < i2; m++) somma += campo[j2 * cols + m];
                        var q = (somma / (i2 - i0) - SOGLIA) / 0.16; if (q > 1) q = 1;
                        c.strokeStyle = 'rgba(' + INK + ',' + (0.32 + q * 0.5).toFixed(2) + ')';
                        c.beginPath(); c.moveTo(i0 * PASSO, y); c.lineTo(i2 * PASSO, y); c.stroke();
                        i0 = -1;
                    }
                }
            }
            c.strokeStyle = 'rgba(' + INK + ',0.55)';
            for (var j3 = 0; j3 < rows; j3++) for (var i3 = 0; i3 < cols; i3++) {
                var k3 = j3 * cols + i3;
                if (!terra[k3] || campo[k3] < SOGLIA + 0.07 || (i3 + j3) % 2) continue;
                c.beginPath(); c.moveTo(i3 * PASSO, j3 * PASSO + PASSO); c.lineTo(i3 * PASSO + PASSO, j3 * PASSO); c.stroke();
            }
            // coste: marching squares con interpolazione
            c.strokeStyle = 'rgba(' + INK + ',0.95)'; c.lineWidth = 1.1; c.beginPath();
            function punto(i, j) { return campo[j * cols + i]; }
            function fra(a, b) { var d = b - a; return Math.abs(d) < 1e-6 ? 0.5 : (SOGLIA - a) / d; }
            for (var j4 = 0; j4 < rows - 1; j4++) for (var i4 = 0; i4 < cols - 1; i4++) {
                var a = punto(i4, j4), b = punto(i4 + 1, j4), d = punto(i4 + 1, j4 + 1), e = punto(i4, j4 + 1);
                var idx = (a > SOGLIA ? 8 : 0) | (b > SOGLIA ? 4 : 0) | (d > SOGLIA ? 2 : 0) | (e > SOGLIA ? 1 : 0);
                if (idx === 0 || idx === 15) continue;
                var x0 = i4 * PASSO, y0 = j4 * PASSO;
                var T = [x0 + fra(a, b) * PASSO, y0], R = [x0 + PASSO, y0 + fra(b, d) * PASSO], B = [x0 + fra(e, d) * PASSO, y0 + PASSO], L = [x0, y0 + fra(a, e) * PASSO];
                var seg;
                switch (idx) {
                    case 1: case 14: seg = [[L, B]]; break;
                    case 2: case 13: seg = [[B, R]]; break;
                    case 3: case 12: seg = [[L, R]]; break;
                    case 4: case 11: seg = [[T, R]]; break;
                    case 5: seg = [[T, L], [B, R]]; break;
                    case 6: case 9: seg = [[T, B]]; break;
                    case 7: case 8: seg = [[T, L]]; break;
                    case 10: seg = [[T, R], [L, B]]; break;
                }
                for (var sg = 0; sg < seg.length; sg++) { c.moveTo(seg[sg][0][0], seg[sg][0][1]); c.lineTo(seg[sg][1][0], seg[sg][1][1]); }
            }
            c.stroke();
            reticolo(c);
            offGrat = document.createElement('canvas'); offGrat.width = W * dpr; offGrat.height = H * dpr;
            var cg = offGrat.getContext('2d'); cg.scale(dpr, dpr);
            cg.fillStyle = '#FFFFFF'; cg.fillRect(0, 0, W, H); reticolo(cg);
            inciso = new Uint8Array(W); incise = 0;
            pronto = true;
        }

        var cime = [];
        function reticolo(c) {
            // meridiani e paralleli ogni 30 gradi; equatore e meridiano zero più scuri
            c.lineWidth = 1;
            for (var g = 0; g <= 12; g++) {
                var x = (g / 12) * W; c.strokeStyle = 'rgba(' + INK + ',' + (g === 6 ? 0.35 : 0.14) + ')';
                c.beginPath(); c.moveTo(x, 0); c.lineTo(x, H); c.stroke();
            }
            for (var p = 0; p <= 6; p++) {
                var yy = (p / 6) * H; c.strokeStyle = 'rgba(' + INK + ',' + (p === 3 ? 0.35 : 0.14) + ')';
                c.beginPath(); c.moveTo(0, yy); c.lineTo(W, yy); c.stroke();
            }
        }

        function battezza() {
            // le dieci dimensioni sono le dieci alture di Tlon: i punti più alti del rilievo, mai due a ridosso
            // zone vietate: i margini della tavola, il cartiglio in alto a sinistra, le coordinate in basso a sinistra
            var rb = box.getBoundingClientRect(), vietate = [];
            [box.querySelector('.mappa-titolo'), coord].forEach(function (el) {
                if (!el) return; var r = el.getBoundingClientRect();
                vietate.push([(r.left - rb.left) / rb.width - 0.03, (r.top - rb.top) / rb.height - 0.06, (r.right - rb.left) / rb.width + 0.08, (r.bottom - rb.top) / rb.height + 0.06]);
            });
            var cand = [];
            for (var j = Math.round(rows * 0.1); j < rows * 0.9; j++) for (var i = Math.round(cols * 0.07); i < cols * 0.93; i++) {
                var k = j * cols + i; if (!terra[k] || campo[k] <= SOGLIA + 0.03) continue;
                var fx = i / (cols - 1), fy = j / (rows - 1), dentro = false;
                for (var z = 0; z < vietate.length; z++) { var v = vietate[z]; if (fx > v[0] && fx < v[2] && fy > v[1] && fy < v[3]) { dentro = true; break; } }
                if (!dentro) cand.push(k);
            }
            cand.sort(function (p, q) { return campo[q] - campo[p]; });
            cime = [];
            for (var c = 0; c < cand.length && cime.length < nomi.length; c++) {
                var k2 = cand[c], ci = k2 % cols, cj = (k2 - ci) / cols, ok = true;
                for (var b = 0; b < cime.length; b++) {
                    var dx = Math.abs(ci - cime[b].x); dx = Math.min(dx, cols - dx) / cols;
                    var dy = Math.abs(cj - cime[b].y) / rows;
                    if ((dx / 0.12) * (dx / 0.12) + (dy / 0.2) * (dy / 0.2) < 1) { ok = false; break; }
                }
                if (ok) cime.push({ x: ci, y: cj });
            }
            for (var n = 0; n < nomi.length; n++) {
                var m = cime[n];
                if (!m) { nomi[n].style.display = 'none'; continue; }
                nomi[n].style.display = '';
                nomi[n].style.left = ((m.x / (cols - 1)) * 100).toFixed(2) + '%';
                nomi[n].style.top = ((m.y / (rows - 1)) * 100).toFixed(2) + '%';
            }
            // il nome resta sulla sua altura ma non esce dalla tavola
            var rb2 = box.getBoundingClientRect();
            for (var q = 0; q < nomi.length; q++) {
                if (nomi[q].style.display === 'none') continue;
                var rr = nomi[q].getBoundingClientRect(), meta = rr.width / 2 + 4, x = parseFloat(nomi[q].style.left) / 100 * rb2.width;
                x = Math.max(meta, Math.min(rb2.width - meta, x));
                nomi[q].style.left = (x / rb2.width * 100).toFixed(2) + '%';
            }
        }

        var lonGlobo = null;   // longitudine che il globo mostra allo spettatore, in radianti
        function colonna(lon) { var fx = ((0.5 - lon / (2 * Math.PI)) % 1 + 1) % 1; return Math.floor(fx * W) % W; }
        function marcaArco(centro, raggio) {
            // incide l'arco di colonne attorno a un meridiano: l'emisfero che il globo mostra è ampio W/2
            for (var i = -raggio; i <= raggio; i++) marca(((centro + i) % W + W) % W);
        }
        function marca(x) { if (!inciso[x]) { inciso[x] = 1; incise++; } }
        function mostra() {
            if (!pronto) return;
            ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(offGrat, 0, 0);
            // le colonne incise, a tratti contigui
            var x = 0;
            while (x < W) {
                if (!inciso[x]) { x++; continue; }
                var x0 = x; while (x < W && inciso[x]) x++;
                ctx.drawImage(off, x0 * dpr, 0, (x - x0) * dpr, H * dpr, x0 * dpr, 0, (x - x0) * dpr, H * dpr);
            }
            if (xMeridiano >= 0 && incise < W) {
                ctx.fillStyle = 'rgba(' + SEGNALE + ',0.9)';
                ctx.fillRect(xMeridiano * dpr - dpr / 2, 0, dpr, H * dpr);
                ctx.beginPath(); ctx.moveTo(xMeridiano * dpr - 4 * dpr, 0); ctx.lineTo(xMeridiano * dpr + 4 * dpr, 0); ctx.lineTo(xMeridiano * dpr, 6 * dpr); ctx.closePath(); ctx.fill();
            } else if (xMeridiano >= 0) {
                ctx.fillStyle = 'rgba(' + SEGNALE + ',0.55)';
                ctx.fillRect(xMeridiano * dpr - dpr / 2, 0, dpr, H * dpr);
            }
            rivelato = incise >= W ? 1 : incise / W;
            for (var n = 0; n < nomi.length; n++) {
                var fx = parseFloat(nomi[n].style.left || '-1') / 100;
                nomi[n].classList.toggle('visibile', fx >= 0 && !!inciso[Math.min(W - 1, Math.max(0, Math.floor(fx * W)))]);
            }
        }
        // prima apertura: in due secondi e mezzo la carta si apre dal meridiano in luce fino ai due lembi del globo
        function passo(ts) {
            if (!t0) t0 = ts;
            var t = Math.min(1, (ts - t0) / DURATA), e = 1 - Math.pow(1 - t, 3);
            var centro = lonGlobo === null ? Math.floor(W / 2) : colonna(lonGlobo);
            marcaArco(centro, Math.floor(e * W / 4)); xMeridiano = centro;
            mostra();
            if (t < 1) requestAnimationFrame(passo);
        }
        function avvia() {
            if (avviato) return; avviato = true;
            if (menoMoto.matches || !pronto) { for (var i = 0; i < W; i++) inciso[i] = 1; incise = W; xMeridiano = lonGlobo === null ? -1 : colonna(lonGlobo); mostra(); return; }
            requestAnimationFrame(passo);
        }
        // poi la carta registra quel che il globo mostra: a ogni fotogramma l'emisfero in vista resta inciso,
        // e girando (o trascinando) il globo i due lembi incidono terre nuove
        window.tlonPianeta = window.tlonPianeta || {};
        window.tlonPianeta.onFrame = function (lon) {
            lonGlobo = lon;
            if (!pronto || !avviato || (t0 && (performance.now() - t0) < DURATA)) return;
            var c = colonna(lon);
            if (incise < W) marcaArco(c, Math.floor(W / 4));
            xMeridiano = c;
            mostra();
        };

        function prepara() { misura(); calcola(); incidi(); battezza(); }
        prepara(); mostra();
        if ('ResizeObserver' in window) {
            var largo = W;
            new ResizeObserver(function () {
                var r = box.getBoundingClientRect(); if (Math.abs(r.width - largo) < 2) return; largo = r.width;
                var tutto = incise >= W, quota = rivelato; prepara();
                if (avviato) { for (var i = 0; i < W; i++) inciso[i] = tutto ? 1 : 0; incise = tutto ? W : 0; if (!tutto && lonGlobo !== null) marcaArco(colonna(lonGlobo), Math.floor(W / 4)); }
                mostra();
            }).observe(box);
        }
        if ('IntersectionObserver' in window) {
            new IntersectionObserver(function (voci) { voci.forEach(function (v) { if (v.isIntersecting) avvia(); }); }, { threshold: 0.35 }).observe(box);
        } else avvia();

        // il puntatore legge coordinate e altura più vicina
        box.addEventListener('pointermove', function (ev) {
            if (!pronto) return;
            var r = box.getBoundingClientRect();
            var fx = (ev.clientX - r.left) / r.width, fy = (ev.clientY - r.top) / r.height;
            if (fx < 0 || fx > 1 || fy < 0 || fy > 1) return;
            var lon = (0.5 - fx) * 360, lat = (0.5 - fy) * 180;
            var i = Math.min(cols - 1, Math.max(0, Math.round(fx * (cols - 1)))), j = Math.min(rows - 1, Math.max(0, Math.round(fy * (rows - 1))));
            var nome = null, vicino = -1, dmin = 1e9;
            for (var n = 0; n < cime.length; n++) {
                var dx = Math.abs(i - cime[n].x); dx = Math.min(dx, cols - dx) / cols;
                var dy = Math.abs(j - cime[n].y) / rows;
                var d = Math.sqrt(dx * dx * 4 + dy * dy);
                if (d < dmin) { dmin = d; vicino = n; }
            }
            if (dmin > 0.16 || (vicino >= 0 && !nomi[vicino].classList.contains('visibile'))) vicino = -1;
            for (var n2 = 0; n2 < nomi.length; n2++) { var acc = n2 === vicino; nomi[n2].classList.toggle('acceso', acc); if (acc) nome = nomi[n2].textContent; }
            if (coord) {
                coord.textContent = Math.abs(lat).toFixed(1) + '°' + (lat >= 0 ? 'N' : 'S') + ' ' + Math.abs(lon).toFixed(1) + '°' + (lon >= 0 ? 'E' : 'W') + (nome ? ' · ' + nome : '');
                coord.classList.add('visibile');
            }
        });
        box.addEventListener('pointerleave', function () {
            for (var n = 0; n < nomi.length; n++) nomi[n].classList.remove('acceso');
            if (coord) coord.classList.remove('visibile');
        });

        // nodi in orbita e alture sulla carta si accendono a vicenda (stesso ordine delle dimensioni)
        var nodiGlobo = [].slice.call(document.querySelectorAll('.cost-nodo'));
        nodiGlobo.forEach(function (nodo, i) {
            nodo.addEventListener('mouseenter', function () { if (nomi[i]) nomi[i].classList.add('acceso'); });
            nodo.addEventListener('mouseleave', function () { if (nomi[i]) nomi[i].classList.remove('acceso'); });
        });
        nomi.forEach(function (nome, i) {
            nome.addEventListener('mouseenter', function () { if (nodiGlobo[i]) nodiGlobo[i].classList.add('acceso'); });
            nome.addEventListener('mouseleave', function () { if (nodiGlobo[i]) nodiGlobo[i].classList.remove('acceso'); });
        });
    })();
"""

TESTI = {
    'it': dict(titolo='Tlon', sotto='Tavola I · la geografia del pianeta', lista='Le alture di Tlon',
               did='La carta registra quello che il globo ha mostrato: a ogni giro la tavola si completa. Le dieci dimensioni sono le sue alture.'),
    'en': dict(titolo='Tlon', sotto='Plate I · the geography of the planet', lista='The heights of Tlon',
               did='The chart records what the globe has shown: with each turn the plate fills in. The ten dimensions are its heights.'),
    'es': dict(titolo='Tlon', sotto='Lámina I · la geografía del planeta', lista='Las alturas de Tlon',
               did='La carta registra lo que el globo ha mostrado: a cada vuelta la lámina se completa. Las diez dimensiones son sus alturas.'),
}


def markup(lang, nodi):
    """La colonna della carta: tavola, nomi delle alture (stesse dimensioni e stessi link dei nodi), didascalia."""
    import html
    T = TESTI[lang]
    voci = ''.join('<li><a class="mappa-nome" href="%s"%s>%s</a></li>' % (
        html.escape(h[lang], quote=True), ' target="_blank" rel="noopener"' if h[lang].startswith('http') else '', html.escape(e[lang]))
        for _, _, e, h in nodi)
    return ('                <div class="mappa-colonna">\n'
            '                    <div class="mappa" id="mappaTlon">\n'
            '                        <canvas class="mappa-canvas" id="mappaCanvas" aria-hidden="true"></canvas>\n'
            '                        <div class="mappa-titolo" aria-hidden="true"><strong>%s</strong><span>%s</span></div>\n'
            '                        <ul class="mappa-nomi" aria-label="%s">%s</ul>\n'
            '                        <span class="mappa-coord mono" aria-hidden="true"></span>\n'
            '                    </div>\n'
            '                    <p class="mappa-didascalia">%s</p>\n'
            '                </div>\n') % (html.escape(T['titolo']), html.escape(T['sotto']), html.escape(T['lista'], quote=True), voci, html.escape(T['did']))
