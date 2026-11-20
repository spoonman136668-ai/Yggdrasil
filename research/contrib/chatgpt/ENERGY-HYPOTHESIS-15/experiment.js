/* ENERGY-HYPOTHESIS-15 — source-free, frozen causal hypothesis repair study.
 * Node.js >=18: node experiment.js [--smoke|--primary|--cold-check <json-path>]
 * No external packages, native learner, environment access, or API.
 */
const EnergyHypothesis15 = (function () {
"use strict";
const SEEDS=[88103,88117,88129,88141,88153,88169,88177,88189,88201,88211,88223,88237];
const SCENARIOS=["NULL","SINGLE_EDGE","DOUBLE_EDGE"];
const ARMS=["local_active","full_bayes_ig","full_bayes_random","local_on_bayes_trace"];
const OLD_N=24,NEW_N=16,HELD_N=20,NOISE=0.1;
const HYPS=[];
for(let mask=1;mask<32;mask++)for(let bias=0;bias<2;bias++)HYPS.push({mask,bias});
function hash(...parts) {
  const s=parts.join(":");let h=2166136261;
  for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}
  h^=h>>>16;h=Math.imul(h,2246822507)>>>0;h^=h>>>13;
  h=Math.imul(h,3266489909)>>>0;h^=h>>>16;return h>>>0;
}
function popcount(v){let n=0;while(v){v&=v-1;n++;}return n;}
function bit(x,h){return (popcount(x&h.mask)&1)^h.bias;}
function hdist(h,g){return popcount(h.mask^g.mask)+(h.bias!==g.bias?1:0);}
function binEntropy(p){return -(p>0?p*Math.log(p):0)-(p<1?(1-p)*Math.log(1-p):0);}
function sample(seed,scenario,phase,x,ordinal,truth){
 const y=bit(x,truth);
 return hash(seed,scenario,phase,x,ordinal,"flip")/4294967296<NOISE?1-y:y;
}
function world(seed,scenario){
 const choices=HYPS.filter(h=>h.bias===0 && [2,3].includes(popcount(h.mask)));
 const base=choices[hash(seed,scenario,"mask")%choices.length];
 const old={mask:base.mask,bias:hash(seed,scenario,"bias")%2};
 const next={...old};
 if(scenario==="SINGLE_EDGE"){
  next.mask^=1<<(hash(seed,scenario,"changed")%5);
 } else if(scenario==="DOUBLE_EDGE"){
  const on=[],off=[];
  for(let i=0;i<5;i++)((old.mask>>i)&1?on:off).push(i);
  next.mask^=(1<<on[hash(seed,scenario,"off")%on.length])|(1<<off[hash(seed,scenario,"on")%off.length]);
 }
 const oldSamples=[];
 for(let i=0;i<OLD_N;i++){
  const x=hash(seed,scenario,"old-x",i)%32;
  oldSamples.push([x,sample(seed,scenario,"old",x,i,old)]);
 }
 const held=[];
 for(let x=0;x<32;x++){
  const ys=[];for(let j=0;j<HELD_N;j++)ys.push(sample(seed,scenario,"held",x,j,next));held.push(ys);
 }
 return {seed,scenario,oldSamples,oldTrue:old,newTrue:next,held};
}
function estimateOld(samples){
 const llike=HYPS.map(h=>samples.reduce((s,[x,y])=>s+Math.log(bit(x,h)===y?0.9:0.1),0));
 let best=0;for(let i=1;i<llike.length;i++)if(llike[i]>llike[best])best=i;
 const max=Math.max(...llike),exps=llike.map(v=>Math.exp(v-max)),z=exps.reduce((a,b)=>a+b,0);
 const ps=exps.map(v=>v/z),readout=[];
 for(let x=0;x<32;x++){
  let p=NOISE;for(let i=0;i<HYPS.length;i++)p+=0.8*ps[i]*bit(x,HYPS[i]);
  readout.push(p);
 }
 return {oldMap:HYPS[best],readout,evals:HYPS.length*OLD_N+HYPS.length*32};
}
function model(oldMap,isLocal){
 let radius=isLocal?1:6,hs=[],logs=[],observed=[],cost=0,sumLogLoss=0,expanded=false;
 function reset(){
  hs=HYPS.filter(h=>!isLocal || popcount(h.mask^oldMap.mask)<=radius);
  logs=hs.map(h=>-hdist(h,oldMap));
  for(const [x,y] of observed){for(let i=0;i<hs.length;i++){logs[i]+=Math.log(bit(x,hs[i])===y?0.9:0.1);cost++;}}
 }
 reset();
 function weights(){
  const mx=Math.max(...logs),w=logs.map(z=>Math.exp(z-mx)),sum=w.reduce((a,b)=>a+b,0);
  return w.map(v=>v/sum);
 }
 function predict(x,w){
  let p=NOISE;for(let i=0;i<hs.length;i++)p+=0.8*w[i]*bit(x,hs[i]);
  cost+=hs.length;return p;
 }
 function query(){
  const w=weights();let best=0,ent=-1;
  for(let x=0;x<32;x++){
   const h=binEntropy(predict(x,w));
   if(h>ent+1e-12){ent=h;best=x;}
  }
  return best;
 }
 function update(x,y){
  const w=weights(),p=predict(x,w);
  sumLogLoss-=Math.log(y?p:1-p);
  observed.push([x,y]);
  for(let i=0;i<hs.length;i++){logs[i]+=Math.log(bit(x,hs[i])===y?0.9:0.1);cost++;}
  if(isLocal && !expanded && observed.length>=6 && sumLogLoss/observed.length>0.75){
   expanded=true;radius=2;reset();
  }
 }
 function final(){
  const w=weights(),readout=[];for(let x=0;x<32;x++)readout.push(predict(x,w));
  let best=0;for(let i=1;i<logs.length;i++)if(logs[i]>logs[best])best=i;
  return {readout,changed:hs[best].mask!==oldMap.mask || hs[best].bias!==oldMap.bias,selected:hs[best],cost,expanded,number_hypotheses:hs.length};
 }
 return {query,update,final};
}
function runArm(w,old,arm,trace){
 const local=arm.startsWith("local_"),m=model(old.oldMap,local),counts=Array(32).fill(0),actions=[];
 for(let i=0;i<NEW_N;i++){
  const x=trace?trace[i][0]:(arm==="full_bayes_random"?hash(w.seed,w.scenario,"random",i)%32:m.query());
  const y=sample(w.seed,w.scenario,"new",x,counts[x],w.newTrue);
  counts[x]++;m.update(x,y);actions.push([x,y]);
  if(trace && y!==trace[i][1])throw Error("paired intervention outcome mismatch");
 }
 const state=m.final();
 let total=0;
 for(let x=0;x<32;x++)for(const y of w.held[x])total+=(state.readout[x]-y)**2;
 return {brier:total/(32*HELD_N),cost:state.cost+old.evals,identified:state.selected.mask===w.newTrue.mask&&state.selected.bias===w.newTrue.bias,
  declared_change:state.changed,expanded:state.expanded,hypotheses:state.number_hypotheses,unique_actions:counts.filter(v=>v>0).length,
  count:actions.length,actions,readout:state.readout};
}
function coldReadout(snapshot){
 const parsed=JSON.parse(snapshot);
 if(!Array.isArray(parsed)||parsed.length!==32)return false;
 return parsed.every(v=>Number.isFinite(v)&&v>=0&&v<=1);
}
function study(seeds){
 const rows=[];let oldCold=0;
 for(const seed of seeds)for(const scenario of SCENARIOS){
  const w=world(seed,scenario),old=estimateOld(w.oldSamples);
  const snapshot=JSON.stringify(old.readout);
  if(!coldReadout(snapshot)||JSON.stringify(JSON.parse(snapshot))!==snapshot)throw Error("OLD cold serialization failure");
  oldCold++;
  const full=runArm(w,old,"full_bayes_ig");
  const results={full_bayes_ig:full};
  results.local_active=runArm(w,old,"local_active");
  results.full_bayes_random=runArm(w,old,"full_bayes_random");
  results.local_on_bayes_trace=runArm(w,old,"local_on_bayes_trace",full.actions);
  const compact={seed,scenario,old_map:old.oldMap,old_readout_digest:hash(snapshot),new_truth:w.newTrue,results:{}};
  for(const arm of ARMS){
   const r=results[arm];
   compact.results[arm]={brier:r.brier,cost:r.cost,identified:r.identified,declared_change:r.declared_change,expanded:r.expanded,
    hypotheses:r.hypotheses,unique_actions:r.unique_actions,count:r.count};
  }
  rows.push(compact);
 }
 const summary={};
 for(const arm of ARMS){
  const a=rows.map(r=>r.results[arm]);
  const mean=k=>a.reduce((s,r)=>s+r[k],0)/a.length;
  summary[arm]={brier:mean("brier"),cost:mean("cost"),identified_shift_rate:
   rows.reduce((s,r)=>s+(r.scenario!=="NULL"&&r.results[arm].identified?1:0),0)/(2*seeds.length),
   null_false_report_rate:rows.reduce((s,r)=>s+(r.scenario==="NULL"&&r.results[arm].declared_change?1:0),0)/seeds.length,
   expanded_worlds:a.filter(r=>r.expanded).length,unique_actions:mean("unique_actions"),by_scenario:{}};
  for(const scenario of SCENARIOS){
   summary[arm].by_scenario[scenario]=rows.filter(r=>r.scenario===scenario).reduce((s,r)=>s+r.results[arm].brier,0)/seeds.length;
  }
 }
 const c=summary.local_active,b=summary.full_bayes_ig;
 const verdict={
  loss_gap:c.brier-b.brier, cost_ratio:b.cost/c.cost,
  improvement_threshold_pass:c.brier<=b.brier+0.015&&SCENARIOS.every(s=>c.by_scenario[s]<=b.by_scenario[s]+0.015),
  compute_proxy_pass:b.cost/c.cost>=2,
  changed_hypothesis_recovery_pass:c.identified_shift_rate>=0.80,
  null_false_change_pass:c.null_false_report_rate<=0.05,
  cold_readout_pass:oldCold===rows.length
 };
 verdict.development_signal=Object.entries(verdict).filter(([k])=>k.endsWith("_pass")).every(([,v])=>v===true);
 return {schema:"energy-hypothesis-15-result.v1",seeds,scenarios:SCENARIOS,worlds:rows.length,old_cold_serializations:oldCold,
  old_samples:rows.length*OLD_N,new_samples_per_arm:rows.length*NEW_N,held_samples:rows.length*32*HELD_N,summary,verdict,rows};
}
return {study,coldReadout,SEEDS,SCENARIOS};
})();
if(typeof module!=="undefined" && module.exports){
 module.exports=EnergyHypothesis15;
 if(typeof require!=="undefined" && require.main===module){
  const fs=require("fs");
  if(process.argv[2]==="--cold-check"){
   process.stdout.write(JSON.stringify({pass:EnergyHypothesis15.coldReadout(fs.readFileSync(process.argv[3],"utf8"))})+"\n");
  }else{
   process.stdout.write(JSON.stringify(EnergyHypothesis15.study(process.argv[2]==="--smoke"?[88091]:EnergyHypothesis15.SEEDS),null,2)+"\n");
  }
 }
}
