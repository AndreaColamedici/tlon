/* Da grande · il mondo.
   Un labirinto di 27 per 27 celle diviso in nove quartieri, uno per età.
   Ogni telefono genera il suo, a partire da un seme: nessuno cammina nello stesso labirinto.
   Texture: Poly Haven, CC0. */
import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";

export const C = 2.4;          // lato della cella, in metri
export const B = 9;            // celle per lato di un quartiere
export const N = B * 3;        // celle per lato del labirinto
export const T = 0.34;         // spessore dei muri
const OFF = N * C / 2;

export const ZONE = {
  cameretta: { muro: "carta", pav: "legno", h: 2.7, colMuro: 0xffffff, colPav: 0xffffff, fog: 0x231b31, dens: .085, luce: 0xffc58a, int: 9, emi: 0x2b2340, eta: "5 anni", occhio: .95, passo: 1.35, ruv: .9 },
  scuola: { muro: "intonaco", pav: "linoleum", h: 3.6, colMuro: 0xb7cbb6, colPav: 0x9fa496, fog: 0x1a2224, dens: .065, luce: 0xe9f3ff, int: 16, emi: 0x202a2c, eta: "18 anni", occhio: 1.6, passo: 1.6, ruv: .55 },
  notte: { muro: "cemento", pav: "asfalto", h: 4.4, colMuro: 0x8d939d, colPav: 0x4a4d55, fog: 0x060912, dens: .075, luce: 0xffae66, int: 14, emi: 0x0a0e18, eta: "23 anni", occhio: 1.65, passo: 1.65, ruv: .42 },
  oracolo: { muro: "vetro", pav: "asfalto", h: 5, colMuro: 0x0b1424, colPav: 0x1a1f2a, fog: 0x050a16, dens: .055, luce: 0x86bcff, int: 14, emi: 0x0a1426, eta: "28 anni", occhio: 1.68, passo: 1.7, ruv: .12 },
  vicolo: { muro: "mattoni", pav: "ciottoli", h: 5.6, colMuro: 0xc0aa98, colPav: 0x8f8f96, fog: 0x0e1018, dens: .085, luce: 0xffa35a, int: 20, emi: 0x14161f, eta: "35 anni", occhio: 1.7, passo: 1.6, ruv: .35 },
  ritorno: { muro: "arenaria", pav: "pavimento", h: 6, colMuro: 0xd8c8b0, colPav: 0xb8a690, fog: 0x17110b, dens: .07, luce: 0xffa850, int: 20, emi: 0x1d150d, eta: "35 anni", occhio: 1.7, passo: 1.7, ruv: .8 },
  antico: { muro: "arenaria", pav: "pavimento", h: 6, colMuro: 0xd0bfa6, colPav: 0xb0a088, fog: 0x17110b, dens: .07, luce: 0xffa850, int: 18, emi: 0x1d150d, eta: "", occhio: 1.7, passo: 1.7, ruv: .8 },
  centro: { muro: "marmo", pav: "pavimento", h: 6.6, colMuro: 0xf0e2c8, colPav: 0xc9b597, fog: 0x1c1208, dens: .05, luce: 0xffb158, int: 22, emi: 0x24180b, eta: "Da grande", occhio: 1.72, passo: 1.7, ruv: .7 },
};
export const BLOCCHI = { "0,0": "cameretta", "1,0": "scuola", "2,0": "notte", "2,1": "oracolo", "2,2": "vicolo", "1,2": "ritorno", "0,2": "antico", "0,1": "antico", "1,1": "centro" };
const ORIGINE = { cameretta: [0, 0], scuola: [1, 0], notte: [2, 0], oracolo: [2, 1], vicolo: [2, 2], ritorno: [1, 2], centro: [1, 1] };
// stanze e porte, in coordinate locali al quartiere
const PIANTA = {
  cameretta: { letto: [0, 0, 2, 2], sala: [5, 3, 7, 5], uscita: [8, 4, "E"] },
  scuola: { sala: [2, 2, 6, 6], ingresso: [0, 4, "W"], uscita: [8, 4, "E"] },
  notte: { sala: [3, 3, 5, 5], ingresso: [0, 4, "W"], uscita: [4, 8, "S"] },
  oracolo: { sala: [3, 3, 5, 5], ingresso: [4, 0, "N"], uscita: [4, 8, "S"] },
  vicolo: { ingresso: [4, 0, "N"], uscita: [0, 4, "W"] },
  ritorno: { ingresso: [8, 4, "E"], uscita: [4, 0, "N"] },
  centro: { sala: [3, 3, 5, 5], ingresso: [4, 8, "S"] },
};

/* ---------- caso con seme ---------- */
export function semeDa(testo) { let h = 2166136261; for (const c of String(testo)) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619) } return h >>> 0 }
export function caso(seme) { let a = seme >>> 0; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296 } }
const mescola = (a, r) => { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1));[a[i], a[j]] = [a[j], a[i]] } return a };

/* ---------- il labirinto ---------- */
export const zonaDi = (x, z) => BLOCCHI[Math.floor(x / B) + "," + Math.floor(z / B)];
export const centroCella = (x, z, y = 0) => new THREE.Vector3((x + .5) * C - OFF, y, (z + .5) * C - OFF);

export function genera(seme) {
  const r = caso(semeDa(seme));
  const H = Array.from({ length: N + 1 }, () => new Uint8Array(N).fill(1)); // muro a nord della cella (x,z)
  const V = Array.from({ length: N }, () => new Uint8Array(N + 1).fill(1)); // muro a ovest della cella (x,z)
  const apri = (x, z, nx, nz) => { if (nx === x + 1) V[z][x + 1] = 0; else if (nx === x - 1) V[z][x] = 0; else if (nz === z + 1) H[z + 1][x] = 0; else H[z][x] = 0 };
  for (let bz = 0; bz < 3; bz++) for (let bx = 0; bx < 3; bx++) {
    const x0 = bx * B, z0 = bz * B, vis = new Set(), pila = [[x0 + Math.floor(r() * B), z0 + Math.floor(r() * B)]];
    vis.add(pila[0].join());
    while (pila.length) {
      const [x, z] = pila[pila.length - 1];
      const vicini = [[x + 1, z], [x - 1, z], [x, z + 1], [x, z - 1]].filter(([a, b]) => a >= x0 && a < x0 + B && b >= z0 && b < z0 + B && !vis.has(a + "," + b));
      if (!vicini.length) { pila.pop(); continue }
      const [a, b] = vicini[Math.floor(r() * vicini.length)]; apri(x, z, a, b); vis.add(a + "," + b); pila.push([a, b]);
    }
    // qualche anello, perché la strada più breve non sia interminabile (il vicolo resta più chiuso)
    const zona = BLOCCHI[bx + "," + bz], anelli = zona === "vicolo" ? 4 : zona === "antico" ? 6 : 11;
    for (let k = 0; k < anelli; k++) {
      const x = x0 + 1 + Math.floor(r() * (B - 2)), z = z0 + 1 + Math.floor(r() * (B - 2));
      if (r() < .5) V[z][x] = 0; else H[z][x] = 0;
    }
  }
  // stanze
  const sgombra = (zona, [a, b, c, d]) => { const [ox, oz] = ORIGINE[zona].map(v => v * B); for (let z = oz + b; z <= oz + d; z++) for (let x = ox + a; x <= ox + c; x++) { if (x > ox + a) V[z][x] = 0; if (z > oz + b) H[z][x] = 0 } };
  for (const [zona, p] of Object.entries(PIANTA)) { if (p.letto) sgombra(zona, p.letto); if (p.sala) sgombra(zona, p.sala) }
  // passaggi tra i quartieri
  const varco = (zona, [lx, lz, lato]) => { const [ox, oz] = ORIGINE[zona].map(v => v * B), x = ox + lx, z = oz + lz; if (lato === "E") V[z][x + 1] = 0; if (lato === "W") V[z][x] = 0; if (lato === "S") H[z + 1][x] = 0; if (lato === "N") H[z][x] = 0 };
  for (const [zona, p] of Object.entries(PIANTA)) { if (p.uscita) varco(zona, p.uscita); if (p.ingresso) varco(zona, p.ingresso) }
  V[22][9] = 0; H[18][4] = 0; H[9][4] = 0; // gli altri quartieri antichi, collegati tra loro: le strade non prese
  const lab = { seme, H, V };
  lab.passa = (x, z, nx, nz) => { if (nx < 0 || nz < 0 || nx >= N || nz >= N) return false; if (nx === x + 1) return !V[z][x + 1]; if (nx === x - 1) return !V[z][x]; if (nz === z + 1) return !H[z + 1][x]; return !H[z][x] };
  lab.pareti = (x, z) => [H[z][x], H[z + 1][x], V[z][x], V[z][x + 1]].reduce((s, v) => s + v, 0);
  lab.cammino = (da, a, zone) => bfs(lab, da, a, zone);
  // le stanze delle porte tengono solo i varchi della strada vera: così restano muri per tutte le porte
  const chiudi = (zona, rett, da, verso) => {
    const dentro = inRett(zona, rett), tieni = new Set();
    for (const c of [lab.cammino(da, dentro, [zona]), lab.cammino(lab.cammino(da, dentro, [zona]).at(-1), verso, [zona])])
      for (let i = 1; i < c.length; i++) { const [a, b] = c[i - 1], [x, z] = c[i]; if (dentro(a, b) !== dentro(x, z)) tieni.add([a, b, x, z].join()) }
    const [x0, z0] = glob(zona, rett[0], rett[1]), [x1, z1] = glob(zona, rett[2], rett[3]);
    const muro = (a, b, x, z) => { if (tieni.has([a, b, x, z].join()) || tieni.has([x, z, a, b].join())) return; if (x === a + 1) V[b][x] = 1; else if (x === a - 1) V[b][a] = 1; else if (z === b + 1) H[z][a] = 1; else H[b][a] = 1 };
    for (let x = x0; x <= x1; x++) { muro(x, z0, x, z0 - 1); muro(x, z1, x, z1 + 1) }
    for (let z = z0; z <= z1; z++) { muro(x0, z, x0 - 1, z); muro(x1, z, x1 + 1, z) }
  };
  chiudi("cameretta", PIANTA.cameretta.sala, glob("cameretta", 1, 1), glob("cameretta", ...PIANTA.cameretta.uscita));
  chiudi("scuola", PIANTA.scuola.sala, glob("scuola", ...PIANTA.scuola.ingresso), glob("scuola", ...PIANTA.scuola.uscita));
  lab.percorsi = percorsi(lab, r);
  return lab;
}

