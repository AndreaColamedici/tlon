/* Da grande · le voci sui muri.
   Ogni età ha le frasi che ci sentiamo dire mentre cresciamo: molte si contraddicono.
   Il soprannome dato all'ingresso resta sul telefono e compare nelle voci rivolte a te. */
import * as THREE from "three";

const CARTA = "#f3ecdc";
const avvolgi = (g, testo, larg) => { const parole = String(testo).split(" "), righe = []; let r = ""; for (const p of parole) { const t = r ? r + " " + p : p; if (g.measureText(t).width > larg && r) { righe.push(r); r = p } else r = t } righe.push(r); return righe };
const sporco = (g, w, h, n = 900, a = .06) => { for (let i = 0; i < n; i++) { g.fillStyle = `rgba(60,40,20,${Math.random() * a})`; g.fillRect(Math.random() * w, Math.random() * h, 2, 2) } };
const nastro = (g, x, y, r) => { g.save(); g.translate(x, y); g.rotate(r); g.fillStyle = "rgba(235,225,190,.75)"; g.fillRect(-22, -8, 44, 16); g.restore() };

/* il testo riempie lo spazio che ha: si parte grande e si scende finché non ci sta, andando a capo */
const adatta = (g, testo, larg, alt, smax, smin, font, inter = 1.1) => {
  for (let s = smax; ; s -= 2) { g.font = font(s); const righe = avvolgi(g, testo, larg); if ((righe.length * s * inter <= alt && Math.max(...righe.map(r => g.measureText(r).width)) <= larg) || s <= smin) return { s, righe } }
};
const GROTESK = (peso) => s => `${peso} ${s}px "Familjen Grotesk", sans-serif`, CAVEAT = s => `600 ${s}px Caveat, cursive`;
/* stili: ognuno disegna su una tela e restituisce le sue proporzioni */
const STILI = {
  // manifesto stampato: fascia di colore, titolo grande, testo
  manifesto: (g, w, h, { testa, corpo, colore = "#E2523F" }) => {
    g.fillStyle = CARTA; g.fillRect(0, 0, w, h); sporco(g, w, h, 1400, .07);
    g.fillStyle = colore; g.fillRect(0, 0, w, h * .36);
    g.fillStyle = "#fff"; g.textAlign = "left"; g.textBaseline = "top";
    const T = adatta(g, testa, w - 40, h * .36 - 34, 104, 30, GROTESK(700), 1.02); T.righe.forEach((r, i) => g.fillText(r, 20, 18 + i * T.s * 1.02));
    g.fillStyle = "#24201c"; if (corpo) { const C = adatta(g, corpo, w - 40, h * .6 - 26, 66, 26, GROTESK(500), 1.18); C.righe.forEach((r, i) => g.fillText(r, 20, h * .39 + i * C.s * 1.18)) }
    nastro(g, 24, 10, -.4); nastro(g, w - 24, 10, .4);
  },
  // post-it scritto a mano
  postit: (g, w, h, { testo, colore = "#f6e27a" }) => {
    g.fillStyle = colore; g.fillRect(6, 6, w - 12, h - 12); g.fillStyle = "rgba(0,0,0,.08)"; g.fillRect(6, h - 30, w - 12, 24);
    g.fillStyle = "#1f2a5a"; g.textAlign = "center"; g.textBaseline = "middle"; const { s, righe } = adatta(g, testo, w - 44, h - 50, 130, 28, CAVEAT, 1);
    righe.forEach((r, i) => g.fillText(r, w / 2, h / 2 + (i - (righe.length - 1) / 2) * s));
  },
  // foglio appeso dagli adulti, a pennarello blu
  foglio: (g, w, h, { testo }) => {
    g.fillStyle = "#fbf8f0"; g.fillRect(0, 0, w, h); g.strokeStyle = "rgba(90,120,200,.35)"; g.lineWidth = 2; for (let y = 60; y < h; y += 38) { g.beginPath(); g.moveTo(10, y); g.lineTo(w - 10, y); g.stroke() }
    g.fillStyle = "#1d3c8f"; g.textAlign = "center"; g.textBaseline = "middle"; const { s, righe } = adatta(g, testo, w - 50, h - 44, 130, 30, CAVEAT, 1.02);
    righe.forEach((r, i) => g.fillText(r, w / 2, h / 2 + (i - (righe.length - 1) / 2) * s * 1.02)); nastro(g, w / 2, 8, 0);
  },
  // scritta a pennarello o a bomboletta, su fondo trasparente
  graffito: (g, w, h, { testo, colore = "#1b1b1b" }) => {
    g.clearRect(0, 0, w, h); g.fillStyle = colore; g.textAlign = "center"; g.textBaseline = "middle"; const { s, righe } = adatta(g, testo, w - 30, h - 16, 170, 34, s => `${s}px "Permanent Marker", "Caveat", cursive`, 1.04);
    g.save(); g.translate(w / 2, h / 2); g.rotate((Math.random() - .5) * .08); g.globalAlpha = .92; righe.forEach((r, i) => g.fillText(r, 0, (i - (righe.length - 1) / 2) * s * 1.04)); g.restore();
    for (let i = 0; i < 4; i++) { const x = w / 2 + (Math.random() - .5) * w * .7; g.fillRect(x, h / 2 + righe.length * s * .4, 3, 14 + Math.random() * 24) }
  },
  // scritta a pastello del bambino
  pastello: (g, w, h, { testo, colore = "#d0462f" }, P) => { g.clearRect(0, 0, w, h); const { s, righe } = adatta(g, testo, w - 20, h - 8, Math.floor(h * .8), 26, s => `${s}px Caveat, "Comic Sans MS", cursive`, .95); righe.forEach((r, i) => P.pastello(g, r, w / 2, h / 2 + (i - (righe.length - 1) / 2) * s * .95, s, colore)) },
  // lettera dattiloscritta
  lettera: (g, w, h, { testo, firma }) => {
    g.fillStyle = "#fdfcf8"; g.fillRect(0, 0, w, h); sporco(g, w, h, 600, .05); g.fillStyle = "#222"; g.textAlign = "left"; g.textBaseline = "top"; const { s, righe } = adatta(g, testo, w - 50, h - 120, 48, 20, s => `400 ${s}px "DM Mono", monospace`, 1.3);
    righe.forEach((r, i) => g.fillText(r, 25, 30 + i * s * 1.3)); if (firma) { g.font = `500 24px "DM Mono", monospace`; g.fillText(firma, 25, h - 58, w - 50) }
  },
  // notifica, come su un telefono
  bolla: (g, w, h, { testo }) => {
    g.fillStyle = "rgba(20,28,40,.94)"; const r = 30; g.beginPath(); g.roundRect ? g.roundRect(4, 4, w - 8, h - 8, r) : g.rect(4, 4, w - 8, h - 8); g.fill();
    g.fillStyle = "#7fb8d9"; g.beginPath(); g.arc(40, h / 2, 16, 0, 7); g.fill();
    g.fillStyle = "#eef3fa"; g.textAlign = "left"; g.textBaseline = "middle"; const { s, righe } = adatta(g, testo, w - 88, h - 20, 72, 22, GROTESK(500), 1.1); righe.forEach((t, i) => g.fillText(t, 70, h / 2 + (i - (righe.length - 1) / 2) * s * 1.1));
  },
  // incisione nella pietra
  inciso: (g, w, h, { testo }) => {
    g.clearRect(0, 0, w, h); g.textAlign = "center"; g.textBaseline = "middle"; const { s } = adatta(g, testo, w - 30, h - 10, 170, 34, s => `${s}px Marcellus, serif`, 1); g.font = `${s}px Marcellus, serif`;
    g.fillStyle = "rgba(255,240,210,.45)"; g.fillText(testo, w / 2 + 3, h / 2 + 3); g.fillStyle = "rgba(30,18,6,.92)"; g.fillText(testo, w / 2, h / 2);
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
    { s: "manifesto", testa: "SILENZIO", corpo: "Esame in corso.", w: .5, h: .5, y: 2.5, colore: "#24201c" },
    { s: "postit", testo: "Scegli qualcosa di sicuro", w: .3, h: .3, y: 1.5, colore: "#f6e27a" },
    { s: "postit", testo: "Non sprecare il tuo talento", w: .3, h: .3, y: 1.52, colore: "#f7b9c4" },
    { s: "graffito", testo: "chi sarò?", w: 1, h: .4, y: 2.3, colore: "#2d6a4f" },
    { s: "manifesto", testa: "OPEN DAY", corpo: "Scegli il tuo futuro. Aula magna, ore 10.", w: .62, h: .86, y: 2.6, colore: "#3b6fb6" },
    { s: "manifesto", testa: "TEST DI AMMISSIONE", corpo: "Iscrizioni entro il 30 aprile. Posti limitati.", w: .62, h: .86, y: 2.6, colore: "#b84a3b" },
    { s: "manifesto", testa: "ORIENTAMENTO", corpo: "Che cosa farai dopo la maturità? Incontro con gli ex studenti.", w: .62, h: .86, y: 2.6, colore: "#3f8f73" },
    { s: "manifesto", testa: "MATURITÀ", corpo: "Calendario delle prove scritte e orali.", w: .6, h: .84, y: 2.6, colore: "#6d5a9a" },
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
    { s: "manifesto", testa: "MUTUO 30 ANNI", corpo: "Tasso fisso. Rata costante. Fino ai 65.", w: .6, h: .84, y: 1.55, colore: "#1f4e79" },
    { s: "bolla", testo: "Ma quindi tu cosa fai, di preciso?", w: 1.1, h: .26, y: 1.7 },
    { s: "postit", testo: "Prenotare il check-up", w: .3, h: .3, y: 1.45, colore: "#f6e27a" },
    { s: "manifesto", testa: "SPEED DATING OVER 35", corpo: "Giovedì. Aperitivo incluso.", w: .6, h: .84, y: 1.55, colore: "#a0306a" },
    { s: "bolla", testo: "{n}, e i figli?", w: .9, h: .24, y: 1.74 },
    { s: "graffito", testo: "ancora qui", w: 1.1, h: .42, y: 2.15, colore: "#9fd3c7" },
  ],
  ritorno: [
    { s: "inciso", testo: "ΜΗΔΕΝ ΑΓΑΝ", w: 1.6, h: .38, y: 2.6 },
    { s: "inciso", testo: "|||| |||| ||", w: .7, h: .3, y: 1.3 },
  ],
  centro: [
    { s: "inciso", testo: "ΓΝΩΘΙ ΣΑΥΤΟΝ", w: 2, h: .44, y: 3.5 },
  ],
};

