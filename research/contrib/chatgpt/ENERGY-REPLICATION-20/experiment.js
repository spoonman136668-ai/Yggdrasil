/* ENERGY-REPLICATION-20: independently authored source-free five-input causal simulator.
 * Frozen before first calibration or primary evaluation.
 * Node >=18: node experiment.js --smoke | --primary
 * No dependency, external model, network, native weights or checkpoint.
 */
const EnergyReplication20=(()=>{
"use strict";
const REGIMES=[{id:"flip15",noise:.15,calStart:120013,primaryStart:140021},
               {id:"flip20",noise:.20,calStart:160019,primaryStart:180043}];
const FAMILIES=["NULL","SINGLE_EDGE","DOUBLE_EDGE","NONLINEAR_AND"];
const METHODS=["top8","top4","top1","full","full_local"];
const OLDN=24,NEWN=16,INPUTN=32,PC=.25,SHAPES=[];
for(let bits=1;bits<32;bits++)for(let bias=0;bias<2;bias++)SHAPES.push({bits,bias});
function countBits(x){let n=0;for(let i=0;i<5;i++)n+=(x>>i)&1;return n;}
function output(shape,x){return (countBits(shape.bits&x)&1)^shape.bias;}
function diff(a,b){return countBits(a.bits^b.bits)+Number(a.bias!==b.bias);}
function mix(...args){
 let s=0x91e10da5>>>0;
 for(const arg of args){
  for(const c of String(arg)){s=Math.imul(s+c.charCodeAt(0),0x9e3779b1)>>>0;s^=s>>>15;}
  s^=0xb5297a4d;s=Math.imul(s,0x68e31da4)>>>0;s^=s>>>13;
 }
 s=Math.imul(s^(s>>>16),0x7feb352d)>>>0;
 s=Math.imul(s^(s>>>15),0x846ca68b)>>>0;
 return (s^(s>>>16))>>>0;
}
function noisyBit(seed,regime,family,phase,x,index,raw){
 return mix(seed,regime.id,family,phase,x,index,"flip")/4294967296<regime.noise?1-raw:raw;
}
function buildWorld(seed,regime,family){
 const candidates=SHAPES.filter(h=>h.bias===0&&(countBits(h.bits)===2||countBits(h.bits)===3));
 const chosen=candidates[mix(seed,regime.id,family,"oldmask")%candidates.length];
 const original={bits:chosen.bits,bias:mix(seed,regime.id,family,"bias")%2};
 const changed={...original},latent=[];
 if(family==="SINGLE_EDGE")changed.bits^=1<<(mix(seed,regime.id,family,"one")%5);
 if(family==="DOUBLE_EDGE"){
  const active=[],inactive=[];for(let i=0;i<5;i++)(((original.bits>>i)&1)?active:inactive).push(i);
  changed.bits^=1<<active[mix(seed,regime.id,family,"remove")%active.length];
  changed.bits^=1<<inactive[mix(seed,regime.id,family,"add")%inactive.length];
 }
 if(family==="NONLINEAR_AND"){
  const i=mix(seed,regime.id,family,"i")%5;
  latent.push(i,(i+1+mix(seed,regime.id,family,"j")%4)%5);
 }
 const old=[];
 for(let t=0;t<OLDN;t++){
  const x=mix(seed,regime.id,family,"old-context",t)%INPUTN;
  old.push([x,noisyBit(seed,regime,family,"old",x,t,output(original,x))]);
 }
 const contexts=Array.from({length:INPUTN},(_,i)=>i);
 contexts.sort((a,b)=>mix(seed,regime.id,family,"choose",a)-mix(seed,regime.id,family,"choose",b)||a-b);
 const schedule=contexts.slice(0,12);
 for(let i=0;i<4;i++)schedule.push(mix(seed,regime.id,family,"extra",i)%INPUTN);
 const newCounts=Array(INPUTN).fill(0),fresh=[];
 for(const x of schedule){
  let bit=output(changed,x);
  if(latent.length)bit^=((x>>latent[0])&1)&((x>>latent[1])&1);
  fresh.push([x,noisyBit(seed,regime,family,"new",x,newCounts[x]++,bit)]);
 }
 return {seed,family,regime:regime.id,old,fresh,oldShape:original,newShape:changed,
 nonlinear:latent.length>0,schedule,source_truth_hidden_from_models:true};
}
function normalizeLog(xs){
 const peak=Math.max(...xs),f=xs.map(x=>Math.exp(x-peak)),s=f.reduce((a,b)=>a+b,0);
 return f.map(z=>z/s);
}
function fitOld(world,regime){
 let ops=0;
 const log=SHAPES.map(h=>{
  let value=0;
  for(const [x,y] of world.old){value+=Math.log(output(h,x)===y?1-regime.noise:regime.noise);ops++;}
  return value;
 });
 const posterior=normalizeLog(log);
 const order=Array.from({length:SHAPES.length},(_,i)=>i).sort((a,b)=>posterior[b]-posterior[a]||a-b);
 const prediction=Array.from({length:INPUTN},(_,x)=>{
  let p=regime.noise;
  for(let i=0;i<SHAPES.length;i++){p+=(1-2*regime.noise)*posterior[i]*output(SHAPES[i],x);ops++;}
  return p;
 });
 const snapshot=JSON.stringify({posterior,prediction});
 const coldSameProcess=JSON.stringify(JSON.parse(snapshot))===snapshot;
 return {posterior,order,prediction,ops,coldSameProcess,snapshot};
}
function detector(old,world,regime,method){
 const cap=method==="top1"?1:method==="top4"?4:method==="top8"?8:62;
 let anchors=[],mass=0;
 for(const i of old.order){
  anchors.push(i);mass+=old.posterior[i];
  if(method==="full"||method==="full_local")continue;
  if(anchors.length>=cap||mass>=.95)break;
 }
 let transitions=0,likelihoodOps=0;const ll=new Map(),terms=[];
 function likelihood(i){
  if(!ll.has(i)){
   let value=0;
   for(const [x,y] of world.fresh){
    value+=Math.log(output(SHAPES[i],x)===y?1-regime.noise:regime.noise);
    likelihoodOps++;
   }
   ll.set(i,value);
  }
  return ll.get(i);
 }
 const radius=method==="full"?5:2;
 for(const i of anchors){
  const weight=old.posterior[i]/mass;
  const options=[];
  let total=0;
  for(let j=0;j<SHAPES.length;j++){
   if(i===j||countBits(SHAPES[i].bits^SHAPES[j].bits)>radius)continue;
   const w=Math.exp(-diff(SHAPES[i],SHAPES[j]));options.push([j,w]);total+=w;transitions++;
  }
  terms.push({log:Math.log((1-PC)*weight)+likelihood(i),changed:false});
  for(const [j,w] of options)terms.push({log:Math.log(PC*weight*w/total)+likelihood(j),changed:true});
 }
 const peak=Math.max(...terms.map(t=>t.log));
 let same=0,different=0;
 for(const t of terms){const v=Math.exp(t.log-peak);if(t.changed)different+=v;else same+=v;}
 return {p:different/(different+same),ops:old.ops+likelihoodOps+transitions,
   old_used:anchors.length,old_mass:mass,new_likelihood_hypotheses:ll.size,transitions};
}
function getScore(world,regime){
 const old=fitOld(world,regime),detectors={};
 for(const m of METHODS)detectors[m]=detector(old,world,regime,m);
 return {scores:detectors,coldSameProcess:old.coldSameProcess,
  first12_unique:new Set(world.schedule.slice(0,12)).size,
  old_event_count:world.old.length,new_event_count:world.fresh.length,
  action_trace:world.fresh,old_prediction_digest:mix(old.snapshot)};
}
function quantile(data){
 const sorted=data.slice().sort((a,b)=>a-b),rank=Math.ceil(.98*(data.length+1));
 return {rank,size:data.length,cutoff:sorted[rank-1]};
}
function summarize(rows,cuts){
 const report={};
 for(const name of METHODS){
  const changed=rows.filter(w=>w.family==="SINGLE_EDGE"||w.family==="DOUBLE_EDGE"),nulls=rows.filter(w=>w.family==="NULL");
  const known=rows.filter(w=>w.family!=="NONLINEAR_AND"),out=rows.filter(w=>w.family==="NONLINEAR_AND");
  const vote=x=>x.scores[name].p>cuts[name].cutoff;
  const rate=xs=>xs.filter(vote).length/xs.length;
  const brier=known.reduce((v,w)=>v+(w.scores[name].p-Number(w.family!=="NULL"))**2,0)/known.length;
  report[name]={null_fpr:rate(nulls),familiar_recall:rate(changed),nonlinear_recall:rate(out),
   event_brier:brier,avg_ops:rows.reduce((v,w)=>v+w.scores[name].ops,0)/rows.length,
   avg_old_hypotheses:rows.reduce((v,w)=>v+w.scores[name].old_used,0)/rows.length};
 }
 return report;
}
function trial(smoke=false){
 if(smoke){
  const w=buildWorld(119071,REGIMES[0],"NULL"),s=getScore(w,REGIMES[0]);
  return {schema:"energy-replication-20-smoke.v1",old:s.old_event_count,new:s.new_event_count,first12:s.first12_unique,cold:s.coldSameProcess,models:METHODS};
 }
 const results=[];
 for(const regime of REGIMES){
  const calibration=[];
  for(let i=0;i<120;i++){
   const seed=regime.calStart+23*i,w=buildWorld(seed,regime,"NULL"),z=getScore(w,regime);
   calibration.push({seed,noise:regime.noise,scores:Object.fromEntries(METHODS.map(m=>[m,z.scores[m].p])),cold:z.coldSameProcess});
  }
  const cuts=Object.fromEntries(METHODS.map(m=>[m,quantile(calibration.map(z=>z.scores[m]))]));
  const primary=[];
  for(let i=0;i<60;i++)for(const family of FAMILIES){
   const seed=regime.primaryStart+29*i,w=buildWorld(seed,regime,family),z=getScore(w,regime);
   primary.push({seed,family,noise:regime.noise,scores:z.scores,cold:z.coldSameProcess,
    first12_unique:z.first12_unique,old_event_count:z.old_event_count,new_event_count:z.new_event_count,
    action_trace:z.action_trace,old_prediction_digest:z.old_prediction_digest});
  }
  const summary=summarize(primary,cuts),a=summary.top8,b=summary.full;
  const gates={
   false_alarm_pass:a.null_fpr<=.05&&a.null_fpr<=b.null_fpr+.025,
   recall_pass:a.familiar_recall>=(regime.noise===.15?.70:.55)&&a.familiar_recall>=b.familiar_recall-.10,
   brier_pass:a.event_brier<=b.event_brier+.020,
   operations_pass:b.avg_ops/a.avg_ops>=1.5,
   integrity_pass:calibration.every(x=>x.cold)&&primary.length===240&&primary.every(x=>
    x.cold&&x.first12_unique===12&&x.old_event_count===OLDN&&x.new_event_count===NEWN)&&
    cuts.top8.rank===119&&cuts.full.rank===119
  };
  gates.pass=Object.entries(gates).filter(([k])=>k.endsWith("_pass")).every(([,v])=>v);
  results.push({regime:regime.id,noise:regime.noise,calibration,thresholds:cuts,primary,summary,gates});
 }
 return {schema:"energy-replication-20-result.v1",results,
  total_calibration_worlds:results.reduce((s,x)=>s+x.calibration.length,0),
  total_primary_worlds:results.reduce((s,x)=>s+x.primary.length,0),
  verdict:results.every(x=>x.gates.pass)?"DEV_SIGNAL_UNQUALIFIED":"SCIENTIFIC_NO_GO"};
}
return {trial,REGIMES,FAMILIES,METHODS};
})();
if(typeof module!=="undefined"&&module.exports){
 module.exports=EnergyReplication20;
 if(typeof require!=="undefined"&&require.main===module){
  process.stdout.write(JSON.stringify(EnergyReplication20.trial(process.argv[2]==="--smoke"),null,2)+"\n");
 }
}
