/* Da grande · il gioco sul telefono.
   Si entra a cinque anni. Ogni capitolo si apre dal palco; senza collegamento si prosegue da soli. */
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";
import * as M from "../mondo.js";
import { decoraMuri, tabellaAltezza } from "./voci.js";

const $ = s => document.querySelector(s);
const LV = window.DGLive || { attivo: false, invia() { }, ascolta() { return () => { } }, dispositivo: "x" };
const ls = { get(k) { try { return JSON.parse(localStorage.getItem(k)) } catch (e) { return null } }, set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)) } catch (e) { } } };
const PARAM = new URLSearchParams(location.search);
const PROVA = PARAM.has("prova");
const VEL = +PARAM.get("veloce") || 1;
const LIBERO = PARAM.has("libero");      // da soli, senza aspettare il palco (prove, o dopo l'evento)    // per le prove: cammino accelerato         // per le prove: ?prova salta le attese
const SEME = PARAM.get("seme") || LV.dispositivo || String(Math.random());
const pausa = ms => new Promise(r => setTimeout(r, PROVA ? Math.min(ms, 250) : ms));
const lerp = (a, b, k) => a + (b - a) * k;
const angolo = (a, b, k) => { let d = ((b - a + Math.PI) % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2) - Math.PI; return a + d * k };