function bfs(lab, [sx, sz], meta, zone) {
  const fine = typeof meta === "function" ? meta : (x, z) => x === meta[0] && z === meta[1];
  const prima = new Map([[sx + "," + sz, null]]), coda = [[sx, sz]];
  while (coda.length) {
    const [x, z] = coda.shift();
    if (fine(x, z)) { const out = []; let k = x + "," + z; while (k) { out.unshift(k.split(",").map(Number)); k = prima.get(k) } return out }
    for (const [a, b] of [[x + 1, z], [x - 1, z], [x, z + 1], [x, z - 1]]) {
      const k = a + "," + b; if (prima.has(k) || !lab.passa(x, z, a, b)) continue;
      if (zone && !zone.includes(zonaDi(a, b))) continue;
      prima.set(k, x + "," + z); coda.push([a, b]);
    }
  }
  return [[sx, sz]];
}
const glob = (zona, lx, lz) => [ORIGINE[zona][0] * B + lx, ORIGINE[zona][1] * B + lz];
const inRett = (zona, rett) => { const [a, b] = glob(zona, rett[0], rett[1]), [c, d] = glob(zona, rett[2], rett[3]); return (x, z) => x >= a && x <= c && z >= b && z <= d };
const centroRett = (zona, rett) => { const [a, b] = glob(zona, rett[0], rett[1]), [c, d] = glob(zona, rett[2], rett[3]); return new THREE.Vector3(((a + c + 1) / 2) * C - OFF, 0, ((b + d + 1) / 2) * C - OFF) };

/* i sei capitoli: dove si arriva, dove si sceglie, dove si aspetta */
function percorsi(lab) {
  const P = {}, Z = (...z) => z;
  const u = z => glob(z, ...PIANTA[z].uscita), i = z => glob(z, ...PIANTA[z].ingresso);
  // 1. cameretta: dal letto alla stanza delle porte
  const letto = glob("cameretta", 1, 1);
  P.cameretta = { andata: lab.cammino(letto, inRett("cameretta", PIANTA.cameretta.sala), Z("cameretta")), sala: centroRett("cameretta", PIANTA.cameretta.sala), rett: PIANTA.cameretta.sala };
  P.cameretta.ritorno = lab.cammino(P.cameretta.andata.at(-1), u("cameretta"), Z("cameretta"));
  for (const z of ["scuola", "notte", "oracolo"]) {
    const a = lab.cammino(i(z), inRett(z, PIANTA[z].sala), Z(z));
    P[z] = { andata: a, sala: centroRett(z, PIANTA[z].sala), rett: PIANTA[z].sala };
    P[z].ritorno = lab.cammino(a.at(-1), u(z), Z(z));
  }
  // 5. vicolo: si finisce in un vicolo cieco, poi si torna indietro e si esce dal quartiere antico
  const e = i("vicolo"), uscV = u("vicolo"), dritto = new Set(lab.cammino(e, uscV, Z("vicolo")).map(c => c.join()));
  const dist = new Map([[e.join(), 0]]), coda = [e];
  while (coda.length) { const [x, z] = coda.shift(); for (const [a, b] of [[x + 1, z], [x - 1, z], [x, z + 1], [x, z - 1]]) { if (dist.has(a + "," + b) || !lab.passa(x, z, a, b) || zonaDi(a, b) !== "vicolo") continue; dist.set(a + "," + b, dist.get(x + "," + z) + 1); coda.push([a, b]) } }
  let cieco = null, voto = -1e9;
  for (const [k, d] of dist) { const [x, z] = k.split(",").map(Number); if (lab.pareti(x, z) !== 3 || dritto.has(k)) continue; const v = -Math.abs(d - 9); if (v > voto) { voto = v; cieco = [x, z] } }
  if (!cieco) cieco = [...dist.entries()].sort((a, b) => b[1] - a[1])[0][0].split(",").map(Number);
  P.vicolo = { andata: lab.cammino(e, cieco, Z("vicolo")), cieco };
  const fuori = lab.cammino(cieco, uscV, Z("vicolo")), oltre = lab.cammino(i("ritorno"), u("ritorno"), Z("ritorno"));
  P.vicolo.ritorno = fuori.concat(oltre);
  // 6. centro
  P.centro = { andata: lab.cammino(glob("centro", ...PIANTA.centro.ingresso), inRett("centro", PIANTA.centro.sala), Z("centro")), sala: centroRett("centro", PIANTA.centro.sala), rett: PIANTA.centro.sala };
  return P;
}

