"use strict";
// Gate18: predict strictly withheld 5-bit action combinations in fresh worlds.
// Protocol frozen at 666a5ef577186e2ca94998f523c6b07de9c053cc.
// No teacher inference, no accepted checkpoint, no production integration.
const check=(v,m)=>{if(!v)throw Error("GATE17_INVARIANT "+m);};
const pc=x=>{let k=0;for(;x;x>>>=1)k+=x&1;return k;};
const BASE=Array.from({length:31},(_,i)=>i+1);
const LOW=BASE.filter(m=>pc(m)<=2),TRIPLES=BASE.filter(m=>pc(m)===3),FULL=LOW.concat(TRIPLES);
check(LOW.length===15&&TRIPLES.length===10&&FULL.length===25,"subset cardinality");
const built=[...new Set(LOW.filter(m=>pc(m)===1).flatMap(a=>LOW.filter(b=>pc(b)===2&&(a&b)===0).map(b=>a|b)))].sort((a,b)=>a-b);
check(built.every((x,i)=>x===TRIPLES[i])&&built.length===10,"compositional construction");
function rng(seed){let a=seed>>>0;return()=>{a^=a<<13;a^=a>>>17;a^=a<<5;return a>>>0;};}
function mix(x){x=(x^(x>>>16))>>>0;x=Math.imul(x,0x7feb352d)>>>0;x=(x^(x>>>15))>>>0;x=Math.imul(x,0x846ca68b)>>>0;return (x^(x>>>16))>>>0;}
function hash(seed,ctx,x,visit,domain){
 let v=mix(seed^Math.imul(ctx+1,0x9e3779b1)^Math.imul(domain+1,0x85ebca6b));
 v=mix(v^Math.imul(x+1,0xc2b2ae35));return mix(v^Math.imul(visit+1,0x27d4eb2f));
}
function bits(mask){const b=[];for(let k=0;k<5;k++)if(mask&(1<<k))b.push(k);return b;}
function bin(x,mask){let v=0;for(const bit of bits(mask))v=(v<<1)|((x>>bit)&1);return v;}
function essential(table){for(let bit=0;bit<3;bit++){let seen=false;for(let x=0;x<8;x++){const y=x^(1<<(2-bit));if(((table>>x)&1)!==((table>>y)&1)){seen=true;break;}}if(!seen)return false;}return true;}
function makeWorld(seed,ctx,family){
 const g=rng(mix(seed^Math.imul(ctx+1,819311)));
 const masks=family==="pair"?LOW.filter(m=>pc(m)===2):family==="unary"?LOW.filter(m=>pc(m)===1):TRIPLES;
 const mask=family==="independent"?0:masks[g()%masks.length],inv=g()&1;
 let table=0;
 if(family==="random_essential3"){do{table=g()&255;}while(!essential(table));}
 return {family,mask,inv,table};
}
function consequence(world,seed,ctx,x,visit,domain){
 const h=hash(seed,ctx,x,visit,domain),{family,mask,inv}=world;
 if(family==="independent")return h&1;
 const idx=bin(x,mask),k=pc(mask);
 let y;
 if(family==="majority3")y=pc(x&mask)>=2?1:0;
 else if(family==="mux3")y=(idx&4)?(idx&1):((idx>>1)&1);
 else if(family==="random_essential3")y=(world.table>>idx)&1;
 else if(family==="parity3"||family==="pair"||family==="unary")y=pc(x&mask)&1;
 else throw Error("world family");
 return y^inv^(h%20===0?1:0);
}
function data(seed,ctx,family){
 const w=makeWorld(seed,ctx,family),g=rng(mix(seed^Math.imul(ctx+1,111222333))),visits=new Uint8Array(32);
 const partition=Array.from({length:32},(_,x)=>x);
 // Exactly one split PER seed/context, independent of evaluator's true mask/table.
 for(let i=31;i>0;i--){const j=g()%(i+1);[partition[i],partition[j]]=[partition[j],partition[i]];}
 const allowed=partition.slice(0,24),held=partition.slice(24);
 check(new Set(allowed).size===24&&new Set(held).size===8&&allowed.every(x=>!held.includes(x)),"disjoint action custody");
 const obs=[];
 for(let round=0;round<4;round++){
  const xs=allowed.slice();
  for(let i=xs.length-1;i>0;i--){const j=g()%(i+1);[xs[i],xs[j]]=[xs[j],xs[i]];}
  for(const x of xs)obs.push([x,consequence(w,seed,ctx,x,visits[x]++,23000)]);
 }
 check(obs.length===96&&obs.every(([x])=>allowed.includes(x)),"fit-only actions");
 return {w,obs,allowed,held};
}
const clamp=p=>Math.min(.95,Math.max(.05,p)),sq=(p,y)=>(p-y)**2;
function stats(obs,mask){
 const n=new Uint16Array(1<<pc(mask)),yes=new Uint16Array(n.length);
 for(const [x,y]of obs){let b=bin(x,mask);n[b]++;yes[b]+=y;}
 return {n,yes};
}
function predict(st,x,mask){
 const b=bin(x,mask);return clamp((st.yes[b]+1)/(st.n[b]+2));
}
function loo(obs,mask){
 const s=stats(obs,mask);let total=0;
 for(const [x,y]of obs){const b=bin(x,mask);const p=clamp((s.yes[b]-y+1)/(s.n[b]+1));total+=sq(p,y);}
 return {raw:total/obs.length,work:obs.length*2};
}
function validation(obs,mask,trained){
 const s=stats(trained,mask);let total=0;
 for(const [x,y]of obs)total+=sq(predict(s,x,mask),y);
 return total/obs.length;
}
function fitSelection(obs,mode){
 const train=obs.slice(0,64),valid=obs.slice(64);
 let work=0,bestLow=0,lowRisk=Infinity,lowRaw=Infinity;
 for(const m of LOW){
  const x=loo(train,m);work+=x.work;
  const risk=x.raw+.003*(1<<pc(m));
  if(risk<lowRisk-1e-12){bestLow=m;lowRisk=risk;lowRaw=x.raw;}
 }
 const useHigh=lowRaw>=.09;
 let bestHigh=0,highRisk=Infinity;
 if(mode==="fixed_full"||mode==="adaptive"){
  if(mode==="fixed_full"||useHigh)for(const m of TRIPLES){
   const x=loo(train,m);work+=x.work;
   const risk=x.raw+.003*8;
   if(risk<highRisk-1e-12){bestHigh=m;highRisk=risk;}
  }
 }
 let route=0;
 const lowVal=validation(valid,bestLow,train);
 work+=valid.length+train.length;
 if(mode!=="truncated"&&useHigh&&highRisk<lowRisk-1e-12){
  const highVal=validation(valid,bestHigh,train);work+=valid.length+train.length;
  if(lowVal-highVal>=.025&&highVal<=.18)route=bestHigh;
 }
 if(!route){
  const nullVal=validation(valid,0,train);work+=valid.length+train.length;
  if(nullVal-lowVal>=.02&&lowVal<=.19)route=bestLow;
 }
 return {route,work,expand:mode==="adaptive"&&useHigh};
}
function parityPhi(x,m){return pc(x&m)%2?-1:1;}
function parityCorr(rows,m){let sum=0;for(const [x,y]of rows)sum+=(2*y-1)*parityPhi(x,m);return sum/rows.length;}
function paritySelect(rows){
 const tr=rows.slice(0,64),val=rows.slice(64);
 let lowBest=0,lowRho=0,work=0;
 for(const mask of LOW){const r=parityCorr(tr,mask);work+=64;if(Math.abs(r)>Math.abs(lowRho)+1e-12){lowBest=mask;lowRho=r;}}
 let winner=lowBest,rho=lowRho;
 if(Math.abs(rho)<.70)for(const mask of TRIPLES){const r=parityCorr(tr,mask);work+=64;if(Math.abs(r)>Math.abs(rho)+1e-12){winner=mask;rho=r;}}
 let route=0;
 if(Math.abs(rho)>=.70){
  const nullModel=stats(tr,0),p0=predict(nullModel,0,0);
  let loss1=0,loss0=0;
  for(const [x,y]of val){loss1+=sq(clamp(.5+.5*rho*parityPhi(x,winner)),y);loss0+=sq(p0,y);}
  loss1/=32;loss0/=32;work+=64;
  if(loss0-loss1>=.10&&loss1<=.15)route=winner;
 }
 return {route,work,expand:false};
}
const ARMS=["adaptive","fixed_full","truncated","flat","parity_only","bayes"];
class Compact{
 constructor(arm){this.arm=arm;this.c=[0,1].map(()=>({rows:[],route:0,work:0,expand:false,ready:false}));}
 fit(ctx,rows){
  const c=this.c[ctx];check(rows.length===96&&!c.ready,"fit once");
  c.rows=rows.map(([x,y])=>[x,y]);
  const r=this.arm==="parity_only"?paritySelect(c.rows):
    this.arm==="adaptive"||this.arm==="fixed_full"||this.arm==="truncated"?fitSelection(c.rows,this.arm):{route:0,work:0,expand:false};
  c.route=r.route;c.work=r.work;c.expand=r.expand;c.ready=true;
 }
 forecast(ctx,x){
  const c=this.c[ctx];check(c.ready&&x>=0&&x<32,"fit before forecast");
  if(this.arm==="flat")return predict(stats(c.rows,31),x,31);
  if(this.arm==="parity_only"&&c.route){
   return clamp(.5+.5*parityCorr(c.rows,c.route)*parityPhi(x,c.route));
  }
  return predict(stats(c.rows,c.route),x,c.route);
 }
 pack(){
  const b=new Uint8Array(388);
  for(let k=0;k<2;k++){const c=this.c[k],off=k*194;check(c.ready&&c.rows.length===96,"pack complete");
   for(let i=0;i<96;i++){b[off+i*2]=c.rows[i][0];b[off+i*2+1]=c.rows[i][1];}
   b[off+192]=c.route;b[off+193]=0;
  }return b;
 }
 static restored(b,arm){
  check(b instanceof Uint8Array&&b.length===388,"packed state size");
  const model=new Compact(arm);
  for(let k=0;k<2;k++){const c=model.c[k],off=k*194;
   for(let i=0;i<96;i++){const x=b[off+i*2],y=b[off+i*2+1];check(x<32&&y<=1,"packed examples");c.rows.push([x,y]);}
   c.route=b[off+192];c.ready=true;check(c.route===0||FULL.includes(c.route),"packed route range");
   if(arm==="truncated")check(c.route===0||LOW.includes(c.route),"order constraint");
  }return model;
 }
}
const LOGFAC=[0];for(let i=1;i<=97;i++)LOGFAC[i]=LOGFAC[i-1]+Math.log(i);
const ORDER={0:[0],1:LOW.filter(m=>pc(m)===1),2:LOW.filter(m=>pc(m)===2),3:TRIPLES};
const CONFIG=[0,...FULL];
function bayes(ctxrows){
 const weights=[],pred=[];
 for(const m of CONFIG){
  const s=stats(ctxrows,m);let logE=0;
  for(let b=0;b<s.n.length;b++){
   const n=s.n[b],yes=s.yes[b];logE+=LOGFAC[yes]+LOGFAC[n-yes]-LOGFAC[n+1];
  }
  const prior=Math.log(.25/ORDER[pc(m)].length);
  weights.push(logE+prior);pred.push(s);
 }
 const peak=Math.max(...weights);const posterior=weights.map(w=>Math.exp(w-peak));
 const mass=posterior.reduce((a,b)=>a+b,0);check(mass>0&&Number.isFinite(mass),"Bayes normalized");
 return {forecast:x=>posterior.reduce((sum,w,i)=>sum+w*predict(pred[i],x,CONFIG[i]),0)/mass,work:CONFIG.length*ctxrows.length};
}
const round=x=>Number(x.toFixed(10));
function trial(seed,family){
 const worlds=[data(seed,0,family),data(seed,1,family)];
 const comps=ARMS.slice(0,5).map(a=>new Compact(a));
 const bayesWorld=[];
 for(let ctx=0;ctx<2;ctx++){
  for(const model of comps)model.fit(ctx,worlds[ctx].obs);
  bayesWorld.push(bayes(worlds[ctx].obs));
 }
 const copies=comps.map(m=>Compact.restored(m.pack(),m.arm));
 let restore=true,correct=0,falseTriple=0,expanded=0,exactFixed=true,disjoint=true;
 const comparisons=Object.fromEntries(comps.map(m=>[m.arm,m.c.reduce((n,c)=>n+c.work,0)]));
 comparisons.bayes=bayesWorld.reduce((n,v)=>n+v.work,0);
 const scores=Object.fromEntries([...ARMS,"null"].map(a=>[a,0]));
 let trueBinCovered=0,trueBinUncovered=0;
 const coverageErrors={covered:{adaptive:0,flat:0,bayes:0},uncovered:{adaptive:0,flat:0,bayes:0}};
 for(let ctx=0;ctx<2;ctx++){
  const chosen=comps[0].c[ctx],w=worlds[ctx].w,trainActions=new Set(worlds[ctx].obs.map(row=>row[0]));
  if(["majority3","mux3","random_essential3","parity3"].includes(family)&&chosen.route===w.mask)correct++;
  if(family==="independent"&&pc(chosen.route)===3)falseTriple++;
  if(chosen.expand)expanded++;
  const observedBins=new Set(worlds[ctx].obs.map(([x])=>bin(x,w.mask)));
  for(const x of worlds[ctx].held){
   if(trainActions.has(x))disjoint=false;
   const y=consequence(w,seed,ctx,x,0,45000);
   const trueBinSeen=observedBins.has(bin(x,w.mask));
   const bucket=trueBinSeen?"covered":"uncovered";
   if(trueBinSeen)trueBinCovered++;else trueBinUncovered++;
   for(let i=0;i<comps.length;i++){
    const pred=comps[i].forecast(ctx,x);
    scores[comps[i].arm]+=sq(pred,y);
    if(pred!==copies[i].forecast(ctx,x))restore=false;
    if(["adaptive","flat"].includes(comps[i].arm))coverageErrors[bucket][comps[i].arm]+=sq(pred,y);
   }
   if(comps[0].forecast(ctx,x)!==comps[1].forecast(ctx,x))exactFixed=false;
   const pBayes=bayesWorld[ctx].forecast(x);
   scores.bayes+=sq(pBayes,y);
   coverageErrors[bucket].bayes+=sq(pBayes,y);
   scores.null+=.25;
  }
 }
 check(trueBinCovered+trueBinUncovered===16,"held 8 per context");
 for(const k of Object.keys(scores))scores[k]/=16;
 return {scores,correct,falseTriple,expanded,restore,exactFixed,disjoint,
  trueBinCovered,trueBinUncovered,coverageErrors,comparisons};
}
function paired(values){
 const n=values.length,mean=values.reduce((a,x)=>a+x,0)/n;
 const variance=values.reduce((a,x)=>a+(x-mean)*(x-mean),0)/(n-1);
 const margin=1.96*Math.sqrt(variance/n);return {mean:round(mean),ci95:[round(mean-margin),round(mean+margin)]};
}
function cohort(family,start,count){
 const runs=Array.from({length:count},(_,i)=>trial(start+i,family));
 const scores=Object.fromEntries([...ARMS,"null"].map(k=>[k,round(runs.reduce((s,x)=>s+x.scores[k],0)/count)]));
 const covered=runs.reduce((s,x)=>s+x.trueBinCovered,0),uncovered=runs.reduce((s,x)=>s+x.trueBinUncovered,0);
 const coverage_brier={};
 for(const bucket of ["covered","uncovered"]){
  const n=bucket==="covered"?covered:uncovered;
  coverage_brier[bucket]=n===0?null:Object.fromEntries(["adaptive","flat","bayes"].map(k=>[k,round(runs.reduce((s,x)=>s+x.coverageErrors[bucket][k],0)/n)]));
 }
 return {family,seed_first:start,seed_last:start+count-1,seeds:count,worlds:count*2,scores,
  parents_exact:runs.reduce((a,x)=>a+x.correct,0),
  false_third_order_routes:runs.reduce((a,x)=>a+x.falseTriple,0),
  expanded_worlds:runs.reduce((a,x)=>a+x.expanded,0),
  cold_prediction_passes:runs.filter(x=>x.restore).length,
  disjoint_action_split_passes:runs.filter(x=>x.disjoint).length,
  exactly_matched_fixed_seeds:runs.filter(x=>x.exactFixed).length,
  held_true_parent_bins_covered:covered,held_true_parent_bins_uncovered:uncovered,
  held_coverage_brier:coverage_brier,
  gain_vs_flat:paired(runs.map(x=>x.scores.flat-x.scores.adaptive)),
  gain_vs_parity:paired(runs.map(x=>x.scores.parity_only-x.scores.adaptive)),
  gain_vs_fixed:paired(runs.map(x=>x.scores.fixed_full-x.scores.adaptive)),
  difference_vs_bayes:paired(runs.map(x=>x.scores.adaptive-x.scores.bayes)),
  work:Object.fromEntries(ARMS.map(k=>[k,runs.reduce((s,x)=>s+x.comparisons[k],0)]))};
}
function run(){
 const majority=cohort("majority3",71000,48),mux=cohort("mux3",72000,48),
 random3=cohort("random_essential3",73000,48),parity=cohort("parity3",74000,48),
 pair=cohort("pair",75000,48),unary=cohort("unary",76000,48),independent=cohort("independent",77000,48);
 const families={majority,mux,random3,parity,pair,unary,independent},all=Object.values(families);
 const candidate=[majority,mux,random3,parity];
 const maxBayesDeficit=Math.max(...candidate.map(x=>x.scores.adaptive-x.scores.bayes));
 const g={
  majority_brier_max_0_14:majority.scores.adaptive<=.14,
  mux_brier_max_0_14:mux.scores.adaptive<=.14,
  random3_brier_max_0_17:random3.scores.adaptive<=.17,
  parity_brier_max_0_14:parity.scores.adaptive<=.14,
  majority_flat_gain_min_0_08:majority.gain_vs_flat.mean>=.08,
  mux_flat_gain_min_0_08:mux.gain_vs_flat.mean>=.08,
  random3_flat_gain_min_0_06:random3.gain_vs_flat.mean>=.06,
  parity_flat_gain_min_0_08:parity.gain_vs_flat.mean>=.08,
  flat_gain_paired_CI_lower_all:candidate.every(x=>x.gain_vs_flat.ci95[0]>0),
  majority_parent_recovery_min_78:majority.parents_exact>=78,
  mux_parent_recovery_min_78:mux.parents_exact>=78,
  random3_parent_recovery_min_60:random3.parents_exact>=60,
  parity_parent_recovery_min_78:parity.parents_exact>=78,
  pair_regression_vs_truncated_max_0_015:pair.scores.adaptive-pair.scores.truncated<=.015,
  unary_regression_vs_truncated_max_0_015:unary.scores.adaptive-unary.scores.truncated<=.015,
  random_independent_brier_max_0_27:independent.scores.adaptive<=.27,
  random_independent_spurious_triple_max_8:independent.false_third_order_routes<=8,
  max_deficit_vs_bayes_0_02:maxBayesDeficit<=.02,
  structural_gain_vs_fixed_0_015:majority.gain_vs_fixed.mean>=.015,
  structural_fixed_CI_lower_positive:majority.gain_vs_fixed.ci95[0]>0,
  exact_cold_prediction_all:all.every(x=>x.cold_prediction_passes===x.seeds),
  fully_disjoint_action_sets_all:all.every(x=>x.disjoint_action_split_passes===x.seeds),
  equal_persisted_state_388:all.every(x=>x.exactly_matched_fixed_seeds===x.seeds)
 };
 const keyGates=Object.keys(g).filter(k=>!k.startsWith("structural_"));
 const generalize=keyGates.every(k=>g[k]);
 const structural=generalize&&g.structural_gain_vs_fixed_0_015&&g.structural_fixed_CI_lower_positive;
 return {schema:"yggdrasil.gate18.strictly-unseen-interventions.v1",
  prereg_commit:"666a5ef577186e2ca94998f523c6b07de9c053cc",
  parent_sha:"a0cd5ef90cf3a7b931a3414cda831674ec148c91",
  design:{binary_inputs:5,all_actions:32,train_unique_actions:24,
   withheld_unseen_actions:8,training_events_per_world:96,held_events_per_world:8,
   small_model_persisted_bytes:388,training_action_split_independent_of_evaluator_parent_masks:true,
   full_parent_bin_coverage_not_guaranteed:true},
  families,gates:g,summary:{max_bayes_deficit:round(maxBayesDeficit),true_parent_bins_unseen_total:all.reduce((n,x)=>n+x.held_true_parent_bins_uncovered,0)},
  withheld_action_signal:generalize,structural_superiority:structural,
  verdict:structural?"STRUCTURAL_GAIN_DEVELOPMENT_ONLY":generalize?"STRICTLY_UNSEEN_ACTION_DEVELOPMENT_ONLY":"STRICTLY_UNSEEN_ACTION_MIXED_OR_NO_GO",
  exclusions:{native_first_use:false,new_world_transfer:false,unknown_parent_bin_inference_proven:false,
    structural_superiority_accepted:false,process_memory_cost_measured:false}};
}
if(typeof module!=="undefined"&&typeof require!=="undefined"&&require.main===module){
 const fs=require("fs"),result=run();
 if(process.argv.includes("--verify")){
  const path=process.argv[process.argv.indexOf("--verify")+1];check(path,"missing verification path");
  const sealed=JSON.parse(fs.readFileSync(path,"utf8"));
  check(JSON.stringify(sealed)===JSON.stringify(result),"exact frozen replay mismatch");
  process.stdout.write("GATE18_EXACT_REPLAY_PASS "+result.verdict+"\n");
 }else process.stdout.write(JSON.stringify(result,null,2)+"\n");
}
