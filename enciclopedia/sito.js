(function () {
  'use strict';
    var V = window.VOCI, $ = function (id) { return document.getElementById(id); };
  var quieto = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* scala del tempo a tratti: l'ultimo decennio occupa un quarto della carta */
  var TRATTI = [[-9000, -1000, 0, 7], [-1000, 1600, 7, 17], [1600, 1900, 17, 40], [1900, 2026, 40, 75], [2026, 2036, 75, 99]];
  function x(a) {
    for (var k = 0; k < TRATTI.length; k++) { var t = TRATTI[k]; if (a <= t[1] || k === TRATTI.length - 1) return t[2] + (Math.max(t[0], Math.min(a, t[1])) - t[0]) / (t[1] - t[0]) * (t[3] - t[2]); }
  }
  function anno(a) { return a < 0 ? (-a) + ' a.C.' : String(a); }
  function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;'); }

  /* la fascia a righe del cartoncino: una riga per voce, larga quanto la sua durata */
  var righe = $('righe');
  V.forEach(function (v, k) {
    var w = Math.max(.5, Math.log(Math.max(2, v.y1 - v.y0)));
    var a = document.createElement('i'); a.style.flex = w + ' 1 0'; if (k % 7 === 3) a.className = 'r';
    var b = document.createElement('i'); b.className = 'v'; b.style.flex = '0.9 1 0';
    righe.appendChild(a); righe.appendChild(b);
  });

  /* la carta delle durate */
  var campo = $('campo'), dito = $('dito');
  V.forEach(function (v, k) {
    var a = document.createElement('a');
    a.className = 'vita'; a.href = 'voce/' + v.s + '/'; a.setAttribute('role', 'listitem'); a.dataset.k = k;
    a.style.top = (k / V.length * 100) + '%'; a.style.height = (100 / V.length) + '%';
    var x0 = x(v.y0), x1 = x(v.y1);
    var b = document.createElement('b'); b.style.left = x0 + '%'; b.style.width = Math.max(.6, x1 - x0) + '%'; b.style.transitionDelay = (k * 18) + 'ms';
    if (v.inc) b.className = 'inc';
    var p = document.createElement('i'); p.style.left = x1 + '%'; p.className = v.doc ? 'doc' : (v.ap ? 'ap' : '');
    var s = document.createElement('span'); s.textContent = v.l;
    if (x0 > 30) { s.style.right = (100 - x0) + '%'; } else { s.style.left = (x1 > 60 ? x0 : x1 + 1) + '%'; if (x1 > 60) { s.style.background = 'var(--bg)'; s.style.marginLeft = '10px'; } }
    a.appendChild(b); a.appendChild(p); a.appendChild(s);
    a.setAttribute('aria-label', v.l + ', ' + v.nq + ', fino a ' + v.fq);
    a.addEventListener('mouseenter', function () { racconta(v); });
    a.addEventListener('focus', function () { racconta(v); });
    a.addEventListener('click', function (e) { e.preventDefault(); apri(k, true); });
    campo.appendChild(a);
  });
  function racconta(v) { dito.innerHTML = '<strong>' + esc(v.l) + '.</strong> ' + esc(v.nq) + ' → <span style="color:var(--accent)">' + esc(v.fq) + '</span>'; }
  var ep = $('epoche');
  [[-3000, '3000 a.C.'], [1600, '1600'], [1750, '1750'], [1900, '1900'], [1960, '1960'], [2026, '2026', 1], [2036, '2036', 1]].forEach(function (e) {
    var s = document.createElement('span'); s.textContent = e[1]; s.style.left = Math.min(96.5, x(e[0])) + '%'; if (e[2]) s.className = 'r'; ep.appendChild(s);
  });
  racconta(V[V.length - 1]);
  setTimeout(function () { $('carta').classList.add('nuova'); }, quieto ? 0 : 700);

  /* lo scaffale */
  var scaffale = $('scaffale');
  V.forEach(function (v, k) {
    var d = document.createElement('button');
    d.type = 'button'; d.className = 'dorso' + (v.ap ? ' rosso' : ''); d.style.setProperty('--i', k);
    d.innerHTML = '<span class="costa">' + esc(v.l) + '</span><span class="piatto"><strong>' + esc(v.l) + '</strong><em>' + esc(v.nq) + '</em><p>' + esc(v.n.split('. ')[0]) + '.</p>' +
      (v.b[0].c ? '<img src="' + v.b[0].c + '" alt="" loading="lazy" width="74" height="74">' : '') + '<u>Leggi</u></span>';
    d.setAttribute('aria-label', 'Apri la voce ' + v.l);
    d.addEventListener('click', function () {
      if (window.matchMedia('(hover: none)').matches && window.innerWidth > 900 && !d.classList.contains('aperto')) {
        [].forEach.call(scaffale.children, function (c) { c.classList.remove('aperto'); }); d.classList.add('aperto'); return;
      }
      apri(k, true);
    });
    scaffale.appendChild(d);
  });

  /* la voce */
  var qui = 0, parte = 'n';
  var voce = $('voce'), pann = $('pannello'), cop = $('copertina');
  function corpo(v) {
    if (parte === 'n') return '<p>' + esc(v.n) + '</p>';
    if (parte === 'f') return '<p>' + esc(v.f) + '</p>' + (v.o ? '<p class="ori">' + esc(v.o) + '</p>' : '') + '<p class="res">Residuo. ' + esc(v.r) + '</p>' + (v.doc ? '<p>Per questa sola voce anche la fine è documentata dal libro.</p>' : '');
    return v.p.map(function (p) { var b = v.b[p.b]; return '<blockquote><p>«' + esc(p.x) + '»</p><cite>' + esc(b.a) + ', ' + esc(b.t) + ', p. ' + p.g + ' del file di stampa</cite></blockquote>'; }).join('');
  }
  function dipingi(subito) {
    var v = V[qui];
    var fa = function () {
      $('lemma').textContent = v.l;
      $('date').innerHTML = esc(v.nq) + ' → <b>' + esc(v.fq) + '</b>';
      pann.innerHTML = corpo(v); pann.classList.remove('via');
      var b = v.b[0];
      if (b.c) { cop.hidden = false; $('lastra-vuota').hidden = true; if (cop.getAttribute('src') !== b.c) { cop.src = b.c; } cop.alt = 'Copertina di ' + b.t + ', ' + b.a; cop.classList.remove('via'); }
      else { cop.hidden = true; $('lastra-vuota').hidden = false; $('lastra-vuota').textContent = b.t; }
      var l = $('libro'); l.textContent = b.u ? 'Il libro: ' + b.t.split('.')[0] : b.t.split('.')[0]; if (b.u) { l.href = b.u; l.removeAttribute('aria-disabled'); } else { l.removeAttribute('href'); }
      $('pagina-voce').href = 'voce/' + v.s + '/';
      voce.classList.toggle('fine', parte === 'f' && !v.doc);
      ['n', 'f', 'p'].forEach(function (t) { $('t-' + t).setAttribute('aria-selected', String(t === parte)); });
      var st = stato()[v.s]; $('accetta').setAttribute('aria-pressed', String(!!st)); $('accetta').textContent = st ? (st.fatto ? 'Incarico compiuto' : 'Incarico accettato') : "Accetta l'incarico";
      [].forEach.call(campo.querySelectorAll('.vita'), function (a) { a.classList.toggle('qui', +a.dataset.k === qui); });
    };
    if (subito || quieto) { fa(); return; }
    pann.classList.add('via'); if (V[qui].b[0].c !== cop.getAttribute('src')) cop.classList.add('via');
    setTimeout(fa, 380);
  }
  function apri(k, scorri) {
    qui = (k + V.length) % V.length; parte = 'n'; dipingi();
    history.replaceState(null, '', '#v-' + V[qui].s);
    if (scorri) voce.scrollIntoView({ behavior: quieto ? 'auto' : 'smooth', block: 'start' });
  }
  ['n', 'f', 'p'].forEach(function (t) { $('t-' + t).addEventListener('click', function () { parte = t; dipingi(); }); });
  $('prima').addEventListener('click', function () { apri(qui - 1); });
  $('dopo').addEventListener('click', function () { apri(qui + 1); });
  $('a-caso').addEventListener('click', function () { apri(Math.floor(Math.random() * V.length), true); });
  document.addEventListener('click', function (e) {
    var a = e.target.closest('[data-voce]'); if (!a) return; e.preventDefault();
    var k = V.findIndex(function (v) { return v.s === a.dataset.voce; }); if (k >= 0) apri(k, true);
  });
  voce.addEventListener('keydown', function (e) { if (e.key === 'ArrowRight') apri(qui + 1); if (e.key === 'ArrowLeft') apri(qui - 1); });

  /* gli incarichi: settantadue ore, tenute sul dispositivo */
  var ORE = 72 * 3600 * 1000;
  function stato() { try { return JSON.parse(localStorage.getItem('tlon-incarichi') || '{}'); } catch (e) { return {}; } }
  function salva(s) { try { localStorage.setItem('tlon-incarichi', JSON.stringify(s)); } catch (e) { } }
  function resta(t) {
    var r = t + ORE - Date.now(); if (r <= 0) return 'scaduto';
    var h = Math.floor(r / 3600000), m = Math.floor(r % 3600000 / 60000), s = Math.floor(r % 60000 / 1000);
    return h + ' h ' + (m < 10 ? '0' : '') + m + ' min ' + (s < 10 ? '0' : '') + s + ' s';
  }
  function scontrino() {
    var s = stato(), chiavi = Object.keys(s).sort(function (a, b) { return s[b].t - s[a].t; });
    var corso = chiavi.filter(function (k) { return !s[k].fatto; }), fatti = chiavi.filter(function (k) { return s[k].fatto; });
    var primo = corso[0] && V.find(function (v) { return v.s === corso[0]; });
    $('s-voce').textContent = primo ? primo.l : (fatti.length ? 'Nessun incarico in corso' : 'Nessun incarico accettato');
    $('s-testo').textContent = primo ? primo.i : 'Apri una voce e accetta il suo incarico. Comparirà qui, con il tempo che resta.';
    $('s-esito').hidden = !primo; $('s-esito').dataset.s = primo ? primo.s : '';
    var h = '';
    if (corso.length) { h += '<h4>In corso</h4>'; corso.forEach(function (k) { var v = V.find(function (v) { return v.s === k; }); if (v) h += '<div class="riga"><button type="button" data-voce="' + k + '">' + esc(v.l) + '</button><i></i><span data-t="' + s[k].t + '">' + resta(s[k].t) + '</span></div>'; }); }
    if (fatti.length) { h += '<h4>Compiuti</h4>'; fatti.forEach(function (k) { var v = V.find(function (v) { return v.s === k; }); if (v) h += '<div class="riga"><button type="button" data-voce="' + k + '">' + esc(v.l) + '</button><i></i><span>fatto</span></div>'; }); }
    $('s-righe').innerHTML = h;
  }
  $('accetta').addEventListener('click', function () {
    var s = stato(), v = V[qui];
    if (!s[v.s]) { s[v.s] = { t: Date.now() }; salva(s); }
    dipingi(true); scontrino(); $('incarico').scrollIntoView({ behavior: quieto ? 'auto' : 'smooth', block: 'start' });
  });
  $('s-esito').addEventListener('click', function () { var s = stato(), k = this.dataset.s; if (s[k]) { s[k].fatto = Date.now(); salva(s); } scontrino(); dipingi(true); });
  setInterval(function () { [].forEach.call(document.querySelectorAll('#s-righe [data-t]'), function (e) { e.textContent = resta(+e.dataset.t); }); }, 1000);

  /* il mondo */
  $('mondo').innerHTML = window.MONDO.map(function (m) { return '<dt>' + esc(m[0]) + '</dt><dd>' + esc(m[1]) + '</dd>'; }).join('');

  /* entrate, una volta, in ordine di lettura; un controllo sullo scorrimento recupera ciò che l'osservatore perde */
  var attesa = [].slice.call(document.querySelectorAll('[data-entra]')).concat([scaffale]);
  function entra(el) {
    var k = attesa.indexOf(el); if (k < 0) return; attesa.splice(k, 1);
    var fr = el.parentNode ? [].indexOf.call(el.parentNode.children, el) : 0;
    if (el !== scaffale) el.style.transitionDelay = (Math.min(4, Math.max(0, fr)) * 80) + 'ms';
    el.classList.add('dentro');
    var c = el.querySelector('[data-conta]'); if (c && !quieto) conta(c);
  }
  function guarda() { attesa.slice().forEach(function (el) { if (el.getBoundingClientRect().top < window.innerHeight * .96) entra(el); }); }
  if (quieto) { attesa.slice().forEach(entra); }
  else {
    document.documentElement.classList.add('js');
    if ('IntersectionObserver' in window) { var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) entra(e.target); }); }); attesa.forEach(function (e) { io.observe(e); }); }
    window.addEventListener('scroll', guarda, { passive: true }); window.addEventListener('resize', guarda); guarda();
  }
  function conta(el) { var n = +el.dataset.conta, t0 = performance.now(); (function g(t) { var p = Math.min(1, (t - t0) / 900); el.textContent = Math.round(n * (1 - Math.pow(1 - p, 3))); if (p < 1) requestAnimationFrame(g); })(t0); }

  /* avvio */
  var h = location.hash.replace('#v-', ''), k0 = V.findIndex(function (v) { return v.s === h; });
  qui = k0 >= 0 ? k0 : V.findIndex(function (v) { return v.s === 'istinto-materno'; });
  dipingi(true); scontrino();
  if (k0 >= 0) setTimeout(function () { voce.scrollIntoView(); }, 60);
})();