/* ---------- texture ---------- */
const caricatore = new THREE.TextureLoader();
const cacheTex = {};
export function tex(base, nome, colore = true) {
  const k = nome + colore; if (cacheTex[k]) return cacheTex[k];
  const t = caricatore.load(base + "tex/" + nome + ".jpg"); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8;
  if (colore) t.colorSpace = THREE.SRGBColorSpace; return cacheTex[k] = t;
}
export function tela(w, h, disegna) {
  const c = document.createElement("canvas"); c.width = w; c.height = h; const g = c.getContext("2d"); disegna(g, w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.userData.canvas = c; return t;
}
/* scrittura a pastello */
export function pastello(g, testo, x, y, size, col, r = Math.random) {
  g.save(); g.font = `${size}px Caveat, "Comic Sans MS", cursive`; g.textAlign = "center"; g.textBaseline = "middle"; g.fillStyle = col;
  for (let i = 0; i < 7; i++) { g.globalAlpha = .22 + r() * .18; g.fillText(testo, x + (r() - .5) * size * .05, y + (r() - .5) * size * .05) }
  g.globalCompositeOperation = "destination-out"; g.globalAlpha = 1;
  for (let i = 0; i < size * 6; i++) { g.fillRect(x - size * testo.length * .3 + r() * size * testo.length * .6, y - size * .5 + r() * size, 1.4, 1.4) }
  g.restore();
}
export function tratto(g, punti, col, larg, r = Math.random) {
  g.save(); g.strokeStyle = col; g.lineCap = "round"; g.lineJoin = "round";
  for (let p = 0; p < 3; p++) { g.globalAlpha = .45; g.lineWidth = larg * (.7 + r() * .5); g.beginPath(); punti.forEach(([x, y], i) => { const a = x + (r() - .5) * larg * .6, b = y + (r() - .5) * larg * .6; i ? g.lineTo(a, b) : g.moveTo(a, b) }); g.stroke() }
  g.restore();
}
function cartaDaParati(r) {
  return tela(512, 512, (g, w, h) => {
    g.fillStyle = "#c9b8e6"; g.fillRect(0, 0, w, h);
    for (let x = 0; x < w; x += 128) { g.fillStyle = "rgba(255,255,255,.28)"; g.fillRect(x, 0, 52, h); g.fillStyle = "rgba(120,90,170,.18)"; g.fillRect(x + 56, 0, 6, h) }
    const stella = (x, y, s, c) => { g.fillStyle = c; g.beginPath(); for (let i = 0; i < 10; i++) { const a = i * Math.PI / 5 - Math.PI / 2, q = i % 2 ? s * .45 : s; g.lineTo(x + Math.cos(a) * q, y + Math.sin(a) * q) } g.fill() };
    for (let i = 0; i < 16; i++) { const x = (i % 4) * 128 + 26 + (Math.floor(i / 4) % 2) * 64, y = Math.floor(i / 4) * 128 + 40; stella(x, y, 20, ["#f6df7a", "#ffffff", "#f39aa6", "#8fd3bd"][i % 4]); g.fillStyle = "rgba(255,255,255,.7)"; g.beginPath(); g.arc(x + 40, y + 52, 5, 0, 7); g.fill() }
    for (let i = 0; i < 2600; i++) { g.fillStyle = `rgba(80,60,110,${r() * .07})`; g.fillRect(r() * w, r() * h, 2, 2) }
    g.fillStyle = "rgba(255,250,240,.9)"; g.fillRect(0, h - 70, w, 70); g.fillStyle = "rgba(120,90,170,.35)"; g.fillRect(0, h - 74, w, 6);
  });
}
/* ---------- geometrie ---------- */
function scatola(w, h, d, tile, ou = 0, ov = 0) {
  const g = new THREE.BoxGeometry(w, h, d), uv = g.attributes.uv;
  const dim = [[d, h], [d, h], [w, d], [w, d], [w, h], [w, h]];
  for (let f = 0; f < 6; f++) for (let i = 0; i < 4; i++) { const k = f * 4 + i; uv.setXY(k, uv.getX(k) * dim[f][0] / tile + ou, uv.getY(k) * dim[f][1] / tile + ov) }
  return g;
}
function altezzaTra(...zone) { return Math.max(...zone.filter(Boolean).map(z => ZONE[z].h)) }

/* ---------- costruzione ---------- */
export async function costruisci(scena, lab, { base = "../", qualita = 1, env } = {}) {
  const r = caso(semeDa(lab.seme + "arredi"));
  const mondo = { gruppi: {}, ancore: [], anima: [], porte: [], decalchi: [], muriZona: {}, materiali: {} };
  // materiali
  const M = {};
  const ombra = m => { m.onBeforeCompile = sh => {
      sh.vertexShader = sh.vertexShader.replace("#include <common>", "#include <common>\nvarying float vY;").replace("#include <begin_vertex>", "#include <begin_vertex>\nvY = (modelMatrix * vec4(transformed, 1.0)).y;");
      sh.fragmentShader = sh.fragmentShader.replace("#include <common>", "#include <common>\nvarying float vY;").replace("#include <lights_fragment_end>", "#include <lights_fragment_end>\nfloat ao = smoothstep(0.0, 1.1, vY);\nreflectedLight.indirectDiffuse *= mix(.25, 1., ao);\nreflectedLight.directDiffuse *= mix(.5, 1., smoothstep(0.0, .5, vY));");
    }; return m };
  mondo.ombra = ombra;
  const mat = (zona) => {
    const Z = ZONE[zona]; if (M[zona]) return M[zona];
    let muro;
    if (Z.muro === "vetro") muro = new THREE.MeshStandardMaterial({ color: Z.colMuro, metalness: .85, roughness: .16, envMap: env, envMapIntensity: .9 });
    else if (Z.muro === "carta") muro = new THREE.MeshStandardMaterial({ map: cartaDaParati(r), normalMap: tex(base, "intonaco_n", false), normalScale: new THREE.Vector2(.6, .6), roughness: .92 });
    else muro = new THREE.MeshStandardMaterial({ color: Z.colMuro, map: tex(base, Z.muro + "_c"), normalMap: tex(base, Z.muro + "_n", false), roughness: .88 });
    const pav = new THREE.MeshStandardMaterial({ color: Z.colPav, map: tex(base, Z.pav + "_c"), normalMap: tex(base, Z.pav + "_n", false), roughness: Z.ruv, envMap: env, envMapIntensity: Z.ruv < .4 ? .55 : .2 });
    ombra(muro); return M[zona] = { muro, pav };
  };
  // muri, raggruppati per quartiere
  const perZona = {};
  const metti = (zona, g) => (perZona[zona] = perZona[zona] || []).push(g);
  const tileDi = z => ZONE[z].muro === "carta" ? 1.8 : ZONE[z].muro === "mattoni" ? 1.5 : 3.2;
  for (let z = 0; z <= N; z++) for (let x = 0; x < N; x++) if (lab.H[z][x]) {
    const za = z > 0 ? zonaDi(x, z - 1) : null, zb = z < N ? zonaDi(x, z) : null, zona = (za && zb) ? (ZONE[za].h >= ZONE[zb].h ? za : zb) : (za || zb), h = altezzaTra(za, zb);
    const g = scatola(C + T, h, T, tileDi(zona), x * C / tileDi(zona), 0); g.translate((x + .5) * C - OFF, h / 2, z * C - OFF); metti(zona, g);
  }
  for (let z = 0; z < N; z++) for (let x = 0; x <= N; x++) if (lab.V[z][x]) {
    const za = x > 0 ? zonaDi(x - 1, z) : null, zb = x < N ? zonaDi(x, z) : null, zona = (za && zb) ? (ZONE[za].h >= ZONE[zb].h ? za : zb) : (za || zb), h = altezzaTra(za, zb);
    const g = scatola(T, h, C + T, tileDi(zona), z * C / tileDi(zona), 0); g.translate(x * C - OFF, h / 2, (z + .5) * C - OFF); metti(zona, g);
  }
  for (const [zona, gs] of Object.entries(perZona)) {
    const m = new THREE.Mesh(mergeGeometries(gs), mat(zona).muro); m.name = "muri-" + zona; scena.add(m); mondo.muriZona[zona] = m;
  }
  // pavimenti
  for (const [k, zona] of Object.entries(BLOCCHI)) {
    const [bx, bz] = k.split(",").map(Number), lato = B * C, rep = lato / (ZONE[zona].pav === "ciottoli" ? 2.2 : 2.6);
    const g = new THREE.PlaneGeometry(lato, lato); g.rotateX(-Math.PI / 2);
    const uv = g.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * rep, uv.getY(i) * rep);
    // ombra di contatto alla base dei muri, dipinta su una tela
    const uv1 = new Float32Array(uv.count * 2); for (let i = 0; i < uv.count; i++) { uv1[i * 2] = uv.getX(i) / rep; uv1[i * 2 + 1] = uv.getY(i) / rep } g.setAttribute("uv1", new THREE.BufferAttribute(uv1, 2));
    const ao = tela(512, 512, (cx, w, h) => {
      cx.fillStyle = "#fff"; cx.fillRect(0, 0, w, h); cx.filter = "blur(9px)"; cx.strokeStyle = "#141414"; cx.lineWidth = 22; cx.lineCap = "square"; const k = w / B;
      cx.beginPath();
      for (let z = 0; z <= B; z++) for (let x = 0; x < B; x++) if (lab.H[bz * B + z][bx * B + x]) { cx.moveTo(x * k, z * k); cx.lineTo((x + 1) * k, z * k) }
      for (let z = 0; z < B; z++) for (let x = 0; x <= B; x++) if (lab.V[bz * B + z][bx * B + x]) { cx.moveTo(x * k, z * k); cx.lineTo(x * k, (z + 1) * k) }
      cx.stroke(); cx.filter = "none";
    });
    ao.colorSpace = THREE.NoColorSpace; ao.channel = 1;
    const pm = mat(zona).pav.clone(); pm.aoMap = ao; pm.aoMapIntensity = 1;
    const p = new THREE.Mesh(g, pm); p.position.set((bx + .5) * lato - OFF, 0, (bz + .5) * lato - OFF); p.name = "pav-" + zona; scena.add(p);
    // soffitti, solo dove si sta al chiuso
    if (["cameretta", "scuola", "oracolo"].includes(zona)) {
      const sg = new THREE.PlaneGeometry(lato, lato); sg.rotateX(Math.PI / 2); const su = sg.attributes.uv; for (let i = 0; i < su.count; i++) su.setXY(i, su.getX(i) * lato / 2.4, su.getY(i) * lato / 2.4);
      const sm = zona === "oracolo" ? new THREE.MeshStandardMaterial({ color: 0x060b14, metalness: .8, roughness: .2, envMap: env, envMapIntensity: .5 })
        : zona === "scuola" ? new THREE.MeshStandardMaterial({ map: tela(256, 256, (cx, w, h) => { cx.fillStyle = "#d9d6cc"; cx.fillRect(0, 0, w, h); for (let i = 0; i < 2500; i++) { cx.fillStyle = `rgba(80,70,60,${Math.random() * .25})`; cx.fillRect(Math.random() * w, Math.random() * h, 2, 2) } cx.strokeStyle = "#9a978d"; cx.lineWidth = 6; for (let i = 0; i <= 2; i++) { cx.beginPath(); cx.moveTo(i * w / 2, 0); cx.lineTo(i * w / 2, h); cx.moveTo(0, i * h / 2); cx.lineTo(w, i * h / 2); cx.stroke() } }), roughness: .95 })
        : new THREE.MeshStandardMaterial({ color: 0x5a4f78, normalMap: tex(base, "intonaco_n", false), roughness: .95 });
      const so = new THREE.Mesh(sg, sm); so.position.set(p.position.x, ZONE[zona].h, p.position.z); scena.add(so); (mondo.soffitti = mondo.soffitti || []).push(so);
    }
  }
  mondo.materiali = M;
  // fregio di Cnosso nel centro: zoccolo rosso e fascia d'ocra a spirali
  {
    const rosso = new THREE.MeshStandardMaterial({ map: tex(base, "rosso_c"), normalMap: tex(base, "rosso_n", false), color: 0xd06048, roughness: .85 });
    const spirali = tela(1024, 128, (g, w, h) => {
      g.fillStyle = "#c9953c"; g.fillRect(0, 0, w, h); g.strokeStyle = "#1d2a3a"; g.lineWidth = 7;
      for (let i = 0; i < 8; i++) { const cx = i * 128 + 64; g.beginPath(); for (let t = 0; t < 14; t += .1) { const q = 6 + t * 3.4; g.lineTo(cx + Math.cos(t) * q, h / 2 + Math.sin(t) * q) } g.stroke(); g.beginPath(); g.moveTo(cx + 50, h / 2 + 10); g.quadraticCurveTo(cx + 64, h - 10, cx + 78, h / 2 - 10); g.stroke() }
      g.fillStyle = "#1d2a3a"; g.fillRect(0, 0, w, 10); g.fillRect(0, h - 10, w, 10);
      for (let i = 0; i < 4000; i++) { g.fillStyle = `rgba(60,30,10,${Math.random() * .08})`; g.fillRect(Math.random() * w, Math.random() * h, 3, 3) }
    });
    spirali.wrapS = THREE.RepeatWrapping;
    const ocra = new THREE.MeshStandardMaterial({ map: spirali, roughness: .9 });
    const gz = [], go = [];
    const fascia = (cx, cz, lungo, lungoX) => {
      const a = scatola(lungoX ? lungo : T + .04, 1.15, lungoX ? T + .04 : lungo, 2.4); a.translate(cx, .575, cz); gz.push(a);
      const b = new THREE.BoxGeometry(lungoX ? lungo : T + .04, .5, lungoX ? T + .04 : lungo); const uv = b.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setX(i, uv.getX(i) * lungo / 2.4); b.translate(cx, 2.55, cz); go.push(b);
    };
    for (let z = 0; z <= N; z++) for (let x = 0; x < N; x++) if (lab.H[z][x] && (zonaDi(x, Math.min(z, N - 1)) === "centro" || (z > 0 && zonaDi(x, z - 1) === "centro"))) fascia((x + .5) * C - OFF, z * C - OFF, C + T, true);
    for (let z = 0; z < N; z++) for (let x = 0; x <= N; x++) if (lab.V[z][x] && (zonaDi(Math.min(x, N - 1), z) === "centro" || (x > 0 && zonaDi(x - 1, z) === "centro"))) fascia(x * C - OFF, (z + .5) * C - OFF, C + T, false);
    if (gz.length) { scena.add(new THREE.Mesh(mergeGeometries(gz), rosso)); scena.add(new THREE.Mesh(mergeGeometries(go), ocra)) }
  }
  arreda(scena, lab, mondo, r, base, env);
  return mondo;
}