/* ---------- motore ---------- */
const tela = $("#c");
const renderer = new THREE.WebGLRenderer({ canvas: tela, antialias: false, powerPreference: "high-performance" });
let qualitaPR = Math.min(window.devicePixelRatio || 1, 1.75);
renderer.setPixelRatio(qualitaPR);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
const scena = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(74, 1, .05, 400); camera.rotation.order = "YXZ"; scena.add(camera);
const pmrem = new THREE.PMREMGenerator(renderer);
const env = pmrem.fromScene(new RoomEnvironment(), .04).texture;
scena.fog = new THREE.FogExp2(0x231b31, .08); scena.background = new THREE.Color(0x231b31);
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scena, camera));
// un pixel malformato (NaN) su alcune GPU dei telefoni, sfocato dal bagliore, può annerire mezzo schermo: lo si neutralizza prima
composer.addPass(new ShaderPass({ uniforms: { tDiffuse: { value: null } }, vertexShader: `varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
  fragmentShader: `uniform sampler2D tDiffuse;varying vec2 vUv;void main(){vec4 c=texture2D(tDiffuse,vUv);
    if(any(isnan(c.rgb))||any(isinf(c.rgb))||!(c.r==c.r)||c.r>6e4||c.g>6e4||c.b>6e4)c=vec4(0.,0.,0.,1.);gl_FragColor=vec4(min(c.rgb,vec3(64.)),c.a);}` }));
const bloom = new UnrealBloomPass(new THREE.Vector2(256, 256), .75, .5, .9); composer.addPass(bloom);
if (PARAM.has("semplice")) bloom.enabled = false; // ?semplice: senza bagliore, per i telefoni che danno problemi
composer.addPass(new OutputPass());
const finitura = new ShaderPass({
  uniforms: { tDiffuse: { value: null }, t: { value: 0 }, vign: { value: .85 }, buio: { value: 0 }, ab: { value: 1 } },
  vertexShader: `varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
  fragmentShader: `uniform sampler2D tDiffuse;uniform float t;uniform float vign;uniform float buio;uniform float ab;varying vec2 vUv;
    float h(vec2 p){return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453);}
    void main(){vec2 d=vUv-.5;float r=length(d);vec2 o=d*r*.012*ab;
    vec3 c=vec3(texture2D(tDiffuse,vUv+o).r,texture2D(tDiffuse,vUv).g,texture2D(tDiffuse,vUv-o).b);
    c*=1.-smoothstep(.3,.95,r)*vign;c*=1.-buio*smoothstep(.12,.7,r);c+=(h(vUv*937.+t)-.5)*.045;gl_FragColor=vec4(c,1.);}`
});
composer.addPass(finitura);
function adatta() { const w = innerWidth, h = innerHeight; renderer.setSize(w, h, false); composer.setSize(w, h); composer.setPixelRatio(qualitaPR); bloom.resolution.set(w * qualitaPR / 2, h * qualitaPR / 2); camera.aspect = w / h; camera.fov = w > h ? 62 : 74; camera.updateProjectionMatrix() }
addEventListener("resize", adatta); adatta();

/* luci: un piccolo gruppo di luci che segue il cammino, più una torcia per il buio */
const emisfero = new THREE.HemisphereLight(0x8070a0, 0x201810, .5); scena.add(emisfero);
const pool = Array.from({ length: 4 }, () => { const l = new THREE.PointLight(0xffffff, 0, 18, 2); scena.add(l); return { l, anc: null, cur: 0 } });
const torcia = new THREE.SpotLight(0xfff0d0, 0, 26, .42, .55, 1.6); camera.add(torcia); torcia.position.set(.15, -.1, 0); camera.add(torcia.target); torcia.target.position.set(0, -.3, -5);
let oscurita = 1; // 1 = luci normali, 0 = buio
const luceMoneta = new THREE.PointLight(0xffe0a0, 0, 2, 2); camera.add(luceMoneta); luceMoneta.position.set(0, .1, -.3);
const luna = new THREE.DirectionalLight(0xffe2b8, 0); luna.position.set(-30, 80, 20); scena.add(luna); let cielo = 0;

/* ---------- stato ---------- */
const S = { lab: null, mondo: null, cap: 0, palco: 0, scelte: ls.get("dg3-scelte") || {}, interattivi: [], onTap: null, cammino: [], live: false };
const salva = () => ls.set("dg3-scelte", S.scelte);
const invia = (stanza, k, v) => { try { LV.invia(stanza, k, v) } catch (e) { } };

/* ---------- camera ---------- */
const cam = { pos: new THREE.Vector3(), yaw: 0, yawT: 0, yawU: 0, pitchU: 0, occhio: .95, passi: 0, giro: null, script: null, gy: null };
const giroscopio = { on: false, yaw: 0, pitch: 0, roll: 0, cy: null, cp: 0 };
{
  const zee = new THREE.Vector3(0, 0, 1), eu = new THREE.Euler(), q0 = new THREE.Quaternion(), q1 = new THREE.Quaternion(-Math.sqrt(.5), 0, 0, Math.sqrt(.5)), q = new THREE.Quaternion(), e2 = new THREE.Euler();
  addEventListener("deviceorientation", ev => {
    if (ev.alpha == null) return; const d = Math.PI / 180, or = (screen.orientation && screen.orientation.angle || window.orientation || 0) * d;
    eu.set(ev.beta * d, ev.alpha * d, -ev.gamma * d, "YXZ"); q.setFromEuler(eu); q.multiply(q1); q.multiply(q0.setFromAxisAngle(zee, -or));
    e2.setFromQuaternion(q, "YXZ"); giroscopio.yaw = e2.y; giroscopio.pitch = e2.x; giroscopio.roll = e2.z;
    if (giroscopio.cy === null) { giroscopio.cy = e2.y; giroscopio.cp = e2.x } giroscopio.on = true;
  });
}
function cammina(punti, { velocita, guarda = 1.6, mira = null } = {}) {
  const pts = [cam.pos.clone().setY(0)];
  for (const p of punti) if (p.distanceTo(pts[pts.length - 1]) > .35) pts.push(p.clone().setY(0));
  if (pts.length < 2) return Promise.resolve();
  const curva = new THREE.CatmullRomCurve3(pts, false, "centripetal", .5), L = curva.getLength();
  S.cammino.push(...pts.slice(1));
  return new Promise(res => { cam.giro = { curva, L, s: 0, v: velocita, vmin: L / 26, guarda, mira, res } }); // nessun tratto dura più di 26 secondi (più le soste davanti alle voci)
}
const celle = cs => cs.map(([x, z]) => M.centroCella(x, z));
function guardaVerso(p, subito) { const d = p.clone().sub(cam.pos); cam.yawT = Math.atan2(-d.x, -d.z); if (subito) cam.yaw = cam.yawT }
function zonaQui() { const x = Math.floor((cam.pos.x + M.N * M.C / 2) / M.C), z = Math.floor((cam.pos.z + M.N * M.C / 2) / M.C); return M.zonaDi(Math.max(0, Math.min(M.N - 1, x)), Math.max(0, Math.min(M.N - 1, z))) || "cameretta" }
function animaCamera(dt, t) {
  const Z = M.ZONE[zonaQui()];
  if (cam.giro) {
    const g = cam.giro, v = Math.max(g.v || Z.passo, g.vmin || 0) * VEL * rallenta(); g.s = Math.min(g.L, g.s + v * dt);
    const p = g.curva.getPointAt(g.s / g.L), a = g.curva.getPointAt(Math.min(1, (g.s + g.guarda) / g.L));
    cam.pos.copy(p); filo.aggiungi(p); const d = g.mira ? g.mira.clone().sub(p) : a.sub(p); if (d.lengthSq() > .0004) cam.yawT = Math.atan2(-d.x, -d.z); // con una mira si cammina guardandola
    const prima = Math.sin(cam.passi); cam.passi += dt * v * 3.7; if (prima > 0 && Math.sin(cam.passi) <= 0 || prima < 0 && Math.sin(cam.passi) >= 0) suono.passo(zonaQui());
    cam.yawU *= Math.exp(-dt * 1.1); cam.pitchU *= Math.exp(-dt * 1.1);
    if (giroscopio.on) { giroscopio.cy = angolo(giroscopio.cy, giroscopio.yaw, 1 - Math.exp(-dt * .9)) }
    if (g.s >= g.L) { cam.giro = null; g.res() }
  } else cam.passi = lerp(cam.passi, Math.round(cam.passi / Math.PI) * Math.PI, 1 - Math.exp(-dt * 6));
  if (cam.script) cam.script(dt, t);
  if (cam.occhioFisso != null) cam.occhio = cam.occhioFisso; else { const passo = Math.min(.35, dt * .45); cam.occhio += Math.max(-passo, Math.min(passo, Z.occhio - cam.occhio)) }
  cam.yaw = angolo(cam.yaw, cam.yawT, 1 - Math.exp(-dt * (cam.giro ? 3.2 : 2.4)));
  const ampiezza = cam.giro ? 1 : 0, bobY = Math.abs(Math.sin(cam.passi)) * .045 * ampiezza * (cam.occhio < 1.2 ? .8 : 1), bobX = Math.sin(cam.passi) * .022 * ampiezza;
  const respiro = Math.sin(t * 1.3) * .006;
  camera.position.set(cam.pos.x + Math.cos(cam.yaw) * bobX, cam.pos.y + cam.occhio + bobY + respiro, cam.pos.z - Math.sin(cam.yaw) * bobX);
  let gy = 0, gp = 0, gr = 0;
  if (giroscopio.on && giroscopio.cy !== null) { gy = angolo(0, giroscopio.yaw - giroscopio.cy, 1); gp = Math.max(-1.2, Math.min(1.2, giroscopio.pitch - giroscopio.cp)); gr = giroscopio.roll * .25 }
  camera.rotation.set(Math.max(-1.35, Math.min(1.35, cam.pitchU + gp + (cam.pitchExtra || 0))), cam.yaw + cam.yawU + gy, gr);
}

/* le voci di un'età si scrivono sui muri quando quell'età comincia: poche tele vive alla volta */
function vociPer(...zone) { try { decoraMuri(scena, S.lab, M, S.nome, M.caso(M.semeDa(SEME + "voci" + zone[0])), zone); S.voci = []; scena.traverse(o => { if (o.userData.voce) S.voci.push(o) }) } catch (e) { console.warn(e) } }
/* si rallenta passando davanti alle voci sui muri, per avere il tempo di leggerle */
let _rall = 1, _rallT = 0;
function rallenta() {
  const t = performance.now(); if (t - _rallT < 150) return _rall; _rallT = t;
  let vicina = 9; for (const v of S.voci || []) { if (!v.parent) continue; const d = v.position.distanceTo(camera.position); if (d < vicina) vicina = d }
  const meta = vicina < 3.2 ? .5 : 1; _rall += (meta - _rall) * .35; return _rall;
}
/* tocchi e trascinamenti */
{
  let giu = null;
  tela.addEventListener("pointerdown", e => { try { suono.ctx && suono.ctx.state !== "running" && suono.ctx.resume() } catch (er) { } giu = { x: e.clientX, y: e.clientY, t: performance.now(), lx: e.clientX, ly: e.clientY }; tela.setPointerCapture(e.pointerId); if (S.disegno) S.disegno.inizia(e) });
  tela.addEventListener("pointermove", e => {
    if (!giu) return; if (S.disegno) { S.disegno.muovi(e); return }
    cam.yawU += (e.clientX - giu.lx) * .0055; cam.pitchU = Math.max(-1.1, Math.min(1.1, cam.pitchU + (e.clientY - giu.ly) * .0045)); giu.lx = e.clientX; giu.ly = e.clientY;
  });
  tela.addEventListener("pointerup", e => { if (S.disegno) S.disegno.fine(e); if (giu && Math.hypot(e.clientX - giu.x, e.clientY - giu.y) < 12 && performance.now() - giu.t < 500) tocca(e.clientX, e.clientY); giu = null });
  tela.addEventListener("pointercancel", () => { giu = null });
}
const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
function colpito(x, y) { ndc.set(x / innerWidth * 2 - 1, -(y / innerHeight) * 2 + 1); ray.setFromCamera(ndc, camera); const h = ray.intersectObjects(S.interattivi, true)[0]; return h ? (h.object.userData.porta || h.object.userData.azione || h.object.parent?.userData.azione) : null }
function tocca(x, y) { if (!S.onTap) return; const c = colpito(x, y); if (c) S.onTap(c) }
let mira = null;
/* il nome della porta che stai guardando, scritto grande sotto il mirino */
function nome(t) { const e = $("#nome"); if (e.textContent !== t) { e.textContent = t; e.classList.toggle("on", !!t) } }
function aggiornaMira() {
  if (!S.interattivi.length) { if (mira) { mira.evidenzia?.(false); mira = null } nome(""); return }
  const c = colpito(innerWidth / 2, innerHeight / 2); if (c !== mira) { mira?.evidenzia?.(false); c?.evidenzia?.(true); mira = c }
  nome(c && c.etichetta ? (c.etichetta === "?" ? "?" : c.etichetta) : "");
}

/* ---------- interfaccia ---------- */
const UI = {
  eta(t) { const e = $("#eta"); if (e.textContent === t) return; e.classList.remove("su"); void e.offsetWidth; e.textContent = t; e.classList.add("su") },
  dici(t, durata) { const s = $("#sotto"); s.innerHTML = t ? `<span>${t}</span>` : ""; s.classList.toggle("on", !!t); clearTimeout(UI._t); if (t && durata) UI._t = setTimeout(() => UI.dici(""), durata) },
  scegli(opzioni, classe = "") {
    const box = $("#scelte"); box.className = "on " + classe; box.innerHTML = "";
    const sotto = $("#sotto"); const p = new Promise(res => opzioni.forEach(([k, testo]) => { const b = document.createElement("button"); b.innerHTML = testo; b.onclick = () => { suono.tocco(); box.className = ""; box.innerHTML = ""; sotto.style.bottom = ""; res(k) }; box.appendChild(b) }));
    requestAnimationFrame(() => { sotto.style.bottom = (box.offsetHeight + 34) + "px" }); return p;
  },
  velo(colore, opacita, ms = 900) { const v = $("#velo"); v.style.transition = `opacity ${ms}ms ease`; v.style.background = colore; v.style.opacity = opacita; return pausa(ms) },
};

/* ---------- suono ---------- */
const suono = (() => {
  let ctx = null, master, riverbero, umido, rumore, zonaAtt = null; const ambienti = {};
  function avvia() {
    if (ctx) return; const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return; ctx = new AC();
    master = ctx.createGain(); master.gain.value = .9; master.connect(ctx.destination);
    riverbero = ctx.createConvolver(); const n = ctx.sampleRate * 2.6, ir = ctx.createBuffer(2, n, ctx.sampleRate);
    for (let c = 0; c < 2; c++) { const d = ir.getChannelData(c); for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / n, 3.2) }
    riverbero.buffer = ir; umido = ctx.createGain(); umido.gain.value = .25; riverbero.connect(umido); umido.connect(master);
    rumore = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate); const d = rumore.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    costruisciAmbienti();
  }
  const out = (g, wet = .4) => { g.connect(master); const s = ctx.createGain(); s.gain.value = wet; g.connect(s); s.connect(riverbero) };
  function rum(durata, filtro, freq, q, vol, wet = .3, quando = 0) {
    const t = ctx.currentTime + quando, s = ctx.createBufferSource(); s.buffer = rumore; const f = ctx.createBiquadFilter(); f.type = filtro; f.frequency.value = freq; f.Q.value = q;
    const g = ctx.createGain(); g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(vol, t + .004); g.gain.exponentialRampToValueAtTime(.0001, t + durata);
    s.connect(f); f.connect(g); out(g, wet); s.start(t, Math.random() * 1.5, durata + .05); return f;
  }
  function ton(freq, durata, vol, tipo = "sine", wet = .4, quando = 0, a = .005) {
    const t = ctx.currentTime + quando, o = ctx.createOscillator(); o.type = tipo; o.frequency.value = freq; const g = ctx.createGain();
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(vol, t + a); g.gain.exponentialRampToValueAtTime(.0001, t + durata); o.connect(g); out(g, wet); o.start(t); o.stop(t + durata + .05); return o;
  }
  const SUOLI = { cameretta: [650, 1.2, .5, .15], scuola: [1700, 2.5, .38, .35], notte: [480, .9, .55, .3], oracolo: [2600, 3, .3, .6], vicolo: [900, .8, .5, .35], ritorno: [1100, 1.4, .45, .55], antico: [1100, 1.4, .45, .55], centro: [1250, 1.6, .45, .7] };
  function costruisciAmbienti() {
    const pad = (freqs, tipo, taglio, vol) => { const g = ctx.createGain(); g.gain.value = 0; const f = ctx.createBiquadFilter(); f.type = "lowpass"; f.frequency.value = taglio; f.connect(g); out(g, .6);
      freqs.forEach((fr, i) => { const o = ctx.createOscillator(); o.type = tipo; o.frequency.value = fr; o.detune.value = (i - 1) * 6; const og = ctx.createGain(); og.gain.value = vol / freqs.length; const lfo = ctx.createOscillator(); lfo.frequency.value = .07 + i * .04; const lg = ctx.createGain(); lg.gain.value = vol / freqs.length * .5; lfo.connect(lg); lg.connect(og.gain); o.connect(og); og.connect(f); o.start(); lfo.start() }); return g };
    const fruscio = (filtro, freq, q, vol) => { const s = ctx.createBufferSource(); s.buffer = rumore; s.loop = true; const f = ctx.createBiquadFilter(); f.type = filtro; f.frequency.value = freq; f.Q.value = q; const g = ctx.createGain(); g.gain.value = vol; s.connect(f); f.connect(g); s.start(); return g };
    const mix = (...pezzi) => { const g = ctx.createGain(); g.gain.value = 0; pezzi.forEach(p => { if (p.gain && p.gain.value === 0 && p !== g) p.gain.value = 1; p.connect(g) }); g.connect(master); return g };
    ambienti.cameretta = mix(pad([174.6, 220, 261.6], "triangle", 900, .05));
    ambienti.scuola = mix(pad([100, 200, 300], "sawtooth", 420, .012), fruscio("bandpass", 3000, .6, .006));
    ambienti.notte = mix(pad([73.4, 110, 146.8], "sine", 400, .06), fruscio("lowpass", 180, .7, .05));
    ambienti.oracolo = mix(pad([392, 587.3, 880, 1174.7], "sine", 2400, .028), pad([98, 147], "sine", 300, .04));
    ambienti.vicolo = mix(fruscio("bandpass", 2400, .5, .05), fruscio("lowpass", 700, .5, .04), pad([65.4, 98], "sine", 250, .04));
    ambienti.ritorno = ambienti.antico = mix(pad([73.4, 110, 146.8, 220], "triangle", 520, .045));
    ambienti.centro = mix(pad([73.4, 110, 146.8, 220, 277.2], "triangle", 700, .05), fruscio("bandpass", 900, .4, .01));
  }
  let carillon = 0;
  return {
    avvia, get ctx() { return ctx },
    zona(z, t) {
      if (!ctx) return; if (z !== zonaAtt) { zonaAtt = z; for (const [k, g] of Object.entries(ambienti)) g.gain.setTargetAtTime(k === z || (z === "antico" && k === "ritorno") ? 1 : 0, ctx.currentTime, 1.2); const s = SUOLI[z]; umido.gain.setTargetAtTime(s ? s[3] : .3, ctx.currentTime, .8) }
      if (z === "cameretta" && t > carillon) { carillon = t + 1.8 + Math.random() * 3.5; const sc = [523.3, 587.3, 659.3, 784, 880, 1046.5]; ton(sc[Math.floor(Math.random() * sc.length)], 1.6, .035, "sine", .7) }
      if (z === "vicolo" && Math.random() < .02) ton(1800 + Math.random() * 1600, .08, .015, "sine", .5);
      if ((z === "centro" || z === "ritorno") && Math.random() < .05) rum(.03, "bandpass", 2000 + Math.random() * 3000, 2, .03, .3);
    },
    passo(z) { if (!ctx) return; const s = SUOLI[z] || SUOLI.centro; rum(.11, "bandpass", s[0] * (.85 + Math.random() * .3), s[1], s[2] * .35, s[3]); ton(70 + Math.random() * 15, .08, .08, "sine", .1) },
    tocco() { if (!ctx) return; ton(880, .25, .05, "sine", .5); ton(1320, .3, .03, "sine", .6, .03) },
    cuore(forte = 1) { if (!ctx) return; ton(55, .18, .5 * forte, "sine", .05); ton(48, .2, .38 * forte, "sine", .05, .17); try { navigator.vibrate && navigator.vibrate([40, 110, 30]) } catch (e) { } },
    moneta() { if (!ctx) return; [2793, 3729, 4700, 5900].forEach((f, i) => ton(f, .9 - i * .15, .06 / (i + 1), "sine", .5, 0, .002)) },
    cade() { if (!ctx) return;[0, .16, .27, .34].forEach((q, i) => [2793, 3729].forEach(f => ton(f * (1 - i * .01), .3, .05 / (i + 1), "sine", .5, q, .002))); try { navigator.vibrate && navigator.vibrate(60) } catch (e) { } },
    fruscia(salita = true) { if (!ctx) return; const f = rum(2.4, "bandpass", salita ? 300 : 2500, 1.2, .25, .6); f.frequency.exponentialRampToValueAtTime(salita ? 3200 : 260, ctx.currentTime + 2.2) },
    cresci() { if (!ctx) return; this.fruscia(true); [196, 293.7, 392, 587.3].forEach((f, i) => ton(f, 2.8, .05, "triangle", .8, i * .18, .4)); try { navigator.vibrate && navigator.vibrate([30, 60, 30, 60, 80]) } catch (e) { } },
    porta() { if (!ctx) return; const o = ton(140, 1.1, .05, "sawtooth", .4, 0, .05); o.frequency.exponentialRampToValueAtTime(320, ctx.currentTime + 1); rum(.5, "lowpass", 400, 1, .2, .4, .9) },
    colpo() { if (!ctx) return; ton(48, .5, .9, "sine", .3); rum(.25, "lowpass", 300, 1, .6, .4); try { navigator.vibrate && navigator.vibrate(120) } catch (e) { } },
    ticchetta() { if (!ctx) return; rum(.03, "highpass", 3500, 1, .25, .4) },
    oracolo() { if (!ctx) return; [392, 523.3, 659.3, 784].forEach((f, i) => ton(f, 3.5, .03, "sine", .9, i * .09, .6)) },
    gesso() { if (!ctx) return; rum(.06, "bandpass", 3800 + Math.random() * 800, 4, .05, .2) },
    vittoria() { if (!ctx) return; [261.6, 329.6, 392, 523.3, 659.3].forEach((f, i) => ton(f, 3.6, .06, "triangle", .9, i * .12, .02)) },
    sali() { if (!ctx) return; [73.4, 110, 146.8, 220, 293.7, 440, 587.3].forEach((f, i) => ton(f, 9, .045, "sine", .9, i * .55, 1.5)) },
    sospendi(s) { if (!ctx) return; s ? ctx.suspend() : ctx.resume() }
  };
})();
document.addEventListener("visibilitychange", () => suono.sospendi(document.hidden));

