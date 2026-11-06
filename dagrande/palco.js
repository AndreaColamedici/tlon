/* Da grande · lo schermo del palco.
   La sala vista dall'alto: il labirinto, le luci di chi gioca, quello che è successo in ogni capitolo.
   Tasti: → ← capitoli · X simulazione · R regia · P parola di regia · F schermo intero · S suono · ? aiuto */
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";
import * as M from "./mondo.js";

const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const LV = window.DGLive || { attivo: false };
const ls = { get(k) { try { return JSON.parse(localStorage.getItem(k)) } catch (e) { return null } }, set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)) } catch (e) { } } };
const REGIA = location.hash === "#regia";
const canale = "BroadcastChannel" in window ? new BroadcastChannel("tlon-dagrande-3") : null;
const manda = m => { try { canale && canale.postMessage(m) } catch (e) { } };

export const CAPITOLI = [
  { k: "soglia", eta: "", titolo: "Da grande", sotto: "Inquadra il codice ed entra nel labirinto", zona: null, nota: "Prima di far entrare la sala: Azzera qui sotto (doppio clic), che riporta la scena a zero. Il codice resta sullo schermo mentre la sala entra: i telefoni aspettano nella cameretta. Quando le luci sono abbastanza, la freccia apre il primo movimento (cinque e diciotto anni, di seguito)." },
  { k: "cameretta", eta: "5 anni", titolo: "Cosa vuoi fare da grande?", zona: [0, 0], nota: "Primo movimento, in corso: i telefoni passano da soli ai diciotto anni. Qui guardi il punto interrogativo. Quando il contatore dice che quasi tutti hanno finito, freccia: dati delle porte." },
  { k: "scuola", eta: "18 anni", titolo: "Le porte", zona: [1, 0], nota: "Fine del primo movimento: i telefoni sono fermi, abbassano il suono, si apre il tetto e chi guarda vede le luci degli altri. Scegliere <i>di</i> e scegliere <i>tra</i>; sullo schermo anche la porta che alla sala mancherà di più, che ciascuno ha visto chiudersi e ritroverà ai ventotto anni. Poi la freccia apre il secondo movimento (ventitré e ventotto anni)." },
  { k: "notte", eta: "23 anni", titolo: "La moneta", zona: [2, 0], nota: "Secondo movimento, in corso: dopo la moneta i telefoni vanno da soli all'oracolo. Quando il contatore sale, freccia: dati dell'oracolo." },
  { k: "oracolo", eta: "28 anni", titolo: "L'oracolo", zona: [2, 1], nota: "Fine del secondo movimento: i telefoni sono fermi. Ognuno ha ritrovato la porta che ha lasciato: lo schermo mostra chi ha voluto sapere che vita avrebbe avuto e chi no. Poi la freccia apre il terzo movimento (il vicolo e il centro)." },
  { k: "vicolo", eta: "35 anni", titolo: "Il vicolo cieco", zona: [2, 2], nota: "Terzo movimento, in corso: nel vicolo i telefoni chiedono su che cosa ci si sente in ritardo, poi arrivano al centro, scrivono a chi erano a cinque anni e si fermano. Intanto si riempie la galleria dei segni." },
  { k: "centro", eta: "Da grande", titolo: "Il centro", zona: [1, 1], nota: "I telefoni sono fermi al centro con il tetto aperto: sopra le luci ognuno legge quanti, in questa sala, sono in ritardo sulla stessa cosa, e lo schermo mostra il conto intero. Quando sei pronto, la freccia fa salire tutta la sala sopra i muri nello stesso momento." },
  { k: "fine", eta: "", titolo: "Il labirinto continua", sotto: "Grazie", zona: null, nota: "Tutti i telefoni salgono sopra i muri: ognuno vede il suo filo rosso e il labirinto che continua. Dopo circa quindici secondi il telefono dice che il labirinto era uno spiazzo per ballare, tenendosi per i polsi; otto secondi dopo chiede di posarlo e di cercare il polso di chi si ha accanto. Quel gesto lo reggi tu dal palco. Poi la carta, sul telefono di ciascuno. Congedo." },
];
const SOGNI = { luna: "andare sulla luna", animali: "curare gli animali", gol: "fare gol", ballare: "ballare", incendi: "spegnere gli incendi", scoprire: "scoprire cose nuove", dipingere: "dipingere", insegnare: "insegnare", cantare: "cantare", cucinare: "cucinare", volare: "pilotare gli aerei", misteri: "risolvere misteri", curare: "curare le persone", inventare: "inventare macchine", esplorare: "esplorare il mondo", scavare: "scavare tesori antichi" };
const RITARDI = { lavoro: "Sul lavoro", casa: "Sulla casa", soldi: "Sui soldi", amore: "Sull'amore", figli: "Sui figli", niente: "Su niente" };
const nomePorta = k => k === "sogno" ? "La porta del sogno" : STRADE[+String(k).slice(1)] || k;
const STRADE = ["Medicina", "Giurisprudenza", "Ingegneria", "Economia", "Lettere", "Filosofia", "Psicologia", "Architettura", "Design", "Informatica", "Biologia", "Lingue", "Scienze politiche", "Belle Arti", "Conservatorio", "Fisica", "Matematica", "Infermieristica", "Scienze della formazione", "Cinema", "Agraria", "Lavorare subito", "Un anno all'estero", "Servizio civile"];

