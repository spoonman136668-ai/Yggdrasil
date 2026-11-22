// CSRR-01: isolated, source-free public action-consequence structural regeneration study.
// Not native Yggdrasil training and not protected original-world first-use.
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';

const PHASES=['A','B','A','C','A','B'];
const SEEDS=[101,202,303];
const PER_PHASE=256;
const WINDOW=8;
const LOW=.1, HIGH=.9;
const bit=(v)=>Number.isInteger(v)&&(v===0||v===1);
function inputCheck(row){
  if(!row||Object.keys(row).sort().join(',')!=='a,x,z'||![row.a,row.x,row.z].every(bit))throw Error('BAD_PUBLIC_INPUT');
}
function cellOf(row){inputCheck(row);return (row.a<<2)|(row.x<<1)|row.z;}
function inputOf(cell){if(!Number.isInteger(cell)||cell<0||cell>7)throw Error('BAD_CELL');return {a:(cell>>2)&1,x:(cell>>1)&1,z:cell&1};}
function baseline(cell){const {a,x}=inputOf(cell);return a^x;}
function prob(cell,flipped){return (baseline(cell)^Number(flipped))?HIGH:LOW;}
function expectedBrier(actual,predicted){return actual*(1-predicted)**2+(1-actual)*predicted**2;}
// Only the harness knows the phase/world law; learners get public input and sampled outcome.
function worldProb(phase,cell){
  if(!PHASES.includes(phase))throw Error('BAD_PHASE');
  return prob(cell,(phase==='B'&&cell===7)||(phase==='C'&&cell===5));
}
function observed(seed,t,cell,p){
  const h=createHash('sha256').update('csrr01:'+seed+':'+t+':'+cell).digest();
  return h.readUInt32BE(0)/2**32<p?1:0;
}
function initHistory(){return Array.from({length:8},()=>[]);}
class Regenerator {
  constructor(){this.hist=initHistory();this.active=Array(8).fill(false);this.ever=Array(8).fill(false);this.promotions=0;this.reversions=0;this.reuses=0;}
  predict(row){return prob(cellOf(row),this.active[cellOf(row)]);}
  update(row,y){const cell=cellOf(row);if(!bit(y))throw Error('BAD_PUBLIC_CONSEQUENCE');
    const h=this.hist[cell], mismatched=Number(y!==baseline(cell));h.push(mismatched);if(h.length>WINDOW)h.shift();
    if(h.length<6)return;
    const n=h.reduce((a,b)=>a+b,0), next=n>=5?true:n<=1?false:this.active[cell];
    if(next!==this.active[cell]){if(next){this.promotions++;if(this.ever[cell])this.reuses++;this.ever[cell]=true;}else this.reversions++;this.active[cell]=next;}
  }
  snapshot(){const data={schema:'csrr01.regen.v1',hist:this.hist,active:this.active,ever:this.ever,promotions:this.promotions,reversions:this.reversions,reuses:this.reuses};
    const payload=JSON.stringify(data);const digest=createHash('sha256').update(payload).digest('hex');return JSON.stringify({payload,digest});}
  static restore(serialized){let v,d;try{const obj=JSON.parse(serialized);v=JSON.parse(obj.payload);d=obj.digest;if(createHash('sha256').update(obj.payload).digest('hex')!==d)throw Error();}catch{throw Error('BAD_CHECKPOINT');}
    if(v.schema!=='csrr01.regen.v1'||!Array.isArray(v.hist)||v.hist.length!==8||!v.hist.every(a=>Array.isArray(a)&&a.length<=8&&a.every(bit))||
      !['active','ever'].every(k=>Array.isArray(v[k])&&v[k].length===8&&v[k].every(x=>typeof x==='boolean'))||
      !['promotions','reversions','reuses'].every(k=>Number.isSafeInteger(v[k])&&v[k]>=0))throw Error('BAD_CHECKPOINT');
    const model=new Regenerator();Object.assign(model,v);return model;
  }
}
class ObservedCounts {
  constructor(window){this.window=window;this.hist=initHistory();}
  predict(row){const c=cellOf(row),h=this.hist[c];const posteriorFlip=(h.reduce((s,v)=>s+v,0)+.2)/(h.length+2);return prob(c,false)+(.8*(1-2*baseline(c)))*posteriorFlip;}
  update(row,y){const c=cellOf(row);if(!bit(y))throw Error('BAD_PUBLIC_CONSEQUENCE');this.hist[c].push(Number(y!==baseline(c)));if(this.window&&this.hist[c].length>this.window)this.hist[c].shift();}
}
// Strong, fully specified symbolic comparator: it knows the possible exception loci (5/7)
// and uses the same observation/history/hysteresis rule but NEVER receives true phase.
class SymbolicKnownMechanisms extends Regenerator {
  update(row,y){const c=cellOf(row);if(c===5||c===7)super.update(row,y);else {inputCheck(row);if(!bit(y))throw Error('BAD_PUBLIC_CONSEQUENCE');}}
}
function emptyMetrics(){return {raw:0,regen:0,global:0,window:0,symbolic:0};}
function run(seed){
  const regen=new Regenerator(),global=new ObservedCounts(0),window=new ObservedCounts(8),symbolic=new SymbolicKnownMechanisms();
  let cold=null,coldMismatches=0,observations=0;
  const phases=[];
  for(let pi=0;pi<PHASES.length;pi++){
    const phase=PHASES[pi],metrics=emptyMetrics(),dense=emptyMetrics();
    let promotionsBefore=regen.promotions,reversionsBefore=regen.reversions,reusesBefore=regen.reuses;
    let phaseFirstPromote=null,phaseFirstRestore=null;
    for(let i=0;i<PER_PHASE;i++){
      const t=pi*PER_PHASE+i;
      const cell=(5*t+seed)%8, publicRow=inputOf(cell),actual=worldProb(phase,cell);
      const preds={raw:prob(cell,false),regen:regen.predict(publicRow),global:global.predict(publicRow),window:window.predict(publicRow),symbolic:symbolic.predict(publicRow)};
      if(cold && cold.predict(publicRow)!==preds.regen)coldMismatches++;
      for(const [name,q] of Object.entries(preds))metrics[name]+=expectedBrier(actual,q);
      // Dense counterfactual evaluation is harness-only. It never feeds a learner.
      for(let c=0;c<8;c++){
        const r=inputOf(c),p=worldProb(phase,c);
        const all={raw:prob(c,false),regen:regen.predict(r),global:global.predict(r),window:window.predict(r),symbolic:symbolic.predict(r)};
        for(const [name,q] of Object.entries(all))dense[name]+=expectedBrier(p,q)/8;
      }
      const y=observed(seed,t,cell,actual);
      regen.update(publicRow,y);global.update(publicRow,y);window.update(publicRow,y);symbolic.update(publicRow,y);if(cold)cold.update(publicRow,y);
      if(regen.promotions>promotionsBefore && phaseFirstPromote===null)phaseFirstPromote=i+1;
      if(regen.reversions>reversionsBefore && phaseFirstRestore===null)phaseFirstRestore=i+1;
      observations++;
      if(t===2*PER_PHASE-1){cold=Regenerator.restore(regen.snapshot());assert.equal(cold.snapshot(),regen.snapshot(),'cold restore must roundtrip');}
    }
    phases.push({index:pi,world:phase,mean_brier:Object.fromEntries(Object.entries(metrics).map(([k,v])=>[k,v/PER_PHASE])),
      uniform_grid_brier:Object.fromEntries(Object.entries(dense).map(([k,v])=>[k,v/PER_PHASE])),
      activations:regen.promotions-promotionsBefore,reversions:regen.reversions-reversionsBefore,reuses:regen.reuses-reusesBefore,
      first_activation_step:phaseFirstPromote,first_reversion_step:phaseFirstRestore,active_exception_cells:regen.active.map((v,i)=>v?i:null).filter(v=>v!==null)});
  }
  return {seed,phases,observations,coldMismatches,final_snapshot_sha256:createHash('sha256').update(regen.snapshot()).digest('hex'),
    discovered_cells:regen.ever.map((v,i)=>v?i:null).filter(v=>v!==null),promotions:regen.promotions,reversions:regen.reversions,reuses:regen.reuses};
}
function exerciseControls(){const r=new Regenerator();assert.throws(()=>r.predict({a:1,x:0,z:1,y:1}),/BAD_PUBLIC_INPUT/);assert.throws(()=>r.update({a:1,x:0,z:1},2),/BAD_PUBLIC_CONSEQUENCE/);
  const old=r.snapshot(),bad=JSON.parse(old);bad.digest='0'.repeat(64);assert.throws(()=>Regenerator.restore(JSON.stringify(bad)),/BAD_CHECKPOINT/);
  assert.throws(()=>Regenerator.restore('{}'),/BAD_CHECKPOINT/);assert.equal(r.snapshot(),old,'failed restore cannot mutate current state');
  assert.throws(()=>r.predict({a:2,x:1,z:0}),/BAD_PUBLIC_INPUT/);
}
exerciseControls();
const runs=SEEDS.map(run);
assert.ok(runs.every(r=>r.observations===PHASES.length*PER_PHASE && r.coldMismatches===0),'matched observations and cold functional identity');
const pooled={};for(const name of ['raw','regen','global','window','symbolic']){pooled[name]=runs.reduce((s,r)=>s+r.phases.reduce((u,p)=>u+p.mean_brier[name],0),0)/(runs.length*PHASES.length);}
const changed=[1,3,5],restored=[2,4];
const meanFor=(group,name)=>runs.reduce((s,r)=>s+group.reduce((t,i)=>t+r.phases[i].mean_brier[name],0),0)/(runs.length*group.length);
const diagnostics={changed_regen_vs_raw_gain:meanFor(changed,'raw')-meanFor(changed,'regen'),changed_regen_vs_window_gain:meanFor(changed,'window')-meanFor(changed,'regen'),
  changed_regen_vs_symbolic_gain:meanFor(changed,'symbolic')-meanFor(changed,'regen'),restored_old_drift:meanFor(restored,'regen')-meanFor(restored,'raw'),
  whole_regen_vs_global_gain:pooled.global-pooled.regen,whole_regen_vs_window_gain:pooled.window-pooled.regen,whole_regen_vs_symbolic_gain:pooled.symbolic-pooled.regen};
