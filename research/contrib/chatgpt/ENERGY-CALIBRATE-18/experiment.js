/* ENERGY-CALIBRATE-18 -- source-free frozen causal change calibration.
 * node experiment.js --smoke | --primary
 * No packages, API, native learner, runner or checkpoint.
 */
const EnergyCalibrate18=(function(){
"use strict";
const N=5,OLD_N=24,NEW_N=16,K=32,NOISE=0.15,CHANGE_PRIOR=0.25;
const FAMILIES=["NULL","SINGLE_EDGE","DOUBLE_EDGE","NONLINEAR_AND"];
const CAL_SEEDS=Array.from({length:120},(_,i)=>91001+11*i);
const PRIMARY_SEEDS=Array.from({length:60},(_,i)=>95003+13*i);
const HYPS=[];for(let mask=1;mask<32;mask++)for(let bias=0;bias<=1;bias++)HYPS.push({mask,bias});
const METHODS=["local_calibrated","local_p80","full_calibrated","full_p95","map_calibrated","raw_new_map","never_change"];
function digest(...v){
 let n=0x811c9dc5;
 for(const part of v){for(const c of String(part)){n=Math.imul((n^c.charCodeAt(0))>>>0,0x01000193)>>>0;}
 n=Math.imul(n^0x9e3779b9,0x85ebca6b)>>>0;}
 n^=n>>>16;n=Math.imul(n,0x7feb352d)>>>0;n^=n>>>15;
 n=Math.imul(n,0x846ca68b)>>>0;return (n^(n>>>16))>>>0;
}
function pop(x){let n=0;while(x){x&=x-1;n++;}return n;}
function parity(h,x){return (pop(h.mask&x)&1)^h.bias;}
function dist(a,b){return pop(a.mask^b.mask)+(a.bias!==b.bias?1:0);}
function probability(seed,family,phase,x,ordinal,bit){
 return (digest(seed,family,phase,x,ordinal,"noise")/4294967296)<NOISE?1-bit:bit;
}
function world(seed,family){
 const eligible=HYPS.filter(h=>h.bias===0&&(pop(h.mask)===2||pop(h.mask)===3));
 const basis=eligible[digest(seed,family,"origin")%eligible.length];
 const OLD={mask:basis.mask,bias:digest(seed,family,"origin-bias")&1},NEW={...OLD};
 let and=null;
 if(family==="SINGLE_EDGE"){
  NEW.mask^=1<<(digest(seed,family,"toggle")%N);
 }else if(family==="DOUBLE_EDGE"){
  const on=[],off=[];for(let i=0;i<N;i++)((OLD.mask>>i)&1?on:off).push(i);
  NEW.mask^=1<<on[digest(seed,family,"remove")%on.length];
  NEW.mask^=1<<off[digest(seed,family,"add")%off.length];
 }else if(family==="NONLINEAR_AND"){
  const a=digest(seed,family,"and-a")%N;
  const b=(a+1+digest(seed,family,"and-b")%(N-1))%N;
  and=[a,b];
 }
 const old=[];
 for(let i=0;i<OLD_N;i++){
  const x=digest(seed,family,"old-x",i)%K;
  old.push([x,probability(seed,family,"old",x,i,parity(OLD,x))]);
 }
 const ranked=Array.from({length:K},(_,i)=>i).sort((a,b)=>digest(seed,family,"scheduled",a)-digest(seed,family,"scheduled",b)||a-b);
 const actions=ranked.slice(0,12);
 for(let i=0;i<4;i++)actions.push(digest(seed,family,"extra",i)%K);
 const counter=Array(K).fill(0),news=[];
 for(const x of actions){
  let y=parity(NEW,x);
  if(and!==null)y^=((x>>and[0])&1)&((x>>and[1])&1);
  news.push([x,probability(seed,family,"new",x,counter[x]++,y)]);
 }
 return {seed,family,old,news,oldTruth:OLD,newTruth:NEW,nonlinear:and,unique:new Set(actions).size,first12:new Set(actions.slice(0,12)).size};
}
function weight(logs){
 const mx=Math.max(...logs),w=logs.map(v=>Math.exp(v-mx)),z=w.reduce((s,v)=>s+v,0);
 return w.map(v=>v/z);
}
function fitOld(events){
 const logp=HYPS.map(h=>events.reduce((s,[x,y])=>s+Math.log(parity(h,x)===y?1-NOISE:NOISE),0));
 const p=weight(logp),i=p.indexOf(Math.max(...p));
 const pred=Array.from({length:K},(_,x)=>{
  let t=NOISE;for(let j=0;j<HYPS.length;j++)t+=(1-2*NOISE)*p[j]*parity(HYPS[j],x);
  return t;
 });
 const snapshot=JSON.stringify({posterior:p,pred});
 const copy=JSON.parse(snapshot);
 const coldEqual=JSON.stringify(copy)===snapshot&&JSON.stringify(copy.pred)===JSON.stringify(pred)&&copy.posterior.length===62;
 return {p,i,pred,coldEqual,operations:HYPS.length*(events.length+K)};
}
function infer(w){
 const old=fitOld(w.old),memo=new Map();
 let likelihoodOps=0;
 function likelihood(j){
  if(!memo.has(j)){
   let ll=0;for(const [x,y] of w.news){ll+=Math.log(parity(HYPS[j],x)===y?1-NOISE:NOISE);likelihoodOps++;}
   memo.set(j,ll);
  }
  return memo.get(j);
 }
 const oldH=HYPS[old.i];
 const localIdx=HYPS.map((h,j)=>({h,j})).filter(o=>o.j!==old.i&&pop(o.h.mask^oldH.mask)<=2).map(o=>o.j);
 function anchorPosterior(i,alternatives){
  let norm=0,alt=0,prOps=0;
  const base=likelihood(i);
  const vals=alternatives.map(j=>{prOps++;return {j,prior:Math.exp(-dist(HYPS[i],HYPS[j]))};});
  norm=vals.reduce((s,x)=>s+x.prior,0);
  for(const v of vals)alt+=(v.prior/norm)*Math.exp(likelihood(v.j)-base);
  const numerator=CHANGE_PRIOR*alt,denominator=(1-CHANGE_PRIOR)+numerator;
  return {p:numerator/denominator,ops:old.operations+likelihoodOps+prOps};
 }
 const local=anchorPosterior(old.i,localIdx);
 const all=HYPS.map((_,j)=>j);
 const map=anchorPosterior(old.i,all.filter(j=>j!==old.i));
 const pivot=Math.max(...all.map(j=>likelihood(j)));
 const evidence=all.map(j=>Math.exp(likelihood(j)-pivot));
 let same=0,changed=0,pairOps=0;
 for(let i=0;i<HYPS.length;i++){
  same+=(1-CHANGE_PRIOR)*old.p[i]*evidence[i];
  const vals=[];let z=0;
  for(let j=0;j<HYPS.length;j++)if(i!==j){
   const d=Math.exp(-dist(HYPS[i],HYPS[j]));z+=d;vals.push([j,d]);pairOps++;
  }
  for(const [j,v] of vals)changed+=CHANGE_PRIOR*old.p[i]*(v/z)*evidence[j];
 }
 const full=changed/(changed+same);
 let maxNew=0;for(let j=1;j<all.length;j++)if(likelihood(j)>likelihood(maxNew))maxNew=j;
 return {p:{local:local.p,map:map.p,full},raw:HYPS[maxNew].mask!==oldH.mask||HYPS[maxNew].bias!==oldH.bias,
  operations:{local:local.ops,full:old.operations+likelihoodOps+pairOps,map:map.ops},oldExact:old.coldEqual};
}
function calibratedThreshold(scores){
 const s=[...scores].sort((a,b)=>a-b);
 const q=Math.min(s.length-1,Math.max(0,Math.ceil(0.97*(s.length+1))-1));
 return {threshold:s[q],rank:q+1,n:s.length};
}
function methodOutcome(z,cal){
 return {
  local_calibrated:z.p.local>cal.local.threshold,
  local_p80:z.p.local>=0.80,
  full_calibrated:z.p.full>cal.full.threshold,
  full_p95:z.p.full>=0.95,
  map_calibrated:z.p.map>cal.map.threshold,
  raw_new_map:z.raw,
  never_change:false
 };
}
function runPrimary(cal,seeds){
 const rows=[];
 for(const seed of seeds)for(const family of FAMILIES){
  const w=world(seed,family),z=infer(w),pred=methodOutcome(z,cal);
  rows.push({seed,family,is_change:family!=="NULL",posterior:z.p,ops:z.operations,predictions:pred,
   raw_map_change:z.raw,old_roundtrip:z.oldExact,first12_unique:w.first12,new_unique:w.unique,
   old_count:w.old.length,new_count:w.news.length,action_digest:digest(JSON.stringify(w.news))});
 }
 const metrics={};
 for(const name of METHODS){
  const yes=rows.filter(r=>r.family==="NULL"),shift=rows.filter(r=>r.family==="SINGLE_EDGE"||r.family==="DOUBLE_EDGE"),nonlin=rows.filter(r=>r.family==="NONLINEAR_AND");
  metrics[name]={false_alarm:yes.filter(r=>r.predictions[name]).length/yes.length,
   familiar_detection:shift.filter(r=>r.predictions[name]).length/shift.length,
   nonlinear_detection:nonlin.filter(r=>r.predictions[name]).length/nonlin.length,
   total_detection:rows.filter(r=>r.is_change&&r.predictions[name]).length/180,
   binary_misclassification:rows.filter(r=>r.predictions[name]!==r.is_change).length/rows.length};
 }
 const known=rows.filter(r=>r.family!=="NONLINEAR_AND");
 const eventBrier={};
 for(const n of ["local","full","map"])eventBrier[n]=known.reduce((s,r)=>s+(r.posterior[n]-Number(r.is_change))**2,0)/known.length;
 const operations={};
 for(const k of ["local","full","map"])operations[k]=rows.reduce((s,r)=>s+r.ops[k],0)/rows.length;
 const candidate=metrics.local_calibrated,full=metrics.full_calibrated,raw=metrics.local_p80;
 const gates={
  false_alarm_pass:candidate.false_alarm<=.05,
  sensitivity_pass:candidate.familiar_detection>=.65&&candidate.familiar_detection>=full.familiar_detection-.10,
  event_brier_pass:eventBrier.local<=eventBrier.full+.025,
  noise_reduction_pass:candidate.false_alarm<=raw.false_alarm && (raw.false_alarm<.10||raw.false_alarm-candidate.false_alarm>=.10),
  operation_proxy_pass:operations.full/operations.local>=2,
  integrity_pass:rows.length===seeds.length*FAMILIES.length&&rows.every(r=>r.old_count===24&&r.new_count===16&&r.first12_unique===12&&r.old_roundtrip)&&
   new Set(rows.map(r=>r.seed+":"+r.family)).size===rows.length
 };
 gates.development_signal=Object.entries(gates).filter(([k])=>k.endsWith("_pass")).every(([,v])=>v===true);
 return {rows,metrics,eventBrier,operations,ratio:operations.full/operations.local,gates};
}
function study(isSmoke){
 if(isSmoke){
  const w=world(90031,"NULL"),z=infer(w);
  return {schema:"energy-calibrate-18-smoke.v1",old_count:w.old.length,new_count:w.news.length,
   unique_first12:w.first12,posterior:z.p,old_roundtrip:z.oldExact};
 }
 const nullCalibration=CAL_SEEDS.map(seed=>infer(world(seed,"NULL")));
 const cal={local:calibratedThreshold(nullCalibration.map(z=>z.p.local)),
  full:calibratedThreshold(nullCalibration.map(z=>z.p.full)),
  map:calibratedThreshold(nullCalibration.map(z=>z.p.map))};
 const primary=runPrimary(cal,PRIMARY_SEEDS);
 return {schema:"energy-calibrate-18-result.v1",calibration_seeds:CAL_SEEDS,primary_seeds:PRIMARY_SEEDS,
  calibration_null_worlds:CAL_SEEDS.length,primary_worlds:primary.rows.length,calibration_thresholds:cal,
  calibration_alarm_count:{local:nullCalibration.filter(z=>z.p.local>cal.local.threshold).length,
   full:nullCalibration.filter(z=>z.p.full>cal.full.threshold).length,
   map:nullCalibration.filter(z=>z.p.map>cal.map.threshold).length},
  old_events_primary:primary.rows.length*OLD_N,new_events_primary:primary.rows.length*NEW_N,
  eventBrier:primary.eventBrier,operations:primary.operations,ratio:primary.ratio,
  metrics:primary.metrics,gates:primary.gates,rows:primary.rows};
}
return {study,world,infer,CAL_SEEDS,PRIMARY_SEEDS,FAMILIES,METHODS};
})();
if(typeof module!=="undefined"&&module.exports){
 module.exports=EnergyCalibrate18;
 if(typeof require!=="undefined" && require.main===module)
  process.stdout.write(JSON.stringify(EnergyCalibrate18.study(process.argv[2]==="--smoke"),null,2)+"\n");
}