export const LUCE_VOCI = .34;
const SCALA = { foglio: [3, 3], postit: [3, 3], manifesto: [2.4, 2.4], lettera: [3, 3], bolla: [2.2, 3], graffito: [2.2, 2.2], pastello: [2.2, 2.4], inciso: [1.6, 2] };
export function decoraMuri(scena, lab, M, nome, r = Math.random, soloZone = null, mie = {}) {
  const n = (nome || "").trim();
  const sost = t => {
    if (!t) return t;
    if (!n) t = t.replace("Gentile {n},", "Buongiorno,").replace("{n} c'era", "io c'ero").replace(/\{n\}, /g, "").replace(/\{N\}/g, "IO");
    t = t.replace(/\{N\}/g, n.toUpperCase()).replace(/\{n\}/g, n);
    return t.charAt(0).toUpperCase() + t.slice(1);
  };
  const voci = {}; for (const [z, l] of Object.entries(VOCI)) voci[z] = [...(mie[z] || []), ...l].map(v => ({ ...v, testo: v.s === "graffito" || v.s === "pastello" ? (v.testo ? sost(v.testo).replace(/^./, c => v.s === "graffito" && /^[a-z]/.test(v.testo) ? c.toLowerCase() : c) : v.testo) : sost(v.testo) }));
  const P = lab.percorsi, stanze = ["cameretta", "scuola", "notte", "oracolo", "centro"].filter(z => P[z] && P[z].rett).map(z => ({ c: P[z].sala, mezzo: (P[z].rett[2] - P[z].rett[0] + 1) * M.C / 2 + .2 }));
  const inStanza = (x, z) => { const c = M.centroCella(x, z); return stanze.some(s => Math.abs(c.x - s.c.x) < s.mezzo && Math.abs(c.z - s.c.z) < s.mezzo) };
  const percorsiZona = { cameretta: P.cameretta.andata.concat(P.cameretta.ritorno), scuola: P.scuola.andata.concat(P.scuola.ritorno), notte: P.notte.andata.concat(P.notte.ritorno), oracolo: P.oracolo.andata.concat(P.oracolo.ritorno), vicolo: P.vicolo.andata.concat(P.vicolo.ritorno), centro: P.centro.andata };
  const usati = []; const su = new THREE.Vector3(0, 1, 0);
  scena.traverse(o => { if (o.userData.ingombro) usati.push({ p: o.position.clone(), ...o.userData.ingombro }) }); // disegni e tabelle già appesi
  for (const [zona, lista] of Object.entries(voci)) {
    if (soloZone && !soloZone.includes(zona)) continue;
    const celle = (zona === "ritorno" ? P.vicolo.ritorno : percorsiZona[zona] || []).filter(([x, z]) => M.zonaDi(x, z) === zona && (zona === "centro" || !inStanza(x, z)));
    const facce = []; celle.forEach(([x, z], i) => { if (i < 3 || (P.vicolo.cieco && x === P.vicolo.cieco[0] && z === P.vicolo.cieco[1])) return; /* dove ci si ferma a disegnare o a spingere il muro, il muro resta libero */ const [px, pz] = celle[i - 1], dx = x - px, dz = z - pz, unita = Math.abs(dx) + Math.abs(dz) === 1; for (const l of "NSEW") { const f = M.facciaMuro(lab, x, z, l); if (f) facce.push({ f, i, fronte: unita && f.n.x * dx + f.n.z * dz < -.5 }) } });
    if (!facce.length) continue;
    // sul telefono in verticale un muro di lato resta tagliato finché non ci sei accanto: prima i muri che si hanno di fronte camminando
    const difronte = facce.filter(c => c.fronte); let dopo = 0;
    const passo = facce.length / lista.length;
    lista.forEach((v0, k) => {
      // grandi, perché si leggono camminando; alla scuola sopra gli armadietti, che altrimenti li coprirebbero
      const [sw, sh] = SCALA[v0.s] || [2, 2], fondo = zona === "scuola" ? 1.92 : .18, cima = M.ZONE[zona].h - .12, largo = M.C - M.T - .16;
      let vw = Math.min(largo, v0.w * sw), vh = v0.h * sh; if (vh > cima - fondo) { const q = (cima - fondo) / vh; vh *= q; vw *= q }
      const v = { ...v0, w: vw, h: vh, y: Math.min(cima - vh / 2, Math.max(fondo + vh / 2, v0.y)) };
      for (let t = 0; t < 14; t++) {
        const c = t < 6 && dopo < difronte.length ? difronte[(dopo + t) % difronte.length] : facce[Math.floor((k * passo + t * 1.7 + r() * passo) % facce.length)], lat = new THREE.Vector3().crossVectors(c.f.n, su);
        const gioco = Math.max(0, (M.C - M.T - v.w) / 2 - .02), off = (r() - .5) * 2 * gioco;
        const pos = c.f.p.clone().addScaledVector(lat, off).setY(v.y);
        // niente sovrapposizioni: si confrontano i rettangoli, non solo i centri
        if (usati.some(u => Math.hypot(u.p.x - pos.x, u.p.z - pos.z) < (u.w + v.w) / 2 + .08 && Math.abs(u.p.y - pos.y) < (u.h + v.h) / 2 + .05)) continue;
        usati.push({ p: pos, w: v.w, h: v.h });
        // tele piccole: sono decine, e la memoria grafica dei telefoni è poca
        const cw = { postit: 240, foglio: 320, manifesto: 400, lettera: 400, bolla: 480, graffito: 480, pastello: 480, inciso: 480 }[v.s] || 320;
        const ch = Math.max(48, Math.round(cw * v.h / v.w / 4) * 4), sc = cw / 512;
        const tx = M.tela(cw, ch, (g, w, h) => { g.scale(sc, sc); STILI[v.s](g, 512, h / sc, v, M) }); tx.anisotropy = 8;
        // una luce propria appena accennata: anche dove le lampade non arrivano si deve poter leggere
        const mat = new THREE.MeshStandardMaterial({ map: tx, transparent: true, roughness: .9, polygonOffset: true, polygonOffsetFactor: -2, emissive: 0xffffff, emissiveMap: tx, emissiveIntensity: LUCE_VOCI });
        const m = new THREE.Mesh(new THREE.PlaneGeometry(v.w, v.h), mat);
        M.sulMuro(m, c.f, v.y); m.position.addScaledVector(lat, off).addScaledVector(c.f.n, .014 + (usati.length % 20) * .0004); m.rotateZ((r() - .5) * (v.s === "postit" || v.s === "foglio" ? .12 : .03));
        m.userData.voce = zona; scena.add(m); if (t < 6) dopo += t + 1; break;
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
  M.sulMuro(m, f, .4 + .55); m.position.addScaledVector(f.n, .008); m.userData.ingombro = { w: .3, h: 1.1 }; scena.add(m); return m;
}
