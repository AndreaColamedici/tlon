/* Da grande · l'atmosfera del telefono.
   Le quattro luci vere seguono chi cammina: tutto il resto del labirinto sarebbe nero. Qui stanno le luci finte
   (pozze a terra, chiarori sui muri, aloni, coni), il cielo, il pulviscolo di ogni età e il colore di ogni età.
   Niente tele nuove, tutto calcolato negli shader e disegnato a istanze: sui telefoni il limite è la memoria grafica.
   Nel cielo non ci sono stelle, di proposito: quando il tetto si apre, ogni luce che si vede è una persona. */
import * as THREE from "three";

const TONI = {
  cameretta: { alto: 0x2a2358, alone: 0x54386e, nuvole: .1, nuvola: 0x3f3568, sat: 1.05, contr: .95, lift: [.028, .016, .05], gain: [1.05, 1, .97], p: { col: 0xffe2b0, size: 2.4, drift: [.02, .03, -.015], op: .45, quadro: 0 } },
  scuola: { alto: 0x3a4a52, alone: 0x5a6a66, nuvole: .3, nuvola: 0x55625f, sat: .8, contr: 1.04, lift: [0, .018, .018], gain: [.97, 1.02, 1], p: { col: 0xf4f7ff, size: 2.4, drift: [.01, -.015, .01], op: .26, quadro: 0 } },
  notte: { alto: 0x0d1630, alone: 0x5a3020, nuvole: .22, nuvola: 0x241f2c, sat: 1.1, contr: 1.08, lift: [0, .014, .034], gain: [1.03, 1, .98], p: { col: 0xffc080, size: 2.4, drift: [.03, -.04, .02], op: .26, quadro: 0 } },
  oracolo: { alto: 0x071430, alone: 0x123a6a, nuvole: 0, nuvola: 0x06183a, sat: .88, contr: 1.1, lift: [0, .02, .05], gain: [.93, 1, 1.09], p: { col: 0x8fc8ff, size: 2.2, drift: [0, .22, 0], op: .5, quadro: 1 } },
  vicolo: { alto: 0x171b30, alone: 0x3a2c30, nuvole: .75, nuvola: 0x34364a, sat: .9, contr: 1.06, lift: [.008, .014, .03], gain: [1, .99, .99], p: { col: 0xb8c8e0, size: 1.8, drift: [.04, -.06, .03], op: .16, quadro: 0 } },
  ritorno: { alto: 0x2c2048, alone: 0x8a4420, nuvole: .4, nuvola: 0x5a3440, sat: 1, contr: 1.03, lift: [.02, .012, .012], gain: [1.03, 1, .94], p: { col: 0xffa050, size: 2.6, drift: [.02, .16, .01], op: .5, quadro: 0 } },
  centro: { alto: 0x3a2a58, alone: 0xc87830, nuvole: .35, nuvola: 0x8a5040, sat: 1.02, contr: 1, lift: [.028, .018, .012], gain: [1.03, 1, .92], p: { col: 0xffd28a, size: 2.2, drift: [.01, .1, .01], op: .55, quadro: 0 } },
};
TONI.antico = TONI.ritorno;

const VERT_DIST = `uniform float dens;varying float vF;varying vec3 vC;`;