/* ---------- le cose dentro il labirinto ---------- */
/* raccoglie oggetti posizionati e li disegna in un solo colpo */
function istanze(scena, geo, mat, segnaposti, contenitore) {
  if (!segnaposti.length) return null;
  const m = new THREE.InstancedMesh(geo, mat, segnaposti.length);
  segnaposti.forEach((o, i) => { o.updateMatrix(); m.setMatrixAt(i, o.matrix) });
  m.instanceMatrix.needsUpdate = true; (contenitore || scena).add(m); return m;
}
function lungoIlCammino(lab, celle, ogni, fn) { celle.forEach((c, i) => { if (i % ogni === Math.floor(ogni / 2)) fn(c, i) }) }
/* muro accanto a una cella: restituisce posizione sulla faccia interna e normale verso la cella */
export function facciaMuro(lab, x, z, lato) {
  const c = centroCella(x, z), d = C / 2 - T / 2 - .015;
  if (lato === "N" && lab.H[z][x]) return { p: c.clone().add(new THREE.Vector3(0, 0, -d)), n: new THREE.Vector3(0, 0, 1) };
  if (lato === "S" && lab.H[z + 1][x]) return { p: c.clone().add(new THREE.Vector3(0, 0, d)), n: new THREE.Vector3(0, 0, -1) };
  if (lato === "W" && lab.V[z][x]) return { p: c.clone().add(new THREE.Vector3(-d, 0, 0)), n: new THREE.Vector3(1, 0, 0) };
  if (lato === "E" && lab.V[z][x + 1]) return { p: c.clone().add(new THREE.Vector3(d, 0, 0)), n: new THREE.Vector3(-1, 0, 0) };
  return null;
}
export function sulMuro(obj, f, y) { obj.position.copy(f.p).setY(y); obj.lookAt(f.p.clone().add(f.n).setY(y)) }