/* il filo rosso che si srotola dietro di te */
const filo = (() => {
  const MAX = 6000, pos = new Float32Array(MAX * 2 * 3), idx = [];
  for (let i = 0; i < MAX - 1; i++) { const a = i * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2) }
  const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(pos, 3)); g.setIndex(idx); g.setDrawRange(0, 0);
  const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: 0xc8231a, emissive: 0x8a0f08, emissiveIntensity: .9, roughness: .7, side: THREE.DoubleSide }));
  m.frustumCulled = false; scena.add(m);
  let n = 0, ultimo = null, salto = false; const L = .022;
  const coppia = (x, z, y) => { pos.set([x, y, z, x, y, z], n * 6); n++ };
  return {
    stacca() { salto = true; S.cammino.push(null) },
    aggiungi(p) {
      if (n >= MAX - 4) return; if (ultimo && !salto && p.distanceTo(ultimo) < .25) return;
      if (salto && ultimo) { coppia(ultimo.x, ultimo.z, -.6); coppia(p.x, p.z, -.6); ultimo = null } salto = false;
      const d = ultimo ? p.clone().sub(ultimo).setY(0).normalize() : new THREE.Vector3(0, 0, -1), lat = new THREE.Vector3(-d.z, 0, d.x).multiplyScalar(L);
      const y = .012 + (n % 7) * .0004, k = n * 6; // leggere ondulazioni del filo
      const o = Math.sin(n * .7) * .03;
      pos.set([p.x + lat.x + d.z * o, y, p.z + lat.z - d.x * o, p.x - lat.x + d.z * o, y, p.z - lat.z - d.x * o], k);
      g.attributes.position.needsUpdate = true; n++; g.setDrawRange(0, Math.max(0, (n - 1) * 6)); ultimo = p.clone();
    }
  };
})();

/* ---------- ciclo ---------- */
const orologio = new THREE.Clock(); let tAcc = 0, frames = 0, tLuci = 0, tMira = 0;
const nebbia = { col: new THREE.Color(0x231b31), dens: .08 }, tmpC = new THREE.Color();
function aggiornaLuci(dt, t) {
  const pos = camera.position, anc = S.mondo.ancore;
  if (t - tLuci > .2) {
    tLuci = t; const vicine = anc.map(a => [a, a.p.distanceToSquared(pos)]).sort((a, b) => a[1] - b[1]).slice(0, pool.length).map(a => a[0]);
    const libere = vicine.filter(a => !pool.some(p => p.anc === a));
    for (const p of pool) { if (p.anc && !vicine.includes(p.anc)) p.via = true; if ((!p.anc || p.via) && p.cur < .05 && libere.length) { p.anc = libere.shift(); p.via = false; p.l.position.copy(p.anc.p); p.l.color.setHex(p.anc.col) } }
  }
  for (const p of pool) { const tgt = p.anc && !p.via ? p.anc.int * oscurita * (p.anc.zona === "cameretta" ? 1.2 : 2.3) : 0; p.cur = lerp(p.cur, tgt, 1 - Math.exp(-dt * 3)); p.l.intensity = p.cur * (p.anc && p.anc.tremola ? p.anc.tremola(t) : 1) }
  const Z = M.ZONE[zonaQui()];
  nebbia.col.lerp(tmpC.setHex(Z.fog), 1 - Math.exp(-dt * .8)); nebbia.dens = lerp(nebbia.dens, Z.dens * (S.nebbiaX || 1), 1 - Math.exp(-dt * (cielo > .01 ? 4 : .8)));
  scena.fog.color.copy(nebbia.col); scena.fog.density = nebbia.dens; scena.background.copy(nebbia.col);
  emisfero.color.lerp(cielo > .01 ? tmpC.setHex(0xc8b8ff) : tmpC.setHex(Z.emi).multiplyScalar(3), 1 - Math.exp(-dt)); emisfero.intensity = lerp(emisfero.intensity, .9 * oscurita + .05 + cielo * 2, 1 - Math.exp(-dt * 2)); luna.intensity = cielo * 4.5; finitura.uniforms.vign.value = .85 - cielo * .5; finitura.uniforms.ab.value = 1 - cielo * .85;
}
let pioggia = null;
function creaPioggia() {
  const n = 900, g = new THREE.BufferGeometry(), p = new Float32Array(n * 6);
  for (let i = 0; i < n; i++) { const x = (Math.random() - .5) * 16, y = Math.random() * 9, z = (Math.random() - .5) * 16; p.set([x, y, z, x + .02, y - .35, z], i * 6) }
  g.setAttribute("position", new THREE.BufferAttribute(p, 3));
  pioggia = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: 0x9fb4d0, transparent: true, opacity: .35 })); pioggia.frustumCulled = false; scena.add(pioggia);
}
function ciclo() {
  const dt = Math.min(PROVA ? .3 : .05, orologio.getDelta()), t = orologio.elapsedTime;
  if (S.mondo) {
    animaCamera(dt, t); aggiornaLuci(dt, t); for (const f of S.mondo.anima) f(t);
    if (t - tMira > .12) { tMira = t; aggiornaMira() }
    const z = zonaQui(); suono.zona(z, t);
    if (pioggia) { const vis = z === "vicolo"; pioggia.visible = vis; if (vis) { pioggia.position.set(camera.position.x, 0, camera.position.z); pioggia.position.y = -((t * 9) % 9) + 0 ; pioggia.material.opacity = .3 } }
    finitura.uniforms.t.value = t;
    for (const f of S.extra || []) f(dt, t);
    if (!S.sblocca || t - (S._ultimoRender || 0) > .08) { S._ultimoRender = t; composer.render(dt) }
    // qualità adattiva
    tAcc += dt; frames++; if (tAcc > 2.5) { const fps = frames / tAcc; tAcc = 0; frames = 0; if (fps < 32 && qualitaPR > .85) { qualitaPR = Math.max(.85, qualitaPR - .3); renderer.setPixelRatio(qualitaPR); adatta() } else if (fps < 24 && bloom.enabled) bloom.enabled = false }
  }
  requestAnimationFrame(ciclo);
}

/* ---------- etichette ---------- */
/* a cinque anni si risponde con un verbo: quello che si vuole fare, prima del nome del mestiere */
export const SOGNI = { luna: "andare sulla luna", animali: "curare gli animali", gol: "fare gol", ballare: "ballare", incendi: "spegnere gli incendi", scoprire: "scoprire cose nuove", dipingere: "dipingere", insegnare: "insegnare", cantare: "cantare", cucinare: "cucinare", volare: "pilotare gli aerei", misteri: "risolvere misteri", curare: "curare le persone", inventare: "inventare macchine", esplorare: "esplorare il mondo", scavare: "scavare tesori antichi" };
export const STRADE = ["Medicina", "Giurisprudenza", "Ingegneria", "Economia", "Lettere", "Filosofia", "Psicologia", "Architettura", "Design", "Informatica", "Biologia", "Lingue", "Scienze politiche", "Belle Arti", "Conservatorio", "Fisica", "Matematica", "Infermieristica", "Scienze della formazione", "Cinema", "Agraria", "Lavorare subito", "Un anno all'estero", "Servizio civile"];

