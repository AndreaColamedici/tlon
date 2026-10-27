/* Da grande · lo schermo del palco.
   La sala vista dall'alto: il labirinto, le luci di chi gioca, quello che è successo in ogni capitolo.
   Tasti: → ← capitoli · X simulazione · R regia · P parola di regia · F schermo intero · S suono · ? aiuto */
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import * as M from "./mondo.js";

const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const LV = window.DGLive || { attivo: false };
const ls = { get(k) { try { return JSON.parse(localStorage.getItem(k)) } catch (e) { return null } }, set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)) } catch (e) { } } };
const REGIA = location.hash === "#regia";
const canale = "BroadcastChannel" in window ? new BroadcastChannel("tlon-dagrande-3") : null;
const manda = m => { try { canale && canale.postMessage(m) } catch (e) { } };

export const CAPITOLI = [
  { k: "soglia", eta: "", titolo: "Da grande", sotto: "Inquadra il codice ed entra nel labirinto", zona: null },
  { k: "cameretta", eta: "5 anni", titolo: "Cosa vuoi fare da grande?", zona: [0, 0], nota: "A cinque anni si sceglie <i>di</i>: ogni porta è possibile, anche quella col punto interrogativo. Guarda quante persone l'hanno aperta: non sapere cosa fare della propria vita comincia presto, ed è normale." },
  { k: "scuola", eta: "18 anni", titolo: "Le porte", zona: [1, 0], nota: "Adesso si sceglie <i>tra</i>. Metà sala aveva ventiquattro porte, l'altra metà sei: confronta il tempo e la certezza. E guarda chi ha riaperto la porta del sogno." },
  { k: "notte", eta: "23 anni", titolo: "La moneta", zona: [2, 0], nota: "Pancia e intuito. La moneta non decide niente: mentre è in aria ti fa sapere cosa speri. Quanti hanno seguito la speranza contro la moneta?" },
  { k: "oracolo", eta: "28 anni", titolo: "L'oracolo", zona: [2, 1], nota: "L'IA come strumento e come fine. Chi ha chiesto la strada è arrivato dove arrivano quasi tutti; chi ha chiesto una domanda ha tenuto la propria strada." },
  { k: "vicolo", eta: "35 anni", titolo: "Il vicolo cieco", zona: [2, 2], nota: "Il fallimento non è un valore in sé: conta cosa fai davanti al muro. I segni che vedete sono stati lasciati da questa sala: chi è passato dopo li ha trovati sulla sua strada." },
  { k: "centro", eta: "Da grande", titolo: "Il centro", zona: [1, 1], nota: "Giochi finiti e infiniti. La coppa chiude il gioco: hai vinto, è finita. Oltre la coppa il labirinto continua, e si vedono le luci di tutti gli altri." },
  { k: "fine", eta: "", titolo: "Il labirinto continua", sotto: "Grazie", zona: null },
];
const SOGNI = { luna: "andare sulla luna", animali: "curare gli animali", gol: "fare gol", ballare: "ballare", incendi: "spegnere gli incendi", scoprire: "scoprire cose nuove", dipingere: "dipingere", insegnare: "insegnare", cantare: "cantare", cucinare: "cucinare", volare: "pilotare gli aerei", misteri: "risolvere misteri", curare: "curare le persone", inventare: "inventare macchine", esplorare: "esplorare il mondo", scavare: "scavare tesori antichi" };
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
const composer = new EffectComposer(renderer); composer.addPass(new RenderPass(scena, camera));
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
  try { dati = indicizza(await LV.conteggi(liveDal)); stato("dal vivo", "vivo") } catch (e) { stato("collegamento perso", "ko") }
  disegnaDati();
}
let segniCache = [], segniT = 0;
async function prendiSegni() { if (demo) return; if (!LV.attivo || Date.now() - segniT < 6000) return; segniT = Date.now(); try { segniCache = await LV.segni(24) || [] } catch (e) { } }
function stato(t, c) { const s = $("#stato"); s.textContent = t; s.className = "stato " + c }

