/* Da grande · le voci sui muri.
   Ogni età ha le frasi che ci sentiamo dire mentre cresciamo: molte si contraddicono.
   Il soprannome dato all'ingresso resta sul telefono e compare nelle voci rivolte a te. */
import * as THREE from "three";

const CARTA = "#f3ecdc";
const avvolgi = (g, testo, larg) => { const parole = String(testo).split(" "), righe = []; let r = ""; for (const p of parole) { const t = r ? r + " " + p : p; if (g.measureText(t).width > larg && r) { righe.push(r); r = p } else r = t } righe.push(r); return righe };
const sporco = (g, w, h, n = 900, a = .06) => { for (let i = 0; i < n; i++) { g.fillStyle = `rgba(60,40,20,${Math.random() * a})`; g.fillRect(Math.random() * w, Math.random() * h, 2, 2) } };
const nastro = (g, x, y, r) => { g.save(); g.translate(x, y); g.rotate(r); g.fillStyle = "rgba(235,225,190,.75)"; g.fillRect(-22, -8, 44, 16); g.restore() };

/* stili: ognuno disegna su una tela e restituisce le sue proporzioni */
const STILI = {
  // manifesto stampato: fascia di colore, titolo grande, testo
  manifesto: (g, w, h, { testa, corpo, colore = "#E2523F" }) => {
    g.fillStyle = CARTA; g.fillRect(0, 0, w, h); sporco(g, w, h, 1400, .07);
    g.fillStyle = colore; g.fillRect(0, 0, w, h * .34);
    g.fillStyle = "#fff"; g.textAlign = "left"; g.textBaseline = "top"; let s = 46; g.font = `700 ${s}px "Familjen Grotesk", sans-serif`;
    while (g.measureText(testa).width > w - 40 && s > 20) { s -= 2; g.font = `700 ${s}px "Familjen Grotesk", sans-serif` }
    avvolgi(g, testa, w - 40).slice(0, 2).forEach((r, i) => g.fillText(r, 20, 22 + i * s * 1.05));
    g.fillStyle = "#24201c"; g.font = `500 26px "Familjen Grotesk", sans-serif`; avvolgi(g, corpo || "", w - 40).slice(0, 5).forEach((r, i) => g.fillText(r, 20, h * .4 + i * 34));
    nastro(g, 24, 10, -.4); nastro(g, w - 24, 10, .4);
  },
  // post-it scritto a mano
  postit: (g, w, h, { testo, colore = "#f6e27a" }) => {
    g.fillStyle = colore; g.fillRect(6, 6, w - 12, h - 12); g.fillStyle = "rgba(0,0,0,.08)"; g.fillRect(6, h - 30, w - 12, 24);
    g.fillStyle = "#1f2a5a"; g.textAlign = "center"; g.textBaseline = "middle"; let s = 50; g.font = `600 ${s}px Caveat, cursive`;
    let righe = avvolgi(g, testo, w - 40); while (righe.length * s * 1.05 > h - 40 && s > 24) { s -= 2; g.font = `600 ${s}px Caveat, cursive`; righe = avvolgi(g, testo, w - 40) }
    righe.forEach((r, i) => g.fillText(r, w / 2, h / 2 + (i - (righe.length - 1) / 2) * s * 1.05));
  },
  // foglio appeso dagli adulti, a pennarello blu
  foglio: (g, w, h, { testo }) => {
    g.fillStyle = "#fbf8f0"; g.fillRect(0, 0, w, h); g.strokeStyle = "rgba(90,120,200,.35)"; g.lineWidth = 2; for (let y = 60; y < h; y += 38) { g.beginPath(); g.moveTo(10, y); g.lineTo(w - 10, y); g.stroke() }
    g.fillStyle = "#1d3c8f"; g.textAlign = "center"; g.textBaseline = "middle"; let s = 54; g.font = `600 ${s}px Caveat, cursive`;
    let righe = avvolgi(g, testo, w - 50); while (righe.length * s * 1.1 > h - 50 && s > 26) { s -= 2; g.font = `600 ${s}px Caveat, cursive`; righe = avvolgi(g, testo, w - 50) }
    righe.forEach((r, i) => g.fillText(r, w / 2, h / 2 + (i - (righe.length - 1) / 2) * s * 1.1)); nastro(g, w / 2, 8, 0);
  },
  // scritta a pennarello o a bomboletta, su fondo trasparente
  graffito: (g, w, h, { testo, colore = "#1b1b1b" }) => {
    g.clearRect(0, 0, w, h); g.fillStyle = colore; g.textAlign = "center"; g.textBaseline = "middle"; let s = 120; g.font = `${s}px "Permanent Marker", "Caveat", cursive`;
    while (g.measureText(testo).width > w - 30 && s > 30) { s -= 4; g.font = `${s}px "Permanent Marker", "Caveat", cursive` }
    g.save(); g.translate(w / 2, h / 2); g.rotate((Math.random() - .5) * .12); g.globalAlpha = .9; g.fillText(testo, 0, 0); g.restore();
    for (let i = 0; i < 4; i++) { const x = w / 2 + (Math.random() - .5) * g.measureText(testo).width * .8; g.fillRect(x, h / 2 + s * .3, 3, 20 + Math.random() * 40) }
  },
  // scritta a pastello del bambino
  pastello: (g, w, h, { testo, colore = "#d0462f" }, P) => { g.clearRect(0, 0, w, h); let s = Math.min(h * .7, w * 1.5 / Math.max(3, testo.length)); P.pastello(g, testo, w / 2, h / 2, s, colore) },
  // lettera dattiloscritta
  lettera: (g, w, h, { testo, firma }) => {
    g.fillStyle = "#fdfcf8"; g.fillRect(0, 0, w, h); sporco(g, w, h, 600, .05); g.fillStyle = "#222"; g.font = `400 22px "DM Mono", monospace`; g.textAlign = "left"; g.textBaseline = "top";
    avvolgi(g, testo, w - 60).slice(0, 12).forEach((r, i) => g.fillText(r, 30, 40 + i * 32)); if (firma) { g.font = `500 20px "DM Mono", monospace`; g.fillText(firma, 30, h - 60) }
  },
  // notifica, come su un telefono
  bolla: (g, w, h, { testo }) => {
    g.fillStyle = "rgba(20,28,40,.92)"; const r = 30; g.beginPath(); g.roundRect ? g.roundRect(4, 4, w - 8, h - 8, r) : g.rect(4, 4, w - 8, h - 8); g.fill();
    g.fillStyle = "#7fb8d9"; g.beginPath(); g.arc(50, h / 2, 22, 0, 7); g.fill();
    g.fillStyle = "#eef3fa"; g.textAlign = "left"; g.textBaseline = "middle"; let s = 32; g.font = `500 ${s}px "Familjen Grotesk", sans-serif`;
    while (g.measureText(testo).width > w - 110 && s > 18) { s -= 1; g.font = `500 ${s}px "Familjen Grotesk", sans-serif` } g.fillText(testo, 86, h / 2);
  },
  // incisione nella pietra
  inciso: (g, w, h, { testo }) => {
    g.clearRect(0, 0, w, h); g.textAlign = "center"; g.textBaseline = "middle"; let s = 96; g.font = `${s}px Marcellus, serif`; while (g.measureText(testo).width > w - 40 && s > 30) { s -= 3; g.font = `${s}px Marcellus, serif` }
    g.fillStyle = "rgba(255,240,210,.35)"; g.fillText(testo, w / 2 + 2, h / 2 + 2); g.fillStyle = "rgba(40,25,10,.8)"; g.fillText(testo, w / 2, h / 2);
  },
};

