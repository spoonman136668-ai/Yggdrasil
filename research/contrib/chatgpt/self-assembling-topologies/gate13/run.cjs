"use strict";
// Gate 13 — frozen synthetic intervention selection under matched actions/info/candidate scans.
// This contributor-only research never invokes a native Yggdrasil teacher or checkpoint.
// Preregistered before source execution: 756b97735c9042fcd2d1d3534c37ae240151d9e0.
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
const POLICIES=["active","balanced","random"];
class Posterior {
 constructor(policy){
  this.policy=policy;
  this.c=[0,1].map(()=>({logs:Float64Array.from(hyps,h=>h.logPrior),counts:new Uint8Array(32),step:0}));
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
  if(this.policy==="balanced")return (11*c.step+(seed%32)+13*ctx)%32;
  if(this.policy==="random")return noiseHash(seed,ctx,0,c.step,9201)&31;
  let best=-Infinity,winner=0;
  for(let x=0;x<32;x++){
   const h=entropy(probs[x]);
   if(h>best+1e-12 || (Math.abs(h-best)<=1e-12 && (c.counts[x]<c.counts[winner]||(c.counts[x]===c.counts[winner]&&x<winner)))){
    best=h;winner=x;
   }
  }
  return winner;
 }
 observe(ctx,x,y){
  const c=this.c[ctx];
  check(x>=0&&x<32&&(y===0||y===1)&&c.step<16&&c.counts[x]<255,"training update bounds");
  for(let i=0;i<hyps.length;i++){const p=hp(hyps[i],x);c.logs[i]+=Math.log(y?p:1-p);}
  this.hypothesisEvaluations+=hyps.length;
  c.counts[x]++;c.step++;
 }
 pack(){
  const bytes=new Uint8Array(1874),view=new DataView(bytes.buffer);
  for(let ctx=0;ctx<2;ctx++){
   const c=this.c[ctx],offset=ctx*937;
   for(let k=0;k<113;k++)view.setFloat64(offset+k*8,c.logs[k],true);
   bytes.set(c.counts,offset+904);bytes[offset+936]=c.step;
  }
  return bytes;
 }
 static restore(bytes,policy){
  check(bytes instanceof Uint8Array&&bytes.length===1874,"wrong checkpoint size");
  const b=new Uint8Array(bytes),view=new DataView(b.buffer);
  const model=new Posterior(policy);
  for(let ctx=0;ctx<2;ctx++){
   const c=model.c[ctx],offset=ctx*937;
   for(let k=0;k<113;k++)c.logs[k]=view.getFloat64(offset+k*8,true);
   c.counts.set(b.subarray(offset+904,offset+936));c.step=b[offset+936];
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
    snapshots.push({log:Array.from(c.logs),counts:Array.from(c.counts),step:c.step});
  }
 }
 for(let i=0;i<arms.length;i++){
  const a=arms[i].c[0],prior=snapshots[i];
  if(a.step!==prior.step||a.logs.some((v,k)=>v!==prior.log[k])||
      a.counts.some((v,k)=>v!==prior.counts[k]))aPreserved=false;
 }
 const errors={active:0,balanced:0,random:0};
 // Held labels are immutable, common for all three arms, disjoint noise domain.
 for(let ctx=0;ctx<2;ctx++)for(let x=0;x<32;x++){
  const y=consequence(worlds[ctx],seed,ctx,x,0,31337);
  for(const arm of arms){const p=arm.predict(ctx,x);errors[arm.policy]+=(p-y)*(p-y);}
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
 return {errors,cold,returnConsistent,aPreserved,work,checkpointBytes};
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
  cold_restore_success:runs.filter(x=>x.cold).length,
  cold_continuation_success:runs.filter(x=>x.returnConsistent).length,
  context_A_preservation_success:runs.filter(x=>x.aPreserved).length,
  total_hypothesis_evaluations:Object.fromEntries(POLICIES.map(k=>[k,runs.reduce((s,x)=>s+x.work[k],0)])),
  checkpoint_bytes:Array.from(new Set(runs.flatMap(x=>x.checkpointBytes))).sort((a,b)=>a-b)};
}
function run(){
 const pair=summarize("pair",23000,64),unary=summarize("unary",24000,32),
  parity3=summarize("parity3",25000,32),random=summarize("random",26000,32);
 const arms=POLICIES, families=[pair,unary,parity3,random];
 const bestControl=z=>Math.min(z.means.balanced,z.means.random);
 const gate={
  pair_gain_balanced_at_least_0_010:pair.paired_balanced_minus_active.mean>=.01,
  pair_gain_random_at_least_0_010:pair.paired_random_minus_active.mean>=.01,
  pair_CI_lower_balanced_positive:pair.paired_balanced_minus_active.ci95[0]>0,
  pair_CI_lower_random_positive:pair.paired_random_minus_active.ci95[0]>0,
  unary_worsening_at_most_0_010:unary.means.active-bestControl(unary)<=.01,
  parity_worsening_at_most_0_020:parity3.means.active-bestControl(parity3)<=.02,
  random_worsening_at_most_0_020:random.means.active-bestControl(random)<=.02,
  exact_cold_continuation_all:families.every(z=>z.cold_restore_success===z.seeds&&z.cold_continuation_success===z.seeds&&z.context_A_preservation_success===z.seeds),
  state_bytes_1874:families.every(z=>z.checkpoint_bytes.length===1&&z.checkpoint_bytes[0]===1874)
 };
 const success=Object.values(gate).every(Boolean);
 return {schema:"yggdrasil.gate13.intervention-choice-synthetic-result.v1",
  prereg_commit:"756b97735c9042fcd2d1d3534c37ae240151d9e0",
  predecessor_sha:"d9353a780e4f9107002ce4dada4b48505c834bf9",
  families:{pair,unary,parity3,random},gates:gate,
  outcome:success?"ACTION_CHOICE_DEVELOPMENT_SIGNAL_ONLY":"ACTION_CHOICE_DEVELOPMENT_NO_GO_OR_MIXED",
  claims:{native_yggdrasil_first_use:false,model_structure_learned:false,
   candidate_family_known:true,actual_compute_advantage:false,
   checkpoint_bytes:1874,full_process_RAM_measured:false},
  work_note:"Each arm intentionally scans all 32 posterior-predictive actions per step; this equalizes measured hypothesis evaluations but overstates minimal required fixed/random cost."};
}
if(typeof module!=="undefined"&&typeof require!=="undefined"&&require.main===module){
 const fs=require("fs");const r=run();
 if(process.argv.includes("--verify")){
  const f=process.argv[process.argv.indexOf("--verify")+1];
  check(f,"missing verification path");
  const expected=JSON.parse(fs.readFileSync(f,"utf8"));
  check(JSON.stringify(expected)===JSON.stringify(r),"sealed result changed");
  process.stdout.write("GATE13_DETERMINISTIC_REPLAY_PASS "+r.outcome+"\n");
 }else process.stdout.write(JSON.stringify(r,null,2)+"\n");
}