function arreda(scena, lab, mondo, r, base, env) {
  const P = lab.percorsi, an = (p, zona, col, int) => mondo.ancore.push({ p, zona, col: col ?? ZONE[zona].luce, int: int ?? ZONE[zona].int });
  // --- cameretta: letto, giochi, stelle fosforescenti, disegni sui muri
  {
    const [lx, lz] = [0, 0], c0 = centroCella(lx, lz), legno = new THREE.MeshStandardMaterial({ color: 0x9a6a42, map: tex(base, "legno_c"), roughness: .7 });
    const letto = new THREE.Group();
    const telaio = new THREE.Mesh(new THREE.BoxGeometry(1.1, .35, 2.1), legno); telaio.position.y = .18; letto.add(telaio);
    const materasso = new THREE.Mesh(new THREE.BoxGeometry(1, .18, 2), new THREE.MeshStandardMaterial({ color: 0xf2efe6, roughness: 1 })); materasso.position.y = .44; letto.add(materasso);
    const coperta = new THREE.Mesh(new THREE.BoxGeometry(1.06, .08, 1.3), new THREE.MeshStandardMaterial({ map: tela(256, 256, (g, w, h) => { g.fillStyle = "#3f5f9a"; g.fillRect(0, 0, w, h); g.fillStyle = "#f2c94c"; for (let i = 0; i < 40; i++) { g.beginPath(); g.arc(Math.random() * w, Math.random() * h, 5 + Math.random() * 6, 0, 7); g.fill() } }), roughness: 1 })); coperta.position.set(0, .55, .32); letto.add(coperta);
    const cuscino = new THREE.Mesh(new THREE.BoxGeometry(.7, .14, .38), materasso.material); cuscino.position.set(0, .58, -.72); letto.add(cuscino);
    const testiera = new THREE.Mesh(new THREE.BoxGeometry(1.1, .9, .08), legno); testiera.position.set(0, .45, -1.05); letto.add(testiera);
    letto.position.copy(centroCella(0, 0)).add(new THREE.Vector3(-.3, 0, .25)); scena.add(letto);
    const lettere = ["A", "B", "C", "7", "?"], colori = ["#e2523f", "#3d7fd9", "#f2c94c", "#55b07a", "#9b6fd0"];
    lettere.forEach((L, i) => {
      const t = tela(128, 128, (g, w, h) => { g.fillStyle = colori[i]; g.fillRect(0, 0, w, h); g.strokeStyle = "rgba(0,0,0,.25)"; g.lineWidth = 8; g.strokeRect(4, 4, w - 8, h - 8); g.fillStyle = "#fff"; g.font = "bold 84px Familjen Grotesk, sans-serif"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText(L, w / 2, h / 2 + 4) });
      const cubo = new THREE.Mesh(new THREE.BoxGeometry(.22, .22, .22), new THREE.MeshStandardMaterial({ map: t, roughness: .6 }));
      cubo.position.copy(centroCella(1, 2)).add(new THREE.Vector3(-.5 + i * .27 + (r() - .5) * .1, .11 + (i === 4 ? .22 : 0), .4 + (r() - .5) * .3)); if (i === 4) cubo.position.x -= .27; cubo.rotation.y = r(); scena.add(cubo);
    });
    const palla = new THREE.Mesh(new THREE.SphereGeometry(.16, 32, 16), new THREE.MeshStandardMaterial({ map: tela(256, 128, (g, w, h) => { ["#e2523f", "#fff", "#3d7fd9", "#fff", "#f2c94c", "#fff"].forEach((c, i) => { g.fillStyle = c; g.fillRect(i * w / 6, 0, w / 6, h) }) }), roughness: .35 }));
    palla.position.copy(centroCella(2, 1)).add(new THREE.Vector3(.3, .16, -.2)); scena.add(palla);
    const lume = new THREE.Mesh(new THREE.SphereGeometry(.12, 24, 12), new THREE.MeshStandardMaterial({ color: 0xffd9a0, emissive: 0xffb060, emissiveIntensity: 3 }));
    lume.position.copy(centroCella(0, 1)).add(new THREE.Vector3(.75, .55, -.4)); scena.add(lume); an(lume.position.clone().setY(.9), "cameretta", 0xffb060, 7);
    // stelle che brillano al buio, sui muri della cameretta
    const stellaG = new THREE.ShapeGeometry((() => { const s = new THREE.Shape(); for (let i = 0; i < 10; i++) { const a = i * Math.PI / 5 - Math.PI / 2, q = i % 2 ? .035 : .08; i ? s.lineTo(Math.cos(a) * q, Math.sin(a) * q) : s.moveTo(Math.cos(a) * q, Math.sin(a) * q) } return s })());
    const stellaM = new THREE.MeshStandardMaterial({ color: 0xd8ffcf, emissive: 0xb6ff9e, emissiveIntensity: 2.2 });
    const stelle = [];
    for (let z = 0; z < B; z++) for (let x = 0; x < B; x++) for (const lato of "NSEW") { if (r() > .22) continue; const f = facciaMuro(lab, x, z, lato); if (!f) continue; const s = new THREE.Object3D(); sulMuro(s, f, 1.3 + r() * 1.2); s.position.addScaledVector(new THREE.Vector3().crossVectors(f.n, new THREE.Vector3(0, 1, 0)), (r() - .5) * 1.6); s.rotateZ(r() * 3); stelle.push(s) }
    istanze(scena, stellaG, stellaM, stelle);
    // disegni di bambino
    const soggetti = [disegnoSole, disegnoCasa, disegnoFamiglia, disegnoArcobaleno, disegnoRazzo, disegnoAlbero];
    let k = 0; const celle = P.cameretta.andata.concat(P.cameretta.ritorno);
    lungoIlCammino(lab, celle, 2, ([x, z]) => {
      for (const lato of mescola([..."NSEW"], r)) { const f = facciaMuro(lab, x, z, lato); if (!f) continue; const d = new THREE.Mesh(new THREE.PlaneGeometry(.9, .7), new THREE.MeshStandardMaterial({ map: tela(360, 280, soggetti[k++ % soggetti.length]), transparent: true, roughness: 1 })); sulMuro(d, f, .7 + r() * .4); d.userData.ingombro = { w: .9, h: .7 }; scena.add(d); break }
    });
    lungoIlCammino(lab, celle, 4, ([x, z]) => an(centroCella(x, z, 2.2), "cameretta"));
    mondo.anima.push(pulviscolo(scena, centroCella(1, 1), 3, 160, 0xffe2b0));
  }
  // --- scuola: armadietti e neon
  {
    const celle = P.scuola.andata.concat(P.scuola.ritorno), cols = [0x3b6fb6, 0xb84a3b, 0x6d7a86, 0x3f8f73];
    const facciata = tela(128, 256, (g, w, h) => { g.fillStyle = "#cfd6dc"; g.fillRect(0, 0, w, h); g.fillStyle = "rgba(0,0,0,.35)"; for (let i = 0; i < 6; i++) g.fillRect(28, 22 + i * 12, 72, 5); g.fillRect(96, 120, 10, 34); g.strokeStyle = "rgba(0,0,0,.4)"; g.lineWidth = 4; g.strokeRect(4, 4, w - 8, h - 8); for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(60,40,30,${Math.random() * .12})`; g.fillRect(Math.random() * w, Math.random() * h, 2, 2) } });
    const ag = new THREE.BoxGeometry(.5, 1.85, .42), am = cols.map(c => new THREE.MeshStandardMaterial({ color: c, map: facciata, metalness: .55, roughness: .45, envMap: env, envMapIntensity: .5 }));
    const banchi = cols.map(() => []);
    celle.forEach(([x, z], i) => {
      if (i < 1 || i > celle.length - 2) return;
      for (const lato of "NSEW") {
        const f = facciaMuro(lab, x, z, lato); if (!f || r() < .35) continue;
        const k0 = Math.floor(r() * cols.length);
        for (let k = -1; k <= 1; k++) { const a = new THREE.Object3D(); sulMuro(a, f, .925); a.position.addScaledVector(f.n, .21).addScaledVector(new THREE.Vector3().crossVectors(f.n, new THREE.Vector3(0, 1, 0)), k * .52); banchi[k0].push(a) }
      }
    });
    banchi.forEach((b, i) => istanze(scena, ag, am[i], b));
    const tubo = new THREE.BoxGeometry(.08, .05, 1.3), neon = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xe6f2ff, emissiveIntensity: 4 });
    lungoIlCammino(lab, celle, 3, ([x, z], i) => {
      const p = centroCella(x, z, ZONE.scuola.h - .25), m = new THREE.Mesh(tubo, neon.clone()); m.position.copy(p); m.rotation.y = r() < .5 ? 0 : Math.PI / 2; scena.add(m);
      const tremula = r() < .3; if (tremula) mondo.anima.push(t => { const on = Math.sin(t * 23 + i) > -.6 || Math.sin(t * 3.1 + i) > .2; m.material.emissiveIntensity = on ? 4 : .2 });
      an(p.clone().setY(ZONE.scuola.h - .5), "scuola");
    });
    const sala = P.scuola.sala; an(sala.clone().setY(3.1), "scuola", 0xe9f3ff, 26);
    for (const [dx, dz] of [[-3, -3], [3, -3], [-3, 3], [3, 3], [0, 0]]) { const m = new THREE.Mesh(tubo, neon); m.position.copy(sala).add(new THREE.Vector3(dx, ZONE.scuola.h - .25, dz)); scena.add(m) }
  }
  // --- notte: finestre accese in alto, lampioni
  {
    const pannello = new THREE.PlaneGeometry(.46, .64), cols = [0xffc27a, 0xffe2b0, 0x9fc4ff, 0xff9f60];
    const vetri = tela(128, 180, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, "#fff"); gr.addColorStop(1, "#8a7a6a"); g.fillStyle = gr; g.fillRect(0, 0, w, h); g.fillStyle = "#1a1612"; g.fillRect(0, 0, w, 10); g.fillRect(0, h - 10, w, 10); g.fillRect(0, 0, 10, h); g.fillRect(w - 10, 0, 10, h); g.fillRect(w / 2 - 4, 0, 8, h); g.fillRect(0, h * .45, w, 7); g.fillStyle = "rgba(60,30,20,.55)"; g.fillRect(10, 10, 30, h - 20); g.fillRect(w - 40, 10, 30, h - 20) });
    const finestre = cols.map(c => new THREE.MeshStandardMaterial({ color: 0x000000, emissive: c, emissiveMap: vetri, emissiveIntensity: .75 }));
    const buie = new THREE.MeshStandardMaterial({ color: 0x0a0d14, roughness: .2, metalness: .6 });
    const fin = [[], [], [], [], []];
    for (let z = 0; z < B; z++) for (let x = 18; x < 27; x++) for (const lato of "NSEW") {
      const f = facciaMuro(lab, x, z, lato); if (!f) continue;
      for (let y = 2.9; y < ZONE.notte.h - .4; y += 1.0) for (const s of [-.6, .6]) { const w = new THREE.Object3D(); sulMuro(w, f, y); w.position.addScaledVector(new THREE.Vector3().crossVectors(f.n, new THREE.Vector3(0, 1, 0)), s); fin[r() < .3 ? Math.floor(r() * 4) : 4].push(w) }
    }
    fin.forEach((l, i) => istanze(scena, pannello, i < 4 ? finestre[i] : buie, l));
    const celle = P.notte.andata.concat(P.notte.ritorno), testa = new THREE.Mesh(new THREE.SphereGeometry(.13, 16, 8), new THREE.MeshStandardMaterial({ color: 0xffe0b0, emissive: 0xffa64d, emissiveIntensity: 5 }));
    lungoIlCammino(lab, celle, 3, ([x, z]) => {
      for (const lato of "NSEW") { const f = facciaMuro(lab, x, z, lato); if (!f) continue; const l = testa.clone(); sulMuro(l, f, 3.1); l.position.addScaledVector(f.n, .25); scena.add(l); an(l.position.clone().addScaledVector(f.n, .3), "notte"); break }
    });
    an(P.notte.sala.clone().setY(3), "notte", 0xffae66, 10);
  }
  // --- oracolo: schermi che scorrono
  {
    const voci = ["Ti potrebbe interessare", "Percorso consigliato per te", "Chi ha scelto come te ha scelto anche", "Il 73% delle persone come te", "Continua da dove eri rimasto", "La strada più veloce", "Nuovo per te", "Perché hai scelto", "Altri hanno guardato anche", "Sei a 4 passi dalla meta", "Basato sulle tue scelte", "Più votato"];
    const larg = 256, alt = 1024, cnv = document.createElement("canvas"); cnv.width = larg; cnv.height = alt; const g = cnv.getContext("2d");
    const st = new THREE.CanvasTexture(cnv); st.colorSpace = THREE.SRGBColorSpace;
    let scorre = 0, ultimo = 0;
    const disegnaSchermo = () => {
      g.fillStyle = "#04101f"; g.fillRect(0, 0, larg, alt);
      for (let i = -1; i < 12; i++) {
        const y = i * 96 - (scorre % 96); g.fillStyle = "rgba(127,184,217,.12)"; g.fillRect(14, y + 8, larg - 28, 80);
        g.fillStyle = "#7fb8d9"; g.fillRect(26, y + 22, 34, 34);
        g.fillStyle = "#dceaff"; g.font = "600 14px Familjen Grotesk, sans-serif"; const v = voci[(i + Math.floor(scorre / 96) + 1200) % voci.length]; g.fillText(v, 72, y + 36, larg - 92);
        g.fillStyle = "rgba(220,234,255,.45)"; g.fillRect(72, y + 50, 120 + ((i * 37) % 50), 6);
      }
      st.needsUpdate = true;
    };
    disegnaSchermo();
    const sm = new THREE.MeshStandardMaterial({ color: 0x000000, emissive: 0xffffff, emissiveMap: st, emissiveIntensity: 1.25 });
    const pg = new THREE.PlaneGeometry(1.1, 4.3), schermi = new THREE.Group(); scena.add(schermi); mondo.schermi = schermi;
    const ss = [];
    for (let z = 9; z < 18; z++) for (let x = 18; x < 27; x++) for (const lato of "NSEW") { if (r() < .55) continue; const f = facciaMuro(lab, x, z, lato); if (!f) continue; const s = new THREE.Object3D(); sulMuro(s, f, 2.4); s.position.addScaledVector(f.n, .01); ss.push(s) }
    istanze(scena, pg, sm, ss, schermi);
    mondo.anima.push(t => { scorre = t * 38; if (t - ultimo > .09) { ultimo = t; disegnaSchermo() } });
    const celle = P.oracolo.andata.concat(P.oracolo.ritorno); lungoIlCammino(lab, celle, 3, ([x, z]) => an(centroCella(x, z, 2.6), "oracolo", 0x5b8fd8, 9));
    // la sfera
    const sfera = new THREE.Mesh(new THREE.IcosahedronGeometry(.55, 24), new THREE.ShaderMaterial({
      uniforms: { t: { value: 0 }, forza: { value: .62 } }, transparent: true,
      vertexShader: `uniform float t;varying vec3 vN;varying vec3 vV;varying vec3 vP;
        void main(){vec3 p=position;float n=sin(p.x*7.+t*1.7)*sin(p.y*6.+t*1.3)*sin(p.z*8.+t*1.1);p+=normal*n*.05;vP=p;
        vec4 mv=modelViewMatrix*vec4(p,1.);vN=normalize(normalMatrix*normal);vV=normalize(-mv.xyz);gl_Position=projectionMatrix*mv;}`,
      fragmentShader: `uniform float t;uniform float forza;varying vec3 vN;varying vec3 vV;varying vec3 vP;
        void main(){float f=pow(1.-max(dot(vN,vV),0.),2.2);float b=.5+.5*sin(vP.y*18.-t*3.+sin(vP.x*9.+t));
        vec3 c=mix(vec3(.25,.55,1.),vec3(.95,.98,1.),f)*(1.2+b*.6);gl_FragColor=vec4(c*forza,.45+f*.55);}`
    }));
    sfera.position.copy(P.oracolo.sala).setY(2.2); scena.add(sfera); mondo.sfera = sfera; mondo.sferaY = 2.2;
    const anello = new THREE.Mesh(new THREE.TorusGeometry(.95, .012, 8, 96), new THREE.MeshBasicMaterial({ color: 0xbfe0ff })); anello.position.copy(sfera.position); scena.add(anello);
    mondo.anima.push(t => { sfera.material.uniforms.t.value = t; sfera.position.y = mondo.sferaY + Math.sin(t * .9) * .08; anello.rotation.set(t * .3, t * .5, 0); anello.position.y = sfera.position.y });
    an(sfera.position.clone(), "oracolo", 0x9cc8ff, 30);
  }
  // --- vicolo: lanterne
  {
    const celle = P.vicolo.andata.concat(P.vicolo.ritorno.filter(([x, z]) => zonaDi(x, z) === "vicolo"));
    const corpo = new THREE.Mesh(new THREE.BoxGeometry(.22, .34, .22), new THREE.MeshStandardMaterial({ color: 0x111111, metalness: .7, roughness: .4 }));
    const vetro = new THREE.Mesh(new THREE.BoxGeometry(.16, .24, .16), new THREE.MeshStandardMaterial({ color: 0xffd9a0, emissive: 0xff9a40, emissiveIntensity: 4 }));
    lungoIlCammino(lab, celle, 3, ([x, z]) => {
      for (const lato of "NSEW") { const f = facciaMuro(lab, x, z, lato); if (!f) continue; const g = new THREE.Group(); g.add(corpo.clone()); g.add(vetro.clone()); sulMuro(g, f, 3); g.position.addScaledVector(f.n, .2); scena.add(g); an(g.position.clone().addScaledVector(f.n, .25), "vicolo"); break }
    });
  }
  // --- ritorno, antico e centro: torce
  {
    const fiamma = tela(64, 128, (g, w, h) => { const gr = g.createRadialGradient(w / 2, h * .68, 2, w / 2, h * .6, w * .55); gr.addColorStop(0, "rgba(255,250,220,1)"); gr.addColorStop(.35, "rgba(255,180,70,.9)"); gr.addColorStop(1, "rgba(255,80,0,0)"); g.fillStyle = gr; g.beginPath(); g.moveTo(w / 2, 4); g.quadraticCurveTo(w, h * .7, w / 2, h - 6); g.quadraticCurveTo(0, h * .7, w / 2, 4); g.fill() });
    const fm = new THREE.SpriteMaterial({ map: fiamma, color: 0xffffff, blending: THREE.AdditiveBlending, depthWrite: false });
    const sost = new THREE.Mesh(new THREE.CylinderGeometry(.05, .03, .45, 8), new THREE.MeshStandardMaterial({ color: 0x2b1d12, roughness: .9 }));
    const torcia = (f, y, zona) => {
      const g = new THREE.Group(); g.userData.torcia = true; const s = sost.clone(); s.rotation.x = .35; g.add(s); const sp = new THREE.Sprite(fm); sp.scale.set(.32, .62, 1); sp.position.set(0, .4, .08); g.add(sp);
      sulMuro(g, f, y); g.position.addScaledVector(f.n, .12); scena.add(g); const o = r() * 10;
      mondo.anima.push(t => { const k = 1 + Math.sin(t * 13 + o) * .08 + Math.sin(t * 7.3 + o) * .06; sp.scale.set(.32 * k, .62 * (2 - k), 1) });
      an(g.position.clone().addScaledVector(f.n, .35).setY(y + .4), zona, null, null);
    };
    const celle = P.vicolo.ritorno.filter(([x, z]) => zonaDi(x, z) === "ritorno").concat(P.centro.andata);
    lungoIlCammino(lab, celle, 3, ([x, z]) => { for (const lato of "NSEW") { const f = facciaMuro(lab, x, z, lato); if (!f) continue; torcia(f, 1.9, zonaDi(x, z)); break } });
    // la sala del centro
    const s = P.centro.sala, [a, b, c, d] = P.centro.rett;
    for (let z = 9 + b; z <= 9 + d; z++) for (let x = 9 + a; x <= 9 + c; x++) for (const lato of "NSEW") { const f = facciaMuro(lab, x, z, lato); if (f && (x + z) % 2 === 0) torcia(f, 2.1, "centro") }
    // piedistallo e coppa
    const pietra = new THREE.MeshStandardMaterial({ map: tex(base, "marmo_c"), normalMap: tex(base, "marmo_n", false), color: 0xf0e4cc, roughness: .6 });
    const ped = new THREE.Mesh(new THREE.CylinderGeometry(.42, .5, 1.05, 48), pietra); ped.position.copy(s).setY(.525); scena.add(ped);
    const scritta = new THREE.Mesh(new THREE.PlaneGeometry(.62, .16), new THREE.MeshStandardMaterial({ map: tela(512, 128, (g, w, h) => { g.clearRect(0, 0, w, h); g.fillStyle = "#e8c06a"; g.font = "600 70px Marcellus, serif"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText("HAI VINTO", w / 2, h / 2 + 4) }), transparent: true, metalness: .8, roughness: .3, envMap: env, emissive: 0x6a4a10, emissiveIntensity: .6 }));
    mondo.scrittaCoppa = scritta; scena.add(scritta);
    const profilo = [[0, 0], [.13, 0], [.13, .02], [.04, .05], [.035, .18], [.06, .22], [.15, .3], [.19, .42], [.2, .52], [.185, .52], [.17, .43], [.13, .32], [.05, .24], [0, .24]].map(([x, y]) => new THREE.Vector2(x, y));
    const oro = new THREE.MeshStandardMaterial({ color: 0xf2c25a, metalness: 1, roughness: .22, envMap: env, envMapIntensity: 1.6, emissive: 0x3a2400, emissiveIntensity: .4 });
    const coppa = new THREE.Group(); coppa.add(new THREE.Mesh(new THREE.LatheGeometry(profilo, 64), oro));
    for (const sgn of [-1, 1]) { const m = new THREE.Mesh(new THREE.TorusGeometry(.08, .015, 12, 32, Math.PI * 1.2), oro); m.position.set(sgn * .2, .36, 0); m.rotation.z = sgn > 0 ? -Math.PI * .6 : Math.PI * .4 + Math.PI; coppa.add(m) }
    coppa.position.copy(s).setY(1.05); scena.add(coppa); mondo.coppa = coppa; mondo.piedistallo = ped;
    // fascio di luce dall'alto
    const fascio = new THREE.Mesh(new THREE.CylinderGeometry(.35, 1.4, 9, 48, 1, true), new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, uniforms: { t: { value: 0 } },
      vertexShader: `varying vec2 vU;void main(){vU=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
      fragmentShader: `uniform float t;varying vec2 vU;void main(){float a=pow(vU.y,1.6)*.22*(.85+.15*sin(vU.x*40.+t));gl_FragColor=vec4(1.,.82,.5,a);}` }));
    fascio.position.copy(s).setY(4.5); scena.add(fascio); mondo.anima.push(t => fascio.material.uniforms.t.value = t);
    an(s.clone().setY(3.4), "centro", 0xffc070, 40);
    mondo.anima.push(pulviscolo(scena, s, 2.2, 260, 0xffd28a));
  }
}