/* cosa c'è scritto, età per età. {n} è il soprannome, {N} lo stesso in maiuscolo */
const VOCI = {
  cameretta: [
    { s: "foglio", testo: "Non si disegna sui muri!", w: .46, h: .34, y: 1.66 },
    { s: "foglio", testo: "A letto, che domani c'è scuola", w: .46, h: .34, y: 1.62 },
    { s: "foglio", testo: "Hai tutta la vita davanti", w: .44, h: .33, y: 1.7 },
    { s: "pastello", testo: "TI VOGLIO BENE", w: 1.1, h: .3, y: .6, colore: "#c0399a" },
    { s: "foglio", testo: "{n}, lavati i denti!", w: .42, h: .32, y: 1.65 },
    { s: "foglio", testo: "Cosa vuoi fare da grande?", w: .46, h: .34, y: 1.7 },
    { s: "foglio", testo: "Mangia, che così diventi grande", w: .46, h: .34, y: 1.62 },
    { s: "foglio", testo: "Quando sarai grande capirai", w: .44, h: .33, y: 1.68 },
    { s: "foglio", testo: "Che bel disegno!", w: .4, h: .3, y: 1.6 },
    { s: "pastello", testo: "{N}", w: .9, h: .38, y: .55, colore: "#3d7fd9" },
    { s: "pastello", testo: "IO DA GRANDE", w: 1, h: .32, y: .62, colore: "#d0462f" },
    { s: "pastello", testo: "CASA", w: .6, h: .3, y: .5, colore: "#3c9a3c" },
  ],
  scuola: [
    { s: "manifesto", testa: "SILENZIO", corpo: "Esame in corso.", w: .5, h: .5, y: 2.2, colore: "#24201c" },
    { s: "postit", testo: "Scegli qualcosa di sicuro", w: .3, h: .3, y: 1.5, colore: "#f6e27a" },
    { s: "postit", testo: "Non sprecare il tuo talento", w: .3, h: .3, y: 1.52, colore: "#f7b9c4" },
    { s: "graffito", testo: "chi sarò?", w: 1, h: .4, y: 2.3, colore: "#2d6a4f" },
    { s: "manifesto", testa: "OPEN DAY", corpo: "Scegli il tuo futuro. Aula magna, ore 10.", w: .62, h: .86, y: 2.25, colore: "#3b6fb6" },
    { s: "manifesto", testa: "TEST DI AMMISSIONE", corpo: "Iscrizioni entro il 30 aprile. Posti limitati.", w: .62, h: .86, y: 2.25, colore: "#b84a3b" },
    { s: "manifesto", testa: "ORIENTAMENTO", corpo: "Che cosa farai dopo la maturità? Incontro con gli ex studenti.", w: .62, h: .86, y: 2.25, colore: "#3f8f73" },
    { s: "manifesto", testa: "MATURITÀ", corpo: "Calendario delle prove scritte e orali.", w: .6, h: .84, y: 2.25, colore: "#6d5a9a" },
    { s: "postit", testo: "Segui la tua passione", w: .3, h: .3, y: 1.5 },
    { s: "postit", testo: "Pensa a cosa ti dà da mangiare", w: .3, h: .3, y: 1.45, colore: "#f7b9c4" },
    { s: "postit", testo: "Hai tempo per decidere", w: .3, h: .3, y: 1.55, colore: "#b8e3c4" },
    { s: "postit", testo: "Decidi adesso, o resti indietro", w: .3, h: .3, y: 1.48, colore: "#a9cff2" },
    { s: "graffito", testo: "e se sbaglio?", w: 1.3, h: .42, y: 2.3 },
    { s: "graffito", testo: "non so cosa voglio", w: 1.4, h: .42, y: 2.35 },
    { s: "graffito", testo: "{n} c'era", w: 1, h: .38, y: 2.3, colore: "#2d4fa0" },
    { s: "graffito", testo: "5ªB per sempre", w: 1.2, h: .4, y: 2.3, colore: "#a02d2d" },
  ],
  notte: [
    { s: "manifesto", testa: "CERCASI PERSONALE DI SALA", corpo: "Turni serali e weekend. Presentarsi con curriculum.", w: .62, h: .86, y: 1.5, colore: "#2f5d8a" },
    { s: "bolla", testo: "Hai visto chi si è sposato?", w: .95, h: .24, y: 1.68 },
    { s: "bolla", testo: "Sei ancora lì?", w: .8, h: .24, y: 1.74 },
    { s: "graffito", testo: "domani", w: 1, h: .4, y: 2.2, colore: "#e2523f" },
    { s: "manifesto", testa: "CERCASI STAGISTA", corpo: "Esperienza richiesta. Rimborso spese.", w: .62, h: .86, y: 1.55, colore: "#1b1b1b" },
    { s: "manifesto", testa: "AFFITTASI STANZA", corpo: "Singola, 650 euro più spese. No perditempo.", w: .6, h: .84, y: 1.5, colore: "#c8781e" },
    { s: "manifesto", testa: "FESTA DI LAUREA", corpo: "Sabato, dalle 22. Portate amici.", w: .6, h: .84, y: 1.55, colore: "#7a3fa0" },
    { s: "bolla", testo: "{n}, e il lavoro?", w: .95, h: .24, y: 1.75 },
    { s: "bolla", testo: "Quando ti laurei?", w: .95, h: .24, y: 1.7 },
    { s: "bolla", testo: "Tutti partono. Tu resti?", w: .95, h: .24, y: 1.72 },
    { s: "graffito", testo: "resta", w: 1, h: .4, y: 1.9, colore: "#e8e3d8" },
    { s: "graffito", testo: "parti", w: 1, h: .4, y: 2.1, colore: "#f2c94c" },
  ],
  oracolo: [
    { s: "bolla", testo: "Ti abbiamo trovato un percorso", w: 1.05, h: .26, y: 1.62 },
    { s: "bolla", testo: "Persone che potresti conoscere", w: 1.05, h: .26, y: 1.72 },
    { s: "bolla", testo: "Il tuo anno in sintesi è pronto", w: 1.05, h: .26, y: 1.66 },
    { s: "bolla", testo: "{n}, persone come te hanno scelto questo", w: 1.15, h: .26, y: 1.75 },
    { s: "bolla", testo: "Sono felice di annunciare il mio nuovo ruolo", w: 1.15, h: .26, y: 1.6 },
    { s: "bolla", testo: "3 persone che conosci si sposano quest'anno", w: 1.15, h: .26, y: 1.7 },
    { s: "bolla", testo: "Sei nella media della tua età?", w: 1.05, h: .26, y: 1.65 },
    { s: "manifesto", testa: "DIVENTA LA VERSIONE MIGLIORE DI TE", corpo: "Il tuo potenziale, ottimizzato. Prova gratis.", w: .7, h: .95, y: 1.6, colore: "#2a6fd6" },
  ],
  vicolo: [
    { s: "manifesto", testa: "AFFITTASI", corpo: "Bilocale. Referenze e contratto a tempo indeterminato.", w: .6, h: .84, y: 1.55, colore: "#6d5a9a" },
    { s: "graffito", testo: "ma tu sei felice?", w: 1.4, h: .42, y: 2.2, colore: "#9fd3c7" },
    { s: "postit", testo: "Ricordati chi volevi essere", w: .32, h: .32, y: 1.5, colore: "#b8e3c4" },
    { s: "manifesto", testa: "RICOMINCIARE A 35 ANNI", corpo: "Corso intensivo. Ultimi posti.", w: .62, h: .86, y: 1.55, colore: "#2f6f5a" },
    { s: "manifesto", testa: "SEI ANCORA IN TEMPO", corpo: "Non aspettare che sia troppo tardi.", w: .6, h: .84, y: 1.6, colore: "#b84a3b" },
    { s: "lettera", testo: "Gentile {n}, la ringraziamo per l'interesse mostrato. Dopo un'attenta valutazione abbiamo deciso di proseguire con altri profili.", firma: "L'ufficio del personale", w: .5, h: .7, y: 1.5 },
    { s: "postit", testo: "{n}, quando ti sistemi?", w: .3, h: .3, y: 1.55 },
    { s: "postit", testo: "Alla tua età io avevo già una casa", w: .32, h: .32, y: 1.5, colore: "#f7b9c4" },
    { s: "graffito", testo: "e adesso?", w: 1.1, h: .42, y: 2.1, colore: "#efe6d2" },
    { s: "graffito", testo: "non è tardi", w: 1.2, h: .42, y: 2.3, colore: "#f2c94c" },
  ],
  ritorno: [
    { s: "inciso", testo: "ΜΗΔΕΝ ΑΓΑΝ", w: 1.6, h: .38, y: 2.6 },
    { s: "inciso", testo: "|||| |||| ||", w: .7, h: .3, y: 1.3 },
  ],
  centro: [
    { s: "inciso", testo: "ΓΝΩΘΙ ΣΑΥΤΟΝ", w: 2, h: .44, y: 3.5 },
  ],
};

