/* Il labirinto · geometria comune a palco e telefoni.
   Labirinto cretese a sette circuiti, come sulle monete di Cnosso.
   Ordine dei circuiti dall'esterno: 3 2 1 4 7 6 5, poi il centro.
   Le cinque stanze stanno sulle svolte: dopo la prima ci si allontana dal centro,
   dopo la seconda si è sul circuito più esterno, poi il percorso precipita verso l'interno. */
(function(){
"use strict";
const T=Math.PI*2;
function percorso(R){
  const u=R/8,r=k=>R-(k-.5)*u,P=(t,q)=>[-q*Math.sin(t),q*Math.cos(t)];
  const pts=[],fine=[];
  const arco=(q,a,b)=>{const n=Math.max(2,Math.ceil(Math.abs(b-a)*q/1.1));for(let i=pts.length?1:0;i<=n;i++)pts.push(P(a+(b-a)*i/n,q))};
  const raggio=(t,a,b)=>{const n=Math.max(2,Math.ceil(Math.abs(b-a)/1.1));for(let i=pts.length?1:0;i<=n;i++)pts.push(P(t,a+(b-a)*i/n))};
  const segna=()=>fine.push(pts.length-1);
  raggio(0,R+u*.9,r(3));segna();
  arco(r(3),0,T-.42);segna();raggio(T-.42,r(3),r(2));
  arco(r(2),T-.42,.2);segna();raggio(.2,r(2),r(1));
  arco(r(1),.2,T-.2);segna();raggio(T-.2,r(1),r(4));
  arco(r(4),T-.2,.3);segna();raggio(.3,r(4),r(7));
  arco(r(7),.3,T-1);segna();raggio(T-1,r(7),r(6));
  arco(r(6),T-1,.7);segna();raggio(.7,r(6),r(5));
  arco(r(5),.7,T-.3);segna();raggio(T-.3,r(5),0);segna();
  const cum=[0];for(let i=1;i<pts.length;i++)cum.push(cum[i-1]+Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]));
  const L=cum[cum.length-1];
  // fine[]: 0 ingresso nel circuito 3, 1 fine del 3, 2 fine del 2, 3 fine dell'1, 4 fine del 4, 5 fine del 7, 6 fine del 6, 7 fine del 5, 8 centro
  const at=i=>cum[i]/L;
  const tappe=[0,at(fine[1]),at(fine[3]),at(fine[4]),at(fine[6]),1];
  function punto(f){f=Math.max(0,Math.min(1,f));const d=f*L;let lo=0,hi=cum.length-1;while(hi-lo>1){const m=(lo+hi)>>1;if(cum[m]<d)lo=m;else hi=m}
    const k=(d-cum[lo])/((cum[hi]-cum[lo])||1);return [pts[lo][0]+(pts[hi][0]-pts[lo][0])*k,pts[lo][1]+(pts[hi][1]-pts[lo][1])*k]}
  function tratto(f0,f1){const a=Math.max(0,f0)*L,b=Math.min(1,f1)*L,out=[punto(f0)];for(let i=0;i<pts.length;i++)if(cum[i]>a&&cum[i]<b)out.push(pts[i]);out.push(punto(f1));return out}
  const d="M"+pts.map(p=>p[0].toFixed(2)+" "+p[1].toFixed(2)).join("L");
  return {R,u,pts,cum,L,d,tappe,punto,tratto,distanza:f=>Math.hypot(...punto(f))/R};
}
const STANZE=[
  {k:"soglia",n:"",t:"La soglia"},
  {k:"porte",n:"I",t:"Le porte"},
  {k:"moneta",n:"II",t:"La moneta"},
  {k:"oracolo",n:"III",t:"L'oracolo"},
  {k:"vicolo",n:"IV",t:"Il vicolo cieco"},
  {k:"uscita",n:"V",t:"Il centro"}
];
/* disegno su canvas: muri d'ocra, corridoio, filo */
function disegna(ctx,geo,{ocra,fondo,filo,fino=0,spessore=1}={}){
  const p=new Path2D(geo.d);ctx.lineCap="round";ctx.lineJoin="round";
  ctx.strokeStyle=ocra;ctx.lineWidth=geo.u*.98*spessore;ctx.stroke(p);
  ctx.strokeStyle=fondo;ctx.lineWidth=geo.u*.66*spessore;ctx.stroke(p);
  ctx.fillStyle=ocra;ctx.beginPath();ctx.arc(0,0,geo.u*.5,0,T);ctx.fill();
  if(fino>0&&filo){const tr=geo.tratto(0,fino);ctx.strokeStyle=filo;ctx.lineWidth=geo.u*.13;ctx.beginPath();tr.forEach((q,i)=>i?ctx.lineTo(q[0],q[1]):ctx.moveTo(q[0],q[1]));ctx.stroke()}
}
window.Filo={percorso,STANZE,disegna};
})();