/* ---------- capitoli ---------- */
const r = M.caso(M.semeDa(SEME + "scelte"));
function puntoAttesa(da, a) { const p = M.centroCella(...da), q = M.centroCella(...a); return p.lerp(q, .38) }
/* tre movimenti: 5 e 18 anni, 23 e 28 anni, 35 anni e il centro.
   Dentro un movimento si cammina di seguito; tra un movimento e l'altro si aspetta il palco. */
const SOGLIE = [3, 5, 7];
async function attendi(k, prossimo = k + 1) {
  invia("progresso", "capitolo", k + ".2");
  if (!SOGLIE.includes(prossimo)) return;
  if (S.palco >= prossimo) return;
  if (LV.attivo && S.live && !LIBERO) {
    // durante l'evento si va avanti solo quando il capitolo si apre dal palco
    UI.dici(prossimo === 7 ? "Resta qui. Tra poco si sale tutti insieme." : "Alza gli occhi verso il palco.");
    raccontaSala(k);
    let senzaRete = 0; const guardia = setInterval(() => { senzaRete = window.DGLive && DGLive.ascolta && DGLive.ascolta.ok === false ? senzaRete + 5 : 0; if (senzaRete >= 180) { clearInterval(guardia); S.sblocca && S.sblocca(true) } }, 5000);
    const forzato = await new Promise(res => { S.sblocca = (forza) => { if (forza || S.palco >= prossimo) { S.sblocca = null; res(!!forza) } } });
    clearInterval(guardia); UI.dici(""); $("#sala").classList.remove("on");
    if (forzato) { UI.dici("Il collegamento con il palco si è interrotto: prosegui da solo."); await UI.scegli([["vai", "Prosegui"]], "una"); UI.dici("") }
    return;
  }
  await pausa(900); await UI.scegli([["vai", prossimo === 7 ? "Sali" : "Prosegui"]], "una");
}
/* anche le voci sui muri di un'età passata si tolgono */
function liberaVoci(...zone) { const via = []; scena.traverse(o => { if (o.userData.voce && zone.includes(o.userData.voce)) via.push(o) }); for (const o of via) { o.geometry.dispose(); if (o.material.map) o.material.map.dispose(); o.material.dispose(); scena.remove(o) } }
/* le porte di un capitolo passato si tolgono: liberano memoria sui telefoni più vecchi */
function liberaPorte(ps) { for (const p of ps || []) { p.gruppo.traverse(o => { if (o.isMesh) { o.geometry.dispose(); for (const m of [].concat(o.material)) { if (m.map && !m.map.userData.condivisa) m.map.dispose(); m.dispose() } } }); scena.remove(p.gruppo) } }
/* mentre aspetti: tu e la sala, a confronto */
async function raccontaSala(k) {
  if (k === 2 || k === 4) { await raccontaSala1(k - 1, true); return raccontaSala1(k, false, true) }
  return raccontaSala1(k);
}
async function raccontaSala1(k, soloSalva, aggiungi) {
  if (!LV.conteggi) return; let D = {};
  try { if (!S._dati || Date.now() - S._dati.t > 4000) S._dati = { t: Date.now(), p: LV.conteggi(Date.now() - 3 * 3600e3) }; for (const r0 of await S._dati.p) { ((D[r0.stanza] = D[r0.stanza] || {})[r0.chiave] = D[r0.stanza][r0.chiave] || {})[r0.valore] = Number(r0.n) } } catch (e) { return }
  const som = o => o ? Object.values(o).reduce((a, b) => a + b, 0) : 0, pc = (a, b) => b ? Math.round(a / b * 100) : 0, sc = S.scelte; let t = "";
  if (k === 1) { const so = D.cameretta?.sogno || {}, tot = som(so); if (tot > 1) t = sc.sogno === "nonlo" ? `Come te, ${so.nonlo || 1} ${so.nonlo === 1 ? "persona" : "persone"} su ${tot} ha${so.nonlo === 1 ? "" : "nno"} aperto la porta col punto interrogativo.` : `In questa sala ${so[sc.sogno] || 1} su ${tot} ${(so[sc.sogno] || 1) === 1 ? "vuole" : "vogliono"} ${sc.sognoTesto}. ${pc(so.nonlo || 0, tot)}% ha aperto la porta col punto interrogativo.` }
  if (k === 2) { const se = D.scuola?.secondi || {}; let a = 0, n = 0; for (const [v, c] of Object.entries(se)) { a += v * c; n += c } if (n > 1) t = `Tu hai scelto in ${sc.secondi} secondi. La sala, in media, in ${Math.round(a / n)}.` }
  if (k === 3) { const sg = D.notte?.seguito || {}, div = (sg.moneta || 0) + (sg.speranza || 0), tot = div + (sg.uguali || 0); if (tot > 1) t = `${pc(div, tot)}% della sala ha sperato il contrario di quello che è uscito. Di questi, ${pc(sg.speranza || 0, div)}% ha seguito la speranza.` }
  if (k === 4) { const o = D.oracolo?.scelta || {}, tot = som(o); if (tot > 1) t = `${pc(o.strada || 0, tot)}% della sala ha chiesto la strada all'oracolo.` }
  if (k === 5) { const a = D.vicolo?.azione || {}; if (som(a) > 1) t = `${a.segno || 0} persone hanno lasciato un segno nel vicolo cieco.` }
  if (k === 6) { const c = D.centro?.scelta || {}, tot = som(c); if (tot > 1) t = `${pc(c.coppa || 0, tot)}% della sala ha preso la coppa. ${pc(c.oltre || 0, tot)}% ha superato la coppa.` }
  if (soloSalva) { S._sala = t; return }
  const tutto = [aggiungi ? S._sala : "", t].filter(Boolean).join("<br><br>"); S._sala = "";
  if (tutto) { $("#sala").innerHTML = `<b>La sala</b>${tutto}`; $("#sala").classList.add("on") }
}
async function porte(lista, { zona, rett, doppie, stile, colori, larg = .95 }) {
  const posti = M.postiPorta(S.lab, zona, rett, lista.length, doppie);
  if (posti.length < lista.length) lista = lista.filter(e => e.codice === "nonlo" || e.codice === "sogno").concat(lista.filter(e => e.codice !== "nonlo" && e.codice !== "sogno")).slice(0, posti.length);
  const porte = lista.slice(0, posti.length).map((e, i) => { const p = M.porta(scena, posti[i], { etichetta: e.testo, stile: e.stile || stile, colore: e.colore || (colori ? colori[i % colori.length] : 0x8a8f99), larg, env, r }); p.codice = e.codice; return p });
  return porte;
}
/* si sceglie in due tempi: un tocco ti porta davanti alla porta, un secondo tocco la apre */
function scegliPorta(porte) {
  S.interattivi = porte.map(p => p.pannello); let vicina = null;
  return new Promise(res => {
    S.onTap = async p => {
      if (!p.pannello) return;
      if (p === vicina && !cam.giro) { S.onTap = null; S.interattivi = []; nome(""); res(p); return }
      vicina = p; suono.tocco(); const n = new THREE.Vector3(); p.gruppo.getWorldDirection(n);
      const meta = p.gruppo.position.clone().addScaledVector(n, 1.85).setY(0);
      UI.dici("");
      await cammina([meta], { velocita: 2.4, guarda: .3, mira: p.gruppo.position.clone().setY(0) });
      if (vicina !== p) return;
      guardaVerso(p.gruppo.position); cam.yawU = 0; cam.pitchU = 0;
      UI.dici(`<b>${p.etichetta === "?" ? "La porta del punto interrogativo" : p.etichetta}</b><br>Tocca di nuovo la porta per aprirla, o scegline un'altra.`);
    };
  });
}
async function attraversa(p) {
  suono.porta(); const n = new THREE.Vector3(); p.gruppo.getWorldDirection(n);
  const fine = p.gruppo.position.clone().addScaledVector(n, .3); guardaVerso(fine);
  S.extra.push(function apri(dt) { p.apri(dt); if (p.aperta >= 1) S.extra.splice(S.extra.indexOf(apri), 1) });
  await pausa(900); cammina([p.gruppo.position.clone().addScaledVector(n, .9)], { velocita: 1.1, guarda: .5 });
  await pausa(700); await UI.velo("#fff8ea", 1, 1000);
}

/* i muri della cameretta per la tabella dell'altezza e per il primo disegno */
function muroCameretta() {
  const cand = [[1, 0, "N"], [2, 0, "N"], [0, 1, "W"], [0, 2, "W"], [1, 2, "S"], [2, 2, "S"], [2, 1, "E"], [2, 0, "E"]].map(([x, z, l]) => M.facciaMuro(S.lab, x, z, l)).filter(Boolean);
  if (!cand.length) return null;
  const da = cam.pos.clone(); cand.sort((a, b) => a.p.distanceTo(da) - b.p.distanceTo(da));
  return { disegno: cand[0], altezza: cand[1] || cand[0] };
}
/* mentre la sala entra: come ti vedi da grande, disegnato col dito sul muro */
async function disegnoIniziale() {
  const m = muroCameretta(); if (!m) return; const f = m.disegno;
  guardaVerso(f.p); await cammina([f.p.clone().addScaledVector(f.n, 1.25).setY(0)], { velocita: .9, guarda: .3, mira: f.p.clone().setY(0) });
  guardaVerso(f.p); await pausa(600);
  const tratti = await disegna(f, { pastelli: true, invito: "Mentre aspetti: disegna sul muro come ti vedi da grande.", larg: 1.4, alt: 1.05, y: 1.05 });
  if (tratti) { S.scelte.disegno = tratti; salva(); UI.dici("Lo ritroverai.", 2600) }
  cam.yawT = cam.yaw + Math.PI * .6;
}
async function capitolo1() {
  S.cap = 1; const P = S.lab.percorsi.cameretta; UI.eta("5 anni"); invia("progresso", "capitolo", "1.0");
  await cammina(celle(P.andata).concat([P.sala]));
  const sale = Object.keys(SOGNI).sort(() => r() - .5).slice(0, 6).map(k => ({ testo: SOGNI[k], codice: k })); sale.splice(Math.floor(r() * 7), 0, { testo: "?", codice: "nonlo" });
  const ps = await porte(sale, { zona: "cameretta", rett: P.rett, stile: "pastello", colori: [0xf2a7a0, 0xa9cff2, 0xf7dc8c, 0xb8e3c4, 0xd6bdf0, 0xf5c19a, 0xc4e0f5] });
  // la domanda scritta sul muro
  const sala = P.sala; const scritta = new THREE.Mesh(new THREE.PlaneGeometry(2.4, .8), new THREE.MeshStandardMaterial({ map: M.tela(768, 256, (g, w, h) => M.pastello(g, "Cosa vuoi fare da grande?", w / 2, h / 2, 74, "#2a2238")), transparent: true, roughness: 1 }));
  const vista = ps[Math.floor(ps.length / 2)]; scritta.position.copy(vista.gruppo.position).setY(2.45); scritta.quaternion.copy(vista.gruppo.quaternion); scritta.position.addScaledVector(new THREE.Vector3(0, 0, 1).applyQuaternion(vista.gruppo.quaternion), .01); scena.add(scritta);
  guardaVerso(scritta.position);
  UI.dici("Cosa vuoi fare da grande? Guardati intorno: tocca una porta per avvicinarti.");
  const p = await scegliPorta(ps); UI.dici(""); S.scelte.sogno = p.codice; S.scelte.sognoTesto = p.etichetta; salva(); invia("cameretta", "sogno", p.codice);
  await attraversa(p);
  UI.dici(p.codice === "nonlo" ? "Non lo sai. A cinque anni va benissimo." : `Da grande vuoi ${p.etichetta}.`, 3600);
  filo.stacca(); cam.pos.copy(M.centroCella(...P.ritorno[0])); await UI.velo("#fff8ea", 0, 1400);
  await cammina(celle(P.ritorno).concat([puntoAttesa(P.ritorno.at(-1), S.lab.percorsi.scuola.andata[0])]));
  liberaPorte(ps);
  await attendi(1);
}