/* ---------- scena ---------- */
const tela = $("#c");
const renderer = new THREE.WebGLRenderer({ canvas: tela, antialias: true, powerPreference: "high-performance" });
renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.5)); renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.1;
const scena = new THREE.Scene(); scena.background = new THREE.Color(0x0c0a08); scena.fog = new THREE.FogExp2(0x0c0a08, .0065);
const camera = new THREE.PerspectiveCamera(38, 16 / 9, 1, 1200);
const env = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), .04).texture;
scena.add(new THREE.HemisphereLight(0xbfb0ff, 0x302010, 1.1));
const sole = new THREE.DirectionalLight(0xffd7a0, 2.2); sole.position.set(-30, 60, 20); scena.add(sole);
const composer = new EffectComposer(renderer); composer.addPass(new RenderPass(scena, camera)); composer.addPass(new ShaderPass({ uniforms: { tDiffuse: { value: null } }, vertexShader: `varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
  fragmentShader: `uniform sampler2D tDiffuse;varying vec2 vUv;void main(){vec4 c=texture2D(tDiffuse,vUv);
    if(any(isnan(c.rgb))||any(isinf(c.rgb))||!(c.r==c.r)||c.r>6e4||c.g>6e4||c.b>6e4)c=vec4(0.,0.,0.,1.);gl_FragColor=vec4(min(c.rgb,vec3(64.)),c.a);}` }));
const bloom = new UnrealBloomPass(new THREE.Vector2(512, 512), .9, .5, .8); composer.addPass(bloom); composer.addPass(new OutputPass());
function adatta() { const w = tela.clientWidth, h = tela.clientHeight; renderer.setSize(w, h, false); composer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix() }
addEventListener("resize", adatta);

let lab, mondo, luci, infinito;
const LATO = M.N * M.C;
const centroZona = ([bx, bz]) => new THREE.Vector3((bx + .5) * M.B * M.C - LATO / 2, 0, (bz + .5) * M.B * M.C - LATO / 2);
const vista = { bersaglio: new THREE.Vector3(), raggio: 120, alt: 95, ang: .6, t: new THREE.Vector3(), r: 120, a: 95 };
function puntaA(s) {
  const c = CAPITOLI[s];
  if (c.zona) { vista.bersaglio.copy(centroZona(c.zona)); vista.raggio = 34; vista.alt = 30 }
  else if (s === 0) { vista.bersaglio.set(0, 0, 0); vista.raggio = 92; vista.alt = 70 }
  else { vista.bersaglio.set(0, 0, 0); vista.raggio = 150; vista.alt = 150 }
}

/* le luci della sala */
const MAXL = 900;
function creaLuci() {
  const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(MAXL * 3), 3)); g.setDrawRange(0, 0);
  const sprite = new THREE.CanvasTexture((() => { const c = document.createElement("canvas"); c.width = c.height = 64; const x = c.getContext("2d"); const gr = x.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, "rgba(255,248,225,1)"); gr.addColorStop(.25, "rgba(255,200,110,.9)"); gr.addColorStop(1, "rgba(255,140,40,0)"); x.fillStyle = gr; x.fillRect(0, 0, 64, 64); return c })());
  luci = new THREE.Points(g, new THREE.PointsMaterial({ size: 4.2, map: sprite, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, color: 0xffffff }));
  luci.userData.persone = []; scena.add(luci);
}
function puntiCapitolo(k, fine) {
  const P = lab.percorsi, nomi = ["", "cameretta", "scuola", "notte", "oracolo", "vicolo", "centro"], n = nomi[k];
  if (!n) return [M.centroCella(13, 13)];
  const p = P[n]; const celle = fine ? (p.ritorno || p.andata).slice(-3) : p.andata;
  return celle.map(([x, z]) => M.centroCella(x, z));
}
function aggiornaPersone() {
  const per = luci.userData.persone, voluti = [];
  const prog = (dati.progresso && dati.progresso.capitolo) || {};
  for (const [v, n] of Object.entries(prog)) { const [k, m] = v.split(".").map(Number); for (let i = 0; i < n; i++) voluti.push([k, m]) }
  const presenti = somma(dati.ingresso?.entrato), senzaCap = Math.max(0, presenti - voluti.length);
  for (let i = 0; i < senzaCap; i++) voluti.push([1, -1]);
  voluti.length = Math.min(voluti.length, MAXL);
  while (per.length < voluti.length) per.push({ p: M.centroCella(1, 1), q: new THREE.Vector3(), seme: Math.random(), k: null });
  per.length = voluti.length;
  voluti.forEach(([k, m], i) => { const o = per[i]; if (o.k !== k + "." + m) { o.k = k + "." + m; const pts = m < 0 ? [M.centroCella(1, 1), M.centroCella(0, 0), M.centroCella(1, 0), M.centroCella(0, 1)] : puntiCapitolo(k, m >= 2); const a = pts[Math.floor(o.seme * pts.length) % pts.length]; o.q.copy(a).add(new THREE.Vector3((Math.random() - .5) * 1.6, 0, (Math.random() - .5) * 1.6)) } });
  luci.geometry.setDrawRange(0, per.length);
}
function muoviLuci(dt, t) {
  const a = luci.geometry.attributes.position, per = luci.userData.persone;
  per.forEach((o, i) => { o.p.lerp(o.q, 1 - Math.exp(-dt * .6)); a.array[i * 3] = o.p.x + Math.sin(t * .7 + o.seme * 20) * .25; a.array[i * 3 + 1] = 1.3 + Math.sin(t * 2 + o.seme * 9) * .15; a.array[i * 3 + 2] = o.p.z + Math.cos(t * .6 + o.seme * 13) * .25 });
  a.needsUpdate = true;
}
function creaInfinito() {
  infinito = new THREE.Mesh(new THREE.PlaneGeometry(4000, 4000), new THREE.ShaderMaterial({ transparent: true, depthWrite: false, uniforms: { k: { value: 0 }, lato: { value: LATO / 2 } },
    vertexShader: `varying vec2 vP;void main(){vec4 w=modelMatrix*vec4(position,1.);vP=w.xz;gl_Position=projectionMatrix*viewMatrix*w;}`,
    fragmentShader: `uniform float k;uniform float lato;varying vec2 vP;float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
      void main(){if(abs(vP.x)<lato&&abs(vP.y)<lato)discard;vec2 c=vP/${M.C.toFixed(1)};vec2 i=floor(c),f=fract(c);float r=h(i);
      float d=r<.5?abs(f.x-.04):abs(f.y-.04);float m=1.-smoothstep(.0,.07,d);float dist=length(vP);
      float fade=exp(-max(0.,dist-lato)*.009)*k;vec3 col=mix(vec3(.08,.05,.03),vec3(.95,.66,.27),m);gl_FragColor=vec4(col,fade*(.3+m*.7));}` }));
  infinito.rotation.x = -Math.PI / 2; infinito.position.y = .02; scena.add(infinito);
}

/* ---------- dati ---------- */
let dati = {}, demo = false, liveDal = ls.get("dg3-dal") || Date.now() - 3 * 3600e3;
const somma = o => o ? Object.values(o).reduce((s, n) => s + n, 0) : 0;
function indicizza(righe) { const d = {}; for (const r of righe || []) { ((d[r.stanza] = d[r.stanza] || {})[r.chiave] = d[r.stanza][r.chiave] || {})[r.valore] = Number(r.n) } return d }
async function interroga() {
  if (!LV.attivo || demo || REGIA || document.hidden) return;
  try { dati = indicizza(await LV.conteggi(liveDal)); if (linea === "ko") { linea = ""; mostraComando() } } catch (e) { linea = "ko"; stato("collegamento perso", "ko") }
  disegnaDati();
}
let segniCache = [], segniT = 0;
async function prendiSegni() { if (demo) return; if (!LV.attivo || Date.now() - segniT < 6000) return; segniT = Date.now(); try { segniCache = await LV.segni(24) || [] } catch (e) { } }
function stato(t, c) { const s = $("#stato"); if (s.textContent === t && s.className === "stato " + c) return; s.textContent = t; s.className = "stato " + c; manda({ t: "stato", testo: t, c }); if (REGIA) { const r = $("#r-stato"); r.textContent = t; r.className = "stato " + c } }

/* simulazione per le prove: numeri inventati, sempre dichiarati come tali */
function simula() {
  demo = !demo; $("#simulazione").hidden = !demo;
  if (!demo) { dati = {}; segniCache = []; disegnaDati(); interroga(); return }
  const n = 240, sogni = { luna: 31, animali: 24, gol: 19, ballare: 14, incendi: 9, scoprire: 22, dipingere: 11, insegnare: 13, cantare: 17, cucinare: 7, volare: 12, misteri: 8, curare: 15, inventare: 6, esplorare: 5, scavare: 4, nonlo: 23 };
  dati = { ingresso: { entrato: { 1: n } }, cameretta: { sogno: sogni },
    scuola: { gruppo: { 24: 118, 6: 113 }, porta: { s5: 14, s0: 21, sogno: 26, s21: 18, s3: 17, s8: 15, s9: 22 }, secondi: { 4: 20, 7: 30, 11: 25, 16: 30, 23: 26, 31: 22, 45: 18, 62: 11 }, sicurezza: { 1: 71, 2: 104, 3: 52 }, lasciata: { s19: 38, s4: 31, sogno: 27, s5: 19, nessuna: 22 } },
    notte: { speranza: { testa: 118, croce: 104 }, esito: { testa: 109, croce: 113 }, seguito: { uguali: 104, moneta: 41, speranza: 77 } },
    oracolo: { scelta: { racconta: 84, no: 131 } },
    vicolo: { azione: { segno: 96, spinto: 61, indietro: 52 }, spinte: { 1: 40, 2: 15, 3: 6 }, ritardo: { lavoro: 72, casa: 41, soldi: 38, amore: 29, figli: 17, niente: 12 } },
    progresso: { capitolo: { "1.0": 20, "2.0": 30, "3.0": 40, "4.0": 40, "5.2": 50, "6.0": 40 } } };
  segniCache = Array.from({ length: 18 }, () => ({ punti: JSON.stringify(scarabocchio()) }));
  disegnaDati();
}
function scarabocchio() { const tr = [], k = 1 + Math.floor(Math.random() * 3); for (let j = 0; j < k; j++) { let x = 20 + Math.random() * 60, y = 20 + Math.random() * 60; const t = [[x, y]]; for (let i = 0; i < 14; i++) { x = Math.max(4, Math.min(95, x + (Math.random() - .5) * 18)); y = Math.max(4, Math.min(95, y + (Math.random() - .5) * 18)); t.push([Math.round(x), Math.round(y)]) } tr.push(t) } return tr }

/* sezioni dei dati per ogni capitolo */
const pct = (a, b) => b ? Math.round(a / b * 100) : 0;
const media = o => { let s = 0, n = 0; for (const [v, c] of Object.entries(o || {})) { s += Number(v) * c; n += c } return n ? s / n : 0 };
const barre = (righe, max) => righe.map(([et, n, cls]) => `<div class="barra ${cls || ""}"><span>${et}</span><i style="--w:${max ? n / max * 100 : 0}%"></i><b>${n}</b></div>`).join("");
const fmt = n => n.toLocaleString("it-IT");
function disegnaDati() {
  const s = cur, box = $("#dati"), D = dati, presenti = somma(D.ingresso?.entrato);
  $("#conta").innerHTML = `<b>${fmt(presenti)}</b> ${presenti === 1 ? "luce" : "luci"} nel labirinto`;
  { const prog = D.progresso?.capitolo || {}; let fatti = 0, dentro = 0; for (const [v, n] of Object.entries(prog)) { const [k, m] = v.split(".").map(Number); dentro += n; if (k > s || (k === s && m >= 2)) fatti += n }
    $("#finiti").innerHTML = s >= 1 && s <= 6 && dentro ? `<b>${fmt(fatti)}</b> su ${fmt(Math.max(dentro, presenti))} ${fatti === 1 ? "ha" : "hanno"} finito il capitolo` : ""; manda({ t: "finiti", testo: $("#finiti").textContent }) }
  let h = "";
  if (s === 1) {
    const so = Object.entries(D.cameretta?.sogno || {}).filter(([k]) => k !== "nonlo").sort((a, b) => b[1] - a[1]).slice(0, 5), nl = D.cameretta?.sogno?.nonlo || 0, tot = somma(D.cameretta?.sogno);
    h = `<div class="cifra"><b>${pct(nl, tot)}%</b><span>ha aperto la porta col punto interrogativo</span></div>${barre(so.map(([k, n]) => [SOGNI[k] || k, n]), so[0]?.[1] || 1)}`;
  } else if (s === 2) {
    const g = D.scuola?.gruppo || {}, sec = D.scuola?.secondi || {}, porte = D.scuola?.porta || {}, tot = somma(porte);
    h = `<div class="due"><div class="cifra"><b>${Math.round(media(sec))}<small>s</small></b><span>per scegliere una porta</span></div><div class="cifra"><b>${pct(porte.sogno || 0, tot)}%</b><span>ha riaperto la porta del sogno</span></div></div>
      <div class="sotto-t">La porta che mancherà</div>${barre(Object.entries(D.scuola?.lasciata || {}).filter(([k]) => k !== "nessuna").sort((a, b) => b[1] - a[1]).slice(0, 2).map(([k, n]) => [nomePorta(k), n]), Math.max(1, ...Object.entries(D.scuola?.lasciata || {}).filter(([k]) => k !== "nessuna").map(([, n]) => n)))}
      <div class="piccolo">${fmt(g[24] || 0)} persone avevano 24 porte, ${fmt(g[6] || 0)} ne avevano 6.</div>`;
  } else if (s === 3) {
    const sg = D.notte?.seguito || {}, div = (sg.moneta || 0) + (sg.speranza || 0), tot = div + (sg.uguali || 0);
    h = `<div class="cifra"><b>${pct(div, tot)}%</b><span>ha sperato il contrario di quello che è uscito</span></div>
      <div class="sotto-t">E poi, davanti al bivio</div>${barre([["ha seguito la speranza", sg.speranza || 0, "rosso"], ["ha seguito la moneta", sg.moneta || 0]], Math.max(1, sg.speranza || 0, sg.moneta || 0))}`;
  } else if (s === 4) {
    const o = D.oracolo?.scelta || {}, tot = (o.racconta || 0) + (o.no || 0);
    h = `<div class="due"><div class="cifra"><b>${pct(o.racconta || 0, tot)}%</b><span>ha voluto sapere che vita avrebbe avuto</span></div><div class="cifra"><b>${pct(o.no || 0, tot)}%</b><span>ha preferito non saperlo</span></div></div>`;
  } else if (s === 5) {
    const a = D.vicolo?.azione || {};
    h = `${barre([["ha lasciato un segno", a.segno || 0, "rosso"], ["ha spinto il muro", a.spinto || 0], ["ha girato le spalle al muro", a.indietro || 0]], Math.max(1, ...Object.values(a)))}<div class="segni">${segniCache.slice(0, 12).map(sg => `<canvas data-punti='${typeof sg.punti === "string" ? sg.punti.replace(/'/g, "") : JSON.stringify(sg.punti)}' width="160" height="120"></canvas>`).join("")}</div>`;
  } else if (s === 6) {
    const ri = Object.entries(D.vicolo?.ritardo || {}).filter(([k]) => RITARDI[k] && k !== "niente").sort((a, b) => b[1] - a[1]), inr = ri.reduce((a, [, n]) => a + n, 0), niente = D.vicolo?.ritardo?.niente || 0;
    h = `<div class="cifra riga"><b>${fmt(inr)}</b><span>${inr === 1 ? "persona si sente" : "persone si sentono"} in ritardo su qualcosa. Ciascuna crede di essere l'unica.${niente ? ` Su niente: ${fmt(niente)}.` : ""}</span></div>${barre(ri.map(([k, n]) => [RITARDI[k], n, k === ri[0][0] ? "rosso" : ""]), ri[0]?.[1] || 1)}`;
  }
  if (box.dataset.s !== String(s) || box.dataset.h !== h) { box.dataset.s = s; box.dataset.h = h; box.innerHTML = h; disegnaSegni() }
  if (luci) aggiornaPersone();
}
function disegnaSegni() { $$(".segni canvas").forEach(c => { const g = c.getContext("2d"); g.fillStyle = "#1a1714"; g.fillRect(0, 0, 160, 120); let tr = []; try { tr = JSON.parse(c.dataset.punti) } catch (e) { } g.strokeStyle = "rgba(245,240,230,.9)"; g.lineWidth = 2.4; g.lineCap = "round"; for (const t of tr) { g.beginPath(); t.forEach(([x, y], i) => i ? g.lineTo(x * 1.6, y * 1.2) : g.moveTo(x * 1.6, y * 1.2)); g.stroke() } }) }

/* ---------- suono di sala ----------
   Lo stesso impasto dei telefoni, ma dalle casse: un fondo per ogni età, un rintocco quando si apre un capitolo.
   Spento all'apertura; S lo accende. Non sostituisce la voce: sta sotto. */
const suonoPalco = (() => {
  let ctx = null, master, riverbero, umido, rumore, zonaAtt = null, acceso = false; const ambienti = {};
  const ZONA_DI = ["soglia", "cameretta", "scuola", "notte", "oracolo", "vicolo", "centro", "fine"];
  function avvia() {
    if (ctx) return; const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return; ctx = new AC();
    master = ctx.createGain(); master.gain.value = 0; master.connect(ctx.destination);
    riverbero = ctx.createConvolver(); const n = ctx.sampleRate * 3.2, ir = ctx.createBuffer(2, n, ctx.sampleRate);
    for (let c = 0; c < 2; c++) { const d = ir.getChannelData(c); for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / n, 3) }
    riverbero.buffer = ir; umido = ctx.createGain(); umido.gain.value = .3; riverbero.connect(umido); umido.connect(master);
    rumore = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate); const d = rumore.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    const out = (g, wet = .5) => { g.connect(master); const w = ctx.createGain(); w.gain.value = wet; g.connect(w); w.connect(riverbero) };
    const pad = (freqs, tipo, taglio, vol) => { const g = ctx.createGain(); g.gain.value = 0; const f = ctx.createBiquadFilter(); f.type = "lowpass"; f.frequency.value = taglio; f.connect(g); out(g, .6);
      freqs.forEach((fr, i) => { const o = ctx.createOscillator(); o.type = tipo; o.frequency.value = fr; o.detune.value = (i - 1) * 6; const og = ctx.createGain(); og.gain.value = vol / freqs.length; const lfo = ctx.createOscillator(); lfo.frequency.value = .05 + i * .03; const lg = ctx.createGain(); lg.gain.value = vol / freqs.length * .5; lfo.connect(lg); lg.connect(og.gain); o.connect(og); og.connect(f); o.start(); lfo.start() }); return g };
    const fruscio = (filtro, freq, q, vol) => { const sr = ctx.createBufferSource(); sr.buffer = rumore; sr.loop = true; const f = ctx.createBiquadFilter(); f.type = filtro; f.frequency.value = freq; f.Q.value = q; const g = ctx.createGain(); g.gain.value = vol; sr.connect(f); f.connect(g); sr.start(); return g };
    const mix = (...pezzi) => { const g = ctx.createGain(); g.gain.value = 0; pezzi.forEach(p => { if (p.gain && p.gain.value === 0 && p !== g) p.gain.value = 1; p.connect(g) }); g.connect(master); return g };
    ambienti.soglia = mix(pad([73.4, 110, 146.8], "triangle", 500, .05));
    ambienti.cameretta = mix(pad([174.6, 220, 261.6], "triangle", 900, .05));
    ambienti.scuola = mix(pad([100, 200, 300], "sawtooth", 420, .012), fruscio("bandpass", 3000, .6, .006));
    ambienti.notte = mix(pad([73.4, 110, 146.8], "sine", 400, .06), fruscio("lowpass", 180, .7, .05));
    ambienti.oracolo = mix(pad([392, 587.3, 880, 1174.7], "sine", 2400, .028), pad([98, 147], "sine", 300, .04));
    ambienti.vicolo = mix(fruscio("bandpass", 2400, .5, .05), fruscio("lowpass", 700, .5, .04), pad([65.4, 98], "sine", 250, .04));
    ambienti.centro = mix(pad([73.4, 110, 146.8, 220, 277.2], "triangle", 700, .05), fruscio("bandpass", 900, .4, .01));
    ambienti.fine = mix(pad([73.4, 110, 146.8, 220, 293.7, 440], "sine", 1200, .045));
    // il carillon della cameretta, ogni tanto
    const sc = [523.3, 587.3, 659.3, 784, 880, 1046.5];
    setInterval(() => { if (acceso && zonaAtt === "cameretta") ton(sc[Math.floor(Math.random() * sc.length)], 1.6, .035, "sine", .7) }, 2600);
  }
  function ton(freq, durata, vol, tipo = "sine", wet = .5, quando = 0, a = .01) {
    const t = ctx.currentTime + quando, o = ctx.createOscillator(); o.type = tipo; o.frequency.value = freq; const g = ctx.createGain();
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(vol, t + a); g.gain.exponentialRampToValueAtTime(.0001, t + durata); o.connect(g); g.connect(master); const w = ctx.createGain(); w.gain.value = wet; g.connect(w); w.connect(riverbero); o.start(t); o.stop(t + durata + .05);
  }
  return {
    get acceso() { return acceso },
    accendi(si) {
      acceso = si; const e = $("#suono"); e.textContent = si ? "suono acceso" : "suono spento"; e.classList.toggle("acceso", si);
      if (si) { avvia(); if (!ctx) return; ctx.resume(); master.gain.setTargetAtTime(.9, ctx.currentTime, .8); zonaAtt = null; this.capitolo(cur) }
      else if (ctx) master.gain.setTargetAtTime(0, ctx.currentTime, .6);
    },
    capitolo(s) {
      if (!ctx || !acceso) return; const z = ZONA_DI[s] || "centro"; if (z === zonaAtt) return; zonaAtt = z;
      for (const [k, g] of Object.entries(ambienti)) g.gain.setTargetAtTime(k === z ? 1 : 0, ctx.currentTime, 1.6);
      // il rintocco dell'apertura: più grave a ogni età
      const base = [261.6, 261.6, 220, 196, 174.6, 146.8, 130.8, 110][s] || 130.8;
      [1, 1.5, 2].forEach((m, i) => ton(base * m, 4 - i, .05 / (i + 1), "triangle", .8, i * .12, .02));
      if (s === 7) [73.4, 110, 146.8, 220, 293.7, 440, 587.3].forEach((f, i) => ton(f, 9, .04, "sine", .9, i * .55, 1.5));
    }
  };
})();