export function decoraMuri(scena, lab, M, nome, r = Math.random) {
  const n = (nome || "").trim();
  const sost = t => {
    if (!t) return t;
    if (!n) t = t.replace("Gentile {n},", "Buongiorno,").replace("{n} c'era", "io c'ero").replace(/\{n\}, /g, "").replace(/\{N\}/g, "IO");
    t = t.replace(/\{N\}/g, n.toUpperCase()).replace(/\{n\}/g, n);
    return t.charAt(0).toUpperCase() + t.slice(1);
  };
  const voci = {}; for (const [z, l] of Object.entries(VOCI)) voci[z] = l.map(v => ({ ...v, testo: v.s === "graffito" || v.s === "pastello" ? (v.testo ? sost(v.testo).replace(/^./, c => v.s === "graffito" && /^[a-z]/.test(v.testo) ? c.toLowerCase() : c) : v.testo) : sost(v.testo) }));
  const P = lab.percorsi, stanze = ["cameretta", "scuola", "notte", "oracolo", "centro"].filter(z => P[z] && P[z].rett).map(z => ({ c: P[z].sala, mezzo: (P[z].rett[2] - P[z].rett[0] + 1) * M.C / 2 + .2 }));
  const inStanza = (x, z) => { const c = M.centroCella(x, z); return stanze.some(s => Math.abs(c.x - s.c.x) < s.mezzo && Math.abs(c.z - s.c.z) < s.mezzo) };
  const percorsiZona = { cameretta: P.cameretta.andata.concat(P.cameretta.ritorno), scuola: P.scuola.andata.concat(P.scuola.ritorno), notte: P.notte.andata.concat(P.notte.ritorno), oracolo: P.oracolo.andata.concat(P.oracolo.ritorno), vicolo: P.vicolo.andata.concat(P.vicolo.ritorno), centro: P.centro.andata };
  const usati = []; const su = new THREE.Vector3(0, 1, 0);
  for (const [zona, lista] of Object.entries(voci)) {
    const celle = (zona === "ritorno" ? P.vicolo.ritorno : percorsiZona[zona] || []).filter(([x, z]) => M.zonaDi(x, z) === zona && (zona === "centro" || !inStanza(x, z)));
    const facce = []; celle.forEach(([x, z], i) => { if (i < 1) return; for (const l of "NSEW") { const f = M.facciaMuro(lab, x, z, l); if (f) facce.push({ f, i }) } });
    if (!facce.length) continue;
    const passo = facce.length / lista.length;
    lista.forEach((v, k) => {
      for (let t = 0; t < 10; t++) {
        const c = facce[Math.floor((k * passo + t * 1.7 + r() * passo) % facce.length)], lat = new THREE.Vector3().crossVectors(c.f.n, su);
        const gioco = Math.max(0, (M.C - v.w) / 2 - .12), off = (r() - .5) * 2 * gioco;
        const pos = c.f.p.clone().addScaledVector(lat, off).setY(v.y);
        if (usati.some(u => u.distanceTo(pos) < Math.max(.65, v.w * .7))) continue;
        usati.push(pos);
        // tele piccole: sono decine, e la memoria grafica dei telefoni è poca
        const cw = { postit: 192, foglio: 256, manifesto: 320, lettera: 320, bolla: 384, graffito: 384, pastello: 384, inciso: 384 }[v.s] || 256;
        const ch = Math.max(48, Math.round(cw * v.h / v.w / 4) * 4), sc = cw / 512;
        const tx = M.tela(cw, ch, (g, w, h) => { g.scale(sc, sc); STILI[v.s](g, 512, h / sc, v, M) }); tx.anisotropy = 4;
        const mat = new THREE.MeshStandardMaterial({ map: tx, transparent: true, roughness: .9, polygonOffset: true, polygonOffsetFactor: -2 });
        const m = new THREE.Mesh(new THREE.PlaneGeometry(v.w, v.h), mat);
        M.sulMuro(m, c.f, v.y); m.position.addScaledVector(lat, off).addScaledVector(c.f.n, .006 + usati.length * .0004); m.rotateZ((r() - .5) * (v.s === "postit" || v.s === "foglio" ? .12 : .03));
        m.userData.voce = zona; scena.add(m); break;
      }
    });
  }
}