/* simulazione per le prove: numeri inventati, sempre dichiarati come tali */
function simula() {
  demo = !demo; $("#simulazione").hidden = !demo;
  if (!demo) { dati = {}; segniCache = []; disegnaDati(); interroga(); return }
  const n = 240, sogni = { luna: 31, animali: 24, gol: 19, ballare: 14, incendi: 9, scoprire: 22, dipingere: 11, insegnare: 13, cantare: 17, cucinare: 7, volare: 12, misteri: 8, curare: 15, inventare: 6, esplorare: 5, scavare: 4, nonlo: 23 };
  dati = { ingresso: { entrato: { 1: n } }, cameretta: { sogno: sogni },
    scuola: { gruppo: { 24: 118, 6: 113 }, porta: { s5: 14, s0: 21, sogno: 26, s21: 18, s3: 17, s8: 15, s9: 22 }, secondi: { 4: 20, 7: 30, 11: 25, 16: 30, 23: 26, 31: 22, 45: 18, 62: 11 }, sicurezza: { 1: 71, 2: 104, 3: 52 } },
    notte: { speranza: { testa: 118, croce: 104 }, esito: { testa: 109, croce: 113 }, seguito: { uguali: 104, moneta: 41, speranza: 77 } },
    oracolo: { scelta: { strada: 84, domanda: 131 } },
    vicolo: { azione: { segno: 96, spinto: 61, indietro: 52 }, spinte: { 1: 40, 2: 15, 3: 6 } },
    centro: { scelta: { coppa: 88, oltre: 117 }, continua: { 1: 79 } },
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
    $("#finiti").innerHTML = s >= 1 && s <= 6 && dentro ? `<b>${fmt(fatti)}</b> su ${fmt(Math.max(dentro, presenti))} hanno finito il capitolo` : ""; manda({ t: "finiti", testo: $("#finiti").textContent }) }
  let h = "";
  if (s === 1) {
    const so = Object.entries(D.cameretta?.sogno || {}).filter(([k]) => k !== "nonlo").sort((a, b) => b[1] - a[1]).slice(0, 5), nl = D.cameretta?.sogno?.nonlo || 0, tot = somma(D.cameretta?.sogno);
    h = `<div class="cifra"><b>${pct(nl, tot)}%</b><span>ha aperto la porta col punto interrogativo</span></div>${barre(so.map(([k, n]) => [SOGNI[k] || k, n]), so[0]?.[1] || 1)}`;
  } else if (s === 2) {
    const g = D.scuola?.gruppo || {}, sic = D.scuola?.sicurezza || {}, sec = D.scuola?.secondi || {}, porte = D.scuola?.porta || {}, tot = somma(porte);
    h = `<div class="due"><div class="cifra"><b>${Math.round(media(sec))}<small>s</small></b><span>per scegliere una porta</span></div><div class="cifra"><b>${pct(porte.sogno || 0, tot)}%</b><span>ha riaperto la porta del sogno</span></div></div>
      <div class="sotto-t">Quanta certezza, dopo</div>${barre([["Poca", sic[1] || 0], ["Abbastanza", sic[2] || 0], ["Tutta", sic[3] || 0]], Math.max(1, ...Object.values(sic)))}
      <div class="piccolo">${fmt(g[24] || 0)} persone avevano 24 porte, ${fmt(g[6] || 0)} ne avevano 6.</div>`;
  } else if (s === 3) {
    const sg = D.notte?.seguito || {}, div = (sg.moneta || 0) + (sg.speranza || 0), tot = div + (sg.uguali || 0);
    h = `<div class="cifra"><b>${pct(div, tot)}%</b><span>ha sperato il contrario di quello che è uscito</span></div>
      <div class="sotto-t">E poi, davanti al bivio</div>${barre([["ha seguito la speranza", sg.speranza || 0, "rosso"], ["ha seguito la moneta", sg.moneta || 0]], Math.max(1, sg.speranza || 0, sg.moneta || 0))}`;
  } else if (s === 4) {
    const o = D.oracolo?.scelta || {}, tot = somma(o);
    h = `<div class="due"><div class="cifra"><b>${pct(o.strada || 0, tot)}%</b><span>ha chiesto la strada</span></div><div class="cifra"><b>${pct(o.domanda || 0, tot)}%</b><span>ha voluto una domanda</span></div></div>`;
  } else if (s === 5) {
    const a = D.vicolo?.azione || {};
    h = `${barre([["ha lasciato un segno", a.segno || 0, "rosso"], ["ha spinto il muro", a.spinto || 0], ["ha girato le spalle al muro", a.indietro || 0]], Math.max(1, ...Object.values(a)))}<div class="segni">${segniCache.slice(0, 12).map(sg => `<canvas data-punti='${typeof sg.punti === "string" ? sg.punti.replace(/'/g, "") : JSON.stringify(sg.punti)}' width="160" height="120"></canvas>`).join("")}</div>`;
  } else if (s === 6) {
    const c = D.centro?.scelta || {}, tot = somma(c), cont = somma(D.centro?.continua);
    h = `<div class="due"><div class="cifra"><b>${pct(c.coppa || 0, tot)}%</b><span>ha preso la coppa</span></div><div class="cifra"><b>${pct(c.oltre || 0, tot)}%</b><span>ha superato la coppa</span></div></div><div class="piccolo">Di chi ha preso la coppa, ${fmt(cont)} ${cont === 1 ? "ha" : "hanno"} deciso di rimetterla a posto e continuare.</div>`;
  }
  if (box.dataset.s !== String(s) || box.dataset.h !== h) { box.dataset.s = s; box.dataset.h = h; box.innerHTML = h; disegnaSegni() }
  if (luci) aggiornaPersone();
}
function disegnaSegni() { $$(".segni canvas").forEach(c => { const g = c.getContext("2d"); g.fillStyle = "#1a1714"; g.fillRect(0, 0, 160, 120); let tr = []; try { tr = JSON.parse(c.dataset.punti) } catch (e) { } g.strokeStyle = "rgba(245,240,230,.9)"; g.lineWidth = 2.4; g.lineCap = "round"; for (const t of tr) { g.beginPath(); t.forEach(([x, y], i) => i ? g.lineTo(x * 1.6, y * 1.2) : g.moveTo(x * 1.6, y * 1.2)); g.stroke() } }) }