async function capitolo2() {
  vociPer("scuola");
  S.cap = 2; const P = S.lab.percorsi.scuola; invia("progresso", "capitolo", "2.0");
  suono.cresci(); UI.eta("18 anni"); UI.dici("Tredici anni dopo.", 2600);
  await cammina(celle(P.andata).concat([P.sala])); liberaVoci("cameretta");
  let gruppo = ls.get("dg3-gruppo"); if (!gruppo) { gruppo = r() < .5 ? 24 : 6; ls.set("dg3-gruppo", gruppo) }
  const strade = [...STRADE.keys()].sort(() => r() - .5).slice(0, gruppo - 1).map(i => ({ testo: STRADE[i], codice: "s" + i }));
  const sogno = S.scelte.sognoTesto && S.scelte.sogno !== "nonlo" ? S.scelte.sognoTesto : "?";
  strade.splice(Math.floor(r() * gruppo), 0, { testo: sogno, codice: "sogno", stile: "pastello", colore: 0xa9cff2 });
  const ps = await porte(strade, { zona: "scuola", rett: P.rett, doppie: gruppo > 12, stile: "targa", colori: [0x8a9099], larg: gruppo > 12 ? .86 : .95 });
  // un orologio che va avanti davvero
  const quadrante = new THREE.Group(); const disco = new THREE.Mesh(new THREE.CircleGeometry(.38, 48), new THREE.MeshStandardMaterial({ map: M.tela(256, 256, (g, w, h) => { g.fillStyle = "#f4f1ea"; g.beginPath(); g.arc(w / 2, h / 2, 124, 0, 7); g.fill(); g.strokeStyle = "#222"; g.lineWidth = 10; g.stroke(); for (let i = 0; i < 12; i++) { const a = i / 12 * 6.283; g.lineWidth = i % 3 ? 4 : 9; g.beginPath(); g.moveTo(w / 2 + Math.sin(a) * 92, h / 2 - Math.cos(a) * 92); g.lineTo(w / 2 + Math.sin(a) * 112, h / 2 - Math.cos(a) * 112); g.stroke() } }), roughness: .4 }));
  quadrante.add(disco); const lancetta = new THREE.Mesh(new THREE.BoxGeometry(.012, .3, .01), new THREE.MeshBasicMaterial({ color: 0xc0392b })); lancetta.geometry.translate(0, .12, .01); quadrante.add(lancetta);
  const ore = new THREE.Mesh(new THREE.BoxGeometry(.025, .18, .01), new THREE.MeshBasicMaterial({ color: 0x111111 })); ore.geometry.translate(0, .08, .008); ore.rotation.z = -2.2; quadrante.add(ore);
  const muro = M.postiPorta(S.lab, "scuola", P.rett, 40, false).find(q => !ps.some(p => p.gruppo.position.distanceTo(q.f.p) < 1.2)) || M.postiPorta(S.lab, "scuola", P.rett, 40, false)[0];
  M.sulMuro(quadrante, muro.f, 2.75); quadrante.position.addScaledVector(muro.f.n, .02); scena.add(quadrante);
  const t0 = performance.now(); let ultimoSec = -1;
  const ticchettio = () => { const s = Math.floor((performance.now() - t0) / 1000); lancetta.rotation.z = -s / 60 * Math.PI * 2; if (s !== ultimoSec) { ultimoSec = s; suono.ticchetta() } };
  S.extra.push(ticchettio);
  UI.dici(gruppo > 12 ? "Adesso le porte sono tante. Tocca una porta per avvicinarti." : "Adesso le porte sono sei. Tocca una porta per avvicinarti.");
  const p = await scegliPorta(ps); UI.dici(""); const sec = Math.round((performance.now() - t0) / 1000); S.extra.splice(S.extra.indexOf(ticchettio), 1);
  Object.assign(S.scelte, { strada: p.codice, stradaTesto: p.etichetta, secondi: sec, gruppo }); salva();
  invia("scuola", "gruppo", gruppo); invia("scuola", "porta", p.codice); invia("scuola", "secondi", Math.min(sec, 600));
  await attraversa(p);
  UI.dici("Quanta certezza hai, adesso?");
  const sic = await UI.scegli([["1", "Poca"], ["2", "Abbastanza"], ["3", "Tutta"]]); S.scelte.sicurezza = sic; salva(); invia("scuola", "sicurezza", sic); UI.dici("");
  filo.stacca(); cam.pos.copy(M.centroCella(...P.ritorno[0])); await UI.velo("#fff8ea", 0, 1400);
  await cammina(celle(P.ritorno).concat([puntoAttesa(P.ritorno.at(-1), S.lab.percorsi.notte.andata[0])]));
  liberaPorte(ps);
  await attendi(2);
}

async function capitolo3() {
  vociPer("notte");
  S.cap = 3; const P = S.lab.percorsi.notte; invia("progresso", "capitolo", "3.0");
  suono.cresci(); UI.eta("23 anni"); UI.dici("La città, di notte.", 2600);
  await cammina(celle(P.andata).concat([P.sala])); liberaVoci("scuola");
  // si spegne la luce
  UI.dici("Si è spenta la luce."); suono.colpo();
  await animaValore(v => { oscurita = v; finitura.uniforms.buio.value = (1 - v) * .9 }, 1, .04, 1600);
  torcia.intensity = 0; await pausa(600); await animaValore(v => torcia.intensity = v, 0, 9, 700);
  // la moneta
  const facce = ["TESTA", "CROCE"].map((t, i) => M.tela(256, 256, (g, w, h) => { const gr = g.createRadialGradient(w / 2, h / 2, 10, w / 2, h / 2, 128); gr.addColorStop(0, "#f7dc8c"); gr.addColorStop(1, "#b98a2e"); g.fillStyle = gr; g.fillRect(0, 0, w, h); g.strokeStyle = "#7a5512"; g.lineWidth = 8; g.beginPath(); g.arc(w / 2, h / 2, 112, 0, 7); g.stroke(); g.fillStyle = "#6b4a10"; g.font = "600 40px Marcellus, serif"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText(t, w / 2, h / 2 + 52); if (i === 0) { g.beginPath(); g.arc(w / 2, h / 2 - 18, 34, 0, 7); g.lineWidth = 7; g.stroke(); g.beginPath(); g.arc(w / 2, h / 2 - 18, 14, 0, 7); g.stroke() } else { g.fillRect(w / 2 - 6, h / 2 - 60, 12, 80); g.fillRect(w / 2 - 34, h / 2 - 32, 68, 12) } }));
  const oro = new THREE.MeshStandardMaterial({ color: 0xe8b850, metalness: 1, roughness: .25, envMap: env });
  const moneta = new THREE.Mesh(new THREE.CylinderGeometry(.07, .07, .008, 48), [oro, new THREE.MeshBasicMaterial({ map: facce[0], color: 0xd8c8a0 }), new THREE.MeshBasicMaterial({ map: facce[1], color: 0xd8c8a0 })]); // facce senza luce: la torcia non le brucia
  camera.add(moneta); moneta.position.set(0, -.1, -.62); moneta.rotation.x = 1.25;
  luceMoneta.intensity = .18;
  S.interattivi = [moneta]; moneta.userData.azione = { moneta: true };
  UI.dici("Testa: vai a sinistra. Croce: vai a destra. Tocca la moneta per lanciarla.");
  const battiti = setInterval(() => suono.cuore(.6), 1100);
  await new Promise(res => S.onTap = () => { S.onTap = null; S.interattivi = []; res() });
  clearInterval(battiti); suono.moneta(); UI.dici("Mentre è in aria: cosa speri che esca?");
  const esito = r() < .5 ? "testa" : "croce"; let speranza = null;
  const battitiVeloci = setInterval(() => suono.cuore(1), 520);
  const scelta = UI.scegli([["testa", "Spero testa"], ["croce", "Spero croce"]]).then(v => speranza = v);
  // volo della moneta, rallentato finché non hai sperato
  await new Promise(res => {
    let t = 0; const giri = 9 + (esito === "croce" ? .5 : 0);
    S.extra.push(function vola(dt) {
      const lento = speranza ? 1 : .18; t = Math.min(1, t + dt * .42 * lento);
      moneta.position.y = -.1 + Math.sin(t * Math.PI) * .36; moneta.rotation.x = 1.25 + t * giri * Math.PI * 2 * .5; moneta.position.z = -.62 - Math.sin(t * Math.PI) * .12;
      if (t >= 1) { S.extra.splice(S.extra.indexOf(vola), 1); res() }
    });
  });
  await scelta; clearInterval(battitiVeloci); suono.cade();
  moneta.rotation.x = esito === "testa" ? Math.PI / 2 + .35 : -Math.PI / 2 + .35;
  const lato = esito === "testa" ? "sinistra" : "destra";
  UI.dici(speranza === esito ? `È uscita ${esito}, come speravi.` : `È uscita ${esito}. Speravi ${speranza}.`);
  Object.assign(S.scelte, { speranza, esito }); salva(); invia("notte", "speranza", speranza); invia("notte", "esito", esito);
  await pausa(2200);
  let dir;
  if (speranza === esito) { dir = lato; UI.dici(`Vai a ${lato}.`, 2000) }
  else { UI.dici("Da che parte vai?"); dir = await UI.scegli([[lato, `A ${lato}, come dice la moneta`], [lato === "sinistra" ? "destra" : "sinistra", `A ${lato === "sinistra" ? "destra" : "sinistra"}, come speravi`]]) }
  const seguito = speranza === esito ? "uguali" : (dir === lato ? "moneta" : "speranza"); S.scelte.seguito = seguito; salva(); invia("notte", "seguito", seguito); UI.dici("");
  camera.remove(moneta); luceMoneta.intensity = 0;
  cam.yawT = cam.yaw + (dir === "sinistra" ? Math.PI / 2 : -Math.PI / 2); await pausa(900);
  const avanti = new THREE.Vector3(-Math.sin(cam.yawT), 0, -Math.cos(cam.yawT)); await cammina([cam.pos.clone().addScaledVector(avanti, 2.4)], { velocita: 1.2 });
  await UI.velo("#000", 1, 900); torcia.intensity = 0; oscurita = 1; finitura.uniforms.buio.value = 0;
  filo.stacca(); cam.pos.copy(M.centroCella(...P.ritorno[0])); await UI.velo("#000", 0, 1200);
  await cammina(celle(P.ritorno).concat([puntoAttesa(P.ritorno.at(-1), S.lab.percorsi.oracolo.andata[0])]));
  await attendi(3);
}
function animaValore(set, da, a, ms) { return new Promise(res => { const t0 = performance.now(); const f = () => { const k = Math.min(1, (performance.now() - t0) / (PROVA ? 100 : ms)); set(da + (a - da) * (k * k * (3 - 2 * k))); k < 1 ? requestAnimationFrame(f) : res() }; f() }) }

