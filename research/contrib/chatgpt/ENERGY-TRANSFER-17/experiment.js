/* ENERGY-TRANSFER-17 — independently written source-free binary causal simulator.
   No import of prior experiment. Node >=18: node experiment.js --smoke|--primary
   No private data, network, native model, paid API, or upstream control. */
const EnergyTransfer17=(function(){
"use strict";
const SEEDS=[88513,88523,88547,88561,88567,88583,88597,88609,88619,88631,88643,88657];
const FAMILIES=["NULL","SINGLE_EDGE","DOUBLE_EDGE","NONLINEAR_AND"];
const ARMS=["local_coverage12","local_entropy","full_map_ig","full_map_coverage12",
            "full_marginal_ig","full_marginal_coverage12","full_random"];
const N_OLD=24,N_NEW=16,N_HELD=20,FLIP=.15,INPUTS=32;
const H=[];
for(let mask=1;mask<32;mask++)for(let bias=0;bias<=1;bias++)H.push({mask,bias});
function randomCounter(...pieces){
  let a=0x6d2b79f5>>>0;
  for(const s of pieces.map(x=>String(x))){
    for(let j=0;j<s.length;j++){
      a=Math.imul(a^s.charCodeAt(j),0x9e3779b1)>>>0;
      a=(a^(a>>>11))>>>0;
    }
    a=Math.imul(a^0x7f4a7c15,0x85ebca6b)>>>0;
  }
  a^=a>>>16;a=Math.imul(a,0x7feb352d)>>>0;
  a^=a>>>15;a=Math.imul(a,0x846ca68b)>>>0;
  return ((a^(a>>>16))>>>0);
}
function countOnes(x){let n=0;for(let b=0;b<5;b++)n+=(x>>>b)&1;return n;}
function parity(h,x){return (countOnes(h.mask & x)&1)^h.bias;}
function xorDistance(a,b){return countOnes(a.mask^b.mask)+Number(a.bias!==b.bias);}
function truthFor(seed,fam){
  const candidates=H.filter(h=>h.bias===0&&(countOnes(h.mask)===2||countOnes(h.mask)===3));
  const base=candidates[randomCounter(seed,fam,"old-structure")%candidates.length];
  const old={mask:base.mask,bias:randomCounter(seed,fam,"old-bias")%2};
  const after={...old};
  let gate=null;
  if(fam==="SINGLE_EDGE"){
    after.mask^=(1<<(randomCounter(seed,fam,"edge")%5));
  }else if(fam==="DOUBLE_EDGE"){
    const active=[],inactive=[];
    for(let b=0;b<5;b++)(old.mask&(1<<b)?active:inactive).push(b);
    after.mask^=(1<<active[randomCounter(seed,fam,"removed")%active.length]);
    after.mask^=(1<<inactive[randomCounter(seed,fam,"added")%inactive.length]);
  }else if(fam==="NONLINEAR_AND"){
    const a=randomCounter(seed,fam,"nonlinear-a")%5;
    const b=(a+1+randomCounter(seed,fam,"nonlinear-b")%4)%5;
    gate=[a,b];
  }
  return {old,after,gate};
}
function underlying(x,struct){let y=parity(struct.after,x);
 if(struct.gate!==null)y^=((x>>struct.gate[0])&1)&((x>>struct.gate[1])&1);
 return y;
}
function observe(seed,fam,phase,x,ordinal,y){
 const flip=randomCounter(seed,fam,phase,x,ordinal,"noise")/4294967296<FLIP;
 return flip ? 1-y : y;
}
function makeWorld(seed,fam){
 const struct=truthFor(seed,fam),oldData=[],held=[];
 for(let j=0;j<N_OLD;j++){
  const x=randomCounter(seed,fam,"old-input",j)%INPUTS;
  oldData.push([x,observe(seed,fam,"old",x,j,parity(struct.old,x))]);
 }
 for(let x=0;x<INPUTS;x++){
  const results=[];
  for(let j=0;j<N_HELD;j++)results.push(observe(seed,fam,"held",x,j,underlying(x,struct)));
  held.push(results);
 }
 return {seed,fam,struct,oldData,held};
}
function normalize(logs){
 const pivot=Math.max(...logs);
 const w=logs.map(v=>Math.exp(v-pivot)),z=w.reduce((a,b)=>a+b,0);
 return w.map(v=>v/z);
}
function oldInference(oldData){
 const logs=H.map(h=>oldData.reduce((acc,[x,y])=>acc+Math.log(parity(h,x)===y?1-FLIP:FLIP),0));
 const priorOld=normalize(logs),map=H[priorOld.indexOf(Math.max(...priorOld))];
 const readout=Array.from({length:INPUTS},(_,x)=>{
  let prob=FLIP;
  for(let k=0;k<H.length;k++)prob+=(1-2*FLIP)*priorOld[k]*parity(H[k],x);
  return prob;
 });
 const wire=JSON.stringify({priorOld,readout});
 const revived=JSON.parse(wire);
 // exact same-process posterior/readout restoration, not an OS-process cold check.
 if(revived.priorOld.length!==H.length||JSON.stringify(revived.readout)!==JSON.stringify(readout))throw Error("OLD_READOUT_ROUNDTRIP");
 let oldCost=H.length*(N_OLD+INPUTS);
 return {map,priorOld,readout,oldCost,wire};
}
function newPrior(old,variant){
 if(variant==="marginal"){
  const out=Array(H.length).fill(0);
  for(let k=0;k<H.length;k++){
   const d=H.map(candidate=>Math.exp(-xorDistance(H[k],candidate)));
   const z=d.reduce((a,b)=>a+b,0);
   for(let j=0;j<H.length;j++)out[j]+=old.priorOld[k]*d[j]/z;
  }
  return {weight:out,cost:H.length*H.length};
 }
 const out=H.map(g=>Math.exp(-xorDistance(old.map,g)));
 const z=out.reduce((a,b)=>a+b,0);
 return {weight:out.map(v=>v/z),cost:H.length};
}
function posteriorModel(old,variant){
 const isLocal=variant==="local";
 const prior=newPrior(old,variant==="marginal"?"marginal":"map");
 let searchRadius=isLocal?1:5,didExpand=false,seen=[],hyp=[],logs=[],ops=prior.cost;
 function rebuild(){
  hyp=[];logs=[];
  for(let i=0;i<H.length;i++){
   if(!isLocal || countOnes(old.map.mask^H[i].mask)<=searchRadius){
    hyp.push(i);
    logs.push(Math.log(prior.weight[i]));
   }
  }
  for(const [x,y] of seen)for(let k=0;k<hyp.length;k++){
   logs[k]+=Math.log(parity(H[hyp[k]],x)===y?1-FLIP:FLIP);ops++;
  }
 }
 rebuild();
 function predictive(weights,x){
  let p=FLIP;
  for(let k=0;k<hyp.length;k++)p+=(1-2*FLIP)*weights[k]*parity(H[hyp[k]],x);
  ops+=hyp.length;return p;
 }
 function choose(counts,novelty){
  const weights=normalize(logs);
  let winner=-1,best=-Infinity;
  for(let x=0;x<INPUTS;x++){
   if(novelty&&counts[x]>0)continue;
   const p=predictive(weights,x);
   const score=-(p? p*Math.log(p):0)-(p<1?(1-p)*Math.log(1-p):0);
   if(score>best+1e-13){best=score;winner=x;}
  }
  if(winner<0)throw Error("ACTION_SELECTION_EMPTY");
  return winner;
 }
 function update(x,y){
  seen.push([x,y]);
  for(let k=0;k<hyp.length;k++){
   logs[k]+=Math.log(parity(H[hyp[k]],x)===y?1-FLIP:FLIP);ops++;
  }
  // Recompute cumulative prequential logloss for the frozen expansion gate:
  // replay likelihood only for the scalar diagnostic, without changing the actual posterior.
  if(isLocal && !didExpand && seen.length>=6){
   let loss=0,diagnostic=normalize(hyp.map(k=>Math.log(prior.weight[k])));
   let ll=diagnostic.map(v=>Math.log(v));
   for(const [a,b] of seen){
     const ww=normalize(ll),priorP=predictive(ww,a);
     loss-=Math.log(b?priorP:1-priorP);
     for(let k=0;k<hyp.length;k++)ll[k]+=Math.log(parity(H[hyp[k]],a)===b?1-FLIP:FLIP);
   }
   if(loss/seen.length>0.75){
    didExpand=true;searchRadius=2;rebuild();
   }
  }
 }
 function finish(){
  const w=normalize(logs),readout=[];
  for(let x=0;x<INPUTS;x++)readout.push(predictive(w,x));
  let top=0;for(let k=1;k<logs.length;k++)if(logs[k]>logs[top])top=k;
  const chosen=H[hyp[top]];
  return {readout,chosen,hasChange:chosen.mask!==old.map.mask||chosen.bias!==old.map.bias,
    ops:ops+old.oldCost,expanded:didExpand,candidate_count:hyp.length};
 }
 return {choose,update,finish};
}
function runOne(w,old,name){
 const variant=name.startsWith("local")?"local":name.startsWith("full_marginal")?"marginal":"map";
 const model=posteriorModel(old,variant),counter=Array(INPUTS).fill(0),actions=[];
 for(let t=0;t<N_NEW;t++){
  const covered=(name.includes("coverage12")&&t<12);
  const x=name==="full_random"?randomCounter(w.seed,w.fam,"baseline-random",t)%INPUTS:model.choose(counter,covered);
  const y=observe(w.seed,w.fam,"fresh",x,counter[x],underlying(x,w.struct));
  counter[x]++;actions.push([x,y]);model.update(x,y);
 }
 const stat=model.finish();
 let squared=0;
 for(let x=0;x<INPUTS;x++)for(let k=0;k<N_HELD;k++)squared+=(stat.readout[x]-w.held[x][k])**2;
 return {brier:squared/(INPUTS*N_HELD),ops:stat.ops,identified:stat.chosen.mask===w.struct.after.mask&&stat.chosen.bias===w.struct.after.bias,
 changed:stat.hasChange,unique:counter.filter(n=>n>0).length,
 expanded:stat.expanded,actions,events:N_NEW};
}
function run(seeds){
 const cells=[],roundtrip=[];
 for(const seed of seeds)for(const fam of FAMILIES){
  const w=makeWorld(seed,fam),old=oldInference(w.oldData);
  // Readout checks are only same-process roundtrips and do not establish native cold retention.
  roundtrip.push(JSON.stringify(JSON.parse(old.wire))===old.wire);
  const arms={};
  for(const name of ARMS)arms[name]=runOne(w,old,name);
  cells.push({seed,fam,truth_family:fam,source_hidden_outcome_law:fam==="NONLINEAR_AND"?"OUT_OF_FAMILY_AND":"FITTED_XOR",
    old_roundtrip:roundtrip[roundtrip.length-1],arms});
 }
 const totals={},byFamily={},byKnown={};
 for(const name of ARMS){
  const all=cells.map(v=>v.arms[name]);
  const avg=(arr,key)=>arr.reduce((sum,v)=>sum+v.arms[name][key],0)/arr.length;
  byFamily[name]={};
  for(const fam of FAMILIES)byFamily[name][fam]=avg(cells.filter(w=>w.fam===fam),"brier");
  const familiar=cells.filter(v=>v.fam!=="NONLINEAR_AND"),changed=cells.filter(v=>v.fam==="SINGLE_EDGE"||v.fam==="DOUBLE_EDGE"),nulls=cells.filter(v=>v.fam==="NULL");
  totals[name]={brier:avg(cells,"brier"),known_brier:avg(familiar,"brier"),nonlinear_brier:byFamily[name].NONLINEAR_AND,ops:avg(cells,"ops"),
     known_recovery:changed.filter(v=>v.arms[name].identified).length/changed.length,
     null_false_declaration:nulls.filter(v=>v.arms[name].changed).length/nulls.length,
     mean_distinct_contexts:avg(cells,"unique"),by_family:byFamily[name]};
 }
 const candidate=totals.local_coverage12,baseline=totals.local_entropy;
 const conventional=["full_map_ig","full_map_coverage12","full_marginal_ig","full_marginal_coverage12","full_random"];
 const bestKnown=conventional.reduce((a,b)=>totals[a].known_brier<=totals[b].known_brier?a:b);
 const bestPerFamily={};
 for(const fam of FAMILIES)bestPerFamily[fam]=conventional.reduce((a,b)=>byFamily[a][fam]<=byFamily[b][fam]?a:b);
 const uniqueOK=cells.every(w=>["local_coverage12","full_map_coverage12","full_marginal_coverage12"].every(a=>w.arms[a].unique>=12));
 const budgetOK=cells.every(w=>ARMS.every(a=>w.arms[a].events===N_NEW));
 const result={
  schema:"energy-transfer-17-result.v1",primary_seeds:seeds,families:FAMILIES,arms:ARMS,
  worlds:cells.length,old_events:cells.length*N_OLD,new_events_each:cells.length*N_NEW,held_events:cells.length*INPUTS*N_HELD,
  summaries:totals,best_known_conventional_arm:bestKnown,best_per_family:bestPerFamily,
  criteria:{
   coverage_gain_pass:baseline.known_brier-candidate.known_brier>=.010 && baseline.by_family.DOUBLE_EDGE-candidate.by_family.DOUBLE_EDGE>=.025,
   strong_control_pass:candidate.known_brier<=totals[bestKnown].known_brier+.015&&
     ["NULL","SINGLE_EDGE","DOUBLE_EDGE"].every(f=>candidate.by_family[f]<=totals[bestPerFamily[f]].by_family[f]+.025),
   nonlinear_robustness_pass:baseline.nonlinear_brier-candidate.nonlinear_brier>=.010&&
     candidate.nonlinear_brier<=totals[bestPerFamily.NONLINEAR_AND].nonlinear_brier+.015,
   parity_recovery_pass:candidate.known_recovery>=.80,
   null_false_alarm_pass:candidate.null_false_declaration<=.05,
   coverage_pass:uniqueOK,budget_pass:budgetOK,roundtrip_pass:roundtrip.every(Boolean),
   operation_proxy_pass:totals.full_marginal_ig.ops/candidate.ops>=2
  },
  cells
 };
 result.criteria.development_signal=Object.entries(result.criteria).filter(([k])=>k.endsWith("_pass")).every(([,v])=>v===true);
 return result;
}
return {run,SEEDS,FAMILIES,ARMS};
})();
if(typeof module!=="undefined"&&module.exports){
 module.exports=EnergyTransfer17;
 if(typeof require!=="undefined"&&require.main===module){
  const mode=process.argv[2],cohort=mode==="--smoke"?[88501]:EnergyTransfer17.SEEDS;
  process.stdout.write(JSON.stringify(EnergyTransfer17.run(cohort),null,2)+"\n");
 }
}
