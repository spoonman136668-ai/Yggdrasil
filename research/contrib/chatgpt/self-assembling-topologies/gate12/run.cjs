"use strict";
// Gate 12: frozen synthetic causal model-order test, zero external dependencies.
// Exact preregistration committed at d6a8e401530029018e54571219b62b8187649b36.
// CONTRIBUTOR ONLY. No native Yggdrasil checkpoint/training/authority used.
const PAIRS=[];
for(let i=0;i<6;i++)for(let j=i+1;j<6;j++)PAIRS.push([i,j]);
const truth=(t,a,b)=>(t>>>((a<<1)|b))&1;
const TABLES=[];
for(let t=0;t<16;t++){
  const depA=truth(t,0,0)!==truth(t,1,0)||truth(t,0,1)!==truth(t,1,1);
  const depB=truth(t,0,0)!==truth(t,0,1)||truth(t,1,0)!==truth(t,1,1);
  if(depA&&depB)TABLES.push(t);
}
const check=(s,m)=>{if(!s)throw Error("GATE12_INVARIANT: "+m);};
check(PAIRS.length===15&&TABLES.length===10,"candidate universe");
function rng(seed){let x=seed>>>0;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};}
const b=(x,k)=>(x>>>k)&1,clamp=p=>Math.min(.95,Math.max(.05,p)),sq=(p,y)=>(p-y)**2;
const pairRow=(x,ij)=>(b(x,ij[0])<<1)|b(x,ij[1]);
function fit(obs,id) {
  const width=id===0?1:id<=6?2:4;
  const n=Array(width).fill(0),yes=Array(width).fill(0);
  const ri=x=>id===0?0:id<=6?b(x,id-1):pairRow(x,PAIRS[id-7]);
  for(const [x,y] of obs){let i=ri(x);n[i]++;yes[i]+=y;}
  return {id,n,yes,p:n.map((v,i)=>clamp((yes[i]+1)/(v+2))),ri};
}
function score(obs,m){let s=0;for(const [x,y] of obs)s+=sq(m.p[m.ri(x)],y);return s/obs.length;}
function contrast(m,cut) {
  if(m.id<7)return true;
  const {n,yes}=m;
  const f=(a,z)=>n[a]>=3&&n[z]>=3&&Math.abs(yes[a]/n[a]-yes[z]/n[z])>=cut;
  return (f(0,2)||f(1,3))&&(f(0,1)||f(2,3));
}
function select(obs,policy) {
  check(obs.length>=32,"minimum scan data");
  const training=obs.slice(0,-16),validation=obs.slice(-16);
  let comparisons=0,best=null,bestRisk=Infinity,bestModel=null;
  if(policy==="legacy"){
    for(let id=7;id<22;id++){
      const m=fit(training,id),val=score(validation,m);
      comparisons+=training.length+validation.length;
      if(val<bestRisk-1e-12){bestRisk=val;best=id;bestModel=m;}
    }
    const nullRisk=score(validation,fit(training,0));
    comparisons+=training.length+validation.length;
    const accept=nullRisk-bestRisk>=0.08&&contrast(bestModel,.45);
    return {id:accept?best:0,accepted:accept?1:0,comparisons};
  }
  for(let id=0;id<22;id++){
    const m=fit(training,id),complexity=id===0?0:id<=6?.015:.045;
    const risk=score(training,m)+complexity;
    comparisons+=training.length*2;
    if(risk<bestRisk-1e-12){bestRisk=risk;best=id;bestModel=m;}
  }
  const loss=score(validation,bestModel);
  const nullFit=fit(training,0),nullLoss=score(validation,nullFit);
  comparisons+=training.length+validation.length*2;
  const improvement=nullLoss-loss;
  const gate=best===0?false:best<=6?improvement>=.05:
    improvement>=.08&&contrast(bestModel,.40);
  return {id:gate?best:0,accepted:gate?1:0,comparisons};
}
class Learner {
  constructor(policy){
    this.policy=policy;this.c=[0,1].map(()=>({obs:[],n:0,id:0,accepted:0}));
    this.scans=0;this.comparisons=0;this.transitions=0;
  }
  observe(ctx,x,y){
    const c=this.c[ctx];
    check(c.n<128&&ctx<2&&x<64&&(y===0||y===1),"input and fit bounds");
    c.n++;c.obs.push([x,y]);if(c.obs.length>64)c.obs.shift();
    const scan=this.policy==="dynamic"?[32,64,96,128].includes(c.n):c.n===128;
    if(scan){const s=select(c.obs,this.policy);this.scans++;this.comparisons+=s.comparisons;
      if(s.id!==c.id)this.transitions++;c.id=s.id;c.accepted=s.accepted;}
  }
  predict(ctx,x){
    const c=this.c[ctx];check(c.n===128&&c.obs.length===64,"no held until trained");
    return fit(c.obs,c.id).p[(c.id===0?0:c.id<=6?b(x,c.id-1):pairRow(x,PAIRS[c.id-7]))];
  }
  pack(){
    const bytes=new Uint8Array(260);
    for(let k=0;k<2;k++){const c=this.c[k],off=k*130;check(c.n===128&&c.obs.length===64,"complete fit for cold restore");
      for(let i=0;i<64;i++){bytes[off+2*i]=c.obs[i][0];bytes[off+2*i+1]=c.obs[i][1];}
      bytes[off+128]=c.id;bytes[off+129]=c.accepted;
    }return bytes;
  }
  static fromPacked(buf,policy){
    check(buf instanceof Uint8Array&&buf.length===260,"packed length");
    const model=new Learner(policy);
    for(let k=0;k<2;k++){const c=model.c[k],off=k*130;c.n=128;
      for(let i=0;i<64;i++){const x=buf[off+2*i],y=buf[off+2*i+1];check(x<64&&y<=1,"stored observations");c.obs.push([x,y]);}
      c.id=buf[off+128];c.accepted=buf[off+129];
      check(c.id<22&&(c.accepted===1)===(c.id!==0),"stored route consistency");
    }return model;
  }
}
const HYP=[];
for(const p of [.5,.05,.95])HYP.push({order:0,p});
for(let i=0;i<6;i++)for(let inv=0;inv<2;inv++)HYP.push({order:1,i,inv});
for(let i=0;i<15;i++)for(const t of TABLES)HYP.push({order:2,i,t});
check(HYP.length===165,"bayes 165 hypotheses");
function param(h,x){
 if(h.order===0)return h.p;
 if(h.order===1)return (b(x,h.i)^h.inv)?.95:.05;
 const ij=PAIRS[h.i],r=pairRow(x,ij);
 return ((h.t>>>r)&1)?.95:.05;
}
class Bayes{
 constructor(){
  this.c=[0,1].map(()=>Float64Array.from(HYP,h=>Math.log((1/3)/(h.order===0?3:h.order===1?12:150))));
  this.comparisons=0;
 }
 observe(ctx,x,y){const v=this.c[ctx];for(let i=0;i<HYP.length;i++){
   const p=param(HYP[i],x);v[i]+=Math.log(y?p:1-p);this.comparisons++;
 }}
 predict(ctx,x){const v=this.c[ctx],peak=Math.max(...v);let mass=0,yes=0;
   for(let i=0;i<HYP.length;i++){const w=Math.exp(v[i]-peak);mass+=w;yes+=w*param(HYP[i],x);this.comparisons++;}
   check(mass>0&&Number.isFinite(mass),"posterior mass");return yes/mass;
 }
}
class Marginal{
 constructor(){this.c=[[],[]];}
 observe(k,x,y){const a=this.c[k];a.push([x,y]);if(a.length>64)a.shift();}
 predict(k){return fit(this.c[k],0).p[0];}
}
function world(g,f){
 const first=g()%6;let second=g()%5;if(second>=first)second++;
 const i=Math.min(first,second),j=Math.max(first,second);
 const table=TABLES[g()%TABLES.length],opts=[0,1,2,3,4,5].filter(x=>x!==i&&x!==j);
 const third=opts[g()%4],unaryIndex=g()%6,inv=g()&1;
 return {i,j,table,third,unaryIndex,inv,f};
}
function label(w,x,g){
 if(w.f==="random")return g()&1;
 if(w.f==="biased_independent")return g()%5!==0?1:0;
 const a=b(x,w.i),b0=b(x,w.j);
 let y=w.f==="pair"?truth(w.table,a,b0):
  w.f==="unary"?(b(x,w.unaryIndex)^w.inv):
  w.f==="parity3"?(a^b0^b(x,w.third)):NaN;
 check(y===0||y===1,"unknown world family");
 if(g()%20===0)y^=1;
 return y;
}
function sample(seed,f){
 const g=rng(seed), worlds=[world(g,f),world(g,f)];
 return worlds.map(w=>{const train=[],held=[];
  for(let i=0;i<128;i++){const x=g()&63;train.push([x,label(w,x,g)]);}
  for(let i=0;i<32;i++){const x=g()&63;held.push([x,label(w,x,g)]);}
  return {w,train,held};
 });
}
const ARMS=["dynamic","fixed","legacy","marginal","bayes"];
function trial(seed,f){
 const contexts=sample(seed,f), learners=["dynamic","fixed","legacy"].map(k=>new Learner(k)),nullModel=new Marginal(),bayes=new Bayes();
 for(let k=0;k<2;k++)for(const [x,y]of contexts[k].train){
  for(const m of learners)m.observe(k,x,y);
  nullModel.observe(k,x,y);bayes.observe(k,x,y);
 }
 const copies=learners.map(m=>Learner.fromPacked(m.pack(),m.policy));
 const errors=Object.fromEntries(ARMS.map(k=>[k,0]));
 let correct=0,pairCorrect=0,unaryCorrect=0,accepted=0,zero=0,cold=true,fixedTie=true;
 for(let k=0;k<2;k++){
  const h=learners[0].c[k].id,w=contexts[k].w,expected=f==="pair"?2:f==="unary"?1:0;
  const order=h===0?0:h<=6?1:2;
  if(order>0)accepted++;else zero++;
  if(expected===2&&order===2){const ij=PAIRS[h-7];if(ij[0]===w.i&&ij[1]===w.j){correct++;pairCorrect++;}}
  if(expected===1&&order===1&&h-1===w.unaryIndex){correct++;unaryCorrect++;}
  for(const [x,y]of contexts[k].held){
   const preds=learners.map(m=>m.predict(k,x));
   for(let i=0;i<3;i++){
    errors[learners[i].policy]+=sq(preds[i],y);
    if(preds[i]!==copies[i].predict(k,x))cold=false;
   }
   if(preds[0]!==preds[1])fixedTie=false;
   errors.marginal+=sq(nullModel.predict(k),y);
   errors.bayes+=sq(bayes.predict(k,x),y);
  }
 }
 for(const k of ARMS)errors[k]/=64;
 return {errors,correct,pairCorrect,unaryCorrect,accepted,zero,cold,fixedTie,
  scans:Object.fromEntries(learners.map(m=>[m.policy,m.scans])),
  comparisons:Object.fromEntries(learners.map(m=>[m.policy,m.comparisons]).concat([["bayes",bayes.comparisons]])),
  transitions:learners[0].transitions};
}
const round=v=>Number(v.toFixed(10));
function ci(values){const n=values.length,mean=values.reduce((s,x)=>s+x,0)/n,
  variance=values.reduce((s,x)=>s+(x-mean)**2,0)/(n-1),margin=1.96*Math.sqrt(variance/n);
 return {mean:round(mean),lower:round(mean-margin),upper:round(mean+margin)};}
