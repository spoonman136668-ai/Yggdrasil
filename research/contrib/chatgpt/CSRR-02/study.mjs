// CSRR-02: source-free adaptive action probes + reversible local causal exceptions.
// NOT native Yggdrasil; no protected original-world action or learned new law.
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const SEEDS=[404,505,606], PHASES=['A','B','A','C','A','B'], STEPS=256, W=12;
const clip=p=>Math.max(0,Math.min(1,p));
const base=(a,x)=>a^x;
const cell=(a,x,z)=>4*a+2*x+z;
const key=(x,z)=>2*x+z;
const oldP=(a,x)=>base(a,x)?.9:.1;
const input=(r)=>{if(!r||Object.keys(r).sort().join(',')!=='a,x,z'||![r.a,r.x,r.z].every(v=>Number.isInteger(v)&&(v===0||v===1)))throw Error('BAD_PUBLIC_INPUT');};
function trueP(phase,a,x,z){if(!PHASES.includes(phase))throw Error('BAD_WORLD');let y=base(a,x);if(a===1&&z===1&&((phase==='B'&&x===1)||(phase==='C'&&x===0)))y^=1;return y?.9:.1;}
function draw(seed,t,a,x,z,p,label){const h=createHash('sha256').update('csrr02:'+seed+':'+label+':'+t+':'+cell(a,x,z)).digest();return Number(h.readUInt32BE(0)/2**32<p);}
function risk(p,q){return p*(1-q)**2+(1-p)*q*q;}
function obsMismatch(r,y){input(r);if(y!==0&&y!==1)throw Error('BAD_OUTCOME');return Number(y!==base(r.a,r.x));}
const empty=()=>Array.from({length:4},()=>[[],[]]);
const push=(h,v)=>{h.push(v);if(h.length>W)h.shift();};
const majority=a=>a.reduce((s,v)=>s+v,0);
class PairedRepair{
  constructor(){this.hist=empty();this.flip=[false,false,false,false];this.ever=[false,false,false,false];this.visits=[0,0,0,0];this.promotions=0;this.reversions=0;this.reuses=0;this.action0_probes=0;this.action1_probes=0;}
  choose(x,z){const k=key(x,z),v=this.visits[k]++;if(this.hist[k][0].length<4)return 0;if(this.hist[k][1].length<8)return 1;return v%4===0?0:1;}
  predict(r){input(r);return oldP(r.a,r.x)+(r.a&&this.flip[key(r.x,r.z)]?(base(r.a,r.x)?-.8:.8):0);}
  update(r,y){const m=obsMismatch(r,y),k=key(r.x,r.z);this['action'+r.a+'_probes']++;push(this.hist[k][r.a],m);const h0=this.hist[k][0],h1=this.hist[k][1],n0=h0.length,n1=h1.length;
    if(n0<4||n1<8)return;const stable0=majority(h0)<=Math.floor(.25*n0),flipped1=majority(h1)>=Math.ceil(.75*n1),stable1=majority(h1)<=Math.floor(.25*n1);
    const next=stable0&&flipped1?true:stable1||!stable0?false:this.flip[k];if(next!==this.flip[k]){if(next){this.promotions++;if(this.ever[k])this.reuses++;this.ever[k]=true;}else this.reversions++;this.flip[k]=next;}
  }
  snapshot(){const payload=JSON.stringify({schema:'csrr02.paired.v1',hist:this.hist,flip:this.flip,ever:this.ever,visits:this.visits,promotions:this.promotions,reversions:this.reversions,reuses:this.reuses,action0_probes:this.action0_probes,action1_probes:this.action1_probes});return JSON.stringify({payload,digest:createHash('sha256').update(payload).digest('hex')});}
  static restore(s){let obj,v;try{obj=JSON.parse(s);if(typeof obj.payload!=='string'||createHash('sha256').update(obj.payload).digest('hex')!==obj.digest)throw Error();v=JSON.parse(obj.payload);}catch{throw Error('BAD_CHECKPOINT');}
    if(v.schema!=='csrr02.paired.v1'||!Array.isArray(v.hist)||v.hist.length!==4||!v.hist.every(a=>Array.isArray(a)&&a.length===2&&a.every(b=>Array.isArray(b)&&b.length<=W&&b.every(i=>i===0||i===1)))||
    !['flip','ever'].every(n=>Array.isArray(v[n])&&v[n].length===4&&v[n].every(Boolean.isBoolean??(i=>typeof i==='boolean')))||!Array.isArray(v.visits)||v.visits.length!==4||!v.visits.every(i=>Number.isSafeInteger(i)&&i>=0)||!['promotions','reversions','reuses','action0_probes','action1_probes'].every(n=>Number.isSafeInteger(v[n])&&v[n]>=0))throw Error('BAD_CHECKPOINT');
    const q=new PairedRepair();Object.assign(q,v);return q;
  }
}
class WindowBayes{
 constructor(){this.hist=Array.from({length:4},()=>[]);}
 predict(r){input(r);if(!r.a)return oldP(r.a,r.x);const h=this.hist[key(r.x,r.z)],n=h.length,m=majority(h);const logit=(2*m-n)*Math.log(9);const post=1/(1+Math.exp(-logit));return oldP(r.a,r.x)+(base(r.a,r.x)?-.8:.8)*post;}
 update(r,y){const m=obsMismatch(r,y);if(r.a)push(this.hist[key(r.x,r.z)],m);}
}
// Reproduce CSRR-01 local rule without importing its side-effectful research harness.
class PriorRepair{
 constructor(){this.hist=Array.from({length:8},()=>[]);this.flip=Array(8).fill(false);this.promotions=0;}
 predict(r){input(r);return oldP(r.a,r.x)+(this.flip[cell(r.a,r.x,r.z)]?(base(r.a,r.x)?-.8:.8):0);}
 update(r,y){const c=cell(r.a,r.x,r.z),h=this.hist[c];h.push(obsMismatch(r,y));if(h.length>8)h.shift();if(h.length<6)return;const m=majority(h);const next=m>=5?true:m<=1?false:this.flip[c];if(next&&!this.flip[c])this.promotions++;this.flip[c]=next;}
}
// Fully informed symbolic comparator knows possible exceptional context loci but NOT phase or observed labels ahead of time.
class SymbolicKnown extends WindowBayes{
 predict(r){if(r.a&&r.z!==1)return oldP(r.a,r.x);return super.predict(r);}
}
function makeModels(){return {paired:new PairedRepair(),passive:new PairedRepair(),prior:new PriorRepair(),bayes:new WindowBayes(),symbolic:new SymbolicKnown(),always1:new SymbolicKnown()};}
function score(seed,kind){const m=makeModels(),out=[],cold=null;let coldErrors=0,syntheticActions=Object.fromEntries(Object.keys(m).map(k=>[k,0]));
 for(let phaseIndex=0;phaseIndex<PHASES.length;phaseIndex++){
  const phase=kind==='null'?'A':PHASES[phaseIndex],total=Object.fromEntries(['raw',...Object.keys(m)].map(n=>[n,0]));
  const before={paired:m.paired.promotions,passive:m.passive.promotions,prior:m.prior.promotions};
  for(let step=0;step<STEPS;step++){
   const t=phaseIndex*STEPS+step,k=(5*t+seed)%4,x=(k>>1)&1,z=k&1;
   // Harness-only equal-support evaluation; no scores or phase are provided to any policy.
   for(let a=0;a<2;a++){
    const r={a,x,z},p=trueP(phase,a,x,z);total.raw+=risk(p,oldP(a,x))/2;
    for(const [name,model] of Object.entries(m))total[name]+=risk(p,model.predict(r))/2;
   }
   const aActive=m.paired.choose(x,z),aPassive=((Math.floor(t/4)+seed+x+z)%2),actions={paired:aActive,passive:aPassive,prior:aActive,bayes:aActive,symbolic:aActive,always1:1};
   for(const [name,model] of Object.entries(m)){
    const a=actions[name],r={a,x,z},y=draw(seed,t,a,x,z,trueP(phase,a,x,z),kind);model.update(r,y);syntheticActions[name]++;
   }
   if(cold){if(JSON.stringify(cold.flip)!==JSON.stringify(m.paired.flip)||cold.predict({a:1,x,z})!==m.paired.predict({a:1,x,z}))coldErrors++;
     const y=draw(seed,t,aActive,x,z,trueP(phase,aActive,x,z),kind);cold.update({a:aActive,x,z},y);cold.choose(x,z);
   }
   if(t===2*STEPS-1){cold=PairedRepair.restore(m.paired.snapshot());assert.equal(cold.snapshot(),m.paired.snapshot());}
  }
  out.push({phase,mean:Object.fromEntries(Object.entries(total).map(([name,val])=>[name,val/STEPS])),
   promotions:{paired:m.paired.promotions-before.paired,passive:m.passive.promotions-before.passive,prior:m.prior.promotions-before.prior},active:m.paired.flip.slice()});
 }
 return {seed,kind,phase:out,coldErrors,actions:syntheticActions,promotions:m.paired.promotions,priorPromotions:m.prior.promotions,activeEver:m.paired.ever,probeCounts:{a0:m.paired.action0_probes,a1:m.paired.action1_probes}};
}
function tests(){const r=new PairedRepair();assert.throws(()=>r.predict({a:1,x:0,z:1,y:1}),/BAD_PUBLIC_INPUT/);assert.throws(()=>r.update({a:1,x:0,z:1},2),/BAD_OUTCOME/);const snapshot=r.snapshot();let tampered=JSON.parse(snapshot);tampered.digest='0'.repeat(64);assert.throws(()=>PairedRepair.restore(JSON.stringify(tampered)),/BAD_CHECKPOINT/);assert.equal(PairedRepair.restore(snapshot).snapshot(),snapshot);}
tests();
const runs=SEEDS.flatMap(seed=>[score(seed,'changed'),score(seed,'null')]);
const selection=(kind)=>runs.filter(r=>r.kind===kind);
const mean=(kind,indices,name)=>selection(kind).reduce((s,r)=>s+indices.reduce((t,i)=>t+r.phase[i].mean[name],0),0)/(SEEDS.length*indices.length);
const change=[1,3,5],restore=[2,4],all=[0,1,2,3,4,5];
const diag={changed_vs_raw:mean('changed',change,'raw')-mean('changed',change,'paired'),changed_vs_passive:mean('changed',change,'passive')-mean('changed',change,'paired'),
 changed_vs_prior:mean('changed',change,'prior')-mean('changed',change,'paired'),changed_vs_bayes:mean('changed',change,'bayes')-mean('changed',change,'paired'),
 changed_vs_symbolic:mean('changed',change,'symbolic')-mean('changed',change,'paired'),changed_vs_always1:mean('changed',change,'always1')-mean('changed',change,'paired'),
 returned_old_drift:mean('changed',restore,'paired')-mean('changed',restore,'raw'),null_drift:mean('null',all,'paired')-mean('null',all,'raw'),null_prior_drift:mean('null',all,'prior')-mean('null',all,'raw')};
