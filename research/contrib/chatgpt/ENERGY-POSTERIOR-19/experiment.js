/* ENERGY-POSTERIOR-19 -- frozen source-free posterior-mass causal repair trial.
   Node >=18: node experiment.js --smoke or --primary
   No native weights, network, original protected source, runner or paid API.
 */
const EnergyPosterior19=(function(){
"use strict";
const N=5,K=32,OLD_N=24,NEW_N=16,NOISE=0.15,PCHANGE=0.25;
const CAL_SEEDS=Array.from({length:160},(_,i)=>101003+17*i);
const PRIMARY_SEEDS=Array.from({length:80},(_,i)=>107011+19*i);
const FAMILIES=["NULL","SINGLE_EDGE","DOUBLE_EDGE","NONLINEAR_AND"];
const H=[];for(let mask=1;mask<32;mask++)for(let bias=0;bias<2;bias++)H.push({mask,bias});
const MODELS=["local_p95_cap8","local_map1","local_p95_cap4","local_p95_cap8_full","exact_full","global_map"];
const POLICIES=["local_p95_cap8","local_map1","local_p95_cap4","local_p95_cap8_full","exact_full","global_map","never_change"];
function h32(...parts){
 let s=0x9e3779b9;
 for(const p of parts){
  for(const ch of String(p)){s=Math.imul((s^ch.charCodeAt(0))>>>0,0x85ebca6b)>>>0;s^=s>>>13;}
  s=(Math.imul(s^0xc2b2ae35,0x27d4eb2d)^(s>>>15))>>>0;
 }
 s^=s>>>16;s=Math.imul(s,0x7feb352d)>>>0;s^=s>>>15;
 s=Math.imul(s,0x846ca68b)>>>0;return (s^(s>>>16))>>>0;
}
function pop(x){let n=0;while(x){x&=x-1;n++;}return n;}
function parity(x,a){return (pop(x&a.mask)&1)^a.bias;}
function distance(a,b){return pop(a.mask^b.mask)+(a.bias!==b.bias?1:0);}
function draw(seed,fam,phase,x,index,raw){
 return h32(seed,fam,phase,x,index,"n")/4294967296<NOISE?1-raw:raw;
}
function makeWorld(seed,fam){
 const oldSet=H.filter(x=>x.bias===0&&[2,3].includes(pop(x.mask)));
 const src=oldSet[h32(seed,fam,"oldmask")%oldSet.length];
 const old={mask:src.mask,bias:h32(seed,fam,"bias")%2},next={...old};
 let nonlinear=null;
 if(fam==="SINGLE_EDGE")next.mask^=1<<(h32(seed,fam,"edge")%N);
 if(fam==="DOUBLE_EDGE"){
  const on=[],off=[];for(let i=0;i<N;i++)((old.mask&(1<<i))?on:off).push(i);
  next.mask^=1<<on[h32(seed,fam,"remove")%on.length];
  next.mask^=1<<off[h32(seed,fam,"add")%off.length];
 }
 if(fam==="NONLINEAR_AND"){
  const a=h32(seed,fam,"nonlinear-a")%N;
  nonlinear=[a,(a+1+h32(seed,fam,"nonlinear-b")%(N-1))%N];
 }
 const oldData=[];
 for(let i=0;i<OLD_N;i++){
  const x=h32(seed,fam,"oldinput",i)%K;
  oldData.push([x,draw(seed,fam,"old",x,i,parity(x,old))]);
 }
 const all=Array.from({length:K},(_,i)=>i);
 all.sort((a,b)=>h32(seed,fam,"schedule",a)-h32(seed,fam,"schedule",b)||a-b);
 const contexts=all.slice(0,12);
 for(let i=0;i<4;i++)contexts.push(h32(seed,fam,"extra",i)%K);
 const seen=Array(K).fill(0),newData=[];
 for(const x of contexts){
  let raw=parity(x,next);
  if(nonlinear)raw^=((x>>nonlinear[0])&1)&((x>>nonlinear[1])&1);
  newData.push([x,draw(seed,fam,"new",x,seen[x]++,raw)]);
 }
 return {seed,fam,oldData,newData,contexts,oldTruth:old,newTruth:next,nonlinear};
}
function normalizeLog(x){
 const mx=Math.max(...x),v=x.map(z=>Math.exp(z-mx)),sum=v.reduce((a,b)=>a+b,0);
 return v.map(z=>z/sum);
}
function fitOld(data){
 const logp=H.map(a=>data.reduce((s,[x,y])=>s+Math.log(parity(x,a)===y?1-NOISE:NOISE),0));
 const p=normalizeLog(logp),rank=Array.from({length:H.length},(_,i)=>i).sort((a,b)=>p[b]-p[a]||a-b);
 const readout=Array.from({length:K},(_,x)=>NOISE+(1-2*NOISE)*H.reduce((s,a,i)=>s+p[i]*parity(x,a),0));
 const snapshot=JSON.stringify({posterior:p,readout});
 const copy=JSON.parse(snapshot);
 if(JSON.stringify(copy)!==snapshot)throw Error("same-process OLD snapshot parity failure");
 return {posterior:p,rank,readout,oldCost:H.length*(OLD_N+K),snapshot};
}
function likelihood(h,data){
 let value=0;for(const [x,y] of data)value+=Math.log(parity(x,H[h])===y?1-NOISE:NOISE);
 return value;
}
function inference(w,old,variant){
 const limit=variant==="local_map1"||variant==="global_map"?1:
  variant==="local_p95_cap4"?4:variant==="exact_full"?62:8;
 const ranked=old.rank;
 let chosen=[],mass=0;
 for(const i of ranked){
  chosen.push(i);mass+=old.posterior[i];
  if(chosen.length>=limit || (variant!=="exact_full" && mass>=0.95))break;
 }
 if(variant==="exact_full")chosen=ranked.slice();
 const posteriorNorm=chosen.reduce((s,i)=>s+old.posterior[i],0);
 const fullRadius=variant==="exact_full"||variant==="global_map"||variant==="local_p95_cap8_full";
 let ops=old.oldCost,transitions=0,likOps=0;
 const LL=new Map(),terms=[];
 function logLike(j){
  if(!LL.has(j)){LL.set(j,likelihood(j,w.newData));likOps+=w.newData.length;}
  return LL.get(j);
 }
 for(const i of chosen){
  const wOld=old.posterior[i]/posteriorNorm;
  const a=H[i];
  const alternatives=[];let norm=0;
  for(let j=0;j<H.length;j++)if(j!==i&&(fullRadius||pop(a.mask^H[j].mask)<=2)){
   const value=Math.exp(-distance(a,H[j]));
   alternatives.push([j,value]);norm+=value;transitions++;
  }
  terms.push({lv:Math.log(wOld*(1-PCHANGE))+logLike(i),changed:false});
  for(const [j,weight] of alternatives)
   terms.push({lv:Math.log(wOld*PCHANGE*weight/norm)+logLike(j),changed:true});
 }
 const highest=Math.max(...terms.map(t=>t.lv));
 let no=0,yes=0;
 for(const term of terms)(term.changed?(yes+=Math.exp(term.lv-highest)):(no+=Math.exp(term.lv-highest)));
 const p=yes/(no+yes);
 return {posterior:p,ops:ops+likOps+transitions,
  old_count:chosen.length,old_mass:posteriorNorm,new_likelihoods:LL.size,
  transition_terms:transitions};
}
function threshold(scores){
 const ordered=[...scores].sort((a,b)=>a-b);
 const rank=Math.ceil(0.97*(ordered.length+1));
 return {cutoff:ordered[rank-1],rank,n:ordered.length};
}
function scoreWorld(w,old,calibration){
 const computed={};for(const m of MODELS)computed[m]=inference(w,old,m);
 const alerts={};for(const m of MODELS)alerts[m]=computed[m].posterior>calibration[m].cutoff;
 alerts.never_change=false;
 return {seed:w.seed,family:w.fam,truth_changed:w.fam!=="NULL",old_events:w.oldData.length,new_events:w.newData.length,
  first12_unique:new Set(w.contexts.slice(0,12)).size,new_unique:new Set(w.contexts).size,
  action_trace:w.newData,old_snapshot:w.seed===-1?old.snapshot:undefined,
  old_roundtrip:JSON.stringify(JSON.parse(old.snapshot))===old.snapshot,
  data:computed,alerts};
}
function study(smoke){
 if(smoke){
  const w=makeWorld(100901,"NULL"),o=fitOld(w.oldData);
  const inferred={};for(const m of MODELS)inferred[m]=inference(w,o,m);
  return {schema:"energy-posterior-19-smoke.v1",source_world:100901,old:w.oldData.length,new:w.newData.length,unique12:new Set(w.contexts.slice(0,12)).size,roundtrip:true,inferred};
 }
 const calibrationWorlds=CAL_SEEDS.map(seed=>{const w=makeWorld(seed,"NULL"),o=fitOld(w.oldData),scores={};
  for(const m of MODELS)scores[m]=inference(w,o,m).posterior;
  return {seed,scores,old_roundtrip:JSON.stringify(JSON.parse(o.snapshot))===o.snapshot};
 });
 const modelCalibration={};
 for(const m of MODELS)modelCalibration[m]=threshold(calibrationWorlds.map(w=>w.scores[m]));
 const primary=[];
 for(const seed of PRIMARY_SEEDS)for(const family of FAMILIES){
  const w=makeWorld(seed,family),o=fitOld(w.oldData);
  primary.push(scoreWorld(w,o,modelCalibration));
 }
 const summary={};const sample=(f)=>primary.filter(f);
 const nullRows=sample(w=>w.family==="NULL");
 const changedRows=sample(w=>w.family==="SINGLE_EDGE"||w.family==="DOUBLE_EDGE");
 const familiar=sample(w=>w.family!=="NONLINEAR_AND");
 const nonlinearRows=sample(w=>w.family==="NONLINEAR_AND");
 for(const m of POLICIES){
  const isDetector=m!=="never_change";
  const a=(items)=>items.filter(w=>w.alerts[m]).length/items.length;
  const eventBrier=isDetector?familiar.reduce((s,w)=>s+(w.data[m].posterior-Number(w.truth_changed))**2,0)/familiar.length:null;
  summary[m]={null_alarm:a(nullRows),familiar_recall:a(changedRows),nonlinear_recall:a(nonlinearRows),familiar_event_brier:eventBrier,
   mean_ops:isDetector?primary.reduce((s,w)=>s+w.data[m].ops,0)/primary.length:null,
   mean_old_hypotheses:isDetector?primary.reduce((s,w)=>s+w.data[m].old_count,0)/primary.length:null,
   mean_retained_old_mass:isDetector?primary.reduce((s,w)=>s+w.data[m].old_mass,0)/primary.length:null};
 }
 const cand=summary.local_p95_cap8,base=summary.local_map1,full=summary.exact_full;
 const gates={
  null_false_alarm_pass:cand.null_alarm<=.05,
  shifted_detection_pass:cand.familiar_recall>=.75 && cand.familiar_recall>=full.familiar_recall-.10,
  improvement_over_map_pass:cand.familiar_recall>=base.familiar_recall+.05&&cand.null_alarm<=base.null_alarm+.025,
  proper_brier_pass:cand.familiar_event_brier<=full.familiar_event_brier+.020&&cand.familiar_event_brier<=base.familiar_event_brier+.005,
  compute_proxy_pass:full.mean_ops/cand.mean_ops>=1.5,
  trace_and_retention_pass:primary.length===320&&primary.every(w=>w.old_events===24&&w.new_events===16&&w.first12_unique===12&&w.old_roundtrip)&&calibrationWorlds.every(w=>w.old_roundtrip),
  nonlinear_pass:cand.nonlinear_recall>=base.nonlinear_recall-.05
 };
 gates.development_signal=Object.entries(gates).filter(([k])=>k.endsWith("_pass")).every(([,v])=>v===true);
 return {schema:"energy-posterior-19-result.v1",calibration_seeds:CAL_SEEDS,primary_seeds:PRIMARY_SEEDS,
  calibration_null_worlds:calibrationWorlds.length,primary_worlds:primary.length,
  calibration_world_scores:calibrationWorlds,calibration_thresholds:modelCalibration,
  primary_world_scores:primary,summary,gates,
  old_events_primary:primary.length*OLD_N,new_events_primary:primary.length*NEW_N,
  operation_ratio:full.mean_ops/cand.mean_ops};
}
return {study,CAL_SEEDS,PRIMARY_SEEDS,FAMILIES,MODELS,POLICIES};
})();
if(typeof module!=="undefined"&&module.exports){
 module.exports=EnergyPosterior19;
 if(typeof require!=="undefined"&&require.main===module)
  process.stdout.write(JSON.stringify(EnergyPosterior19.study(process.argv[2]==="--smoke"),null,2)+"\n");
}