/* ---------- capitoli ---------- */
let cur = Math.max(0, Math.min(CAPITOLI.length - 1, ls.get("dg3-cap") || 0));
function vai(s, daRemoto) {
  cur = Math.max(0, Math.min(CAPITOLI.length - 1, s)); ls.set("dg3-cap", cur);
  const c = CAPITOLI[cur];
  document.body.dataset.s = cur;
  $("#eta").textContent = c.eta; $("#titolo").textContent = c.titolo; $("#sottotitolo").textContent = c.sotto || ""; $("#numero").textContent = cur >= 1 && cur <= 6 ? ["", "I", "II", "III", "IV", "V", "VI"][cur] : "";
  $("#pannello").classList.remove("entra"); void $("#pannello").offsetWidth; $("#pannello").classList.add("entra");
  if (lab) puntaA(cur);
  if (infinito) infinito.userData.k = cur === 7 ? 1 : 0;
  disegnaDati(); if (cur === 5) { segniT = 0; prendiSegni().then(disegnaDati) }
  if (!daRemoto) { manda({ t: "vai", s: cur }); sincronizza() }
  aggiornaRegia();
}
async function sincronizza() {
  const p = ls.get("dg-parola"); if (!LV.attivo || !p) return;
  try { await LV.vai(p, cur, 0); stato("dal vivo", "vivo") } catch (e) { stato(String(e.message).includes("parola") ? "parola di regia errata" : "comando non arrivato", "ko") }
}

/* ---------- regia ---------- */
function aggiornaRegia() {
  if (!REGIA) return;
  const c = CAPITOLI[cur], n = CAPITOLI[cur + 1];
  $("#r-ora").innerHTML = `<b>${cur}. ${c.titolo}</b>${c.eta ? " · " + c.eta : ""}`; $("#r-nota").innerHTML = c.nota || (cur === 0 ? "Lascia il codice sullo schermo mentre la sala entra. Quando le luci sono abbastanza, apri il primo capitolo con la freccia." : "Congedo.");
  $("#r-poi").textContent = n ? "Dopo: " + n.titolo : "";
  $$("#r-scaletta li").forEach((li, i) => li.classList.toggle("ora", i === cur));
}
if (REGIA) {
  document.body.classList.add("regia");
  $("#r-scaletta").innerHTML = CAPITOLI.map((c, i) => `<li data-i="${i}">${i}. ${c.titolo}</li>`).join("");
  $("#r-scaletta").onclick = e => { const li = e.target.closest("li"); if (li) vai(+li.dataset.i) };
  $("#r-parola").value = ls.get("dg-parola") || ""; $("#r-parola").onchange = e => { ls.set("dg-parola", e.target.value.trim()); sincronizza() };
  $("#r-avanti").onclick = () => vai(cur + 1); $("#r-indietro").onclick = () => vai(cur - 1);
  $("#r-azzera").ondblclick = () => { manda({ t: "azzera" }) };
  setInterval(() => { const d = new Date(); $("#r-orologio").textContent = d.toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit" }) }, 1000);
}
canale && (canale.onmessage = e => { const m = e.data; if (m.t === "finiti" && REGIA) $("#r-finiti").textContent = m.testo; if (m.t === "vai" && m.s !== cur) vai(m.s, true); if (m.t === "azzera" && !REGIA) { liveDal = Date.now(); ls.set("dg3-dal", liveDal); dati = {}; disegnaDati() } });

/* ---------- tasti ---------- */
addEventListener("keydown", e => {
  if (e.target.tagName === "INPUT") return;
  const k = e.key;
  if (k === "ArrowRight" || k === "PageDown" || k === " ") { e.preventDefault(); vai(cur + 1) }
  else if (k === "ArrowLeft" || k === "PageUp") { e.preventDefault(); vai(cur - 1) }
  else if (k === "x" || k === "X") simula();
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
  if (REGIA) { vai(cur, true); return }
  try { await Promise.race([Promise.all(["48px Caveat", "48px Marcellus"].map(f => document.fonts.load(f))), new Promise(r => setTimeout(r, 2000))]) } catch (e) { }
  adatta();
  lab = M.genera("palco"); mondo = await M.costruisci(scena, lab, { base: "./", env });
  for (const so of mondo.soffitti || []) so.visible = false;
  creaLuci(); creaInfinito(); vai(cur, true); vista.t.copy(vista.bersaglio); vista.r = vista.raggio; vista.a = vista.alt;
  requestAnimationFrame(ciclo);
  if (LV.attivo) { stato(ls.get("dg-parola") ? "collegamento…" : "manca la parola di regia (P)", "ko"); interroga(); setInterval(interroga, 2000); setInterval(() => { if (cur === 5) prendiSegni().then(disegnaDati) }, 6000) }
  else stato("senza collegamento", "ko");
}
avvia();
window.__palco = { vai, simula, get dati() { return dati } };