export function pulviscolo(scena, centro, raggio, quanti, colore) {
  const p = new Float32Array(quanti * 3); for (let i = 0; i < quanti; i++) p.set([centro.x + (Math.random() - .5) * raggio * 2, Math.random() * 3.2, centro.z + (Math.random() - .5) * raggio * 2], i * 3);
  const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(p, 3));
  const punto = tela(32, 32, (c, w, h) => { const gr = c.createRadialGradient(16, 16, 0, 16, 16, 16); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(.4, "rgba(255,255,255,.35)"); gr.addColorStop(1, "rgba(255,255,255,0)"); c.fillStyle = gr; c.fillRect(0, 0, w, h) });
  const m = new THREE.Points(g, new THREE.PointsMaterial({ color: colore, map: punto, size: .045, transparent: true, opacity: .55, depthWrite: false, blending: THREE.AdditiveBlending }));
  scena.add(m); return t => { const a = g.attributes.position; for (let i = 0; i < quanti; i++) { a.array[i * 3 + 1] += Math.sin(t * .5 + i) * .0009; a.array[i * 3] += Math.cos(t * .3 + i * 1.7) * .0007 } a.needsUpdate = true };
}

/* ---------- disegni a pastello ---------- */
function disegnoSole(g, w, h) { const r = Math.random; const cx = w * .5, cy = h * .45; tratto(g, Array.from({ length: 40 }, (_, i) => [cx + Math.cos(i / 6) * 50, cy + Math.sin(i / 6) * 50]), "#f2b632", 14); for (let i = 0; i < 12; i++) { const a = i / 12 * 6.28; tratto(g, [[cx + Math.cos(a) * 70, cy + Math.sin(a) * 70], [cx + Math.cos(a) * 112, cy + Math.sin(a) * 112]], "#f29a32", 9) } tratto(g, [[cx - 18, cy - 10], [cx - 16, cy - 6]], "#4a2c14", 10); tratto(g, [[cx + 16, cy - 10], [cx + 18, cy - 6]], "#4a2c14", 10); tratto(g, Array.from({ length: 10 }, (_, i) => [cx - 22 + i * 5, cy + 16 + Math.sin(i / 3) * 8]), "#c0392b", 7) }
function disegnoCasa(g, w, h) { tratto(g, [[90, 250], [90, 140], [270, 140], [270, 250], [90, 250]], "#c0392b", 10); tratto(g, [[70, 145], [180, 50], [290, 145]], "#7b4a2a", 12); tratto(g, [[160, 250], [160, 190], [200, 190], [200, 250]], "#2d5a8c", 9); tratto(g, [[110, 165], [145, 165], [145, 195], [110, 195], [110, 165]], "#2d8c5a", 7); tratto(g, [[10, 262], [350, 266]], "#3c9a3c", 14) }
function disegnoFamiglia(g, w, h) { const omino = (x, s, c) => { tratto(g, Array.from({ length: 24 }, (_, i) => [x + Math.cos(i / 3.6) * 18 * s, 90 + Math.sin(i / 3.6) * 18 * s]), c, 7); tratto(g, [[x, 90 + 18 * s], [x, 90 + 90 * s]], c, 7); tratto(g, [[x - 34 * s, 90 + 45 * s], [x + 34 * s, 90 + 45 * s]], c, 7); tratto(g, [[x - 26 * s, 90 + 140 * s], [x, 90 + 90 * s], [x + 26 * s, 90 + 140 * s]], c, 7) }; omino(80, 1.1, "#2d5a8c"); omino(180, 1.05, "#b03a6a"); omino(270, .7, "#d07a1a") }
function disegnoArcobaleno(g, w, h) { ["#e2523f", "#f29a32", "#f2d032", "#55b07a", "#3d7fd9", "#7b5bc9"].forEach((c, k) => tratto(g, Array.from({ length: 30 }, (_, i) => [180 + Math.cos(Math.PI + i / 29 * Math.PI) * (150 - k * 16), 250 + Math.sin(Math.PI + i / 29 * Math.PI) * (150 - k * 16)]), c, 13)) }
function disegnoRazzo(g, w, h) { tratto(g, [[180, 30], [215, 90], [215, 200], [145, 200], [145, 90], [180, 30]], "#8a8f99", 10); tratto(g, Array.from({ length: 20 }, (_, i) => [180 + Math.cos(i / 3.2) * 18, 120 + Math.sin(i / 3.2) * 18]), "#3d7fd9", 8); tratto(g, [[145, 170], [115, 215], [145, 200]], "#e2523f", 9); tratto(g, [[215, 170], [245, 215], [215, 200]], "#e2523f", 9); tratto(g, [[160, 205], [170, 260], [180, 215], [190, 265], [200, 205]], "#f29a32", 9); for (let i = 0; i < 6; i++) tratto(g, [[30 + i * 55, 40 + (i % 2) * 180], [34 + i * 55, 44 + (i % 2) * 180]], "#f2d032", 10) }
function disegnoAlbero(g, w, h) { tratto(g, [[170, 260], [175, 150], [190, 150], [195, 260]], "#7b4a2a", 12); for (let i = 0; i < 7; i++) tratto(g, Array.from({ length: 22 }, (_, k) => [182 + Math.cos(i) * 50 + Math.cos(k / 3.4) * 48, 110 + Math.sin(i) * 30 + Math.sin(k / 3.4) * 40]), "#3c9a3c", 10); for (let i = 0; i < 5; i++) tratto(g, [[150 + i * 18, 100 + (i % 2) * 30], [153 + i * 18, 103 + (i % 2) * 30]], "#e2523f", 12) }