async function capitolo4() {
  vociPer("oracolo");
  S.cap = 4; const P = S.lab.percorsi.oracolo, sfera = S.mondo.sfera; invia("progresso", "capitolo", "4.0");
  suono.cresci(); UI.eta("28 anni"); UI.dici("Vetro e schermi.", 2400);
  const ultima = M.centroCella(...P.andata.at(-1)), dir = P.sala.clone().sub(ultima).setY(0); const stop = P.sala.clone().sub(dir.lengthSq() > .01 ? dir.normalize().multiplyScalar(2.3) : new THREE.Vector3(0, 0, -2.3));
  await cammina(celle(P.andata).concat([stop])); liberaVoci("notte");
  guardaVerso(sfera.position); suono.oracolo(); cam.pitchExtra = .12;
  UI.dici("Conosco ogni strada di questo labirinto. Vuoi che ti dica qual è la tua?");
  const sc = await UI.scegli([["strada", "Dimmi la strada"], ["domanda", "Fammi una domanda"]]);
  S.scelte.oracolo = sc; salva(); invia("oracolo", "scelta", sc); cam.pitchExtra = 0;
  if (sc === "strada") {
    UI.dici("Eccola. È la strada più percorsa."); suono.fruscia(false);
    const muri = S.mondo.muriZona.oracolo, schermi = S.mondo.schermi, h = M.ZONE.oracolo.h;
    await animaValore(v => { muri.position.y = -v * (h - .02); schermi.position.y = -v * (h - .02); S.mondo.sferaY = 2.2 + v * 4 }, 0, 1, 3000);
    const linea = new THREE.Mesh(new THREE.PlaneGeometry(.12, 1), new THREE.MeshBasicMaterial({ color: 0xbfe0ff })); const a = cam.pos.clone(), b = M.centroCella(...P.ritorno.at(-1)); linea.scale.y = a.distanceTo(b); linea.rotation.x = -Math.PI / 2; linea.rotation.z = Math.atan2(b.x - a.x, b.z - a.z); linea.position.copy(a).lerp(b, .5).setY(.02); scena.add(linea);
    await cammina([b], { velocita: 3.2, guarda: 3 });
    UI.dici("Sei dove arrivano quasi tutti.", 3200);
    await animaValore(v => { muri.position.y = -v * (h - .02); schermi.position.y = -v * (h - .02) }, 1, 0, 2600); scena.remove(linea); S.mondo.sferaY = 2.2;
    await cammina([puntoAttesa(P.ritorno.at(-1), S.lab.percorsi.vicolo.andata[0])]);
  } else {
    const sogno = S.scelte.sognoTesto; const domande = ["Che cosa faresti anche se nessuno lo vedesse?", "Quando hai perso l'ultima volta la cognizione del tempo?", "Quale domanda eviti di farti?", "Chi saresti se non dovessi dimostrare niente?"];
    const q = sogno && S.scelte.sogno !== "nonlo" && r() < .6 ? `A cinque anni volevi ${sogno}. Che cosa ne resta?` : domande[Math.floor(r() * domande.length)];
    suono.oracolo(); UI.dici(q);
    await pausa(1600); await UI.scegli([["ok", "Ci penso mentre cammino"]]); UI.dici("");
    await cammina(celle(P.ritorno).concat([puntoAttesa(P.ritorno.at(-1), S.lab.percorsi.vicolo.andata[0])]));
  }
  await attendi(4);
}

async function capitolo5() {
  vociPer("vicolo", "ritorno");
  S.cap = 5; const P = S.lab.percorsi.vicolo; invia("progresso", "capitolo", "5.0");
  suono.cresci(); UI.eta("35 anni"); UI.dici("Piove.", 2000);
  let altri = []; try { if (LV.segni) altri = (await LV.segni()) || [] } catch (e) { }
  await cammina(celle(P.andata)); liberaVoci("oracolo");
  const [cx, cz] = P.cieco, prima = P.andata.at(-2) || P.andata[0], lato = cx > prima[0] ? "E" : cx < prima[0] ? "W" : cz > prima[1] ? "S" : "N";
  const f = M.facciaMuro(S.lab, cx, cz, lato) || M.facciaMuro(S.lab, cx, cz, "NSEW".split("").find(l => M.facciaMuro(S.lab, cx, cz, l)));
  guardaVerso(f.p); await cammina([f.p.clone().addScaledVector(f.n, .95)], { velocita: .8, guarda: .3 });
  UI.dici("Vicolo cieco.");
  let spinte = 0, segno = null;
  for (; ;) {
    const a = await UI.scegli([["spingi", "Spingi il muro"], ["segno", "Lascia un segno"], ["torna", "Torna indietro"]]);
    if (a === "spingi") { spinte++; invia("vicolo", "spinte", spinte); await spinta(f); UI.dici(spinte > 1 ? "Non si muove. Hai spinto " + spinte + " volte." : "Non si muove."); continue }
    if (a === "segno") { segno = await disegna(f); if (segno) { invia("vicolo", "segno", "1"); try { LV.inviaSegno && LV.inviaSegno(segno) } catch (e) { } } UI.dici("Il segno resta qui, per chi passerà dopo di te."); await pausa(1800); }
    break;
  }
  Object.assign(S.scelte, { spinte, segno: !!segno }); salva(); invia("vicolo", "azione", segno ? "segno" : spinte ? "spinto" : "indietro");
  UI.dici(""); cam.yawT = cam.yaw + Math.PI; await pausa(1100);
  // i segni degli altri lungo la strada del ritorno
  const ritornoV = P.ritorno.filter(([x, z]) => M.zonaDi(x, z) === "vicolo"); let messi = 0;
  for (const [i, [x, z]] of ritornoV.entries()) { if (messi >= altri.length || i % 2) continue; for (const l of "NSEW") { const ff = M.facciaMuro(S.lab, x, z, l); if (!ff || (x === cx && z === cz)) continue; posaSegno(ff, altri[messi++]); break } }
  if (altri.length) UI.dici(altri.length === 1 ? "Qualcun altro è passato di qui." : `Altre ${altri.length} persone sono passate di qui.`, 5000);
  await cammina(celle(P.ritorno).concat([puntoAttesa(P.ritorno.at(-1), S.lab.percorsi.centro.andata[0])]));
  await attendi(5);
}
async function spinta(f) { suono.colpo(); const b = cam.pos.clone(); await animaValore(v => cam.pos.copy(b).addScaledVector(f.n, -v * .35), 0, 1, 180); await animaValore(v => cam.pos.copy(b).addScaledVector(f.n, -v * .35), 1, 0, 420) }
function superficieSegno(f, larg = 1.9, alt = 1.5, cw = 760, ch = 600) {
  const c = document.createElement("canvas"); c.width = cw; c.height = ch; const g = c.getContext("2d");
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  const m = new THREE.Mesh(new THREE.PlaneGeometry(larg, alt), new THREE.MeshStandardMaterial({ map: t, transparent: true, roughness: 1, emissive: 0xffffff, emissiveMap: t, emissiveIntensity: .12 }));
  M.sulMuro(m, f, 1.55); m.position.addScaledVector(f.n, .012); scena.add(m); return { m, g, t, c };
}
function gessoTratto(g, a, b, w = 7, colore = "rgba(245,240,230,.85)") { g.strokeStyle = colore; g.lineCap = "round"; for (let i = 0; i < 3; i++) { g.lineWidth = w * (.6 + Math.random() * .6); g.globalAlpha = .5; g.beginPath(); g.moveTo(a[0] + (Math.random() - .5) * 3, a[1] + (Math.random() - .5) * 3); g.lineTo(b[0] + (Math.random() - .5) * 3, b[1] + (Math.random() - .5) * 3); g.stroke() } g.globalAlpha = 1 }
function posaSegno(f, s) {
  let tratti = []; try { tratti = typeof s.punti === "string" ? JSON.parse(s.punti) : s.punti } catch (e) { return }
  const sup = superficieSegno(f, 1.3, 1.03, 256, 200);
  for (const tr of tratti || []) for (let i = 1; i < tr.length; i++) gessoTratto(sup.g, [tr[i - 1][0] * 2.56, tr[i - 1][1] * 2], [tr[i][0] * 2.56, tr[i][1] * 2], 3.5);
  sup.t.needsUpdate = true;
}
function disegna(f, { pastelli = false, invito = "Disegna sul muro con il dito.", larg, alt, y } = {}) {
  return new Promise(res => {
    const sup = superficieSegno(f, larg, alt); if (y) sup.m.position.y = y; const tratti = []; let cur = null, totale = 0;
    const COLORI = ["#d0462f", "#3d7fd9", "#3c9a3c", "#e0a020", "#8a4fc0"];
    const colore = () => pastelli ? COLORI[(tratti.length - 1 + 5) % 5] : undefined;
    const uvDa = e => { ndc.set(e.clientX / innerWidth * 2 - 1, -(e.clientY / innerHeight) * 2 + 1); ray.setFromCamera(ndc, camera); const h = ray.intersectObject(sup.m)[0]; return h ? [Math.round(h.uv.x * 99), Math.round((1 - h.uv.y) * 99)] : null };
    S.disegno = {
      inizia(e) { const p = uvDa(e); if (p && totale < 320) { cur = [p]; tratti.push(cur) } },
      muovi(e) { if (!cur) return; const p = uvDa(e); if (!p) return; const q = cur[cur.length - 1]; if (Math.hypot(p[0] - q[0], p[1] - q[1]) < 1.5 || totale >= 320) return; cur.push(p); totale++; gessoTratto(sup.g, [q[0] * 7.6, q[1] * 6], [p[0] * 7.6, p[1] * 6], pastelli ? 11 : 7, colore()); sup.t.needsUpdate = true; if (totale % 3 === 0) suono.gesso() },
      fine() { cur = null }
    };
    cam.yawU = 0; cam.pitchU = 0; UI.dici(invito);
    UI.scegli([["fatto", "Fatto"], ["no", "Lascia stare"]]).then(v => { S.disegno = null; UI.dici(""); if (v === "no" || !tratti.length) { scena.remove(sup.m); res(null) } else res(JSON.stringify(tratti.filter(t => t.length > 1)).slice(0, 4000)) });
  });
}