/* ---------- capitoli ---------- */
// una finestra nuova riparte dall'inizio: un valore rimasto dalle prove non deve aprire i telefoni.
// Una ricarica della stessa finestra riprende il capitolo: durante l'evento non deve riportare tutti all'inizio.
let cur = 0;
if (!REGIA) { try { cur = Math.max(0, Math.min(CAPITOLI.length - 1, +sessionStorage.getItem("dg3-cap") || 0)) } catch (e) { } }
const APERTURE = [1, 3, 5, 7], ATTESA = 7000; // la scena arriva ai telefoni entro cinque secondi e mezzo, anche a chi non ha il tempo reale
let ultimoS = cur, daAprire = false;
function vai(s, daRemoto, avvio) {
  cur = Math.max(0, Math.min(CAPITOLI.length - 1, s)); ls.set("dg3-cap", cur); try { if (!REGIA) sessionStorage.setItem("dg3-cap", cur) } catch (e) { }
  const c = CAPITOLI[cur];
  document.body.dataset.s = cur;
  $("#eta").textContent = c.eta; $("#titolo").textContent = c.titolo; $("#sottotitolo").textContent = c.sotto || ""; $("#numero").textContent = cur >= 1 && cur <= 6 ? ["", "I", "II", "III", "IV", "V", "VI"][cur] : "";
  $("#pannello").classList.remove("entra"); void $("#pannello").offsetWidth; $("#pannello").classList.add("entra");
  if (lab) puntaA(cur);
  if (infinito) infinito.userData.k = cur === 7 ? 1 : 0;
  $("#qr-sopra").hidden = cur !== 7; $("#qr p:not(#qr-sopra)").textContent = cur === 7 ? "tlon.it/dagrande" : "tlon.it/dagrande/tu";
  // le aperture atterrano sui telefoni dopo qualche secondo: il rintocco del palco cade con il loro
  const apre = !avvio && APERTURE.includes(cur) && cur > ultimoS; ultimoS = cur; if (apre) { daAprire = true; setTimeout(() => suonoPalco.capitolo(cur), ATTESA) } else suonoPalco.capitolo(cur);
  disegnaDati(); if (cur === 5) { segniT = 0; prendiSegni().then(disegnaDati) }
  if (!daRemoto) manda({ t: "vai", s: cur });
  // solo la finestra del palco parla con i telefoni, anche quando il comando arriva dalla regia; una finestra appena aperta li lascia dove sono
  if (!REGIA && lab && !avvio) { prendiComando(); sincronizza() }
  aggiornaRegia();
}
/* il comando arriva ai telefoni anche se la rete perde un colpo: si ritenta finché non passa, poi si controlla ogni dieci secondi.
   I telefoni li comanda una finestra sola: quella in cui si è premuto l'ultimo tasto. Una finestra appena aperta non scrive niente finché non si preme un tasto,
   una finestra dimenticata che trova la scena cambiata da un'altra smette di comandare. Scrive solo quando la scena cambia: ogni scrittura raggiunge trecento telefoni. */