/* ---------- porte ---------- */
export function postiPorta(lab, zona, rett, quante, doppie) {
  const [ox, oz] = ORIGINE[zona].map(v => v * B), [a, b, c, d] = rett, posti = [];
  for (let x = ox + a; x <= ox + c; x++) { posti.push([x, oz + b, "N"]); posti.push([x, oz + d, "S"]) }
  for (let z = oz + b; z <= oz + d; z++) { posti.push([ox + a, z, "W"]); posti.push([ox + c, z, "E"]) }
  const liberi = posti.map(([x, z, l]) => ({ x, z, l, f: facciaMuro(lab, x, z, l) })).filter(p => p.f);
  const out = [];
  for (const p of liberi) { if (doppie) { out.push({ ...p, s: -.58 }); out.push({ ...p, s: .58 }) } else out.push({ ...p, s: 0 }) }
  // distribuzione regolare: prende posti sparsi lungo il perimetro
  if (out.length <= quante) return out;
  const passo = out.length / quante; return Array.from({ length: quante }, (_, i) => out[Math.floor(i * passo)]);
}
const FACCE = {};
export function porta(scena, posto, { larg = .95, alt = 2.1, colore = 0x8a8f99, etichetta, stile = "targa", env, r = Math.random }) {
  const g = new THREE.Group(), f = posto.f, lat = new THREE.Vector3().crossVectors(f.n, new THREE.Vector3(0, 1, 0));
  sulMuro(g, f, 0); g.position.addScaledVector(lat, posto.s);
  const tel = new THREE.MeshStandardMaterial({ color: 0x3a3430, roughness: .6 });
  for (const [w, h, x, y] of [[.07, alt + .07, -larg / 2 - .035, (alt + .07) / 2], [.07, alt + .07, larg / 2 + .035, (alt + .07) / 2], [larg + .14, .07, 0, alt + .035]]) { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, .08), tel); m.position.set(x, y, .03); g.add(m) }
  const luce = new THREE.Mesh(new THREE.PlaneGeometry(larg, alt), new THREE.MeshBasicMaterial({ color: 0xfff6e0 })); luce.position.set(0, alt / 2, .004); luce.visible = false; g.add(luce);
  const cerniera = new THREE.Group(); cerniera.position.set(-larg / 2, 0, .025); g.add(cerniera);
  // la faccia della porta è condivisa tra porte uguali; la scritta è una targa a parte, piccola e nitida.
  // (una tela grande per ogni porta riempiva la memoria grafica dei telefoni e le porte diventavano nere)
  const chiave = stile + colore;
  const fronte = FACCE[chiave] || (FACCE[chiave] = stile === "pastello"
    ? tela(256, 512, (cx, w, h) => { cx.fillStyle = "#" + colore.toString(16).padStart(6, "0"); cx.fillRect(0, 0, w, h); for (let i = 0; i < 2500; i++) { cx.fillStyle = `rgba(255,255,255,${Math.random() * .08})`; cx.fillRect(Math.random() * w, Math.random() * h, 3, 2) } tratto(cx, [[14, 14], [w - 14, 16], [w - 16, h - 14], [16, h - 16], [14, 14]], "#2b2b2b", 9); tratto(cx, Array.from({ length: 16 }, (_, i) => [w - 52 + Math.cos(i / 2.4) * 12, h * .55 + Math.sin(i / 2.4) * 12]), "#f2d032", 9) })
    : tela(256, 512, (cx, w, h) => { cx.fillStyle = "#" + colore.toString(16).padStart(6, "0"); cx.fillRect(0, 0, w, h); cx.strokeStyle = "rgba(0,0,0,.18)"; cx.lineWidth = 6; cx.strokeRect(26, 26, w - 52, h * .42); cx.strokeRect(26, h * .5, w - 52, h * .45); for (let i = 0; i < 1500; i++) { cx.fillStyle = `rgba(0,0,0,${Math.random() * .05})`; cx.fillRect(Math.random() * w, Math.random() * h, 2, 2) } }));
  fronte.userData.condivisa = true;
  const pm = new THREE.MeshStandardMaterial({ map: fronte, roughness: .55 }), lati = new THREE.MeshStandardMaterial({ color: colore, roughness: .6 });
  const pannello = new THREE.Mesh(new THREE.BoxGeometry(larg, alt, .045), [lati, lati, lati, lati, pm, lati]); pannello.position.set(larg / 2, alt / 2, 0); cerniera.add(pannello);
  const maniglia = new THREE.Mesh(new THREE.SphereGeometry(.035, 12, 8), new THREE.MeshStandardMaterial({ color: 0xc8b070, metalness: .8, roughness: .45 })); maniglia.position.set(larg - .1, alt * .47, .05); cerniera.add(maniglia);
  let targa = null;
  if (etichetta) {
    const parole = etichetta.split(" "), righe = []; let rg = ""; const max = stile === "pastello" ? 11 : 12;
    for (const pa of parole) { if ((rg + " " + pa).trim().length > max && rg) { righe.push(rg); rg = pa } else rg = (rg + " " + pa).trim() } righe.push(rg);
    const tw = larg - .12, th = stile === "pastello" ? .36 : .3;
    const tx = tela(512, Math.round(512 * th / tw / 2) * 2, (cx, w, h) => {
      if (stile === "pastello") {
        cx.fillStyle = "rgba(255,255,255,.9)"; cx.fillRect(0, 0, w, h);
        const lung = Math.max(...righe.map(x => x.length)), sz = Math.min(h * .62, Math.floor(w * 1.6 / Math.max(5, lung)));
        righe.forEach((x, i) => pastello(cx, x, w / 2, h / 2 + (i - (righe.length - 1) / 2) * sz * .95, sz, "#1d1d1d"));
      } else {
        cx.fillStyle = "#24201c"; cx.fillRect(0, 0, w, h); cx.strokeStyle = "#8a7a5a"; cx.lineWidth = 6; cx.strokeRect(3, 3, w - 6, h - 6);
        cx.fillStyle = "#f1e6cf"; cx.textAlign = "center"; cx.textBaseline = "middle";
        let sz = righe.length > 1 ? h * .34 : h * .44; cx.font = `600 ${sz}px Familjen Grotesk, sans-serif`;
        while (Math.max(...righe.map(x => cx.measureText(x).width)) > w - 40 && sz > 20) { sz -= 2; cx.font = `600 ${sz}px Familjen Grotesk, sans-serif` }
        righe.slice(0, 2).forEach((x, i) => cx.fillText(x, w / 2, h / 2 + (i - (Math.min(2, righe.length) - 1) / 2) * sz * 1.1));
      }
    });
    targa = new THREE.Mesh(new THREE.PlaneGeometry(tw, th), new THREE.MeshStandardMaterial({ map: tx, roughness: .7 }));
    targa.position.set(0, stile === "pastello" ? alt * .17 : alt * .3, .024); pannello.add(targa);
  }
  scena.add(g);
  const P = { gruppo: g, pannello, cerniera, luce, etichetta, materiale: pm, aperta: 0,
    evidenzia(on) { pm.emissive.setHex(on ? 0x14100a : 0x000000) },
    apri(dt) { P.aperta = Math.min(1, P.aperta + dt * .7); luce.visible = true; cerniera.rotation.y = -P.aperta * 1.45 }
  };
  if (targa) targa.userData.porta = P;
  pannello.userData.porta = P;
  return P;
}
