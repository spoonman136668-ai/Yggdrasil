/* ENERGY-FACTORS-21: frozen 20%-noise posterior-mass x NEW-search-radius falsifier.
 * source-free, separate implementation, no prior experiment imported.
 * Node >=18: node experiment.js --smoke|--primary
 */
const EnergyFactors21=(()=>{
"use strict";
const NOISE=.20,CHANGE=.25,INPUTS=32,OLD_N=24,NEW_N=16;
const FAMILIES=["NULL","SINGLE_EDGE","DOUBLE_EDGE","NONLINEAR_AND"];
const CONFIG=[
 {id:"old_top8_new_local2",old:"top8",newRadius:2},
 {id:"old_top8_new_global",old:"top8",newRadius:5},
 {id:"old_full_new_local2",old:"full",newRadius:2},
 {id:"old_full_new_global",old:"full",newRadius:5},
 {id:"old_top4_new_local2",old:"top4",newRadius:2},
 {id:"old_map_new_local2",old:"map",newRadius:2}
];
const MODEL=[];for(let mask=1;mask<32;mask++)for(let bias=0;bias<2;bias++)MODEL.push({mask,bias});
const CAL=Array.from({length:200},(_,i)=>210007+31*i);
const EVAL=Array.from({length:96},(_,i)=>225011+37*i);
function mix(...parts){
 let a=0xc4ce94e3>>>0;
 for(const part of parts){
  const s=String(part);for(let i=0;i<s.length;i++){
   a=(a^s.charCodeAt(i))>>>0;a=Math.imul(a,0x7feb352d)>>>0;
   a=(a^(a>>>15))>>>0;
  }
  a=Math.imul(a^0x9e3779b9,0x846ca68b)>>>0;
 }
 a^=a>>>16;a=Math.imul(a,0x85ebca6b)>>>0;return (a^(a>>>13))>>>0;
}
function nbits(z){let n=0;while(z){z&=z-1;n++;}return n;}
function bit(h,x){return (nbits(h.mask&x)&1)^h.bias;}
function dist(a,b){return nbits(a.mask^b.mask)+Number(a.bias!==b.bias);}
function sample(seed,scenario,phase,x,k,truth){
 const flip=mix(seed,scenario,phase,x,k,"flip")/4294967296<NOISE;
 return flip?1-truth:truth;
}
function generate(seed,scenario){
 const base=MODEL.filter(h=>h.bias===0&&(nbits(h.mask)===2||nbits(h.mask)===3));
 const chosen=base[mix(seed,scenario,"oldmask")%base.length];
 const h0={mask:chosen.mask,bias:mix(seed,scenario,"oldbias")%2},h1={...h0};
 let gate=null;
 if(scenario==="SINGLE_EDGE")h1.mask^=1<<(mix(seed,scenario,"toggle")%5);
 if(scenario==="DOUBLE_EDGE"){
  const on=[],off=[];for(let b=0;b<5;b++)((h0.mask>>b)&1?on:off).push(b);
  h1.mask^=1<<on[mix(seed,scenario,"removed")%on.length];
  h1.mask^=1<<off[mix(seed,scenario,"added")%off.length];
 }
 if(scenario==="NONLINEAR_AND"){
  const a=mix(seed,scenario,"a")%5;
  gate=[a,(a+1+mix(seed,scenario,"b")%4)%5];
 }
 const old=[];
 for(let k=0;k<OLD_N;k++){
  const x=mix(seed,scenario,"oldinput",k)%INPUTS;
  old.push([x,sample(seed,scenario,"old",x,k,bit(h0,x))]);
 }
 const contexts=Array.from({length:INPUTS},(_,x)=>x);
 contexts.sort((a,b)=>mix(seed,scenario,"permutation",a)-mix(seed,scenario,"permutation",b)||a-b);
 const actions=contexts.slice(0,12);
 for(let k=0;k<4;k++)actions.push(mix(seed,scenario,"extra",k)%INPUTS);
 const counts=Array(INPUTS).fill(0),fresh=[];
 for(const x of actions){
  let expected=bit(h1,x);
  if(gate)expected^=((x>>gate[0])&1)&((x>>gate[1])&1);
  fresh.push([x,sample(seed,scenario,"fresh",x,counts[x]++,expected)]);
 }
 return {seed,scenario,old,fresh,first12new:new Set(actions.slice(0,12)).size,
  hidden_truth:{old:h0,new:h1,gate}};
}
function normalized(logs){
 const hi=Math.max(...logs),w=logs.map(v=>Math.exp(v-hi)),tot=w.reduce((s,v)=>s+v,0);
 return w.map(v=>v/tot);
}
function inferOld(old){
 let work=0;
 const logs=MODEL.map(h=>{
  let total=0;for(const [x,y] of old){total+=Math.log(y===bit(h,x)?1-NOISE:NOISE);work++;}
  return total;
 });
 const probability=normalized(logs);
 const rank=Array.from({length:MODEL.length},(_,i)=>i).sort((a,b)=>probability[b]-probability[a]||a-b);
 const readout=Array.from({length:INPUTS},(_,x)=>{
  let p=NOISE;for(let i=0;i<MODEL.length;i++){p+=(1-2*NOISE)*probability[i]*bit(MODEL[i],x);work++;}
  return p;
 });
 const snapshot=JSON.stringify({probability,readout});
 return {probability,rank,work,retentionSameProcess:JSON.stringify(JSON.parse(snapshot))===snapshot,snapshot};
}
function inferNext(old,fresh,setting){
 const eligible=[];
 let coverage=0;
 const limit=setting.old==="full"?62:setting.old==="top8"?8:setting.old==="top4"?4:1;
 for(const i of old.rank){
  eligible.push(i);coverage+=old.probability[i];
  if(setting.old==="full")continue;
  if(eligible.length>=limit||coverage>=.95)break;
 }
 const terms=[],memo=new Map();
 let likelihoodWork=0,transitionWork=0;
 function ll(i){
  if(!memo.has(i)){
   let total=0;for(const [x,y] of fresh){total+=Math.log(bit(MODEL[i],x)===y?1-NOISE:NOISE);likelihoodWork++;}
   memo.set(i,total);
  }
  return memo.get(i);
 }
 for(const i of eligible){
  const prior=old.probability[i]/coverage,choices=[];let z=0;
  for(let j=0;j<MODEL.length;j++){
   if(j===i||nbits(MODEL[i].mask^MODEL[j].mask)>setting.newRadius)continue;
   const v=Math.exp(-dist(MODEL[i],MODEL[j]));choices.push([j,v]);z+=v;transitionWork++;
  }
  terms.push({change:false,log:Math.log((1-CHANGE)*prior)+ll(i)});
  for(const [j,weight] of choices)terms.push({change:true,log:Math.log(CHANGE*prior*weight/z)+ll(j)});
 }
 const peak=Math.max(...terms.map(x=>x.log));
 let changed=0,unchanged=0;
 for(const t of terms){
  const e=Math.exp(t.log-peak);if(t.change)changed+=e;else unchanged+=e;
 }
 return {p:changed/(changed+unchanged),old_used:eligible.length,old_mass:coverage,
  ops:old.work+likelihoodWork+transitionWork,likelihood_ops:likelihoodWork,transition_ops:transitionWork};
}
function evaluate(w){
 const old=inferOld(w.old),score={};
 for(const conf of CONFIG)score[conf.id]=inferNext(old,w.fresh,conf);
 return {seed:w.seed,scenario:w.scenario,truth_change:w.scenario!=="NULL",
  old_events:w.old,actions:w.fresh,first12new:w.first12new,old_snapshot_roundtrip:old.retentionSameProcess,
  scores:score};
}
function cutoff(scores,rank){
 const ordered=scores.slice().sort((a,b)=>a-b);
 return {n:ordered.length,rank,cutoff:ordered[rank-1]};
}
function summary(primary,thresholds){
 const out={};
 for(const cfg of CONFIG){
  const name=cfg.id,known=primary.filter(w=>w.scenario!=="NONLINEAR_AND");
  const nulls=primary.filter(w=>w.scenario==="NULL");
  const shifted=primary.filter(w=>w.scenario==="SINGLE_EDGE"||w.scenario==="DOUBLE_EDGE");
  const odd=primary.filter(w=>w.scenario==="NONLINEAR_AND");
  const calc={event_brier:known.reduce((s,w)=>s+(w.scores[name].p-Number(w.truth_change))**2,0)/known.length,
   mean_ops:primary.reduce((s,w)=>s+w.scores[name].ops,0)/primary.length,
   mean_old_used:primary.reduce((s,w)=>s+w.scores[name].old_used,0)/primary.length,
   mean_old_mass:primary.reduce((s,w)=>s+w.scores[name].old_mass,0)/primary.length};
  for(const key of ["p95","p98"]){
   const test=w=>w.scores[name].p>thresholds[name][key].cutoff;
   calc[key]={false_alarm:nulls.filter(test).length/nulls.length,
    familiar_recall:shifted.filter(test).length/shifted.length,
    nonlinear_recall:odd.filter(test).length/odd.length};
  }
  out[name]=calc;
 }
 return out;
}
function verdict(s,primary,cal,thresholds){
 const a=s.old_top8_new_local2,n=s.old_top8_new_global,o=s.old_full_new_local2,f=s.old_full_new_global;
 const a95=a.p95,n95=n.p95,o95=o.p95,f95=f.p95;
 const newGain=n95.familiar_recall-a95.familiar_recall,oldGain=o95.familiar_recall-a95.familiar_recall;
 const eligibleNew=newGain>=.12&&n95.false_alarm<=.08&&n95.false_alarm<=f95.false_alarm+.04&&
  n.event_brier<=a.event_brier+.025&&newGain>=oldGain+.05;
 const eligibleOld=oldGain>=.12&&o95.false_alarm<=.08&&o95.false_alarm<=f95.false_alarm+.04&&
  o.event_brier<=a.event_brier+.025&&oldGain>=newGain+.05;
 const selected=eligibleNew?"expanded_new_neighborhood":eligibleOld?"untruncated_old_posterior":"not_isolated";
 const targeted=eligibleNew?n:eligibleOld?o:null;
 const criteria={
  lever_identified_pass:eligibleNew||eligibleOld,
  matched_strong_control_pass:!!targeted&&targeted.p95.familiar_recall>=f95.familiar_recall-.10,
  data_budget_pass:primary.length===384&&cal.length===200&&
   primary.every(w=>w.old_events.length===24&&w.actions.length===16&&w.first12new===12&&w.old_snapshot_roundtrip)&&
   cal.every(w=>w.old_snapshot_roundtrip),
  posterior_calibration_pass:CONFIG.every(c=>thresholds[c.id].p95.rank===191&&thresholds[c.id].p98.rank===197)
 };
 const development_signal=Object.values(criteria).every(Boolean);
 return {newGain,oldGain,selected_lever:selected,criteria,development_signal};
}
function study(smoke){
 if(smoke){
  const w=generate(200003,"NULL"),r=evaluate(w);
  return {schema:"energy-factors-21-smoke.v1",old:r.old_events.length,new:r.actions.length,
   distinct:r.first12new,retained:r.old_snapshot_roundtrip,scores:r.scores};
 }
 const cal=Array.from({length:200},(_,i)=>evaluate(generate(210007+31*i,"NULL")));
 const thresholds={};
 for(const c of CONFIG){
  const arr=cal.map(w=>w.scores[c.id].p);
  thresholds[c.id]={p95:cutoff(arr,191),p98:cutoff(arr,197)};
 }
 const primary=[];
 for(let i=0;i<96;i++)for(const fam of FAMILIES)
  primary.push(evaluate(generate(225011+37*i,fam)));
 const grouped=summary(primary,thresholds),v=verdict(grouped,primary,cal,thresholds);
 return {schema:"energy-factors-21-result.v1",seeds:{smoke:200003,calibration:Array.from({length:200},(_,i)=>210007+31*i),primary:Array.from({length:96},(_,i)=>225011+37*i)},
  arms:CONFIG.map(x=>x.id),families:FAMILIES,thresholds,calibration_rows:cal,primary_rows:primary,
  summary:grouped,verdict:v,classification:v.development_signal?"DEV_MECHANISM_SIGNAL_UNQUALIFIED":"SCIENTIFIC_NO_GO"};
}
return {study,FAMILIES,CONFIG};
})();
if(typeof module!=="undefined"&&module.exports){
 module.exports=EnergyFactors21;
 if(typeof require!=="undefined"&&require.main===module)
  process.stdout.write(JSON.stringify(EnergyFactors21.study(process.argv[2]==="--smoke"),null,2)+"\n");
}
