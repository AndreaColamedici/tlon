/* Da grande · collegamento dal vivo tra il palco e i telefoni.
   Incollare qui l'URL del progetto Supabase e la chiave pubblica
   (Project Settings > API Keys: la "publishable key" sb_publishable_..., oppure la vecchia "anon key").
   Con i due campi vuoti le pagine funzionano lo stesso, in modalità autonoma. */
(function(){
"use strict";
const CONFIG={
  url:"https://tfddbzrvfdoldcbsekvx.supabase.co",
  key:"sb_publishable_P-iweh7iJ7HRhKwUcpZGZQ_-73AXybS"   // chiave pubblica: può stare nel sito
};
const attivo=!!(CONFIG.url&&CONFIG.key);
const base=CONFIG.url.replace(/\/+$/,"");
const intestazioni=()=>{const h={"apikey":CONFIG.key,"Content-Type":"application/json"};if(!/^sb_/.test(CONFIG.key))h.Authorization="Bearer "+CONFIG.key;return h};
const ls={get(k){try{return JSON.parse(localStorage.getItem(k))}catch(e){return null}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}};
const uuid=()=>(window.crypto&&crypto.randomUUID)?crypto.randomUUID():"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g,c=>{const r=Math.random()*16|0;return(c==="x"?r:(r&3|8)).toString(16)});
let dispositivo=ls.get("dg-dispositivo");if(!dispositivo){dispositivo=uuid();ls.set("dg-dispositivo",dispositivo)}

/* ogni richiesta ha un tempo massimo: sul wifi di una sala piena una richiesta appesa non deve fermare niente */
async function chiama(url,opz,ms){
  const ac=window.AbortController?new AbortController():null;const t=ac?setTimeout(()=>ac.abort(),ms||4500):0;
  try{return await fetch(url,{...opz,signal:ac?ac.signal:undefined})}finally{clearTimeout(t)}
}
async function rpc(nome,corpo,ms){const r=await chiama(base+"/rest/v1/rpc/"+nome,{method:"POST",headers:intestazioni(),body:JSON.stringify(corpo||{})},ms);if(!r.ok){let m="HTTP "+r.status;try{const j=await r.json();m=j.message||m}catch(e){}throw new Error(m)}return r.json()}

/* scelte in uscita, con coda che sopravvive alla rete che cade */
let coda=ls.get("dg3-coda")||[],inVolo=false,attesa=0,timer=0;
function invia(stanza,chiave,valore){
  if(!attivo)return;
  coda=coda.filter(r=>!(r.stanza===stanza&&r.chiave===chiave));
  coda.push({dispositivo,stanza,chiave,valore:String(valore).slice(0,20)});ls.set("dg3-coda",coda);
  clearTimeout(timer);timer=setTimeout(svuota,300);
}
async function svuota(){
  if(!attivo||inVolo||!coda.length)return;
  inVolo=true;const lotto=coda.slice(0,40);
  try{const r=await chiama(base+"/rest/v1/dg_voti",{method:"POST",headers:{...intestazioni(),"Prefer":"return=minimal"},body:JSON.stringify(lotto),keepalive:true},6000);
    // un lotto rifiutato dal database (dati non validi) si scarta: non deve bloccare le scelte successive
    if(!r.ok&&![400,403,409,422].includes(r.status))throw new Error("HTTP "+r.status);
    coda=coda.filter(x=>!lotto.includes(x));ls.set("dg3-coda",coda);attesa=0}
  catch(e){attesa=Math.min(30000,(attesa||1500)*2)}
  inVolo=false;if(coda.length)timer=setTimeout(svuota,attesa||200);
}
addEventListener("online",()=>{attesa=0;svuota()});
document.addEventListener("visibilitychange",()=>{if(document.visibilityState==="visible")svuota()});
if(coda.length)setTimeout(svuota,800);

/* orologio del server */
let scarto=0,scartoMisurato=false;
const oraServer=()=>Date.now()+scarto;
async function stato(){const t0=Date.now();const s=await rpc("dg_stato");const t1=Date.now();
  if(s&&s.ora){const stima=Date.parse(s.ora)-(t0+t1)/2;scarto=scartoMisurato?scarto*.6+stima*.4:stima;scartoMisurato=true}return s}

/* ascolto della scena: tempo reale quando c'è, interrogazione periodica sempre (un solo giro alla volta) */
function ascolta(cb){
  if(!attivo)return ()=>{};
  let ultimo="",fermo=false,rt=false,pt=0,inCorso=false;
  const consegna=s=>{if(!s)return;const firma=[s.s,s.b,s.evento_id].join("|");if(firma!==ultimo){ultimo=firma;cb(s)}};
  const giro=async()=>{
    if(fermo||inCorso)return;inCorso=true;clearTimeout(pt);
    try{consegna(await stato());ascolta.ok=true}catch(e){ascolta.ok=false}
    inCorso=false;if(fermo)return;
    const passo=rt?12000:3500+Math.random()*2000;pt=setTimeout(giro,document.hidden?8000:passo)};
  giro();
  try{if(window.supabase&&window.supabase.createClient){
    const cl=window.supabase.createClient(base,CONFIG.key,{auth:{persistSession:false,autoRefreshToken:false}});
    cl.channel("scena").on("postgres_changes",{event:"UPDATE",schema:"public",table:"dg_scena"},p=>consegna(p.new))
      .subscribe(st=>{rt=(st==="SUBSCRIBED")});
  }}catch(e){}
  document.addEventListener("visibilitychange",()=>{if(!document.hidden)giro()});
  return ()=>{fermo=true;clearTimeout(pt)};
}
const vai=(parola,s,b,evento,dato,ritardo)=>rpc("dg_vai",{parola,s,b,evento:evento||null,dato:dato==null?null:String(dato),ritardo_ms:ritardo||0}).then(x=>{if(x&&x.ora){scarto=Date.parse(x.ora)-Date.now()}return x});
const conteggi=dal=>rpc("dg_conteggi",{dal:new Date(dal).toISOString()},6000);
/* segni lasciati nel vicolo cieco: piccoli disegni a gesso, visibili a chi passa dopo */
async function inviaSegno(punti){if(!attivo)return;await chiama(base+"/rest/v1/dg_segni",{method:"POST",headers:{...intestazioni(),"Prefer":"return=minimal"},body:JSON.stringify({dispositivo,punti:String(punti).slice(0,4000)}),keepalive:true},6000)}
const segni=(quanti)=>attivo?rpc("dg_segni_recenti",{quanti:quanti||14,escluso:dispositivo},3500):Promise.resolve([]);
async function presenti(){if(!attivo)return 1;const c=await conteggi(Date.now()-3*3600e3);return c.filter(r=>r.stanza==="ingresso").reduce((s,r)=>s+Number(r.n),0)||1}
/* prima dell'evento: cancella i dati delle prove (serve la parola di regia) */
const azzera=parola=>rpc("dg_azzera",{parola});
window.DGLive={attivo,invia,conteggi,stato,ascolta,vai,oraServer,dispositivo,inviaSegno,segni,presenti,azzera};
})();
