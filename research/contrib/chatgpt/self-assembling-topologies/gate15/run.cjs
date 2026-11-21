"use strict";
// Gate 15 — prequential posterior adequacy residual, frozen synthetic comparison.
// Contributor-only. No native learner, model checkpoint, or training authority touched.
// Preregistered at d0d372ea1e0f0f9683a115fbdc04b72b0fc21470.
const PAIRS=[];
for(let i=0;i<5;i++)for(let j=i+1;j<5;j++)PAIRS.push([i,j]);
const bit=(v,k)=>(v>>>k)&1;
const truth=(t,a,b)=>(t>>>((a<<1)|b))&1;
const TABLES=[];
for(let t=0;t<16;t++){
 const a=truth(t,0,0)!==truth(t,1,0)||truth(t,0,1)!==truth(t,1,1);
 const b=truth(t,0,0)!==truth(t,0,1)||truth(t,1,0)!==truth(t,1,1);
 if(a&&b)TABLES.push(t);
}
const check=(ok,why)=>{if(!ok)throw Error("GATE13_INVARIANT: "+why);};
check(PAIRS.length===10&&TABLES.length===10,"pair templates");
function rng(seed){let x=seed>>>0;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};}
function mix32(x){
 x=(x^(x>>>16))>>>0;x=Math.imul(x,0x7feb352d)>>>0;
 x=(x^(x>>>15))>>>0;x=Math.imul(x,0x846ca68b)>>>0;
 return (x^(x>>>16))>>>0;
}
function noiseHash(seed,ctx,x,visit,domain){
 let h=mix32((seed^Math.imul(ctx+1,0x9e3779b1)^Math.imul(domain+1,0x85ebca6b))>>>0);
 h=mix32(h^Math.imul(x+1,0xc2b2ae35));return mix32(h^Math.imul(visit+1,0x27d4eb2f));
}
const hyps=[];
for(const p of [.05,.5,.95])hyps.push({order:0,p,logPrior:Math.log(1/9)});
for(let k=0;k<5;k++)for(let inv=0;inv<2;inv++)hyps.push({order:1,k,inv,logPrior:Math.log(1/30)});
for(let k=0;k<PAIRS.length;k++)for(const table of TABLES)hyps.push({order:2,k,table,logPrior:Math.log(1/300)});
check(hyps.length===113,"exact hypothesis count");
const row=(x,p)=>(bit(x,p[0])<<1)|bit(x,p[1]);
function hp(h,x){
 if(h.order===0)return h.p;
 if(h.order===1)return (bit(x,h.k)^h.inv)?0.95:0.05;
 return truth(h.table,bit(x,PAIRS[h.k][0]),bit(x,PAIRS[h.k][1]))?0.95:0.05;
}
function entropy(p){if(!(p>0&&p<1))throw Error("invalid predictive probability");return -(p*Math.log(p)+(1-p)*Math.log(1-p));}
const POLICIES=["residual_guard","active","balanced","random","fixed_damp"];
class Posterior {
 constructor(policy){
  this.policy=policy;
  this.c=[0,1].map(()=>({logs:Float64Array.from(hyps,h=>h.logPrior),counts:new Uint8Array(32),step:0,excess:0,alarm:0,chosenPrediction:.5}));
  this.hypothesisEvaluations=0;
 }
 predict(ctx,x){
  const z=this.c[ctx].logs,top=Math.max(...z);
  let sum=0,yes=0;
  for(let i=0;i<hyps.length;i++){
   const w=Math.exp(z[i]-top);sum+=w;yes+=w*hp(hyps[i],x);
  }
  this.hypothesisEvaluations+=hyps.length;
  check(Number.isFinite(sum)&&sum>0,"stable posterior");
  return yes/sum;
 }
 query(ctx,seed){
  const c=this.c[ctx];check(c.step<16,"action budget bound");
  // Compute EXACTLY the same 32 posterior candidates for every arm, including
  // the deliberately compute-equalized fixed/random arms.
  const probs=Array.from({length:32},(_,x)=>this.predict(ctx,x));
  const bal=(11*c.step+(seed%32)+13*ctx)%32;
  if(this.policy==="balanced"||(this.policy==="residual_guard"&&c.alarm))return this.storePrediction(ctx,bal,probs);
  if(this.policy==="random")return this.storePrediction(ctx,noiseHash(seed,ctx,0,c.step,9201)&31,probs);
  let best=-Infinity,winner=0;
  for(let x=0;x<32;x++){
   const h=entropy(probs[x]);
   if(h>best+1e-12 || (Math.abs(h-best)<=1e-12 && (c.counts[x]<c.counts[winner]||(c.counts[x]===c.counts[winner]&&x<winner)))){
    best=h;winner=x;
   }
  }
  return this.storePrediction(ctx,winner,probs);
 }
 storePrediction(ctx,x,probs){
  this.c[ctx].chosenPrediction=probs[x];return x;
 }
 observe(ctx,x,y){
  const c=this.c[ctx];
  check(x>=0&&x<32&&(y===0||y===1)&&c.step<16&&c.counts[x]<255,"training update bounds");
  for(let i=0;i<hyps.length;i++){const p=hp(hyps[i],x);c.logs[i]+=Math.log(y?p:1-p);}
  this.hypothesisEvaluations+=hyps.length;
  const q=c.chosenPrediction;
  c.excess+=(q-y)*(q-y)-q*(1-q);
  c.counts[x]++;c.step++;
  if(c.step>=6&&c.excess/c.step>.06)c.alarm=1;
 }
 pack(){
  const bytes=new Uint8Array(1892),view=new DataView(bytes.buffer);
  for(let ctx=0;ctx<2;ctx++){
   const c=this.c[ctx],offset=ctx*946;
   for(let k=0;k<113;k++)view.setFloat64(offset+k*8,c.logs[k],true);
   bytes.set(c.counts,offset+904);bytes[offset+936]=c.step;
   view.setFloat64(offset+937,c.excess,true);bytes[offset+945]=c.alarm;
  }
  return bytes;
 }
 static restore(bytes,policy){
  check(bytes instanceof Uint8Array&&bytes.length===1892,"wrong checkpoint size");
  const b=new Uint8Array(bytes),view=new DataView(b.buffer);
  const model=new Posterior(policy);
  for(let ctx=0;ctx<2;ctx++){
   const c=model.c[ctx],offset=ctx*946;
   for(let k=0;k<113;k++)c.logs[k]=view.getFloat64(offset+k*8,true);
   c.counts.set(b.subarray(offset+904,offset+936));c.step=b[offset+936];
   c.excess=view.getFloat64(offset+937,true);c.alarm=b[offset+945];
   check(Number.isFinite(c.excess)&&c.alarm<=1,"checkpoint adequacy state");
   check(c.step<=16&&c.counts.reduce((s,x)=>s+x,0)===c.step,"checkpoint visit accounting");
  }
  return model;
 }
}
function genWorld(seed,ctx,family){
 const g=rng(mix32(seed^Math.imul(ctx+1,321347911)));
 const a=g()%5;let second=g()%4;if(second>=a)second++;
 const i=Math.min(a,second),j=Math.max(a,second),table=TABLES[g()%TABLES.length];
 const options=[0,1,2,3,4].filter(k=>k!==i&&k!==j);
 const third=options[g()%3],unary=g()%5,inv=g()&1;
 return {family,i,j,table,third,unary,inv};
}
function consequence(w,seed,ctx,x,visit,domain){
 const a=bit(x,w.i),b=bit(x,w.j);
 if(w.family==="random")return noiseHash(seed,ctx,x,visit,domain)&1;
 let y=w.family==="pair"?truth(w.table,a,b):
       w.family==="unary"?(bit(x,w.unary)^w.inv):
       w.family==="parity3"?(a^b^bit(x,w.third)):-1;
 check(y>=0,"unknown family");
 return y^(noiseHash(seed,ctx,x,visit,domain)%20===0?1:0);
}
function bytesEqual(a,b){return a.length===b.length&&a.every((v,i)=>v===b[i]);}
function runOne(seed,family){
 const worlds=[genWorld(seed,0,family),genWorld(seed,1,family)];
 const arms=POLICIES.map(p=>new Posterior(p));
 let aPreserved=true,cold=true,returnConsistent=true;
 const snapshots=[];
 // Act in world A first, then world B, while A is dormant.
 for(let ctx=0;ctx<2;ctx++){
  for(let step=0;step<12;step++){
   for(const arm of arms){
    const x=arm.query(ctx,seed);
    const visit=arm.c[ctx].counts[x];
    const y=consequence(worlds[ctx],seed,ctx,x,visit,1252);
    arm.observe(ctx,x,y);
   }
  }
  if(ctx===0)for(const arm of arms){
    const c=arm.c[0];
    snapshots.push({log:Array.from(c.logs),counts:Array.from(c.counts),step:c.step,excess:c.excess,alarm:c.alarm});
  }
 }
 for(let i=0;i<arms.length;i++){
  const a=arms[i].c[0],prior=snapshots[i];
  if(a.step!==prior.step||a.logs.some((v,k)=>v!==prior.log[k])||
      a.counts.some((v,k)=>v!==prior.counts[k])||a.excess!==prior.excess||a.alarm!==prior.alarm)aPreserved=false;
 }
 const errors=Object.fromEntries(POLICIES.map(name=>[name,0]));
 // Held labels are immutable and shared, never admitted to posterior or guard.
 for(let ctx=0;ctx<2;ctx++)for(let x=0;x<32;x++){
  const y=consequence(worlds[ctx],seed,ctx,x,0,31337);
  for(const arm of arms){const raw=arm.predict(ctx,x);
   const p=arm.policy==="residual_guard"&&arm.c[ctx].alarm ? .55*raw+.225:
    arm.policy==="fixed_damp"?.7*raw+.15:raw;
   errors[arm.policy]+=(p-y)*(p-y);
  }
 }
 for(const k of POLICIES)errors[k]/=64;
 const checkpointBytes=arms.map(a=>a.pack().length);
 const work=Object.fromEntries(arms.map(a=>[a.policy,a.hypothesisEvaluations]));
 // Compare independent cold reconstitutions under exact four-step learner continuation.
 for(const arm of arms){
  const snapshot=arm.pack(),a=Posterior.restore(snapshot,arm.policy),b=Posterior.restore(snapshot,arm.policy);
  if(!bytesEqual(snapshot,a.pack())||!bytesEqual(snapshot,b.pack()))cold=false;
  for(let t=0;t<4;t++){
   const x=a.query(0,seed),other=b.query(0,seed);
   if(x!==other) returnConsistent=false;
   const visit=a.c[0].counts[x],y=consequence(worlds[0],seed,0,x,visit,1252);
   a.observe(0,x,y);b.observe(0,other,y);
   if(!bytesEqual(a.pack(),b.pack()))returnConsistent=false;
   if(a.predict(0,(t*7)%32)!==b.predict(0,(t*7)%32))returnConsistent=false;
  }
 }
 return {errors,cold,returnConsistent,aPreserved,work,checkpointBytes,alarm_contexts:arms.find(a=>a.policy==="residual_guard").c.reduce((a,c)=>a+c.alarm,0)};
}
const round=x=>Number(x.toFixed(10));
function paired(values){
 const n=values.length,m=values.reduce((a,b)=>a+b,0)/n,
   var0=values.reduce((a,v)=>a+(v-m)**2,0)/(n-1),
   half=1.96*Math.sqrt(var0/n);
 return {mean:round(m),ci95:[round(m-half),round(m+half)]};
}
function summarize(family,start,count){
 const runs=Array.from({length:count},(_,i)=>runOne(start+i,family));
 const means=Object.fromEntries(POLICIES.map(k=>[k,round(runs.reduce((s,r)=>s+r.errors[k],0)/count)]));
 return {family,seed_first:start,seed_last:start+count-1,seeds:count,worlds:count*2,means,
  paired_balanced_minus_active:paired(runs.map(x=>x.errors.balanced-x.errors.active)),
  paired_random_minus_active:paired(runs.map(x=>x.errors.random-x.errors.active)),
  paired_balanced_minus_guard:paired(runs.map(x=>x.errors.balanced-x.errors.residual_guard)),
  paired_random_minus_guard:paired(runs.map(x=>x.errors.random-x.errors.residual_guard)),
  paired_active_minus_guard:paired(runs.map(x=>x.errors.active-x.errors.residual_guard)),
  guard_alarm_contexts:runs.reduce((a,x)=>a+x.alarm_contexts,0),
  cold_restore_success:runs.filter(x=>x.cold).length,
  cold_continuation_success:runs.filter(x=>x.returnConsistent).length,
  context_A_preservation_success:runs.filter(x=>x.aPreserved).length,
  total_hypothesis_evaluations:Object.fromEntries(POLICIES.map(k=>[k,runs.reduce((s,x)=>s+x.work[k],0)])),
  checkpoint_bytes:Array.from(new Set(runs.flatMap(x=>x.checkpointBytes))).sort((a,b)=>a-b)};
}
function run(){
 const pair=summarize("pair",41000,64),unary=summarize("unary",42000,32),
 parity3=summarize("parity3",43000,32),random=summarize("random",44000,32);
 const families={pair,unary,parity3,random},all=Object.values(families);
 const best=z=>Math.min(z.means.balanced,z.means.random);
 const fixedExcess=all.reduce((a,z)=>a+z.means.residual_guard-z.means.fixed_damp,0)/all.length;
 const gates={
  pair_gain_vs_balanced_min_0_010:pair.paired_balanced_minus_guard.mean>=.010,
  pair_ci_lower_vs_balanced_positive:pair.paired_balanced_minus_guard.ci95[0]>0,
  pair_loss_vs_active_max_0_010:pair.means.residual_guard-pair.means.active<=.010,
  parity_loss_vs_best_max_0_015:parity3.means.residual_guard-best(parity3)<=.015,
  random_loss_vs_best_max_0_015:random.means.residual_guard-best(random)<=.015,
  parity_gain_vs_active_min_0_015:parity3.means.active-parity3.means.residual_guard>=.015,
  random_gain_vs_active_min_0_015:random.means.active-random.means.residual_guard>=.015,
  unary_loss_vs_best_max_0_015:unary.means.residual_guard-best(unary)<=.015,
  mean_brier_loss_vs_fixed_damp_max_0_005:fixedExcess<=.005,
  cold_all:all.every(z=>z.cold_restore_success===z.seeds&&z.cold_continuation_success===z.seeds&&z.context_A_preservation_success===z.seeds),
  bytes_exact_1892:all.every(z=>z.checkpoint_bytes.length===1&&z.checkpoint_bytes[0]===1892),
  forced_equal_work:all.every(z=>Object.values(z.total_hypothesis_evaluations).every(w=>w===z.total_hypothesis_evaluations.residual_guard))
 };
 return {
  schema:"yggdrasil.gate15.residual-adequacy-synthetic-result.v1",
  prereg_commit:"d0d372ea1e0f0f9683a115fbdc04b72b0fc21470",
  predecessor_sha:"743237b7efa667bc3cbedfd1f38e25e23a307583",
  families,gates,macro_guard_excess_vs_fixed_damp:Number(fixedExcess.toFixed(10)),
  verdict:Object.values(gates).every(Boolean)?"RESIDUAL_GUARD_DEVELOPMENT_SIGNAL_ONLY":"RESIDUAL_GUARD_DEVELOPMENT_MIXED_NO_GO",
  constraints:{native_first_use:false,known_grammar:true,checkpoint_bytes:1892,process_ram_unmeasured:true,physical_compute_gain_unverified:true}
 };
}
if(typeof module!=="undefined"&&typeof require!=="undefined"&&require.main===module){
 const fs=require("fs");const r=run();
 if(process.argv.includes("--verify")){
  const f=process.argv[process.argv.indexOf("--verify")+1];
  check(f,"missing verification path");
  const expected=JSON.parse(fs.readFileSync(f,"utf8"));
  check(JSON.stringify(expected)===JSON.stringify(r),"sealed result changed");
  process.stdout.write("GATE15_DETERMINISTIC_REPLAY_PASS "+r.verdict+"\n");
 }else process.stdout.write(JSON.stringify(r,null,2)+"\n");
}