function summarize(f,start,n){
 const a=Array.from({length:n},(_,i)=>trial(start+i,f)),scores={};
 for(const k of ARMS)scores[k]=round(a.reduce((s,x)=>s+x.errors[k],0)/n);
 return {family:f,seed_first:start,seed_last:start+n-1,seeds:n,worlds:n*2,scores,
  correct_routes:a.reduce((s,x)=>s+x.correct,0),
  true_pair_routes:a.reduce((s,x)=>s+x.pairCorrect,0),
  true_unary_routes:a.reduce((s,x)=>s+x.unaryCorrect,0),
  accepted:a.reduce((s,x)=>s+x.accepted,0),
  zero_order:a.reduce((s,x)=>s+x.zero,0),
  cold_passes:a.filter(x=>x.cold).length,
  fixed_tie_passes:a.filter(x=>x.fixedTie).length,
  transitions:a.reduce((s,x)=>s+x.transitions,0),
  comparisons:Object.fromEntries(["dynamic","fixed","legacy","bayes"].map(k=>[k,a.reduce((s,x)=>s+x.comparisons[k],0)])),
  paired_gate11_gain:ci(a.map(x=>x.errors.legacy-x.errors.dynamic)),
  paired_fixed_gain:ci(a.map(x=>x.errors.fixed-x.errors.dynamic)),
  seed_gate11_gains:a.map(x=>round(x.errors.legacy-x.errors.dynamic))};
}
function run(){
 const pair=summarize("pair",16000,64),unary=summarize("unary",19000,32),
  parity3=summarize("parity3",18000,32),random=summarize("random",17000,32),
  biased=summarize("biased_independent",20000,32);
 const all=[pair,unary,parity3,random,biased];
 const OOD=[unary,parity3,random,biased];
 const macroGain=OOD.reduce((s,z)=>s+z.scores.legacy-z.scores.dynamic,0)/OOD.length,
  inLoss=pair.scores.dynamic-pair.scores.legacy;
 const gates={
  pair_correct_at_least_116:pair.true_pair_routes>=116,
  unary_correct_at_least_58:unary.true_unary_routes>=58,
  parity_zero_at_least_58:parity3.zero_order>=58,
  random_zero_at_least_58:random.zero_order>=58,
  biased_zero_at_least_58:biased.zero_order>=58,
  ood_macro_gain_at_least_0_045:macroGain>=.045,
  in_family_loss_at_most_0_015:inLoss<=.015,
  cold_all:all.every(z=>z.cold_passes===z.seeds),
  fixed_identical_on_held:all.every(z=>z.fixed_tie_passes===z.seeds)
 };
 const supported=Object.entries(gates).filter(([k])=>k!=="fixed_identical_on_held").every(([,v])=>v);
 const summary={macro_out_of_family_gain_vs_gate11:round(macroGain),in_family_brier_loss_vs_gate11:round(inLoss),
  structural_gain_vs_matched_fixed:round(pair.scores.fixed-pair.scores.dynamic),
  true_pair_recovery:pair.true_pair_routes+"/"+pair.worlds,
  true_unary_recovery:unary.true_unary_routes+"/"+unary.worlds};
 return {schema:"yggdrasil.gate12.hierarchical-0-1-2-synthetic-result.v1",
   prereg_commit:"d6a8e401530029018e54571219b62b8187649b36",
   parent_candidate:"f867f50e85a722a8cab2f747ddfe7e3d828fb62a",
   persistent_bytes_per_local_or_fixed:260,bayes_nominal_bytes:2640,
   split:"64 last fit observations -> 48 fit/16 separate validation; no held updates",
   family:{pair,unary,parity3,random,biased_independent:biased},
   gates,summary,verdict:supported?"CALIBRATION_SUPPORTED_DEV_ONLY":"SCIENTIFIC_NEGATIVE_OR_MIXED_DEV",
   structural_verdict:summary.structural_gain_vs_matched_fixed>=.02&&pair.paired_fixed_gain.lower>0?"STRUCTURAL_GAIN_DEV_ONLY":"STRUCTURAL_SUPERIORITY_NOT_ESTABLISHED",
   native_yggdrasil_first_use:false};
}
if(typeof module!=="undefined"&&typeof require!=="undefined"&&require.main===module){
 const fs=require("fs"),out=run();
 if(process.argv.includes("--verify")){
   const file=process.argv[process.argv.indexOf("--verify")+1];
   check(file,"missing result path");const sealed=JSON.parse(fs.readFileSync(file,"utf8"));
   check(JSON.stringify(sealed)===JSON.stringify(out),"replay mismatch");
   process.stdout.write("GATE12_EXACT_REPLAY_PASS "+out.verdict+" "+out.structural_verdict+"\n");
 }else process.stdout.write(JSON.stringify(out,null,2)+"\n");
}