const novelDetected=runs.every(r=>r.discovered_cells.includes(5)&&r.discovered_cells.includes(7));
const retentionOK=diagnostics.restored_old_drift<=.02;
const gain=diagnostics.changed_regen_vs_raw_gain>=.005;
const strongGain=diagnostics.whole_regen_vs_window_gain>=.005&&diagnostics.whole_regen_vs_symbolic_gain>=.005;
const classification=!novelDetected||!retentionOK||!gain?'NEGATIVE_DEV_ONLY':strongGain?'ENGINEERING_ADVANTAGE_DEV_ONLY':'MIXED_DEV_ONLY';
console.log(JSON.stringify({schema:'csrr01.synthetic-structural-regeneration.v1',parent_sha:'4d50f913324569824fe371252479ba8f4667febf',seeds:SEEDS,
  phase_sequence:PHASES,steps_per_phase:PER_PHASE,observations_per_control:runs.reduce((s,r)=>s+r.observations,0),
  synthetic_observations_only:true,protected_source_actions:0,native_yggdrasil_used:false,trained_donor_verified:false,scientific_gain_verified:false,
  capacity:{exception_cells:8,history_per_cell:WINDOW,public_bits_per_input:3},pooled_brier:pooled,diagnostics,
  cold_mismatch_total:runs.reduce((s,r)=>s+r.coldMismatches,0),novel_exception_locations_detected:novelDetected,
  runs,classification},null,2));
