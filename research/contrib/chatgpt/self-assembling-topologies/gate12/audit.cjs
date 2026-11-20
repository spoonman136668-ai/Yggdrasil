"use strict";
// Gate12 independent mathematical/model-order and receipt audit.
// Does not replace frozen numerical --verify replay. No hidden training authority.
const fs=require("fs"),path=require("path"),assert=require("assert").strict;
const dir=__dirname;
const v=JSON.parse(fs.readFileSync(path.join(dir,"result.json"),"utf8"));
const p=JSON.parse(fs.readFileSync(path.join(dir,"prereg.json"),"utf8"));
assert.equal(p.experiment_id,"GATE12-HIERARCHICAL-0-1-2-CAUSAL-ORDER-20261120");
assert.equal(v.prereg_commit,"d6a8e401530029018e54571219b62b8187649b36");
assert.equal(v.parent_candidate,"f867f50e85a722a8cab2f747ddfe7e3d828fb62a");
assert.equal(v.verdict,"SCIENTIFIC_NEGATIVE_OR_MIXED_DEV");
assert.equal(v.structural_verdict,"STRUCTURAL_SUPERIORITY_NOT_ESTABLISHED");
assert.equal(v.persistent_bytes_per_local_or_fixed,260);
assert.equal(v.bayes_nominal_bytes,2640);
const expected={pair:[16000,16063,64],unary:[19000,19031,32],parity3:[18000,18031,32],random:[17000,17031,32],biased_independent:[20000,20031,32]};
function meanCI(values){const n=values.length,m=values.reduce((a,b)=>a+b,0)/n,
  variance=values.reduce((a,x)=>a+(x-m)**2,0)/(n-1),margin=1.96*Math.sqrt(variance/n);
  return {mean:m,low:m-margin,high:m+margin};}
for(const [k,[first,last,n]]of Object.entries(expected)){
  const z=v.family[k];
  assert.deepEqual([z.seed_first,z.seed_last,z.seeds,z.worlds],[first,last,n,2*n]);
  assert.equal(z.accepted+z.zero_order,z.worlds);
  assert(z.correct_routes<=z.accepted);
  assert.equal(z.fixed_tie_passes,n);
  assert.equal(z.cold_passes,n);
  assert.equal(z.seed_gate11_gains.length,n);
  assert(Math.abs(z.scores.dynamic-z.scores.fixed)<=1e-12,"no dynamic structure benefit");
  for(const value of Object.values(z.scores))assert(value>=0&&value<=1);
  const c=meanCI(z.seed_gate11_gains),t=z.paired_gate11_gain;
  assert(Math.abs(c.mean-t.mean)<1e-9 && Math.abs(c.low-t.lower)<1e-9 && Math.abs(c.high-t.upper)<1e-9);
}
assert.equal(v.family.pair.true_pair_routes,115);
assert.equal(v.family.unary.true_unary_routes,64);
assert.equal(v.family.parity3.zero_order,64);
assert.equal(v.family.random.zero_order,63);
assert.equal(v.family.biased_independent.zero_order,64);
assert.equal(v.gates.pair_correct_at_least_116,false);
assert.equal(v.gates.unary_correct_at_least_58,true);
assert.equal(v.gates.parity_zero_at_least_58,true);
assert.equal(v.gates.random_zero_at_least_58,true);
assert.equal(v.gates.biased_zero_at_least_58,true);
assert.equal(v.gates.ood_macro_gain_at_least_0_045,true);
assert.equal(v.gates.in_family_loss_at_most_0_015,true);
assert.equal(v.gates.cold_all,true);
assert.equal(v.gates.fixed_identical_on_held,true);
const positive=v.family.pair;
const neg=[v.family.unary,v.family.parity3,v.family.random,v.family.biased_independent];
const ood=neg.reduce((s,z)=>s+z.scores.legacy-z.scores.dynamic,0)/4;
const inLoss=positive.scores.dynamic-positive.scores.legacy;
assert(Math.abs(ood-v.summary.macro_out_of_family_gain_vs_gate11)<1e-9);
assert(Math.abs(inLoss-v.summary.in_family_brier_loss_vs_gate11)<1e-9);
assert(ood>=0.045);
assert(inLoss<=0.015);
assert(v.family.unary.paired_gate11_gain.lower>0 && v.family.unary.paired_gate11_gain.mean>0.19);
assert(v.family.pair.scores.bayes<v.family.pair.scores.dynamic,"Bayes remains stronger on known-order pair");
function bit(v,k){return(v>>>k)&1;}
let pairTables=0,parityMinimum=8,unaryExplained=false;
for(let t=0;t<16;t++){
 const f=(a,b)=>(t>>>((a<<1)|b))&1;
 const both=(f(0,0)!==f(1,0)||f(0,1)!==f(1,1))&&
 (f(0,0)!==f(0,1)||f(1,0)!==f(1,1));
 if(both)pairTables++;
 if([0,1].every(a=>[0,1].every(b=>f(a,b)===a)))unaryExplained=true;
 for(let i=0;i<3;i++)for(let j=i+1;j<3;j++){
  let errors=0;
  for(let x=0;x<8;x++){
   const p=f(bit(x,i),bit(x,j));
   const parity=bit(x,0)^bit(x,1)^bit(x,2);
   if(p!==parity)errors++;
  }
  parityMinimum=Math.min(parityMinimum,errors);
 }
}
assert.equal(pairTables,10);
assert.equal(parityMinimum,4,"3-way parity cannot be modeled by 2 parents");
assert(unaryExplained,"unary relationship may be represented by redundant pair model");
process.stdout.write("GATE12_INDEPENDENT_MODEL_ORDER_AUDIT_PASS MIXED_DEV_NO_STRUCTURAL_GAIN\n");