export function atmosfera({ scena, mondo, M, camera, finitura, pr, semplice }) {
  const gruppo = new THREE.Group(); scena.add(gruppo);
  const luce = { value: 1 }, dens = { value: .07 }, tempo = { value: 0 };
  const colore = (hex, k) => new THREE.Color(hex).multiplyScalar(k);

  /* ---------- il cielo ---------- */
  const t0 = TONI.cameretta;
  const cielo = new THREE.Mesh(new THREE.SphereGeometry(180, 24, 16), new THREE.ShaderMaterial({
    // disegnato dopo i muri e dietro di loro: non colora un solo pixel di troppo
    side: THREE.BackSide, transparent: true, depthWrite: false, fog: false,
    uniforms: { basso: { value: scena.fog.color }, alone: { value: new THREE.Color(t0.alone) }, alto: { value: new THREE.Color(t0.alto) }, nuvola: { value: new THREE.Color(t0.nuvola) }, nuvole: { value: t0.nuvole }, luce, t: tempo },
    vertexShader: `varying vec3 vD;void main(){vD=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
    fragmentShader: `uniform vec3 basso;uniform vec3 alone;uniform vec3 alto;uniform vec3 nuvola;uniform float nuvole;uniform float luce;uniform float t;varying vec3 vD;
      float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
      float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1.,0.)),f.x),mix(h(i+vec2(0.,1.)),h(i+vec2(1.,1.)),f.x),f.y);}
      void main(){vec3 d=normalize(vD);float y=max(d.y,0.);
      vec3 c=mix(basso,alone,smoothstep(.0,.16,y));c=mix(c,alto,smoothstep(.1,.7,y));
      if(nuvole>.01){vec2 p=d.xz/(y+.22)*1.3+vec2(t*.012,t*.005);float f=n(p)*.56+n(p*2.1+3.)*.29+n(p*4.3+7.)*.15;c=mix(c,nuvola,smoothstep(.42,.72,f)*nuvole*smoothstep(.02,.22,y));}
      gl_FragColor=vec4(c*mix(.2,1.,luce),1.);}`
  }));
  cielo.renderOrder = -10; cielo.frustumCulled = false; scena.add(cielo);

  /* ---------- le luci finte delle lampade lontane ---------- */
  const lampade = mondo.lampade || [], tmp = new THREE.Object3D();
  const piano = new THREE.PlaneGeometry(1, 1);
  // chiarori: pozze a terra e sui muri, una sola chiamata di disegno
  const chiaroreM = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2,
    uniforms: { dens, luce },
    vertexShader: `${VERT_DIST}varying vec2 vU;void main(){vU=uv-.5;vC=instanceColor;vec4 mv=modelViewMatrix*instanceMatrix*vec4(position,1.);float d=length(mv.xyz)*dens;vF=exp(-d*d);gl_Position=projectionMatrix*mv;}`,
    fragmentShader: `uniform float luce;varying float vF;varying vec3 vC;varying vec2 vU;void main(){float a=max(0.,1.-length(vU)*2.);gl_FragColor=vec4(vC*a*a*vF*luce,1.);}`
  });
  const chiarori = [];
  for (const l of lampade) {
    const f = l.forza ?? 1, c = l.col ?? M.ZONE[l.zona].luce, n = l.n;
    const ax = l.p.x + (n ? n.x * .55 : 0), az = l.p.z + (n ? n.z * .55 : 0);
    chiarori.push({ p: [ax, .018, az], rx: -Math.PI / 2, sx: l.pozza ?? 3.6, sy: l.pozza ?? 3.6, col: colore(c, .5 * f) });
    if (l.muro) chiarori.push({ p: [l.muro.x + n.x * .012, l.p.y, l.muro.z + n.z * .012], giro: Math.atan2(n.x, n.z), sx: 2.6, sy: 3, col: colore(c, .34 * f) });
  }
  if (chiarori.length) {
    const m = new THREE.InstancedMesh(piano, chiaroreM, chiarori.length);
    chiarori.forEach((k, i) => { tmp.position.set(...k.p); tmp.rotation.set(k.rx || 0, k.giro || 0, 0, "YXZ"); tmp.scale.set(k.sx, k.sy, 1); tmp.updateMatrix(); m.setMatrixAt(i, tmp.matrix); m.setColorAt(i, k.col) });
    m.instanceMatrix.needsUpdate = true; m.instanceColor.needsUpdate = true; m.renderOrder = 1; gruppo.add(m);
  }
  // aloni: sempre rivolti a chi guarda, tirati verso di lui per non tagliarsi contro il muro
  const conAlone = lampade.filter(l => l.alone);
  if (conAlone.length) {
    const m = new THREE.InstancedMesh(piano, new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, uniforms: { dens, luce, t: tempo },
      vertexShader: `${VERT_DIST}uniform float t;varying vec2 vU;void main(){vU=uv-.5;vC=instanceColor;vec3 c=(instanceMatrix*vec4(0.,0.,0.,1.)).xyz;float s=length(instanceMatrix[0].xyz);
        vec4 mv=modelViewMatrix*vec4(c,1.);float d=length(mv.xyz);float q=dens*d;float r=sin(t*11.+c.x*7.+c.z*5.)*.06+sin(t*5.3+c.z*3.)*.05;
        vF=exp(-q*q)*smoothstep(.6,2.2,d)*(1.+r);mv.xyz*=max(.2,1.-.55/d);mv.xy+=position.xy*s;gl_Position=projectionMatrix*mv;}`,
      fragmentShader: `uniform float luce;varying float vF;varying vec3 vC;varying vec2 vU;void main(){float a=max(0.,1.-length(vU)*2.);gl_FragColor=vec4(vC*a*a*a*vF*luce,1.);}`
    }), conAlone.length);
    conAlone.forEach((l, i) => { tmp.position.copy(l.p); tmp.rotation.set(0, 0, 0); const s = l.alone; tmp.scale.set(s, s, s); tmp.updateMatrix(); m.setMatrixAt(i, tmp.matrix); m.setColorAt(i, colore(l.col ?? M.ZONE[l.zona].luce, .8 * (l.forza ?? 1))) });
    m.instanceMatrix.needsUpdate = true; m.instanceColor.needsUpdate = true; m.frustumCulled = false; m.renderOrder = 3; gruppo.add(m);
  }
  // coni: l'aria che si vede sotto una lampada
  let coni = null, polvere = null;
  const conConi = lampade.filter(l => l.cono);
  if (conConi.length && !semplice) {
    const g = new THREE.CylinderGeometry(.14, 1, 1, 20, 1, true); g.translate(0, -.5, 0);
    coni = new THREE.InstancedMesh(g, new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, uniforms: { dens, luce },
      vertexShader: `${VERT_DIST}varying float vG;varying vec3 vN;varying vec3 vV;void main(){vC=instanceColor;vec4 mv=modelViewMatrix*instanceMatrix*vec4(position,1.);vN=mat3(modelViewMatrix)*mat3(instanceMatrix)*normal;vV=-mv.xyz;vG=uv.y;float d=length(mv.xyz);float q=d*dens;vF=exp(-q*q)*smoothstep(.8,3.2,d);gl_Position=projectionMatrix*mv;}`,
      fragmentShader: `uniform float luce;varying float vF;varying vec3 vC;varying float vG;varying vec3 vN;varying vec3 vV;void main(){float e=abs(dot(normalize(vN),normalize(vV)));gl_FragColor=vec4(vC*pow(vG,1.6)*e*e*e*vF*luce,1.);}`
    }), conConi.length);
    conConi.forEach((l, i) => { const [lung, larg] = l.cono; tmp.position.copy(l.p); tmp.rotation.set(0, 0, 0); tmp.scale.set(larg, lung, larg); tmp.updateMatrix(); coni.setMatrixAt(i, tmp.matrix); coni.setColorAt(i, colore(l.col ?? M.ZONE[l.zona].luce, .17 * (l.forza ?? 1))) });
    coni.instanceMatrix.needsUpdate = true; coni.instanceColor.needsUpdate = true; coni.renderOrder = 2; gruppo.add(coni);
  }

  /* ---------- gli schermi dell'oracolo sul pavimento bagnato ---------- */
  let riflessi = null;
  if (mondo.schermoPosti && mondo.schermoTex) {
    riflessi = new THREE.InstancedMesh(new THREE.PlaneGeometry(1.1, 2.2), new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2, uniforms: { map: { value: mondo.schermoTex }, dens, forza: { value: 1 }, t: tempo },
      vertexShader: `${VERT_DIST}varying vec2 vU;void main(){vU=uv;vec4 w=instanceMatrix*vec4(position,1.);vec4 mv=modelViewMatrix*w;float d=length(mv.xyz)*dens;vF=exp(-d*d);vC=w.xyz;gl_Position=projectionMatrix*mv;}`,
      fragmentShader: `uniform sampler2D map;uniform float forza;uniform float t;varying float vF;varying vec3 vC;varying vec2 vU;
        void main(){float o=sin(vC.x*9.+vC.z*7.+t*.8)*.018+sin(vC.z*23.+vC.x*5.)*.012;vec3 c=texture2D(map,vec2(vU.x+o,fract(.46+(1.-vU.y)*.3)),2.).rgb;float a=pow(vU.y,1.9)*(1.-pow(abs(vU.x-.5)*2.,3.));gl_FragColor=vec4(c*a*vF*forza*2.2,1.);}`
    }), mondo.schermoPosti.length);
    mondo.schermoPosti.forEach((o, i) => { const n = new THREE.Vector3(0, 0, 1).applyQuaternion(o.quaternion); tmp.position.copy(o.position).addScaledVector(n, 1.1).setY(.02); tmp.rotation.set(-Math.PI / 2, Math.atan2(n.x, n.z), 0, "YXZ"); tmp.scale.set(1, 1, 1); tmp.updateMatrix(); riflessi.setMatrixAt(i, tmp.matrix) });
    riflessi.instanceMatrix.needsUpdate = true; riflessi.renderOrder = 1; gruppo.add(riflessi);
  }

  /* ---------- il pulviscolo di ogni età, attorno a chi guarda ---------- */
  if (!semplice) {
    const n = 240, box = 9, pos = new Float32Array(n * 3), fase = new Float32Array(n);
    for (let i = 0; i < n; i++) { pos.set([Math.random() * box, Math.random() * box, Math.random() * box], i * 3); fase[i] = Math.random() }
    const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(pos, 3)); g.setAttribute("aF", new THREE.BufferAttribute(fase, 1));
    polvere = new THREE.Points(g, new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      uniforms: { col: { value: new THREE.Color(t0.p.col) }, size: { value: t0.p.size * pr }, op: { value: t0.p.op }, quadro: { value: 0 }, scorre: { value: new THREE.Vector3() }, cam: { value: new THREE.Vector3() }, t: tempo, luce },
      vertexShader: `attribute float aF;uniform float size;uniform float op;uniform float t;uniform float luce;uniform vec3 scorre;uniform vec3 cam;varying float vA;
        void main(){vec3 o=vec3(sin(t*.31+aF*19.),cos(t*.23+aF*31.),sin(t*.27+aF*47.))*.25;vec3 r=mod(position+scorre+o-cam,${box.toFixed(1)})-${(box / 2).toFixed(1)};
        vec4 mv=modelViewMatrix*vec4(cam+r,1.);float d=length(r);vA=op*luce*(.45+.55*sin(t*(.6+aF*1.4)+aF*40.))*(1.-smoothstep(3.2,4.5,d))*smoothstep(.35,.9,d);
        gl_PointSize=clamp(size*(.6+aF*.8)*2.4/max(.3,-mv.z),1.,9.);gl_Position=projectionMatrix*mv;}`,
      fragmentShader: `uniform vec3 col;uniform float quadro;varying float vA;void main(){vec2 p=gl_PointCoord-.5;float c=max(0.,1.-length(p)*2.);c=mix(c*c,1.,quadro);gl_FragColor=vec4(col*c*max(vA,0.),1.);}`
    }));
    polvere.frustumCulled = false; polvere.renderOrder = 4; gruppo.add(polvere);
  }

  /* ---------- il colore di ogni età ---------- */
  const u = finitura.uniforms, tn = TONI.cameretta, drift = new THREE.Vector3(...tn.p.drift), tc = new THREE.Color();
  u.sat.value = tn.sat; u.contr.value = tn.contr; u.lift.value.set(...tn.lift); u.gain.value.set(...tn.gain);
  const verso = new THREE.Vector3(); const su = cielo.material.uniforms;
  return {
    aggiorna(dt, t, zona, oscurita, nebbia) {
      const T = TONI[zona] || TONI.antico, k = 1 - Math.exp(-dt * .8);
      tempo.value = t; luce.value = oscurita; dens.value = nebbia;
      cielo.position.copy(camera.position);
      su.alto.value.lerp(tc.setHex(T.alto), k); su.alone.value.lerp(tc.setHex(T.alone), k); su.nuvola.value.lerp(tc.setHex(T.nuvola), k); su.nuvole.value += (T.nuvole - su.nuvole.value) * k;
      u.sat.value += (T.sat - u.sat.value) * k; u.contr.value += (T.contr - u.contr.value) * k; u.lift.value.lerp(verso.set(...T.lift), k); u.gain.value.lerp(verso.set(...T.gain), k);
      if (polvere) { const q = polvere.material.uniforms; drift.lerp(verso.set(...T.p.drift), k); q.scorre.value.addScaledVector(drift, dt); q.cam.value.copy(camera.position); q.col.value.lerp(tc.setHex(T.p.col), k); q.size.value += (T.p.size * pr - q.size.value) * k; q.op.value += (T.p.op - q.op.value) * k; q.quadro.value += (T.p.quadro - q.quadro.value) * k }
      // i lampioni si spengono col buio; i riflessi se ne vanno con i muri dell'oracolo
      for (const m of mondo.luminosi || []) m.emissiveIntensity = m.userData.pieno * oscurita;
      if (riflessi && mondo.schermi) { const f = Math.max(0, 1 + mondo.schermi.position.y / 3); riflessi.material.uniforms.forza.value = f; riflessi.visible = f > .01 }
    },
    // quando il telefono non regge si tolgono prima le cose che riempiono più pixel
    alleggerisci() { if (coni) coni.visible = false; if (polvere) polvere.visible = false }
  };
}