let sincro = 0, inviato = -1, comando = false, linea = "";
try { comando = !REGIA && sessionStorage.getItem("dg3-comando") === "1" } catch (e) { }
function prendiComando() { comando = true; inviato = -1; try { sessionStorage.setItem("dg3-comando", "1") } catch (e) { } }
async function mostraComando() {
  if (!LV.attivo || REGIA) return;
  if (!ls.get("dg-parola")) return stato("manca la parola di regia (P): i telefoni non ti seguono", "ko");
  if (comando) return stato("dal vivo · capitolo " + cur + " aperto", "vivo");
  try { const st = await LV.stato(), s = +st.s || 0; if (comando) return; stato(s === cur ? "pronto · i telefoni sono al capitolo " + s : "i telefoni sono al capitolo " + s + " · premi un tasto per prendere il comando", s === cur ? "vivo" : "ko") } catch (e) { stato("collegamento perso", "ko") }
}
async function sincronizza() {
  clearTimeout(sincro); const p = ls.get("dg-parola"); if (!LV.attivo || !p || REGIA || !comando) { mostraComando(); if (!REGIA && !comando) sincro = setTimeout(sincronizza, 10000); return }
  const s = cur;
  // un'altra finestra ha cambiato la scena dopo l'ultimo invio di questa: cede
  if (inviato === s) { try { const st = await LV.stato(); if (!comando || cur !== s) return; if (+st.s !== inviato) { comando = false; try { sessionStorage.removeItem("dg3-comando") } catch (e) { } return sincronizza() } } catch (e) { } sincro = setTimeout(sincronizza, 10000); return }
  try { const apri = daAprire; await LV.vai(p, s, 0, apri ? "apri" : null, null, apri ? ATTESA : 0); daAprire = false; inviato = s; linea = ""; mostraComando(); sincro = setTimeout(sincronizza, 10000) }
  catch (e) { const parola = String(e.message).includes("parola"); stato(parola ? "parola di regia errata (P)" : "comando non arrivato, ritento…", "ko"); if (!parola) sincro = setTimeout(sincronizza, 2500) }
}