async function capitolo6() {
  vociPer("centro");
  S.cap = 6; const P = S.lab.percorsi.centro, coppa = S.mondo.coppa; invia("progresso", "capitolo", "6.0");
  suono.cresci(); UI.eta("Da grande"); UI.dici("La pietra più antica.", 2600);
  const ultima = M.centroCella(...P.andata.at(-1)), dir = P.sala.clone().sub(ultima).setY(0); const stop = P.sala.clone().sub(dir.lengthSq() > .01 ? dir.normalize().multiplyScalar(1.9) : new THREE.Vector3(0, 0, -1.9));
  M.sulMuro(S.mondo.scrittaCoppa, { p: P.sala.clone().addScaledVector(dir.clone().normalize().negate(), .47), n: dir.clone().normalize().negate() }, .7);
  const quadro = S.scelte.disegno ? appendiDisegno(P, dir) : null;
  await cammina(celle(P.andata).concat([stop])); liberaVoci("vicolo", "ritorno");
  if (quadro) { guardaVerso(quadro.position); cam.pitchExtra = .16; UI.dici("L'hai disegnato a cinque anni."); await pausa(4200) }
  guardaVerso(coppa.position); cam.pitchExtra = -.1; suono.vittoria();
  UI.dici("Sei al centro.");
  await pausa(1400);
  const sc = await UI.scegli([["coppa", "Prendi la coppa"], ["oltre", "Vai oltre"]]);
  S.scelte.centro = sc; salva(); invia("centro", "scelta", sc); cam.pitchExtra = 0; UI.dici("");
  if (sc === "coppa") {
    const da = coppa.position.clone(); const a = () => camera.localToWorld(new THREE.Vector3(0, -.38, -1.05));
    await animaValore(v => coppa.position.copy(da).lerp(a(), v), 0, 1, 1800); suono.vittoria();
    await UI.velo("#fff3d6", 1, 1200);
    $("#fine").classList.add("on");
    await pausa(1200);
    await new Promise(res => $("#rimetti").onclick = () => { suono.tocco(); res() });
    invia("centro", "continua", "1"); S.scelte.continua = true; salva();
    $("#fine").classList.remove("on"); coppa.position.copy(da); await UI.velo("#fff3d6", 0, 1400);
  }
  await letteraAlBambino();
  await attendi(6, 7);
  await oltre();
}
async function oltre() {
  invia("progresso", "capitolo", "6.2");
  UI.dici(""); UI.eta(""); suono.sali();
  // il filo: la strada che hai fatto
  const tratti = [[]]; for (const p of S.cammino) { if (!p) { tratti.push([]); continue } const t = tratti[tratti.length - 1]; if (!t.length || p.distanceTo(t[t.length - 1]) > .4) t.push(p.clone().setY(.5)) }
  const filoM = new THREE.MeshBasicMaterial({ color: 0xff3a22, transparent: true, opacity: 0, fog: false }), filo = { material: filoM };
  for (const t of tratti) if (t.length > 1) scena.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(t, false, "centripetal"), t.length * 3, .42, 8, false), filoM));
  // il labirinto che continua oltre i muri, all'infinito
  const infinito = new THREE.Mesh(new THREE.PlaneGeometry(3000, 3000), new THREE.ShaderMaterial({ transparent: true, depthWrite: false, uniforms: { k: { value: 0 }, lato: { value: M.N * M.C / 2 } },
    vertexShader: `varying vec2 vP;void main(){vec4 w=modelMatrix*vec4(position,1.);vP=w.xz;gl_Position=projectionMatrix*viewMatrix*w;}`,
    fragmentShader: `uniform float k;uniform float lato;varying vec2 vP;float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
      void main(){if(abs(vP.x)<lato&&abs(vP.y)<lato)discard;vec2 c=vP/${M.C.toFixed(1)};vec2 i=floor(c),f=fract(c);float r=h(i);
      float d=r<.5?abs(f.x-.04):abs(f.y-.04);float m=1.-smoothstep(.0,.07,d);float dist=length(vP);
      float fade=exp(-max(0.,dist-lato)*.012)*k;vec3 col=mix(vec3(.08,.05,.03),vec3(.95,.66,.27),m);gl_FragColor=vec4(col,fade*(.35+m*.65));}` }));
  infinito.rotation.x = -Math.PI / 2; infinito.position.y = .02; scena.add(infinito);
  // le luci degli altri
  let n = 1; try { if (LV.presenti) n = Math.max(1, await Promise.race([LV.presenti(), pausa(2000).then(() => 1)])) } catch (e) { }
  const luci = new THREE.Points(new THREE.BufferGeometry().setAttribute("position", new THREE.Float32BufferAttribute(Array.from({ length: Math.min(n - 1, 600) * 3 }, (_, i) => i % 3 === 1 ? 1.2 : (Math.floor(Math.random() * M.N) + .5) * M.C - M.N * M.C / 2), 3)), new THREE.PointsMaterial({ color: 0xffd58a, size: 1.4, sizeAttenuation: true, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending }));
  scena.add(luci);
  const da = cam.pos.clone(), occhio0 = cam.occhio; cam.occhioFisso = cam.occhio; S.nebbiaX = 1;
  const meta = new THREE.Vector3(Math.sin(cam.yaw) * 17, 0, Math.cos(cam.yaw) * 17); // indietro rispetto allo sguardo: il labirinto resta nella metà alta dello schermo
  for (const so of S.mondo.soffitti || []) so.visible = false;
  await animaValore(v => {
    cam.occhioFisso = lerp(occhio0, 108, v * v); cam.pitchExtra = -v * 1.5; cam.yawU *= .95; cam.pitchU *= .95;
    cam.pos.copy(da).lerp(meta, v); S.nebbiaX = lerp(1, .12, v);
    filo.material.opacity = Math.min(1, v * 2); infinito.material.uniforms.k.value = v * .45; luci.material.opacity = v; cielo = v;
  }, 0, 1, 11000);
  UI.dici("Il labirinto continua.", 5000);
  await pausa(3000);
  await cartaFinale();
}

/* il disegno dei cinque anni, incorniciato sul muro dietro la coppa */
function appendiDisegno(P, dir) {
  let tratti = []; try { tratti = JSON.parse(S.scelte.disegno) } catch (e) { return null }
  const d = dir.lengthSq() > .01 ? dir.clone().normalize() : new THREE.Vector3(0, 0, -1);
  const [a, b, c, e] = P.rett, x0 = 9 + a, z0 = 9 + b, x1 = 9 + c, z1 = 9 + e, mx = 9 + Math.round((a + c) / 2), mz = 9 + Math.round((b + e) / 2);
  const lato = Math.abs(d.x) > Math.abs(d.z) ? (d.x > 0 ? "E" : "W") : (d.z > 0 ? "S" : "N");
  const cella = { N: [mx, z0], S: [mx, z1], W: [x0, mz], E: [x1, mz] }[lato];
  let f = M.facciaMuro(S.lab, cella[0], cella[1], lato);
  if (!f) for (const k of [-1, 1]) { const cc = lato === "N" || lato === "S" ? [cella[0] + k, cella[1]] : [cella[0], cella[1] + k]; f = M.facciaMuro(S.lab, cc[0], cc[1], lato); if (f) break }
  if (!f) return null;
  const g = new THREE.Group();
  const tela2 = M.tela(768, 576, (cx, w, h) => { cx.fillStyle = "#efe7d4"; cx.fillRect(0, 0, w, h); for (let i = 0; i < 2500; i++) { cx.fillStyle = `rgba(120,90,50,${Math.random() * .06})`; cx.fillRect(Math.random() * w, Math.random() * h, 2, 2) } const COL = ["#d0462f", "#3d7fd9", "#3c9a3c", "#e0a020", "#8a4fc0"]; tratti.forEach((t, i) => { for (let j = 1; j < t.length; j++) gessoTratto(cx, [t[j - 1][0] * 7.68, t[j - 1][1] * 5.76], [t[j][0] * 7.68, t[j][1] * 5.76], 16, COL[i % 5]) }) });
  // carta senza luce propria: sotto il fascio del centro non deve accendersi in un riquadro bianco
  const foglio = new THREE.Mesh(new THREE.PlaneGeometry(1.8, 1.35), new THREE.MeshBasicMaterial({ map: tela2, color: 0xcfc6b2 })); foglio.position.z = .03; g.add(foglio);
  const oro = new THREE.MeshStandardMaterial({ color: 0xb8892e, metalness: .6, roughness: .5 });
  for (const [w, h, x, y] of [[2, .1, 0, .725], [2, .1, 0, -.725], [.1, 1.55, -.95, 0], [.1, 1.55, .95, 0]]) { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, .07), oro); m.position.set(x, y, .035); g.add(m) }
  const targa = new THREE.Mesh(new THREE.PlaneGeometry(.9, .15), new THREE.MeshBasicMaterial({ map: M.tela(512, 84, (cx, w, h) => { cx.fillStyle = "#2a2018"; cx.fillRect(0, 0, w, h); cx.fillStyle = "#e8c06a"; cx.font = "34px Marcellus, serif"; cx.textAlign = "center"; cx.textBaseline = "middle"; cx.fillText(S.nome ? S.nome + ", a cinque anni" : "A cinque anni", w / 2, h / 2 + 2) }) }));
  targa.position.set(0, -.88, .03); g.add(targa);
  M.sulMuro(g, f, 2.55); scena.add(g);
  // le torce troppo vicine al quadro si spostano via
  const via = []; scena.traverse(o => { if (o.userData.torcia && o.position.distanceTo(g.position) < 1.6) via.push(o) }); via.forEach(o => scena.remove(o));
  return g;
}
/* mentre si aspetta la salita: un messaggio a chi eri. Resta sul telefono. */
function letteraAlBambino() {
  return new Promise(res => {
    const box = $("#lettera"), campo = $("#lettera-testo"); box.classList.add("on"); UI.dici("");
    $("#lettera-titolo").textContent = S.nome ? `Cosa diresti a ${S.nome}, a cinque anni?` : "Cosa diresti a chi eri a cinque anni?";
    const chiudi = v => { box.classList.remove("on"); campo.blur(); if (v) { S.scelte.messaggio = v.slice(0, 160); salva() } res() };
    $("#lettera-fatto").onclick = () => { suono.tocco(); chiudi(campo.value.trim()) };
    $("#lettera-salta").onclick = () => { suono.tocco(); chiudi("") };
  });
}

