// CSRR-03: source-free generic Boolean mechanism induction and cold revival.
// Harness world tables are NOT passed to learners except to a labeled informed upper bound.
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';

const SEEDS = [1123, 2234, 3345];
const PHASES = ['A', 'B', 'A', 'C', 'A', 'B'];
const STEPS = 192, HIST = 32, RELIABILITY = 0.85;
const INPUTS = Array.from({length:8}, (_, i) => i);
const LAW = {
  A: i => ((i>>2)&1) ^ ((i>>1)&1) ^ (i&1),
  B: i => (((i>>2)&1) & (i&1)) ^ ((i>>1)&1),
  C: i => {const a=(i>>2)&1,x=(i>>1)&1,z=i&1;return a ? (x&z) : (x^z);},
};
const mask = fn => INPUTS.reduce((s,i)=>s|(fn(i)<<i),0);
const LAW_MASKS = Object.fromEntries(Object.entries(LAW).map(([k,v])=>[k,mask(v)]));
const probability = (mask,i) => (mask>>i)&1 ? RELIABILITY : 1-RELIABILITY;
const expectedBrier = (p,q) => p*(1-q)**2+(1-p)*q**2;
const hashObservation = (seed,t,i,p) => {
  const hash=createHash('sha256').update('CSRR03:'+seed+':'+t+':'+i).digest();
  return Number(hash.readUInt32BE(0)/2**32<p);
};
const bit = v => Number.isInteger(v) && (v===0||v===1);
const validateObs = (i,y) => {if(!Number.isInteger(i)||i<0||i>7||!bit(y))throw Error('BAD_PUBLIC_WITNESS');};
const sigmoidWeights = scores => {
  const m=Math.max(...scores),exp=scores.map(v=>Math.exp(v-m));
  const sum=exp.reduce((a,b)=>a+b,0);return exp.map(v=>v/sum);
};
const complexity = mask => {
  let n=0;
  for(let i=0;i<8;i++) for(const b of [1,2,4]) if((i&b)===0 && ((mask>>i)&1)!==((mask>>(i|b))&1)) n++;
  return n;
};
class Tournament {
  constructor(withArchive=true){
    this.hist=[];this.archive=[];this.withArchive=withArchive;this.leader=-1;this.streak=0;this.promotions=0;this.revivals=0;
  }
  scores(){
    const p=Math.log(RELIABILITY),q=Math.log(1-RELIABILITY);
    return INPUTS.flatMap((_,v)=>Array.from({length:32},(_,j)=>v*32+j)).map(m=>{
      let score=-0.32*complexity(m)+(this.withArchive&&this.archive.includes(m)?0.9:0);
      for(const [i,y] of this.hist)score+=(((m>>i)&1)===y?p:q);
      return score;
    });
  }
  predict(i){if(!Number.isInteger(i)||i<0||i>7)throw Error('BAD_PUBLIC_INPUT');
    const weights=sigmoidWeights(this.scores());
    return weights.reduce((v,w,m)=>v+w*probability(m,i),0);
  }
  observe(i,y){validateObs(i,y);this.hist.push([i,y]);if(this.hist.length>HIST)this.hist.shift();
    const scores=this.scores(),best=scores.indexOf(Math.max(...scores));
    if(best===this.leader)this.streak++;else{if(this.withArchive && this.leader!== -1 && this.archive.includes(best))this.revivals++;this.leader=best;this.streak=1;}
    if(this.withArchive&&this.hist.length===HIST&&this.streak>=8&&!this.archive.includes(best)){
      if(this.archive.length===4)this.archive.shift();
      this.archive.push(best);this.promotions++;
    }
  }
  snapshot(){const p=JSON.stringify({schema:'csrr03.tournament.v1',hist:this.hist,archive:this.archive,withArchive:this.withArchive,leader:this.leader,streak:this.streak,promotions:this.promotions,revivals:this.revivals});
    return JSON.stringify({payload:p,sha256:createHash('sha256').update(p).digest('hex')});}
  static restore(s){let obj,data;try{obj=JSON.parse(s);if(typeof obj.payload!=='string'||createHash('sha256').update(obj.payload).digest('hex')!==obj.sha256)throw Error();data=JSON.parse(obj.payload);}catch{throw Error('BAD_CHECKPOINT');}
    const validHist=Array.isArray(data.hist)&&data.hist.length<=HIST&&data.hist.every(r=>Array.isArray(r)&&r.length===2&&Number.isInteger(r[0])&&r[0]>=0&&r[0]<8&&bit(r[1]));
    const validArchive=Array.isArray(data.archive)&&data.archive.length<=4&&new Set(data.archive).size===data.archive.length&&data.archive.every(n=>Number.isInteger(n)&&n>=0&&n<256);
    if(data.schema!=='csrr03.tournament.v1'||!validHist||!validArchive||typeof data.withArchive!=='boolean'||!Number.isInteger(data.leader)||data.leader< -1||data.leader>=256||!['streak','promotions','revivals'].every(k=>Number.isSafeInteger(data[k])&&data[k]>=0))throw Error('BAD_CHECKPOINT');
    const r=new Tournament(data.withArchive);Object.assign(r,data);return r;
  }
}
class Counts {
  constructor(windowSize){this.windowSize=windowSize;this.hist=Array.from({length:8},()=>[]);}
  predict(i){if(!Number.isInteger(i)||i<0||i>7)throw Error('BAD_PUBLIC_INPUT');const h=this.hist[i],n=h.length;return (h.reduce((a,b)=>a+b,0)+1)/(n+2);}
  observe(i,y){validateObs(i,y);const h=this.hist[i];h.push(y);if(this.windowSize&&h.length>this.windowSize)h.shift();}
}
class InformedSymbolic {
  constructor(){this.hist=[];}
  predict(i){if(!Number.isInteger(i)||i<0||i>7)throw Error('BAD_PUBLIC_INPUT');
    const models=Object.values(LAW_MASKS),scores=models.map(m=>this.hist.reduce((v,[x,y])=>v+(((m>>x)&1)===y?Math.log(RELIABILITY):Math.log(1-RELIABILITY)),0));
    return sigmoidWeights(scores).reduce((p,w,j)=>p+w*probability(models[j],i),0);
  }
  observe(i,y){validateObs(i,y);this.hist.push([i,y]);if(this.hist.length>HIST)this.hist.shift();}
}
function selfTest(){
  assert.equal(new Set(Object.values(LAW_MASKS)).size,3,'distinct world laws');
  const t=new Tournament();assert.throws(()=>t.observe(8,1),/BAD_PUBLIC_WITNESS/);
  assert.throws(()=>t.predict(8),/BAD_PUBLIC_INPUT/);
  let checkpoint=t.snapshot(),bad=JSON.parse(checkpoint);bad.sha256='0'.repeat(64);
  assert.throws(()=>Tournament.restore(JSON.stringify(bad)),/BAD_CHECKPOINT/);
  assert.equal(Tournament.restore(checkpoint).snapshot(),checkpoint,'snapshot roundtrip');
  assert.equal(t.snapshot(),checkpoint,'negative controls preserve candidate');
  const c=new Counts(4);assert.throws(()=>c.observe(0,2),/BAD_PUBLIC_WITNESS/);
}
function run(seed){
  const agents={archive:new Tournament(true),no_archive:new Tournament(false),window_counts:new Counts(4),global_counts:new Counts(0),informed_symbolic:new InformedSymbolic()};
  const cold={clone:null,mismatch:0},phases=[];
  for(let k=0;k<PHASES.length;k++){
    const phase=PHASES[k],trueMask=LAW_MASKS[phase],scores={raw:0,archive:0,no_archive:0,window_counts:0,global_counts:0,informed_symbolic:0};
    let archiveStart=agents.archive.archive.slice(),promotionsStart=agents.archive.promotions;
    let early={raw:0,archive:0,no_archive:0,window_counts:0,global_counts:0,informed_symbolic:0};
    for(let j=0;j<STEPS;j++){
      const t=k*STEPS+j,i=(5*t+seed)%8;
      // Harness-only expected Brier across all public input combinations before one new observation.
      for(let target=0;target<8;target++){
        const p=probability(trueMask,target),predictions={raw:.5};
        for(const [name,agent] of Object.entries(agents))predictions[name]=agent.predict(target);
        if(cold.clone){if(Math.abs(predictions.archive-cold.clone.predict(target))>1e-12)cold.mismatch++;}
        for(const [name,pred] of Object.entries(predictions)){
          scores[name]+=expectedBrier(p,pred)/8;
          if(j<32)early[name]+=expectedBrier(p,pred)/8;
        }
      }
      const y=hashObservation(seed,t,i,probability(trueMask,i));
      for(const agent of Object.values(agents))agent.observe(i,y);
      if(cold.clone)cold.clone.observe(i,y);
      // Cold restart at a deterministic boundary; the restored instance receives identical future evidence.
      if(t===STEPS*2-1){cold.clone=Tournament.restore(agents.archive.snapshot());assert.equal(cold.clone.snapshot(),agents.archive.snapshot());}
    }
    phases.push({phase,index:k,brier:Object.fromEntries(Object.entries(scores).map(([n,v])=>[n,v/STEPS])),early32_brier:Object.fromEntries(Object.entries(early).map(([n,v])=>[n,v/32])),archive_before:archiveStart,archive_after:agents.archive.archive.slice(),new_archives:agents.archive.promotions-promotionsStart});
  }
  return {seed,phases,cold_prediction_mismatches:cold.mismatch,archive:agents.archive.archive,archive_promotions:agents.archive.promotions,source_actions:0};
}
selfTest();
if(process.argv.includes('--self-test')){console.log('CSRR03_SELF_TEST_PASS');process.exit(0);}
const runs=SEEDS.map(run),names=['raw','archive','no_archive','window_counts','global_counts','informed_symbolic'];
const avg=(indices,name,early=false)=>runs.reduce((s,r)=>s+indices.reduce((t,i)=>t+r.phases[i][early?'early32_brier':'brier'][name],0),0)/(runs.length*indices.length);
const all=[0,1,2,3,4,5],changed=[1,3,5],returns=[2,4];
const overall=Object.fromEntries(names.map(n=>[n,avg(all,n)]));
const diagnostics={changed_vs_raw:avg(changed,'raw')-avg(changed,'archive'),changed_vs_window:avg(changed,'window_counts')-avg(changed,'archive'),
 changed_vs_uncached:avg(changed,'no_archive')-avg(changed,'archive'),overall_vs_informed:overall.informed_symbolic-overall.archive,
 returning_first32_vs_uncached:avg(returns,'no_archive',true)-avg(returns,'archive',true),
 returning_first32_vs_window:avg(returns,'window_counts',true)-avg(returns,'archive',true),
 return_old_drift:avg(returns,'archive')-RELIABILITY*(1-RELIABILITY)};
const coldMismatch=runs.reduce((s,r)=>s+r.cold_prediction_mismatches,0);
const strongAdvantage=overall.informed_symbolic-overall.archive>=.005&&overall.window_counts-overall.archive>=.005;
const returnGain=diagnostics.returning_first32_vs_uncached>=.005;
const novelGain=diagnostics.changed_vs_raw>=.005;
const retention=diagnostics.return_old_drift<=.02;
const classification=coldMismatch?'INVALID_DEV_ONLY':!novelGain||!retention?'NEGATIVE_DEV_ONLY':strongAdvantage&&returnGain?'ENGINEERING_ADVANTAGE_DEV_ONLY':'MIXED_DEV_ONLY';
console.log(JSON.stringify({schema:'csrr03.generic-mechanism-induction.dev.v1',seeds:SEEDS,phase_sequence:PHASES,observations_per_agent:SEEDS.length*PHASES.length*STEPS,
 laws_not_given_to_candidate:true,finite_grammar_size:256,action_policy:'shared deterministic public input schedule',native_yggdrasil:false,protected_actions:0,scientific_gain_verified:false,
 overall_brier:overall,diagnostics,cold_prediction_mismatches:coldMismatch,per_seed:runs,classification},null,2));