const changedBrier=Object.fromEntries(['raw','paired','passive','prior','bayes','symbolic','always1'].map(name=>[name,mean('changed',all,name)]));
const nullActivations=selection('null').reduce((s,r)=>s+r.promotions,0),oldControlsClean=selection('null').reduce((s,r)=>s+r.priorPromotions,0);
const coldMismatch=runs.reduce((s,r)=>s+r.coldErrors,0),actionsOK=runs.every(r=>Object.values(r.actions).every(v=>v===STEPS*PHASES.length));
const basic=diag.changed_vs_raw>=.005&&diag.returned_old_drift<=.02&&nullActivations===0&&coldMismatch===0&&actionsOK;
const strong=diag.changed_vs_prior>=.005&&diag.changed_vs_bayes>=.005&&diag.changed_vs_symbolic>=.005&&diag.changed_vs_always1>=.005;
const classification=!actionsOK||coldMismatch!==0?'INVALID_DEV_ONLY':!basic?'NEGATIVE_DEV_ONLY':strong?'ENGINEERING_ADVANTAGE_DEV_ONLY':'MIXED_DEV_ONLY';
console.log(JSON.stringify({schema:'csrr02.intervention-verified-structural-repair.dev.v1',source_only:true,source_actions:0,native_yggdrasil_used:false,scientific_gain_verified:false,
 seeds:SEEDS,phases:PHASES,steps_per_phase:STEPS,observations_per_policy:SEEDS.length*PHASES.length*STEPS*2,changed_brier:changedBrier,diagnostics:diag,
 null_promotions:nullActivations,null_prior_promotions:oldControlsClean,cold_prediction_mismatch:coldMismatch,actions_equal:actionsOK,
 runs:runs.map(r=>({seed:r.seed,kind:r.kind,promotions:r.promotions,prior_promotions:r.priorPromotions,probe_counts:r.probeCounts,active_ever:r.activeEver,phase:r.phase.map(p=>({phase:p.phase,promotions:p.promotions,active:p.active}))})),classification},null,2));