/* ---------- la carta finale ---------- */
async function cartaFinale() {
  const s = S.scelte, righe = [];
  if (s.sogno) righe.push(["5 anni", s.sogno === "nonlo" ? "non sapevi cosa volevi fare" : "volevi " + s.sognoTesto]);
  if (s.strada) righe.push(["18 anni", (s.strada === "sogno" ? "hai riaperto la porta del sogno" : "hai scelto " + s.stradaTesto) + `, in ${s.secondi} secondi, tra ${s.gruppo} porte`]);
  if (s.esito) righe.push(["23 anni", s.speranza === s.esito ? "la moneta ha detto quello che speravi" : (s.seguito === "speranza" ? "hai seguito la speranza, contro la moneta" : "hai seguito la moneta, contro la speranza")]);
  if (s.oracolo) righe.push(["28 anni", s.oracolo === "strada" ? "hai chiesto la strada all'oracolo" : "hai chiesto all'oracolo di farti una domanda"]);
  if (s.segno !== undefined) righe.push(["35 anni", s.segno ? "hai lasciato un segno nel vicolo cieco" : s.spinte ? "hai spinto il muro " + s.spinte + (s.spinte > 1 ? " volte" : " volta") : "hai girato le spalle al muro"]);
  if (s.centro) righe.push(["Da grande", s.centro === "coppa" ? "hai preso la coppa, poi l'hai rimessa a posto" : "hai superato la coppa e hai continuato"]);
  if (s.messaggio) righe.push([S.nome ? "A " + S.nome : "A te, a 5 anni", "«" + s.messaggio + "»"]);
  $("#carta-righe").innerHTML = righe.map(([a, b]) => `<li><b>${a}</b><span>${b}</span></li>`).join("");
  // istantanea dall'alto
  composer.render(); let foto = null; try { foto = tela.toDataURL("image/jpeg", .9) } catch (e) { }
  const img = await creaImmagine(foto, righe); S.immagine = img;
  $("#carta").classList.add("on");
}
function creaImmagine(foto, righe) {
  return new Promise(res => {
    const c = document.createElement("canvas"); c.width = 1080; c.height = 1350; const g = c.getContext("2d");
    const fine = () => {
      const gr = g.createLinearGradient(0, 380, 0, 1350); gr.addColorStop(0, "rgba(12,10,8,0)"); gr.addColorStop(.35, "rgba(12,10,8,.88)"); gr.addColorStop(1, "rgba(12,10,8,.97)"); g.fillStyle = gr; g.fillRect(0, 0, 1080, 1350);
      g.fillStyle = "#DCA645"; g.font = "500 30px 'DM Mono', monospace"; g.fillText("DA GRANDE · IL MIO LABIRINTO", 80, 92);
      g.fillStyle = "#EFE6D2"; g.font = "86px Marcellus, serif"; g.fillText("La mia strada", 80, 700);
      let y = 790; for (const [a, b] of righe) { g.fillStyle = "#E2523F"; g.font = "500 26px 'DM Mono', monospace"; g.fillText(a.toUpperCase(), 80, y); g.fillStyle = "#EFE6D2"; g.font = "36px 'Familjen Grotesk', sans-serif"; const parole = b.split(" "); let riga = "", yy = y + 46; for (const p of parole) { if (g.measureText(riga + p).width > 900) { g.fillText(riga, 80, yy); riga = ""; yy += 44 } riga += p + " " } g.fillText(riga, 80, yy); y = yy + 62 }
      g.fillStyle = "rgba(239,230,210,.6)"; g.font = "500 24px 'DM Mono', monospace"; g.fillText("tlon.it/dagrande · Da Grande Fest 2026", 80, 1290);
      c.toBlob(b => res(b), "image/png");
    };
    if (!foto) { g.fillStyle = "#120d08"; g.fillRect(0, 0, 1080, 1350); fine(); return }
    const im = new Image(); im.onload = () => { const s = Math.max(1080 / im.width, 1350 / im.height); g.drawImage(im, (1080 - im.width * s) / 2, (1350 - im.height * s) / 2, im.width * s, im.height * s); fine() }; im.onerror = () => { g.fillStyle = "#120d08"; g.fillRect(0, 0, 1080, 1350); fine() }; im.src = foto;
  });
}
$("#condividi").onclick = async () => {
  const b = S.immagine; if (!b) return; const file = new File([b], "da-grande.png", { type: "image/png" });
  try { if (navigator.canShare && navigator.canShare({ files: [file] })) { await navigator.share({ files: [file], title: "Da grande", text: "Il mio labirinto" }); return } } catch (e) { if (e.name === "AbortError") return }
  const a = document.createElement("a"); a.href = URL.createObjectURL(b); a.download = "da-grande.png"; a.click();
};
$("#ancora").onclick = () => { $("#carta").classList.remove("on") };

/* ---------- avvio ---------- */
async function prepara() {
  const barra = $("#barra i");
  THREE.DefaultLoadingManager.onProgress = (u, a, b) => { barra.style.width = Math.round(a / b * 100) + "%" };
  try { await Promise.race([Promise.all(["48px Caveat", "48px Marcellus", "48px 'Familjen Grotesk'", "20px 'DM Mono'", "48px 'Permanent Marker'"].map(f => document.fonts.load(f))), pausa(2500)]) } catch (e) { }
  S.lab = M.genera(SEME);
  S.mondo = await M.costruisci(scena, S.lab, { base: "../", env });
  S.extra = []; creaPioggia();
  cam.pos.copy(M.centroCella(1, 1)).add(new THREE.Vector3(.55, 0, .55)); guardaVerso(M.centroCella(0, 0).add(new THREE.Vector3(-.2, 0, .4)), true); cam.pitchU = -.18;
  await new Promise(res => { const ok = () => res(); THREE.DefaultLoadingManager.onLoad = ok; setTimeout(ok, 6000) });
  barra.style.width = "100%"; $("#entra").disabled = false; $("#entra").textContent = "Entra";
}
async function entra() {
  suono.avvia(); try { suono.ctx && suono.ctx.resume() } catch (e) { }
  try { if (window.DeviceOrientationEvent && DeviceOrientationEvent.requestPermission) await DeviceOrientationEvent.requestPermission() } catch (e) { }
  const sveglia = async () => { try { if (navigator.wakeLock && !(S.blocco && !S.blocco.released)) S.blocco = await navigator.wakeLock.request("screen") } catch (e) { } };
  await sveglia(); document.addEventListener("visibilitychange", () => { if (!document.hidden) sveglia() }); tela.addEventListener("pointerdown", sveglia);
  invia("ingresso", "entrato", "1");
  // il soprannome resta sul telefono: serve solo alle voci sui muri
  S.nome = ($("#nome-bimbo").value || "").replace(/[^\p{L}' .-]/gu, "").trim().slice(0, 14); ls.set("dg3-nome", S.nome);
  try { const f = muroCameretta(); if (f) tabellaAltezza(scena, M, f.altezza, S.nome) } catch (e) { console.warn(e) }
  vociPer("cameretta");
  $("#ingresso").classList.add("via"); setTimeout(() => $("#ingresso").remove(), 1500);
  UI.eta("5 anni"); await pausa(1200);
  UI.dici("Hai cinque anni. Muovi il telefono, o trascina il dito, per guardarti intorno.", 5200);
  if (LV.attivo && !LIBERO) {
    S.live = true;
    LV.ascolta(st => { S.palco = +st.s || 0; $("#vivo").textContent = "dal vivo"; $("#vivo").className = "vivo"; S.sblocca && S.sblocca() });
  }
  await pausa(3500);
  if (!PARAM.get("cap") || PARAM.get("cap") === "1") await disegnoIniziale();
  if (S.live && S.palco < 1) {
    UI.dici("Aspetta: il primo capitolo si apre dal palco.");
    let senzaRete = 0; const guardia = setInterval(() => { senzaRete = window.DGLive && DGLive.ascolta && DGLive.ascolta.ok === false ? senzaRete + 5 : 0; if (senzaRete >= 180) { clearInterval(guardia); S.sblocca && S.sblocca(true) } }, 5000);
    const forzato = await new Promise(res => { S.sblocca = (forza) => { if (forza || S.palco >= 1) { S.sblocca = null; res(!!forza) } } });
    clearInterval(guardia); UI.dici("");
    if (forzato) { UI.dici("Il collegamento con il palco si è interrotto: entra da solo."); await UI.scegli([["vai", "Entra nel labirinto"]], "una"); UI.dici("") }
  }
  const capitoli = [capitolo1, capitolo2, capitolo3, capitolo4, capitolo5, capitolo6];
  // per le prove: ?cap=N parte dal capitolo N
  const da = Math.max(1, Math.min(6, +PARAM.get("cap") || 1));
  if (da > 1) { const nomi = ["cameretta", "scuola", "notte", "oracolo", "vicolo", "centro"], P = S.lab.percorsi, prima = P[nomi[da - 2]]; cam.pos.copy(puntoAttesa(prima.ritorno.at(-1), P[nomi[da - 1]].andata[0])); cam.occhio = M.ZONE[nomi[da - 2]].occhio }
  for (const cap of capitoli.slice(da - 1)) await cap();
}
$("#entra").onclick = entra;
prepara().catch(e => { console.error(e); $("#entra").textContent = "Il telefono non regge il 3D"; });
requestAnimationFrame(ciclo);
window.__dg = { S, cam, UI, M, scena, camera, renderer, salta: k => S.palco = k, oltre, finitura, emisfero, luna, get oscurita() { return oscurita } };