/* la tabella dell'altezza nella cameretta, con le tacche degli anni */
export function tabellaAltezza(scena, M, f, nome) {
  const tx = M.tela(128, 1024, (g, w, h) => {
    g.fillStyle = "#f5eedc"; g.fillRect(0, 0, w, h); g.fillStyle = "#e8b04a"; g.fillRect(0, 0, 18, h);
    g.strokeStyle = "#5a4630"; g.fillStyle = "#5a4630"; g.font = "18px 'DM Mono', monospace";
    for (let cm = 40; cm <= 150; cm += 5) { const y = h - (cm - 40) / 110 * h; g.lineWidth = cm % 10 ? 1 : 2; g.beginPath(); g.moveTo(18, y); g.lineTo(cm % 10 ? 40 : 56, y); g.stroke(); if (cm % 20 === 0) g.fillText(String(cm), 62, y + 6) }
    for (const [cm, anni, col] of [[95, "3 anni", "#3d7fd9"], [102, "4 anni", "#3c9a3c"], [110, "5 anni", "#d0462f"]]) { const y = h - (cm - 40) / 110 * h; g.strokeStyle = col; g.lineWidth = 5; g.beginPath(); g.moveTo(18, y); g.lineTo(w - 4, y); g.stroke(); g.fillStyle = col; g.font = "600 30px Caveat, cursive"; g.fillText(anni, 30, y - 8) }
    if (nome) { g.save(); g.translate(w - 22, 120); g.rotate(Math.PI / 2); g.fillStyle = "#3d2a1a"; g.font = "600 40px Caveat, cursive"; g.fillText(nome, 0, 0); g.restore() }
  });
  const m = new THREE.Mesh(new THREE.PlaneGeometry(.14, 1.1), new THREE.MeshStandardMaterial({ map: tx, roughness: .8 }));
  M.sulMuro(m, f, .4 + .55); m.position.addScaledVector(f.n, .008); scena.add(m); return m;
}