/* ---------- regia ---------- */
function aggiornaRegia() {
  if (!REGIA) return;
  const c = CAPITOLI[cur], n = CAPITOLI[cur + 1];
  $("#r-ora").innerHTML = `<b>${cur}. ${c.titolo}</b>${c.eta ? " · " + c.eta : ""}`; $("#r-nota").innerHTML = c.nota || "";
  $("#r-poi").textContent = n ? "Dopo: " + n.titolo : "";
  $$("#r-scaletta li").forEach((li, i) => li.classList.toggle("ora", i === cur));
}
if (REGIA) {
  document.body.classList.add("regia");
  $("#r-scaletta").innerHTML = CAPITOLI.map((c, i) => `<li data-i="${i}">${i}. ${c.titolo}</li>`).join("");
  $("#r-scaletta").onclick = e => { const li = e.target.closest("li"); if (li) vai(+li.dataset.i) };
  $("#r-parola").value = ls.get("dg-parola") || ""; $("#r-parola").onchange = e => { ls.set("dg-parola", e.target.value.trim()); sincronizza() };
  $("#r-avanti").onclick = () => vai(cur + 1); $("#r-indietro").onclick = () => vai(cur - 1);
  $("#r-azzera").ondblclick = async () => {
    const p = ls.get("dg-parola"); if (!LV.attivo || !p) { $("#r-azzera").textContent = "Serve il collegamento e la parola di regia"; return }
    try { await LV.azzera(p); manda({ t: "azzera" }); manda({ t: "vai", s: 0 }); $("#r-azzera").textContent = "Dati delle prove cancellati, scena all'inizio" } catch (e) { $("#r-azzera").textContent = "Non riuscito: " + e.message }
  };
  setInterval(() => { const d = new Date(); $("#r-orologio").textContent = d.toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit" }) }, 1000);
}
canale && (canale.onmessage = e => { const m = e.data; if (m.t === "finiti" && REGIA) $("#r-finiti").textContent = m.testo; if (m.t === "chiedi" && !REGIA) manda({ t: "vai", s: cur }); if (m.t === "stato" && REGIA) { const r = $("#r-stato"); r.textContent = m.testo; r.className = "stato " + m.c } if (m.t === "vai" && m.s !== cur) vai(m.s, true); if (m.t === "azzera" && !REGIA) { liveDal = Date.now(); ls.set("dg3-dal", liveDal); dati = {}; disegnaDati() } });

addEventListener("storage", e => { if (e.key === "dg-parola" && !REGIA) sincronizza() }); // parola inserita nella finestra di regia: il comando resta da prendere con un tasto

/* ---------- tasti ---------- */
addEventListener("keydown", e => {
  if (e.target.tagName === "INPUT") return;
  const k = e.key;
  if (k === "ArrowRight" || k === "PageDown" || k === " ") { e.preventDefault(); vai(cur + 1) }
  else if (k === "ArrowLeft" || k === "PageUp") { e.preventDefault(); vai(cur - 1) }
  else if (k === "x" || k === "X") simula();
  else if (k === "s" || k === "S") suonoPalco.accendi(!suonoPalco.acceso);
  else if (k === "r" || k === "R") window.open(location.pathname + "#regia", "dg-regia", "width=520,height=820");
  else if (k === "p" || k === "P") { const v = prompt("Parola di regia", ls.get("dg-parola") || ""); if (v !== null) { ls.set("dg-parola", v.trim()); sincronizza() } }
  else if (k === "f" || k === "F") { document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen().catch(() => { }) }
  else if (k === "?") $("#aiuto").hidden = !$("#aiuto").hidden;
  else if (k === "Escape") $("#aiuto").hidden = true;
  else if (/^[0-7]$/.test(k)) vai(+k);
});

/* ---------- avvio ---------- */
const orologio = new THREE.Clock();
function ciclo() {
  const dt = Math.min(.05, orologio.getDelta()), t = orologio.elapsedTime;
  if (mondo) {
    vista.ang += dt * .035;
    vista.t.lerp(vista.bersaglio, 1 - Math.exp(-dt * .9)); vista.r = THREE.MathUtils.lerp(vista.r, vista.raggio, 1 - Math.exp(-dt * .9)); vista.a = THREE.MathUtils.lerp(vista.a, vista.alt, 1 - Math.exp(-dt * .9));
    camera.position.set(vista.t.x + Math.sin(vista.ang) * vista.r, vista.a, vista.t.z + Math.cos(vista.ang) * vista.r); camera.lookAt(vista.t.x, 0, vista.t.z);
    for (const f of mondo.anima) f(t); muoviLuci(dt, t);
    if (infinito) infinito.material.uniforms.k.value = THREE.MathUtils.lerp(infinito.material.uniforms.k.value, infinito.userData.k || 0, 1 - Math.exp(-dt * .7));
    composer.render();
  }
  requestAnimationFrame(ciclo);
}
async function avvia() {
  if (REGIA) { vai(cur, true); manda({ t: "chiedi" }); return }
  try { await Promise.race([Promise.all(["48px Caveat", "48px Marcellus"].map(f => document.fonts.load(f))), new Promise(r => setTimeout(r, 2000))]) } catch (e) { }
  adatta();
  lab = M.genera("palco"); mondo = await M.costruisci(scena, lab, { base: "./", env }); mondo.lunaCameretta.material.emissiveIntensity = .25; // vista dall'alto abbaglierebbe tutta la mappa
  for (const so of mondo.soffitti || []) so.visible = false;
  creaLuci(); creaInfinito(); vai(cur, true, true); vista.t.copy(vista.bersaglio); vista.r = vista.raggio; vista.a = vista.alt;
  requestAnimationFrame(ciclo);
  if (LV.attivo) { stato(ls.get("dg-parola") ? "collegamento…" : "manca la parola di regia (P): i telefoni non ti seguono", "ko"); sincronizza(); interroga(); setInterval(interroga, 2000); setInterval(() => { if (cur === 5) prendiSegni().then(disegnaDati) }, 6000) }
  else stato("senza collegamento", "ko");
}
avvia();
window.__palco = { vai, simula, suono: suonoPalco, get dati() { return dati } };
